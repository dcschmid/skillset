// audit.mjs — static i18n audit: catalogs, keys, placeholders, plurals,
// hardcoded UI text, hreflang/canonical, RTL. Severity-gated: only
// confirmed BLOCKER/HIGH may fail CI; suspicions are MEDIUM/LOW/INFO.
// Ladder: BLOCKER > HIGH > MEDIUM > LOW > INFO.

import { readFileSync } from 'node:fs';
import { relative } from 'node:path';
import { loadCatalogDir, parseCatalog } from './catalog.mjs';
import { diffPlaceholders, checkPluralKeys } from './placeholders.mjs';
import { baseLang, pluralCategories, isValidLocale, normalizeLocale, isRtl } from './locales.mjs';
import { unicodeFindings } from './pseudo.mjs';
import { discover, walk } from './discover.mjs';

export const SEVERITY = ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
const rank = (s) => SEVERITY.indexOf(s);

/**
 * auditProject(root, options) ->
 *  { project:{stack,system,engine,locales,reference,localesDir,libs},
 *    coverage:{locale:percent}, findings:[{severity,type,file?,key?,locale?,detail,confirmed}],
 *    counts:{type:n}, blocking:n, status:'pass'|'review-required'|'fail' }
 * findings with confirmed:false are heuristics — never CI blockers.
 * options: {referenceLocale, failOn, seo, staticAnalysis, localesDir}
 */
