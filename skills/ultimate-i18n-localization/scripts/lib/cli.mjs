// cli.mjs — argument parsing + command implementations for the i18n CLIs.
// Commands: audit | check | fix | translate-plan | validate | pseudo | extract | report
// All output is evidence-only: measured numbers, files, versions. No guesses.

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, relative, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { auditProject, SEVERITY } from './audit.mjs';
import { pseudo, graphemeCount } from './pseudo.mjs';
import { loadCatalogDir, parseCatalog, flatten, serializePo } from './catalog.mjs';
import { normalizeLocale, isValidLocale, localeName, pluralCategories, isRtl } from './locales.mjs';
import { discover, walk } from './discover.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
export const VERSION = '1.0.0';

export function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { out._.push(a); continue; }
    const [k, v] = [a.slice(2), argv[i + 1]];
    if (v !== undefined && !v.startsWith('--')) { out[k] = v; i++; } else out[k] = true;
  }
  return out;
}

const root = (args) => (args.root ? new URL(String(args.root), `file://${process.cwd()}/`).pathname : process.cwd());
const rel = (r, p) => relative(r, p).replaceAll('\\', '/');

// ---------------- audit / check ----------------
export function cmdAudit(cmd, args) {
  const r = root(args);
  const result = auditProject(r, {
    referenceLocale: args.reference,
    localesDir: args['locales-dir'] ? new URL(String(args['locales-dir']), `file://${r}/`).pathname : undefined,
    failOn: args['fail-on'] || (cmd === 'check' ? 'HIGH' : 'HIGH'),
    seo: args.seo === false || args.noSeo ? false : true,
    staticAnalysis: args.static === false ? false : true,
  });
  const fmt = args.format || (cmd === 'check' ? 'text' : 'md');
  const body = fmt === 'json' ? JSON.stringify(result, null, 2) : render(result, { cmd });
  if (cmd === 'check') {
    const pass = result.blocking === 0;
    process.stdout.write(`${pass ? 'VERDICT PASS' : 'VERDICT FAIL'} blocking=${result.blocking} failOn=${args['fail-on'] || 'HIGH'} locales=${result.project.locales.join(',')}\n`);
  }
  if (args.out) { writeOut(r, args.out, body); }
  else process.stdout.write(body + '\n');
  if (cmd === 'check') return result.blocking === 0 ? 0 : 1;
  return 0;
}

// ---------------- fix ----------------
// Non-destructive repair ladder. Only additive edits:
//  1. missing keys inserted into JSON catalogs with source value + needs_translation marker comment sidecar
//  2. missing hreflang self-reference appended to static HTML
// Anything else stays a finding; we never rewrite existing translations.
export function cmdFix(args) {
  const r = root(args);
  const localesDir = args['locales-dir'] ? new URL(String(args['locales-dir']), `file://${r}/`).pathname : undefined;
  const opts = { referenceLocale: args.reference, localesDir, seo: true };
  const result = auditProject(r, opts);
  const applied = [], skipped = [];
  const reference = result.project.reference;
  if (!reference) { emit(args, { fixes: [], skipped: [{ why: 'no reference locale detected' }], applied: 0 }); return 0; }

  // pass 1: JSON missing-key insertion
  const audit2 = auditProject(r, { ...opts, seo: false, staticAnalysis: false });
  const missing = audit2.findings.filter((f) => f.type === 'missing-key');
  const byFileLocale = groupByLocale(audit2, missing);
  for (const [locale, keys] of byFileLocale) {
    const target = pickTargetFile(r, result, locale);
    if (!target || !target.endsWith('.json')) { skipped.push({ why: `no JSON target for locale ${locale}`, keys: keys.length }); continue; }
    const before = JSON.parse(readFileSync(target, 'utf8'));
    const flat = flatten(before);
    let changed = 0;
    for (const f of keys) {
      if (flat[f.key] === undefined) {
        setDeep(before, f.key, `TODO:${f.key}`);
        changed++;
      }
    }
    if (changed) {
      const outPath = args.dry ? null : target;
      if (outPath) writeFileSync(outPath, JSON.stringify(unflattenDeep(before), null, 2) + '\n');
      applied.push({ file: rel(r, target), locale, added: changed, mode: 'scaffold-source-value (needs translation)' });
    }
  }

  // pass 2: hreflang self-reference for static HTML with html lang + hreflang set but no self
  const selfFixes = audit2.findings.filter((f) => f.type === 'hreflang-no-self' && f.file);
  if (args.applyHtml !== false) {
    for (const f of selfFixes) {
      const file = join(r, f.file);
      if (!existsSync(file) || !file.endsWith('.html')) { skipped.push({ why: 'non-static page skipped', file: f.file }); continue; }
      const t = readFileSync(file, 'utf8');
      const locale = /lang="([^"]+)"/.exec(t)?.[1];
      const alt = /<link rel="alternate"[^>]*href="([^"]+)"/.exec(t)?.[1];
      if (!locale || !alt) { skipped.push({ why: 'cannot derive self href', file: f.file }); continue; }
      const inject = `  <link rel="alternate" hreflang="${locale}" href="${alt}">\n`;
      if (!t.includes(`hreflang="${locale}"`)) {
        const out = t.replace(/(\n\s*<link[^>]+canonical)/, inject + '$1');
        writeFileSync(file, out !== t ? out : t.replace('</head>', inject + '</head>'));
        applied.push({ file: f.file, locale, mode: 'hreflang self-reference appended' });
      }
    }
  }

  const remaining = auditProject(r, opts);
  const out = { applied, skipped, verified: remaining.blocking === 0, remainingBlocking: remaining.blocking, status: remaining.status };
  emit(args, out);
  return remaining.blocking ? 1 : 0;
}

