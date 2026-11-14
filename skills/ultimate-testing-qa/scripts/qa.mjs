#!/usr/bin/env node
// qa.mjs — project QA analyzer + report renderer. Node stdlib only.
// Usage:
//   node qa.mjs analyze [dir] [--format json|md]
//   node qa.mjs report <results.json> [--format md|html] [--out <file>]
// analyze: detection facts (framework, runners, routes, CI, tests) with
//   detected/unavailable separation. report: renders a results file; never
//   overwrites, dated suffix on collision.

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, resolve, basename, extname } from 'node:path';

const args = process.argv.slice(2);
const command = args[0];
const rest = args.slice(1);

function flag(name, dflt) {
  const i = rest.indexOf(`--${name}`);
  if (i === -1) return dflt;
  return rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[i + 1] : true;
}
const positional = rest.filter((a, i) => !a.startsWith('--') && !(rest[i - 1] || '').startsWith('--'));

// ---------- helpers ----------
function readJSON(p) {
  try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; }
}
function readText(p, max = 200_000) {
  try { return readFileSync(p, 'utf8').slice(0, max); } catch { return null; }
}
function existsFile(p) { try { return statSync(p).isFile(); } catch { return false; } }
function existsDir(p) { try { return statSync(p).isDirectory(); } catch { return false; } }

// strip comments for jsonc-ish configs (vite.config.ts style is code; we only
// pattern-match, never eval).
function findTests(dir) {
  const hits = [];
  let count = 0;
  const skip = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.astro', 'out', 'target']);
  const walk = (d, depth) => {
    if (depth > 6 || count > 4000) return;
    let entries;
    try { entries = readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name.startsWith('.') && e.name !== '.github') continue;
      if (skip.has(e.name)) continue;
      const p = join(d, e.name);
      if (e.isDirectory()) { walk(p, depth + 1); continue; }
      count++;
      if (/\.(test|spec)\.(js|mjs|cjs|ts|tsx|jsx|vue|svelte)$/.test(e.name)
        || /^(test|tests|__tests__)$/.test(basename(dirnameOf(p))) && /\.(js|ts)$/.test(e.name)) {
        hits.push(p);
      }
    }
  };
  const dirnameOf = (p) => p.slice(0, p.lastIndexOf('/'));
  walk(dir, 0);
  return hits;
}