export function auditProject(root, options = {}) {
  const opts = { failOn: 'HIGH', seo: true, staticAnalysis: true, ...options };
  const info = discover(root);
  if (opts.localesDir) {
    info.i18n.localesDir = typeof opts.localesDir === 'string' && !opts.localesDir.startsWith('/')
      ? new URL(opts.localesDir, `file://${root}/`).pathname : String(opts.localesDir);
  }
  const findings = [];
  const push = (f) => findings.push({ confirmed: f.confirmed !== false, ...f });
  const rel = (p) => relative(root, p).replaceAll('\\', '/');

  // ---- 1. catalogs on disk ----
  let catalogs = [];
  if (info.i18n.localesDir) catalogs = loadCatalogDir(info.i18n.localesDir, { locales: info.i18n.locales });
  const byLocale = new Map();
  for (const c of catalogs) {
    const parsed = parseCatalog(c.text, c.format, {});
    if (parsed.error) {
      push({ severity: 'BLOCKER', type: 'catalog-invalid', file: rel(c.file), detail: parsed.error });
      continue;
    }
    c.keys = parsed.keys;
    let list = byLocale.get(c.locale);
    if (!list) byLocale.set(c.locale, (list = []));
    list.push(c);
  }

  // duplicate keys in flat JSON (JSON.parse silently keeps the last one)
  for (const c of catalogs.filter((c) => c.format === 'json' && isFlatJson(c.text))) {
    const seen = new Map();
    for (const m of c.text.matchAll(/"([^"\\]+)"\s*:/g)) seen.set(m[1], (seen.get(m[1]) || 0) + 1);
    for (const [k, n] of seen) if (n > 1) {
      push({ severity: 'HIGH', type: 'duplicate-key', file: rel(c.file), key: k, detail: `"${k}" defined ${n}x; last wins` });
    }
  }

  const onDisk = [...byLocale.keys()];
  const declared = uniqueSorted([...info.i18n.locales.map((l) => normalizeLocale(l).toLowerCase()).filter((l) => isValidLocale(l)), ...onDisk]);
  const reference = opts.referenceLocale
    ? normalizeLocale(opts.referenceLocale).toLowerCase()
    : (info.i18n.defaultLocale && declared.includes(info.i18n.defaultLocale.toLowerCase())
      ? info.i18n.defaultLocale.toLowerCase()
      : (declared.find((l) => l.startsWith('en')) || declared[0] || null));

  // ---- 2. cross-locale diff: missing/extra keys, placeholders, parity ----
  const coverage = {};
  if (reference && byLocale.size >= 1) {
    const refList = byLocale.get(reference);
    const refKeys = new Set(refList ? refList.flatMap((c) => [...c.keys.keys()]) : []);
    if (refKeys.size) {
      for (const [locale, list] of byLocale) {
        if (locale === reference) { coverage[locale] = 100; continue; }
        const keys = new Set(list.flatMap((c) => [...c.keys.keys()]));
        coverage[locale] = Math.round((1000 * countShared(keys, refKeys)) / refKeys.size) / 10;
        for (const k of refKeys) if (!keys.has(k)) {
          push({ severity: 'HIGH', type: 'missing-key', key: k, locale, file: info.i18n.localesDir ? rel(info.i18n.localesDir) : undefined, detail: `"${k}" missing in ${locale} (reference ${reference})` });
        }
        for (const k of keys) if (!refKeys.has(k)) {
          push({ severity: 'LOW', type: 'extra-key', key: k, locale, detail: `"${k}" in ${locale} absent from ${reference}` });
        }
        for (const k of refKeys) {
          if (!keys.has(k)) continue;
          const src = refList.map((c) => c.keys.get(k)).find((v) => v !== undefined);
          const tgt = list.map((c) => c.keys.get(k)).find((v) => v !== undefined);
          if (typeof src !== 'string' || typeof tgt !== 'string' || !src) continue;
          const d = diffPlaceholders(src, tgt);
          if (d.missing.length || d.extra.length) {
            push({ severity: 'HIGH', type: 'placeholder-mismatch', key: k, locale, detail: [d.missing.length && `missing ${d.missing.join(',')}`, d.extra.length && `extra ${d.extra.join(',')}`].filter(Boolean).join('; ') });
          }
          if (src === tgt && isTranslatableWord(src) && baseLang(locale) !== baseLang(reference)) {
            push({ severity: 'MEDIUM', type: 'untranslated', key: k, locale, detail: `identical to ${reference}: "${trunc(src, 40)}"`, confirmed: false });
          }
          for (const u of unicodeFindings(tgt, locale)) {
            push({ severity: u.type === 'mojibake' ? 'HIGH' : 'LOW', type: 'unicode-' + u.type, key: k, locale, detail: u.detail, confirmed: u.type !== 'bom' });
          }
          const cats = pluralCategories(locale);
          if (cats && /\b(zero|one|two|few|many|other):/.test(tgt)) {
            const leaf = {};
            for (const m of tgt.matchAll(/\b(zero|one|two|few|many|other):/g)) leaf[m[1]] = true;
            for (const p of checkPluralKeys(leaf, cats)) {
              push({ severity: 'HIGH', type: 'plural-categories', key: k, locale, detail: p.problem });
            }
          }
        }
      }
      // suffix plurals: _one/_other present but locale expects more/less
      for (const [locale, list] of byLocale) {
        const cats = pluralCategories(locale);
        if (!cats) {
          push({ severity: 'INFO', type: 'plural-unknown-locale', locale, detail: `no CLDR plural table for ${baseLang(locale)}; plural checks skipped for it` });
          continue;
        }
        const suffixCats = new Set();
        for (const c of list) for (const k of c.keys.keys()) { const s = suffixCat(k); if (s) suffixCats.add(s); }
        if (suffixCats.size) {
          const invalid = [...suffixCats].filter((c) => !cats.includes(c) && c !== 'other');
          if (invalid.length) push({ severity: 'HIGH', type: 'plural-suffix-invalid', locale, detail: `suffixes ${invalid.join(',')} invalid for ${baseLang(locale)} (has ${cats.join(',')})` });
        }
      }
    }
  }

  // ---- 3. hardcoded UI text (suspicion only) ----
  if (opts.staticAnalysis !== false && info.sources.length && (info.i18n.localesDir || info.i18n.system)) {
    let budget = 60;
    for (const f of info.sources.slice(0, 400)) {
      if (skipSource(f)) continue;
      if (budget <= 0) break;
      for (const s of hardcodedHits(readFileSync(f, 'utf8'), f)) {
        if (budget-- <= 0) break;
        push({ severity: 'MEDIUM', type: 'hardcoded-text', file: rel(f), key: s, detail: `visible-text suspect: "${trunc(s, 60)}"`, confirmed: false });
      }
    }
  }

  // ---- 4. international SEO (sites only) ----
  if (opts.seo !== false && info.isSite) auditSeo(root, push, declared, rel);

  // ---- 5. RTL sanity ----
  for (const l of declared.filter((l) => isRtl(l))) {
    for (const c of byLocale.get(l) || []) {
      for (const [k, v] of c.keys || []) {
        if (typeof v === 'string' && /[\u0600-\u06FF\u0590-\u05FF]/.test(v)) {
          if (!/[\u202B\u202E]|dir=|rtl/i.test(v) && /[A-Za-z0-9]/.test(v)) {
            push({ severity: 'INFO', type: 'rtl-isolation', key: k, locale: l, detail: 'RTL text mixed with latin/digits: verify bidi isolation at render site', confirmed: false });
          }
        }
      }
    }
  }

  const counts = {};
  for (const f of findings) counts[f.type] = (counts[f.type] || 0) + 1;
  const cutoff = rank(opts.failOn);
  const blocking = findings.filter((f) => f.confirmed && rank(f.severity) <= cutoff && f.severity !== 'INFO').length;
  const confirmed = findings.filter((f) => f.confirmed);
  return {
    root,
    project: {
      stack: info.stack, system: info.i18n.system, engine: info.gameEngine,
      locales: declared, reference,
      localesDir: info.i18n.localesDir ? rel(info.i18n.localesDir) : null,
      libs: info.i18nLibs,
    },
    coverage, findings, counts, blocking,
    status: blocking ? 'review-required' : confirmed.length ? 'pass-with-notes' : 'pass',
  };
}

