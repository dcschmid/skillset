#!/usr/bin/env node
// tests/run.mjs — reproducible validation of the design-system-ui skill's
// core promise: evidence-based AUDIT finds seeded inconsistency, token
// VALIDATION catches broken refs, FIX tooling (build) is reproducible,
// reports are non-destructive. Run: node tests/run.mjs → PASS/FAIL + VERDICT.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const ds = join(root, 'scripts', 'ds.mjs');
const build = join(root, 'assets', 'ds-tokens-build.mjs');
const messy = join(root, 'examples', 'fixture-messy');
const clean = join(root, 'examples', 'fixture-clean');
const tmp = mkdtempSync('/tmp/dsui-test-');
let pass = 0, fail = 0;
const t = (name, fn) => { try { fn(); console.log(`PASS ${name}`); pass++; } catch (e) { console.log(`FAIL ${name}: ${e.message}`); fail++; } };
const run = (bin, a) => execFileSync('node', [bin, ...a], { encoding: 'utf8' });
const dsRun = (...a) => run(ds, a);
const ok = (c, m) => { if (!c) throw new Error(m); };
const J = (s) => JSON.parse(s);

// ---- Test A: token validation (dirty source → P0s; clean → exit 0) ----
t('tokens: cycles+missing refs reported, exit 1', () => {
  const f = join(tmp, 'bad.tokens.json');
  writeFileSync(f, JSON.stringify({
    a: { '$type': 'color', '$value': '{b}' }, b: { '$type': 'color', '$value': '{a}' },
    m: { '$type': 'color', '$value': '{nope.x}' },
    t: { '$type': 'dimension', '$value': '#fff' },
  }));
  let out = '', code = 0;
  try { out = dsRun('tokens', f); } catch (e) { code = e.status; out = e.stdout; }
  const r = J(out);
  ok(code === 1, `exit ${code} (P0 must fail CI gate)`);
  const codes = r.problems.map((p) => p.code);
  ok(codes.includes('circular-ref') && codes.includes('missing-ref') && codes.includes('type-mismatch'), 'P0/P1 codes present');
});
t('tokens: fixture-messy source validates (0 P0, exit 0)', () => {
  const out = dsRun('tokens', join(messy, 'store.tokens.json'), '--themes', 'light,dark');
  const r = J(out);
  ok(r.stats.tokens >= 18 && r.stats.themes === 2, `stats: ${JSON.stringify(r.stats)}`);
  ok(!r.problems.some((p) => p.severity === 'P0'), 'no P0');
  ok(r.resolved['action-primary'].themes.dark === '#7fb0d0', 'theme alias resolution');
});
t('tokens: theme-parity gap detected', () => {
  const f = join(tmp, 'gap.tokens.json');
  writeFileSync(f, JSON.stringify({ x: { '$type': 'color', '$value': '#fff' }, light: { y: { '$type': 'color', '$value': '#fff' } }, dark: { y: { '$type': 'color', '$value': '#000' }, z: { '$type': 'color', '$value': '#111' } } }));
  const r = J(dsRun('tokens', f, '--themes', 'light,dark'));
  ok(r.problems.some((p) => p.code === 'theme-parity' && p.where.startsWith('z')), 'z missing in light → parity');
});

// ---- Test E: token change → reproducible build + regression detectable ----
t('build: deterministic CSS/TS from source; theme blocks present', () => {
  const out1 = join(tmp, 'b1'), out2 = join(tmp, 'b2');
  run(build, [join(messy, 'store.tokens.json'), '--out', out1, '--themes', 'light,dark', '--css']);
  run(build, [join(messy, 'store.tokens.json'), '--out', out2, '--themes', 'light,dark', '--css']);
  ok(readFileSync(join(out1, 'tokens.css'), 'utf8') === readFileSync(join(out2, 'tokens.css'), 'utf8'), 'regen differs');
  const css = readFileSync(join(out1, 'tokens.css'), 'utf8');
  ok(css.includes('[data-theme="dark"]') && css.includes('--background-primary: #111827'), 'dark block correct');
  ok(/GENERATED/.test(css.split('\n')[0]), 'read-only banner');
  // regression detection: change one primitive → only its downstream moves
  const src = J(readFileSync(join(messy, 'store.tokens.json'), 'utf8'));
  src.color['steel-500']['$value'] = '#0055aa';
  const f3 = join(tmp, 'changed.tokens.json'); writeFileSync(f3, JSON.stringify(src));
  const out3 = join(tmp, 'b3'); run(build, [f3, '--out', out3, '--themes', 'light,dark', '--css']);
  const d1 = css.split('\n').filter((l, i) => l !== readFileSync(join(out3, 'tokens.css'), 'utf8').split('\n')[i]);
  ok(d1.length === 4, `diff scoped to steel-500 chain (shared+2 themes+ts-free): got ${d1.length}\n${d1.join('\n')}`);
});