// ---------- analyze ----------
function analyze(root) {
  const detected = {};
  const unavailable = {};
  const notes = [];

  const pkg = readJSON(join(root, 'package.json'));
  if (!pkg) {
    return { root, detected: {}, unavailable: { project: 'no package.json — not a JS project; treat as static site' }, notes, detectedAt: date() };
  }
  const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
  const scripts = pkg.scripts || {};

  // package manager: lockfiles win, then packageManager field
  const locks = [
    ['pnpm-lock.yaml', 'pnpm'], ['yarn.lock', 'yarn'],
    ['package-lock.json', 'npm'], ['bun.lockb', 'bun'], ['bun.lock', 'bun'],
  ];
  const lock = locks.find(([f]) => existsFile(join(root, f)));
  if (lock) detected.packageManager = { name: lock[1], evidence: lock[0] };
  else if (pkg.packageManager) detected.packageManager = { name: String(pkg.packageManager).split('@')[0], evidence: 'packageManager field' };
  else unavailable.packageManager = 'no lockfile, no packageManager field';

  // framework detection (deps + config files)
  const fw = [];
  const conf = (f) => existsFile(join(root, f));
  if (deps.astro || conf('astro.config.mjs') || conf('astro.config.ts')) fw.push({ name: 'astro', version: deps.astro || null });
  if (deps.next || conf('next.config.mjs') || conf('next.config.ts') || conf('next.config.js')) fw.push({ name: 'next', version: deps.next || null });
  if (deps.nuxt) fw.push({ name: 'nuxt', version: deps.nuxt });
  if (deps.vue) fw.push({ name: 'vue', version: deps.vue });
  if (deps.react) fw.push({ name: 'react', version: deps.react });
  if (deps.svelte) fw.push({ name: 'svelte', version: deps.svelte });
  if (deps.angular || deps['@angular/core']) fw.push({ name: 'angular', version: deps['@angular/core'] });
  if (deps.vite) detected.buildTool = { name: 'vite', version: deps.vite };
  else if (conf('vite.config.ts') || conf('vite.config.js') || conf('vite.config.mjs')) detected.buildTool = { name: 'vite', version: 'unknown', evidence: 'config without dep' };
  else if (fw.some(f => f.name === 'astro')) detected.buildTool = { name: 'vite (via astro)', version: null };
  if (fw.length) detected.frameworks = fw;
  else if (!detected.buildTool) unavailable.framework = 'no known framework dependency or config';

  // rendering model heuristics
  const rendering = [];
  if (existsDir(join(root, 'src/pages')) || existsDir(join(root, 'pages'))) rendering.push('file-based routing detected (pages/ or src/pages/)');
  if (existsDir(join(root, 'src/app')) || existsDir(join(root, 'app'))) rendering.push('app-router style dirs detected');
  if (pkg.type === 'module') notes.push('ESM project ("type":"module")');
  const ssgish = fw.some(f => f.name === 'astro' || f.name === 'nuxt' || f.name === 'next');
  if (ssgish) rendering.push('SSR/SSG decision lives in framework config — read it before assuming CSR');
  if (rendering.length) detected.rendering = rendering;

  // typescript
  if (deps.typescript) detected.typescript = deps.typescript;
  else unavailable.typescript = 'no typescript dep';

  // monorepo
  if (existsFile(join(root, 'pnpm-workspace.yaml')) || pkg.workspaces) {
    detected.monorepo = { packages: Array.isArray(pkg.workspaces) ? pkg.workspaces.join(',') : (pkg.workspaces?.packages || 'see pnpm-workspace.yaml').toString() };
  }

  // test runners already present
  const runners = [];
  if (deps.vitest || deps['vitest']) runners.push({ name: 'vitest', version: deps.vitest || deps['vitest'] });
  if (deps['@playwright/test']) runners.push({ name: 'playwright-test', version: deps['@playwright/test'] });
  if (deps.playwright && !deps['@playwright/test']) runners.push({ name: 'playwright-lib', version: deps.playwright });
  if (deps.jest || scripts.test?.includes('jest')) runners.push({ name: 'jest', version: deps.jest || 'unknown' });
  if (deps.cypress) runners.push({ name: 'cypress', version: deps.cypress });
  const testConfigs = ['vitest.config.ts', 'vitest.config.mts', 'vitest.config.js', 'playwright.config.ts', 'playwright.config.js', 'vite.config.ts', 'vite.config.js']
    .filter(f => existsFile(join(root, f)));
  if (runners.length || testConfigs.length) {
    detected.testRunners = { runners, configs: testConfigs, testScript: scripts.test || null };
  } else {
    unavailable.testRunners = 'no runner deps, no runner configs, no test script — greenfield';
  }

  // existing test files
  const tests = findTests(root);
  if (tests.length) detected.testFiles = { count: tests.length, sample: tests.slice(0, 10).map(p => p.slice(root.length + 1)) };
  else unavailable.testFiles = 'no *.test.* / *.spec.* files found (depth 6, node_modules excluded)';

  // CI
  const wfDir = join(root, '.github/workflows');
  if (existsDir(wfDir)) {
    detected.ci = { system: 'github-actions', workflows: readdirSync(wfDir).filter(f => /\.(yml|yaml)$/.test(f)) };
  } else if (existsFile(join(root, '.gitlab-ci.yml'))) detected.ci = { system: 'gitlab-ci' };
  else unavailable.ci = 'no .github/workflows, no .gitlab-ci.yml';

  // docker
  if (existsFile(join(root, 'Dockerfile')) || existsFile(join(root, 'docker-compose.yml'))) detected.docker = true;

  // routes hint for E2E targeting
  if (conf('svelte.config.js') || fw.some(f => f.name === 'svelte')) detected.routeHint = 'src/routes/**.svelte (SvelteKit file routes)';
  if (fw.some(f => f.name === 'astro')) detected.routeHint = 'src/pages/**.astro + src/pages/**.md(x)';
  if (fw.some(f => f.name === 'next')) detected.routeHint = 'app/ or src/app/ (App Router) vs pages/ (Pages Router)';
  if (fw.some(f => f.name === 'nuxt')) detected.routeHint = 'pages/ (Nuxt file routes)';

  return { root, tool: 'ultimate-testing-qa/qa.mjs', detectedAt: date(), detected, unavailable, notes };
}
function date() { return new Date().toISOString().slice(0, 10); }

