#!/usr/bin/env node
// ds-tokens-build.mjs — DTCG JSON → CSS custom props / TS module. Zero deps.
// Use when the project has NO style-dictionary; if it has one, use that.
// Source of truth = *.tokens.json; generated files are read-only.
// Usage: node ds-tokens-build.mjs <src.tokens.json> --out <dir> [--css|--ts|both]
// Theme layout: top-level groups matching --themes stay OUT of shared :root
// and render per [data-theme="…"] block; everything else is shared.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, resolve, basename } from 'node:path';

const args = process.argv.slice(2);
const src = args[0];
if (!src) { console.error('usage: ds-tokens-build.mjs <tokens.json> --out dir [--themes a,b] [--css|--ts|both]'); process.exit(2); }
const flag = (n, d) => { const i = args.indexOf(`--${n}`); return i < 0 ? d : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
const outDir = resolve(flag('out', 'build'));
const themes = String(flag('themes', '')).split(',').map((s) => s.trim()).filter(Boolean);
const want = flag('both', true) === 'both' || !flag('css', false) && !flag('ts', false) ? ['css', 'ts'] : [flag('css', false) && 'css', flag('ts', false) && 'ts'].filter(Boolean);

const doc = JSON.parse(readFileSync(src, 'utf8'));
const flat = new Map(); // name -> {shared, themed:{th:val}, type}
const kebab = (p) => p.replace(/\./g, '-').replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
const isToken = (o) => o && typeof o === 'object' && !Array.isArray(o) && '$value' in o;
const valueCSS = (v) => Array.isArray(v) ? v.join(' ') : typeof v === 'object' ? Object.entries(v).map(([k, x]) => `${k}: ${x}`).join('; ') : String(v);

function walk(node, path, themeOwner) {
  for (const [k, v] of Object.entries(node)) {
    if (k.startsWith('$')) continue;
    if (themes.includes(k) && !path && !themeOwner && !isToken(v)) { walk(v, '', k); continue; }
    const key = path ? `${path}.${k}` : k;
    if (isToken(v)) {
      let e = flat.get(key); if (!e) { e = { themed: {}, type: v.$type || null }; flat.set(key, e); }
      if (themeOwner) e.themed[themeOwner] = v.$value; else e.shared = v.$value;
    } else if (v && typeof v === 'object') walk(v, key, themeOwner);
  }
}
walk(doc, '', null);

// resolve aliases {a.b} within a theme (fallback shared); cycles/missing throw
const alias = (v) => typeof v === 'string' && /^\{([\w.$-]+)\}$/.test(v) ? v.slice(1, -1) : null;
function resolveVal(raw, theme, seen = []) {
  const t = alias(raw); if (t === null) return raw;
  if (seen.includes(t)) throw new Error(`circular alias ${[...seen, t].join('→')}`);
  const e = flat.get(t); if (!e) throw new Error(`missing token {${t}}`);
  const v = theme && e.themed[theme] !== undefined ? e.themed[theme] : e.shared;
  if (v === undefined) throw new Error(`no value for {${t}} in theme ${theme}`);
  return resolveVal(v, theme, [...seen, t]);
}
const decls = (theme) => [...flat.entries()]
  .filter(([, e]) => theme ? e.themed[theme] !== undefined : e.shared !== undefined)
  .map(([k, e]) => `  --${kebab(k)}: ${valueCSS(resolveVal(theme ? e.themed[theme] : e.shared, theme))};`)
  .join('\n');

const banner = `/* GENERATED from ${basename(src)} by ds-tokens-build.mjs — edit the source, rebuild. */`;
const tsBanner = `// GENERATED from ${basename(src)} by ds-tokens-build.mjs — edit the source, rebuild.`;

let written = [];
if (want.includes('css')) {
  let css = `${banner}\n:root {\n${decls(null)}\n}`;
  for (const th of themes) css += `\n[data-theme="${th}"] {\n${decls(th)}\n}`;
  const p = join(outDir, 'tokens.css'); mkdirSync(outDir, { recursive: true }); writeFileSync(p, css + '\n'); written.push(p);
}
if (want.includes('ts')) {
  const lines = [];
  for (const [k, e] of flat) {
    if (e.shared !== undefined) lines.push(`  '${kebab(k)}': ${JSON.stringify(resolveVal(e.shared, null))},`);
    else for (const th of themes) if (e.themed[th] !== undefined) lines.push(`  '${kebab(k)}-${kebab(th)}': ${JSON.stringify(resolveVal(e.themed[th], th))},`);
  }
  const p = join(outDir, 'tokens.ts'); mkdirSync(outDir, { recursive: true });
  writeFileSync(p, `${tsBanner}\nexport const tokens = {\n${lines.join('\n')}\n} as const;\nexport type TokenName = keyof typeof tokens;\n`);
  written.push(p);
}
console.log(written.map((p) => `wrote ${p}`).join('\n') + `\ntokens: ${flat.size} shared: ${[...flat.values()].filter((e) => e.shared !== undefined).length} themed: ${themes.join(',')}`);