// ---------------- validate ----------------
export function cmdValidate(args) {
  const r = root(args);
  const dir = args.dir ? new URL(String(args.dir), `file://${r}/`).pathname : (discover(r).i18n.localesDir || join(r, 'locales'));
  if (!existsSync(dir)) { process.stdout.write(`VERDICT FAIL dir missing: ${rel(r, dir)}\n`); return 1; }
  const files = walk(dir, { filter: (f) => /\.(json|ya?ml|csv|po|pot|ftl|xlf|xliff)$/.test(f) });
  let fail = 0;
  for (const f of files) {
    const fmt = f.split('.').pop();
    const res = parseCatalog(readFileSync(f, 'utf8'), fmt, {});
    if (res.error) { console.log(`FAIL ${rel(r, f)} — ${res.error}`); fail++; }
    else console.log(`ok   ${rel(r, f)} keys=${res.keys.size}`);
  }
  console.log(`VERDICT ${fail ? 'FAIL' : 'PASS'} files=${files.length} fail=${fail}`);
  return fail ? 1 : 0;
}

// ---------------- pseudo ----------------
export function cmdPseudo(args) {
  const r = root(args);
  const expand = args.expand !== undefined ? Number(args.expand) : 0.3;
  const rtl = args.rtl ? true : false;
  const text = args.text !== undefined ? String(args.text)
    : args.file ? readFileSync(new URL(String(args.file), `file://${r}/`).pathname, 'utf8') : null;
  if (text !== null) {
    process.stdout.write(pseudo(text, { expand, rtl }) + '\n');
    return 0;
  }
  const dir = args.dir ? new URL(String(args.dir), `file://${r}/`).pathname : (discover(r).i18n.localesDir || join(r, 'locales'));
  if (!existsSync(dir)) { console.log('no locales dir; pass --text or --dir'); return 1; }
  const outDir = join(dir, '..', 'locales-pseudo');
  for (const c of loadCatalogDir(dir, {})) {
    const parsed = parseCatalog(c.text, c.format, {});
    if (parsed.error || !parsed.keys) continue;
    const body = c.format === 'json'
      ? JSON.stringify(Object.fromEntries([...parsed.keys].map(([k, v]) => [k, pseudo(String(v), { expand, rtl })])), null, 2)
      : [...parsed.keys].map(([k, v]) => `${k}=${pseudo(String(v), { expand, rtl })}`).join('\n');
    if (!args.dry) {
      mkdirSync(outDir, { recursive: true });
      writeFileSync(join(outDir, basename(c.file).replace(/^[a-z]{2}(-[A-Za-z]{2,4})?/, 'pseudo')), body);
    }
    const src = [...parsed.keys.values()].reduce((n, v) => n + graphemeCount(String(v)), 0);
    const pst = [...parsed.keys.values()].reduce((n, v) => n + graphemeCount(pseudo(String(v), { expand, rtl })), 0);
    console.log(`ok ${rel(r, c.file)} graphemes ${src}->${pst} (+${Math.round((100 * (pst - src)) / Math.max(src, 1))}%)`);
  }
  console.log(`VERDICT PASS pseudo dir=${args.dry ? '(dry)' : rel(r, outDir)} expand=${expand} rtl=${rtl}`);
  return 0;
}