// ---------- report ----------
function renderMD(r) {
  const L = [];
  L.push(`# QA Report — ${r.project || 'project'}`);
  L.push(`\nGenerated ${new Date().toISOString()} · tool qa.mjs · source ${r.source || 'inline'}\n`);
  const statuses = ['PASS', 'FAIL', 'NEEDS REVIEW', 'NOT TESTED'];
  for (const s of statuses) {
    const items = (r.results || []).filter(x => String(x.status || '').toUpperCase() === s);
    if (!items.length) continue;
    L.push(`## ${s} (${items.length})\n`);
    for (const it of items) {
      L.push(`- **${it.name}**${it.detail ? ` — ${it.detail}` : ''}${it.evidence ? ` · evidence: ${it.evidence}` : ''}${it.fix ? ` · fix: ${it.fix}` : ''}`);
    }
    L.push('');
  }
  if (r.retest) { L.push('## Retest log\n'); for (const t of [].concat(r.retest)) L.push(`- ${t}`); L.push(''); }
  L.push('---');
  L.push('Automated results and manual review are separate; NOT TESTED is not PASS.');
  return L.join('\n') + '\n';
}
function esc(s) { return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function renderHTML(r) {
  const colors = { PASS: '#1a7f37', FAIL: '#c0392b', 'NEEDS REVIEW': '#b7791f', 'NOT TESTED': '#666' };
  const rows = (r.results || []).map(x => {
    const s = String(x.status || 'NOT TESTED').toUpperCase();
    return `<tr><td>${esc(x.name)}</td><td style="color:${colors[s] || '#333'}">${esc(s)}</td><td>${esc(x.detail)}</td><td>${esc(x.evidence)}</td><td>${esc(x.fix)}</td></tr>`;
  }).join('\n');
  return `<!doctype html><meta charset="utf-8"><title>QA Report ${esc(r.project || '')}</title>
<style>body{font-family:system-ui;max-width:960px;margin:2rem auto;padding:0 1rem;color:#111}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.4rem .6rem;font-size:.9rem;text-align:left}
th{background:#f6f6f6}</style>
<h1>QA Report — ${esc(r.project || 'project')}</h1>
<p>Generated ${new Date().toISOString()} · source ${esc(r.source || 'inline')} · automated ≠ conformance</p>
<table><thead><tr><th>Check</th><th>Status</th><th>Detail</th><th>Evidence</th><th>Fix</th></tr></thead>
<tbody>\n${rows}\n</tbody></table>`;
}

// ---------- main ----------
try {
  if (command === 'analyze') {
    const root = resolve(positional[0] || '.');
    const out = analyze(root);
    const fmt = flag('format', 'json');
    if (fmt === 'md') {
      console.log(['# Project analysis', '', '```json', JSON.stringify(out, null, 2), '```',
        '', 'detected = evidence-backed; unavailable = not found (report as NOT TESTED, never as clean).'].join('\n'));
    } else {
      console.log(JSON.stringify(out, null, 2));
    }
  } else if (command === 'report') {
    const src = positional[0];
    if (!src || !existsFile(src)) { console.error('report: pass a results JSON file (see references/reporting.md)'); process.exit(2); }
    const r = readJSON(src);
    if (!r) { console.error('report: invalid JSON'); process.exit(2); }
    const fmts = String(flag('format', 'md')).split(',');
    const outBase = flag('out', null);
    for (const f of fmts) {
      const text = f === 'html' ? renderHTML(r) : renderMD(r);
      let dest = outBase
        ? (/\.\w+$/.test(outBase) ? outBase.replace(/\.\w+$/, `.${f}`) : `${outBase}.${f}`)
        : (r.project ? `qa-report-${r.project}.${f}` : `qa-report.${f}`);
      if (existsFile(dest)) dest = dest.replace(/\.(\w+)$/, `-${Date.now()}.$1`); // never overwrite
      writeFileSync(dest, text);
      console.log(`wrote ${dest}`);
    }
  } else {
    console.log('usage: qa.mjs analyze [dir] [--format json|md] | qa.mjs report <results.json> [--format md,html] [--out file]');
  }
} catch (e) {
  console.error(`qa.mjs ${command} failed: ${e.message}`);
  process.exit(1);
}