// ---------- helpers ----------
const uniqueSorted = (a) => [...new Set(a)].sort();
const countShared = (a, b) => { let n = 0; for (const x of a) if (b.has(x)) n++; return n; };
const trunc = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
const suffixCat = (key) => /_(zero|one|two|few|many|other)$/.exec(key)?.[1] || null;
const isTranslatableWord = (s) => /\p{L}{3,}/u.test(s) && !/^(https?:|\/|[A-Z0-9_.-]+$)/.test(s.trim());

function isFlatJson(text) {
  // flat => every "key": sits at depth 1; cheap proxy: brace depth never exceeds 1
  let depth = 0, q = false, esc = false;
  for (const c of text) {
    if (esc) { esc = false; continue; }
    if (c === '\\') { esc = true; continue; }
    if (c === '"') { q = !q; continue; }
    if (q) continue;
    if (c === '{' || c === '[') depth++;
    if (c === '}' || c === ']') depth--;
    if (depth > 1) return false;
  }
  return true;
}

function skipSource(f) {
  return /(?:^|\/)(?:i18n|locales?|lang|translations?|_locales)\//.test(f)
    || /\.(test|spec|stories)\./.test(f) || /\.config\.(m?js|ts)$/.test(f)
    || /fixture|mock|\/scripts\/|\/tools\/|\/build\//.test(f)
    || /node_modules|\/dist\//.test(f);
}