// ---------------- extract ----------------
// Collects translation keys used in code (t('k'), $t, tr("k"), i18n.t, formatMessage ids)
// and emits a base catalog skeleton for the reference locale.
export function cmdExtract(args) {
  const r = root(args);
  const info = discover(r);
  const reference = args.reference ? normalizeLocale(args.reference).toLowerCase() : null;
  const keys = new Map();
  const patterns = [
    /\b(?:i18n\.)?t\(\s*['"]([\w.-]{2,100})['"]/g,
    /\$\{\s*t\(\s*['"]([\w.-]{2,100})['"]\)/g,
    /\b(?:tr|\$t|__)\(\s*["']([^"'{}\n]{2,120})["']/g,
    /\bid:\s*['"]([\w.-]{2,100})['"]/g,
    /<Translation[\s\S]{0,80}?key="([\w.-]+)"/g,
  ];
  for (const f of info.sources) {
    if (/(?:locales?|i18n|lang|translation)s?\//.test(f) || /\.(test|spec)\./.test(f)) continue;
    const t = readFileSync(f, 'utf8');
    for (const re of patterns) {
      for (const m of t.matchAll(re)) {
        const k = m[1];
        if (!/^[a-z][\w.-]*$/.test(k) && !/^[\w ]{2,120}$/.test(k)) continue;
        if (/^(https?|defaultProps|className)$/.test(k)) continue;
        if (!keys.has(k)) keys.set(k, new Set());
        keys.get(k).add(rel(r, f));
      }
    }
  }
  const out = { generated: 'i18n-extract', keys: {} };
  for (const [k, files] of keys) out.keys[k] = { value: reference ? undefined : '', sourceFiles: [...files] };
  const json = JSON.stringify(out.keys, null, 2);
  if (args.out) writeFileSync(new URL(String(args.out), `file://${r}/`).pathname, json + '\n');
  else process.stdout.write(json + '\n');
  console.log(`VERDICT PASS keys=${keys.size} scanned=${info.sources.length}`);
  return 0;
}

// ---------------- report ----------------
export function cmdReport(args) {
  const r = root(args);
  const result = auditProject(r, { referenceLocale: args.reference, seo: true });
  const fmt = args.format || 'md';
  const body = fmt === 'json' ? JSON.stringify(result, null, 2)
    : fmt === 'html' ? html(render(result, { cmd: 'report' }), result)
    : render(result, { cmd: 'report' });
  if (args.out) writeOut(r, args.out, body);
  else process.stdout.write(body + '\n');
  return 0;
}

// ---------------- renderers ----------------
function render(result, { cmd }) {
  const p = result.project;
  const L = [];
  L.push('Ultimate i18n & Localization Audit', '');
  L.push(`Project: ${basename(result.root)}`);
  L.push(`Stack: ${p.stack.join(', ') || 'unknown'} · system: ${p.system || 'none'} · engine: ${p.engine || '-'}`);
  L.push(`Reference locale: ${p.reference || 'n/a'} · locales: ${p.locales.join(', ') || 'none found'}`);
  L.push(`Locales dir: ${p.localesDir || 'none found'} · libs: ${p.libs.map((l) => `${l.name}@${l.version}`).join(', ') || '-'}`);
  L.push('');
  L.push('Translation coverage:');
  if (Object.keys(result.coverage).length) for (const [l, c] of Object.entries(result.coverage)) L.push(`  ${l}: ${c}%`);
  else L.push('  (insufficient data — no reference catalog)');
  L.push('');
  L.push(`Detected issues (${result.findings.length}):`);
  for (const [t, n] of Object.entries(result.counts)) L.push(`  ${t}: ${n}`);
  L.push('');
  L.push(`Findings (blocking cutoff ${cmd === 'check' ? 'HIGH' : 'reported only'}):`);
  const sorted = [...result.findings].sort((a, b) => SEVERITY.indexOf(a.severity) - SEVERITY.indexOf(b.severity));
  for (const f of sorted.slice(0, 100)) {
    L.push(`  [${f.severity}${f.confirmed ? '' : '?'}] ${f.type}${f.file ? ' ' + f.file : ''}${f.key ? ' ' + f.key : ''}${f.locale ? ' (' + f.locale + ')' : ''} — ${f.detail}`);
  }
  if (sorted.length > 100) L.push(`  … +${sorted.length - 100} more`);
  L.push('');
  L.push('Status:', result.status);
  L.push('');
  L.push('Unverified or remaining: heuristic findings marked ? need human review.');
  return L.join('\n');
}
function html(md, result) {
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return `<!doctype html><meta charset="utf-8"><title>i18n audit</title><pre>${esc(md)}</pre>`;
}
function emit(args, out) {
  const body = args.format === 'text' ? JSON.stringify(out, null, 2) : JSON.stringify(out, null, 2);
  if (args.out) writeOut(process.cwd(), args.out, body);
  else process.stdout.write(body + '\n');
}
function writeOut(r, p, body) {
  const abs = new URL(String(p), `file://${r}/`).pathname;
  mkdirSync(dirname(abs), { recursive: true });
  writeFileSync(abs, body + (body.endsWith('\n') ? '' : '\n'));
  console.log(`written ${relative(r, abs)}`);
}
function groupByLocale(auditResult, findings) {
  const m = new Map();
  for (const f of findings) {
    if (!f.locale) continue;
    const list = m.get(f.locale) || [];
    list.push(f); m.set(f.locale, list);
  }
  return m;
}
function pickTargetFile(root, auditResult, locale) {
  const dir = auditResult.project.localesDir;
  if (!dir) return null;
  const base = join(root, dir);
  if (!existsSync(base)) return null;
  const cand = walk(base, { filter: (f) => basename(f).toLowerCase().startsWith(locale.split('-')[0]) && f.endsWith('.json') });
  return cand[0] || null;
}
function setDeep(obj, dottedPath, value) {
  const parts = dottedPath.split('.');
  let t = obj;
  for (const p of parts.slice(0, -1)) t = (t[p] = (t[p] && typeof t[p] === 'object') ? t[p] : {});
  t[parts.at(-1)] = value;
}
function unflattenDeep(o) { return o; } // objects already nested by setDeep

export async function main(argv) {
  const [cmd, ...rest] = argv;
  const args = parseArgs(rest);
  if (!cmd || cmd === 'help' || args.help) {
    process.stdout.write(`i18n ${VERSION} — ultimate i18n & localization CLI
usage: i18n <command> [options]
commands: audit | check | fix | validate | pseudo | extract | report | plan
options: --root DIR --locales-dir DIR --reference LOCALE --fail-on SEVERITY
         --format md|json|html --out FILE --expand 0.3 --rtl --text STR --file F --dry
`);
    return 0;
  }
  switch (cmd) {
    case 'audit': return cmdAudit('audit', args);
    case 'check': return cmdAudit('check', args);
    case 'fix': return cmdFix(args);
    case 'validate': return cmdValidate(args);
    case 'pseudo': return cmdPseudo(args);
    case 'extract': return cmdExtract(args);
    case 'report': return cmdReport(args);
    case 'plan': return cmdPlan(args);
    default: process.stderr.write(`unknown command ${cmd}\n`); return 2;
  }
}

// translate-plan: emits the structured worksheet a human/LLM translator fills.
function cmdPlan(args) {
  const r = root(args);
  const a = auditProject(r, { referenceLocale: args.reference, seo: false, staticAnalysis: false });
  const targets = (args.to || 'de').split(',').map((l) => normalizeLocale(l).toLowerCase());
  const plan = { reference: a.project.reference, targets: targets.map((l) => ({ locale: l, name: localeName(l), rtl: isRtl(l), pluralCategories: pluralCategories(l) || 'CLDR-table-missing' })), batches: [] };
  const missing = a.findings.filter((f) => f.type === 'missing-key');
  const chunk = 40;
  for (let i = 0; i < missing.length; i += chunk) plan.batches.push({ size: Math.min(chunk, missing.length - i), keys: missing.slice(i, i + chunk).map((f) => f.key) });
  const json = JSON.stringify(plan, null, 2);
  if (args.out) writeOut(r, args.out, json); else process.stdout.write(json + '\n');
  return 0;
}
