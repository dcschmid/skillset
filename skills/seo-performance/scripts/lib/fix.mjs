/**
 * fix.mjs — remediation engine. Dry-run default; apply writes files and a
 * reversible diff to <reportDir>/fixes/. Risky classes need approval flags.
 * Safe classes: static HTML meta/lang injection, robots.txt + sitemap edits.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs';
import { join, relative } from 'node:path';
import { spawnSync } from 'node:child_process';

const APPROVAL = ['redirects', 'canonical-changes', 'content-removal', 'architecture', 'framework-migration'];

/** @param findings from detectors; @returns plans (dry-run) or applied results */
export function planFixes(findings, { autoFixClasses = [], approvals = {}, projectDir = null } = {}) {
  const plans = [];
  for (const f of findings ?? []) {
    if (!f.autoFixClass || !autoFixClasses.includes(f.autoFixClass)) {
      plans.push({ finding: f.id, mode: f.autoFixClass ? 'needs-enable' : 'manual',
        detail: f.fix, risk: f.risk, files: f.files ?? [] });
      continue;
    }
    if (APPROVAL.includes(f.autoFixClass) && !approvals[f.autoFixClass])
      plans.push({ finding: f.id, mode: 'awaiting-approval', detail: f.fix, risk: f.risk, files: f.files ?? [] });
    else plans.push({ finding: f.id, mode: 'planned', autoFixClass: f.autoFixClass, urls: f.urls, detail: f.fix });
  }
  return plans;
}

/** Apply safe static-HTML fixes against a built HTML tree (framework out dir).
 *  Returns unified-ish text diff of everything touched. apply=false => dry-run. */
export function applyStaticHtmlFixes(htmlDir, { apply = false, reportDir = null, limit = 200 } = {}) {
  if (!existsSync(htmlDir)) return { status: 'NO_HTML_DIR', dir: htmlDir, changed: [] };
  const files = walkHtml(htmlDir).slice(0, limit);
  const changed = [];
  for (const f of files) {
    const before = readFileSync(f, 'utf8');
    let out = before;
    const edits = [];
    const head = /<head[^>]*>/i;
    if (!/<title[^>]*>[^<]+<\/title>/i.test(out) && head.test(out)) {
      out = out.replace(head, (m) => m + '\n<title>TODO set per-page title</title>');
      edits.push('title');
    }
    if (!/<meta[^>]+name=["']viewport["']/i.test(out) && head.test(out)) {
      out = out.replace(head, (m) => m + '\n<meta name="viewport" content="width=device-width, initial-scale=1">');
      edits.push('viewport');
    }
    const lang = /<html(?![^>]*\blang=)([^>]*)>/i;
    if (lang.test(out)) { out = out.replace(lang, (m, a) => `<html lang="en"${a}>`); edits.push('html-lang'); }
    const imgNoAlt = /<img(?![^>]*\balt=)([^>]*?)\/?>/gi;
    if (imgNoAlt.test(out)) { out = out.replace(imgNoAlt, (m, a) => `<img${a} alt="">`); edits.push('img-alt'); }
    if (edits.length) {
      changed.push({ file: relative(htmlDir, f), edits, diff: diff(before, out), bytes: out.length - before.length });
      if (apply) writeFileSync(f, out);
    }
  }
  const patch = changed.map((c) => `--- a/${c.file}\n+++ b/${c.file}\n${c.diff}`).join('\n');
  if (reportDir) { mkdirSync(reportDir, { recursive: true });
    writeFileSync(join(reportDir, apply ? 'fixes-applied.patch' : 'fixes-dry.patch'), patch || '# no changes\n'); }
  return { status: apply ? 'APPLIED' : 'DRY_RUN', dir: htmlDir, changed: changed.map((c) => ({ file: c.file, edits: c.edits })), files: changed.length,
    hint: 'review with: git diff' };
}

export function writeRobotsTxt(dir, { allow = [], disallow = [], sitemaps = [] }, { apply = true, reportDir = null } = {}) {
  const f = join(dir, 'robots.txt');
  const lines = ['User-agent: *'];
  for (const d of disallow) lines.push(`Disallow: ${d}`);
  for (const a of allow) lines.push(`Allow: ${a}`);
  if (!disallow.length && !allow.length) lines.push('Disallow:');
  for (const s of sitemaps) lines.push(`Sitemap: ${s}`);
  const txt = lines.join('\n') + '\n';
  const before = existsSync(f) ? readFileSync(f, 'utf8') : '';
  if (apply) writeFileSync(f, txt);
  if (reportDir) { mkdirSync(reportDir, { recursive: true }); writeFileSync(join(reportDir, 'robots.txt.patch'), diff(before, txt)); }
  return { file: f, status: apply ? 'WRITTEN' : 'DRY_RUN', content: txt };
}

export function rewriteSitemap(sitemapPath, { keep = (u) => true, apply = true } = {}) {
  if (!existsSync(sitemapPath)) return { status: 'ABSENT', file: sitemapPath };
  const raw = readFileSync(sitemapPath, 'utf8');
  const entries = [...raw.matchAll(/<url>([\s\S]*?)<\/url>/gi)].map((m) => {
    const loc = /<loc>([\s\S]*?)<\/loc>/i.exec(m[1])?.[1]?.trim();
    return { loc, block: m[0], keep: loc ? keep(loc) : false };
  });
  const out = raw.split(/<url>[\s\S]*?<\/url>/gi).length <= entries.length + 1
    ? raw.replace(/<url>[\s\S]*?<\/url>/gi, (m) => { const e = entries.find((x) => x.block === m); return e && e.keep ? e.block : ''; })
    : raw;
  if (apply) writeFileSync(sitemapPath, out);
  return { status: apply ? 'WRITTEN' : 'DRY_RUN', file: sitemapPath, removed: entries.filter((e) => !e.keep).length, kept: entries.filter((e) => e.keep).length };
}

export function gitStatus(dir) {
  const r = spawnSync('git', ['-C', dir, 'diff', '--stat'], { encoding: 'utf8', timeout: 15000 });
  return r.status === 0 ? r.stdout.trim() : null;
}

function walkHtml(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) { if (!['node_modules', '.git'].includes(e.name)) walkHtml(p, acc); }
    else if (e.name.endsWith('.html')) acc.push(p);
  }
  return acc;
}

function diff(a, b) {
  const al = a.split('\n'), bl = b.split('\n'), out = [];
  let i = 0, j = 0;
  while (i < al.length || j < bl.length) {
    if (al[i] === bl[j]) { out.push(' ' + al[i]); i++; j++; continue; }
    if (bl.slice(j, j + 3).join('\n').includes(al[i] ?? '\u0000')) { out.push('+' + bl[j]); j++; continue; }
    if (al[i] != null) out.push('-' + al[i]); i++;
  }
  return out.filter((l) => !l.startsWith(' ')).join('\n');
}