// ---- Test B: AUDIT finds seeded inconsistencies ----
t('audit: fixture-messy → P0 focus + hardcoded colors + dupes', () => {
  const r = J(dsRun('audit', messy, '--max-files', '50'));
  const rules = r.findings.map((f) => f.rule);
  ok(r.findings.some((f) => f.severity === 'P0' && f.rule === 'focus-hidden'), 'outline:none caught as P0');
  const hex = r.findings.find((f) => f.rule === 'hardcoded-color' && f.detail.includes('#3f5f7f'));
  ok(hex && /[3-9]×/.test(hex.detail), 'repeated hex with count');
  ok(/styles\.css:\d+/.test(hex.evidence), 'file:line evidence');
  ok(rules.includes('duplicate-declaration'), '.card display dup');
  ok(r.findings.some((f) => f.rule === 'spacing-scale' || f.rule === 'type-scale'), 'scale scatter');
});
t('audit: fixture-clean → quiet (0 P0/P1)', () => {
  const r = J(dsRun('audit', clean, '--max-files', '50'));
  const loud = r.findings.filter((f) => f.severity === 'P0' || f.severity === 'P1');
  ok(loud.length === 0, `expected quiet, got ${JSON.stringify(loud)}`);
  ok(r.findings.length <= 3, `residual P2/P3 only, got ${r.findings.length}`);
});

// ---- Test C/D: a11y + motion signals surfaced ----
t('audit: reduced-motion gap + mid-luminance contrast review flagged', () => {
  const r = J(dsRun('audit', messy, '--max-files', '50'));
  ok(r.findings.some((f) => f.rule === 'reduced-motion'), 'web motion w/o reduced-motion fallback');
  ok(r.findings.some((f) => f.rule === 'contrast-review' && f.kind === 'heuristic'), 'contrast-review is heuristic');
});

// ---- report: renders + never overwrites ----
t('report: md/html render; existing file → dated suffix, not overwrite', () => {
  const src = join(tmp, 'f.json'); writeFileSync(src, JSON.stringify(J(dsRun('audit', messy, '--max-files', '50'))));
  const dest = join(tmp, 'rep.md'); writeFileSync(dest, 'ORIG');
  dsRun('report', src, '--format', 'md', '--out', dest);
  ok(readFileSync(dest, 'utf8') === 'ORIG', 'original untouched');
  ok(readdirSync(tmp).some((f) => /^rep-\d{4}-\d{2}-\d{2}\.md$/.test(f)), 'dated sibling written');
  ok(dsRun('report', src, '--format', 'html').includes('<table>'), 'html table');
});

// ---- detect: facts not decisions ----
t('detect: separates detected/unavailable', () => {
  const pkg = join(tmp, 'proj'); mkdirSync(join(pkg, 'src'), { recursive: true });
  writeFileSync(join(pkg, 'package.json'), JSON.stringify({ dependencies: { astro: '^5.0.0', tailwindcss: '^4.0.0' } }));
  writeFileSync(join(pkg, 'src', 'app.astro'), '<div style="color:#123456">hi</div>');
  const r = J(dsRun('detect', pkg));
  ok(r.detected.some((d) => d.what === 'framework:astro'), 'astro fact');
  ok(r.detected.some((d) => d.what === 'styling:tailwind'), 'tailwind fact');
  ok(r.unavailable.some((u) => u.what === 'theming:dark'), 'dark absent → unavailable (NOT clean)');
});

// ---- skill self-consistency ----
t('skill: SKILL.md frontmatter + referenced files exist', () => {
  const md = readFileSync(join(root, 'SKILL.md'), 'utf8');
  ok(/^---\nname: design-system-ui\n/.test(md), 'frontmatter name matches dir');
  const refs = [...md.matchAll(/(?:references|assets|scripts|examples)\/[\w./-]+/g)].map((m) => m[0]);
  const missing = [...new Set(refs)].filter((p) => !existsSync(join(root, p)) && !existsSync(join(root, p.replace(/\.md$/, '.md'))));
  ok(missing.length === 0, `missing: ${missing.join(', ')}`);
});

console.log(`\n${pass} passed, ${fail} failed`);
console.log(fail === 0 ? 'VERDICT: PASS' : 'VERDICT: FAIL');
process.exit(fail ? 1 : 0);