function* hardcodedHits(text, file) {
  const seen = new Set();
  const yield_ = (s) => { const v = s.trim(); if (v.length > 2 && !seen.has(v)) { seen.add(v); return v; } return null; };
  if (/\.(tsx|jsx|astro|svelte|vue|html)$/.test(file)) {
    for (const m of text.matchAll(/>([A-ZÄÖÜ][^<>{}\n]{2,60})</g)) { const v = yield_(m[1]); if (v && isHumanText(v)) yield v; }
    for (const m of text.matchAll(/(?:label|placeholder|title|alt|aria-label)="([A-ZÄÖÜ][^"{}$\n]{2,60})"/g)) { const v = yield_(m[1]); if (v && isHumanText(v)) yield v; }
  }
  if (/\.(m?js|ts)$/.test(file) && !/\.(astro|svelte|vue|html)$/.test(file)) {
    for (const m of text.matchAll(/(?:title|message|label|heading|buttonText)\s*[:=]\s*"([A-ZÄÖÜ][^"\n]{2,80})"/g)) { const v = yield_(m[1]); if (v && isHumanText(v)) yield v; }
  }
}
function isHumanText(s) {
  if (/^[A-Z0-9_ .]+$/.test(s) && !/[a-zäöüßéèê]{2}/.test(s)) return false; // codes: "API KEY", "PDF"
  if (/^(OK|TODO|FIXME|HTTP|HTML|JSON|YAML|SVG|ID|URL)\b/.test(s)) return false;
  if (/[{}$`]|=>|\.\w+$/.test(s)) return false; // interpolation/code
  if (!/\s/.test(s) && !/[.,!?]$/.test(s)) return false; // single tokens are too noisy
  return true;
}

function auditSeo(root, push, declared, rel) {
  const langs = declared.filter((l) => l !== 'x-default');
  const htmlFiles = walk(root, { filter: (f) => /\.(html|astro)$/.test(f) && !/\/(dist|node_modules|\.vercel)\//.test(f) && !f.endsWith('404.html') });
  for (const f of htmlFiles.slice(0, 200)) {
    const t = readFileSync(f, 'utf8');
    const file = rel(f);
    if (!/<html/.test(t)) continue;
    const langM = t.match(/<html[^>]*\blang="([^"]+)"/);
    if (langM && !isValidLocale(langM[1])) push({ severity: 'HIGH', type: 'html-lang-invalid', file, detail: `lang="${langM[1]}" invalid` });
    if (!langM) push({ severity: 'MEDIUM', type: 'html-lang-missing', file, detail: 'no lang on <html>', confirmed: false });
    const self = langM?.[1]?.toLowerCase();

    const hreflangs = [];
    for (const m of t.matchAll(/<link[^>]+rel="alternate"[^>]*>/g)) {
      const h = /hreflang="([^"]+)"/.exec(m[0])?.[1], u = /href="([^"]+)"/.exec(m[0])?.[1];
      if (!h) continue;
      hreflangs.push({ h: h.toLowerCase(), u });
      if (!isValidLocale(h)) push({ severity: 'HIGH', type: 'hreflang-invalid', file, detail: `hreflang="${h}" invalid` });
      else if (h !== 'x-default' && langs.length && !langs.some((d) => d === h.toLowerCase() || d.startsWith(h.toLowerCase() + '-'))) {
        push({ severity: 'MEDIUM', type: 'hreflang-undeclared', file, detail: `hreflang="${h}" outside project locales [${langs.join(',')}]`, confirmed: false });
      }
      if (u && !/^https?:\/\//.test(u) && !u.startsWith('/')) push({ severity: 'LOW', type: 'hreflang-relative', file, detail: `href must be absolute: ${u}` });
      if (u && /index\.html|\.html($|\?)/.test(u)) push({ severity: 'LOW', type: 'hreflang-file-ext', file, detail: `target uses file extension: ${u}` });
    }
    if (hreflangs.length && self && self !== 'x-default' && !hreflangs.some((x) => x.h === self)) {
      push({ severity: 'HIGH', type: 'hreflang-no-self', file, detail: `no self hreflang for page locale ${self}` });
    }
    if (hreflangs.filter((x) => x.h === 'x-default').length > 1) push({ severity: 'LOW', type: 'hreflang-xdefault-multi', file, detail: 'multiple x-default entries', confirmed: false });
    // canonical coherence: self-canonical is CORRECT; flag only when canonical
    // resolves to a FOREIGN locale's URL (that merges two locales when indexed).
    const canon = /<link[^>]+rel="canonical"[^>]+href="([^"]+)"/.exec(t)?.[1];
    if (canon && hreflangs.length) {
      const canonPath = canon.replace(/^https?:\/\/[^/]+/, '').replace(/\/$/, '');
      for (const x of hreflangs) {
        if (!x.u) continue;
        const uPath = x.u.replace(/^https?:\/\/[^/]+/, '').replace(/\/$/, '');
        if (uPath === canonPath && x.h !== 'x-default' && self && x.h !== self) {
          push({ severity: 'HIGH', type: 'canonical-merges-locale', file, detail: `canonical=${canon} is ${x.h}'s URL on a ${self} page` });
        }
      }
    }
  }
  for (const f of walk(root, { filter: (f) => /sitemap(-index)?\.xml$/.test(f) && !/\/(dist|node_modules)\//.test(f), maxDepth: 4 })) {
    const t = readFileSync(f, 'utf8');
    for (const m of t.matchAll(/hreflang>([a-zA-Z-]+)</g)) {
      if (!isValidLocale(m[1])) push({ severity: 'HIGH', type: 'sitemap-hreflang-invalid', file: rel(f), detail: m[1] });
    }
  }
}

export const audit = auditProject;
