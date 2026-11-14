#!/usr/bin/env node
// tests/run.mjs — reproducible validation of qa.mjs (the skill's core
// promise: evidence-only analysis + reporting, non-destructive output).
// Run: node tests/run.mjs  → prints PASS/FAIL per check + VERDICT line.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const qa = join(root, 'scripts', 'qa.mjs');
const tmp = mkdtempSync('/tmp/qa-test-');
let pass = 0, fail = 0;
const t = (name, fn) => {
  try { fn(); console.log(`PASS ${name}`); pass++; }
  catch (e) { console.log(`FAIL ${name}: ${e.message}`); fail++; }
};
const run = (...a) => execFileSync('node', [qa, ...a], { encoding: 'utf8', cwd: tmp });
const ok = (c, m) => { if (!c) throw new Error(m); };

// fixture web project: framework + runners + routes + CI + a test file
const fx = join(tmp, 'fx');
mkdirSync(join(fx, 'src/pages'), { recursive: true });
mkdirSync(join(fx, '.github/workflows'), { recursive: true });
writeFileSync(join(fx, 'package.json'), JSON.stringify({
  name: 'fx', type: 'module', packageManager: 'pnpm@9.0.0',
  scripts: { test: 'vitest run' },
  dependencies: { astro: '^7.0.0' }, devDependencies: { vitest: '^5.1.0', '@playwright/test': '^1.65.0' },
}));
writeFileSync(join(fx, 'pnpm-lock.yaml'), 'lockfileVersion: 9.0\n');
writeFileSync(join(fx, 'src/pages/index.astro'), '<h1>hi</h1>');
writeFileSync(join(fx, 'src/pages/cart.test.ts'), 'export {}');
writeFileSync(join(fx, '.github/workflows/ci.yml'), 'name: ci\n');

t('analyze.detects_stack', () => {
  const r = JSON.parse(run('analyze', fx));
  ok(r.detected.frameworks?.some(f => f.name === 'astro'), 'astro missing');
  ok(r.detected.packageManager?.name === 'pnpm', 'pnpm missing');
  ok(r.detected.testRunners.runners.some(x => x.name === 'vitest'), 'vitest missing');
  ok(r.detected.testRunners.runners.some(x => x.name === 'playwright-test'), 'pw missing');
  ok(r.detected.ci.workflows.includes('ci.yml'), 'ci missing');
  ok(r.detected.testFiles?.count === 1, 'test file discovery wrong');
});
t('analyze.separates_unknown', () => {
  const bare = join(tmp, 'bare'); mkdirSync(bare);
  writeFileSync(join(bare, 'index.html'), '<html></html>');
  const r = JSON.parse(run('analyze', bare));
  ok(r.unavailable.project?.includes('not a JS project'), 'static-site path broken');
});
t('analyze.skill_repo_itself', () => {
  const r = JSON.parse(run('analyze', root)); // skill dir has no package.json → static path, no crash
  ok(r.detected !== undefined, 'no structure');
});
t('report.md_and_html', () => {
  const src = join(tmp, 'results.json');
  writeFileSync(src, JSON.stringify({ project: 'fx', results: [
    { name: 'checkout', status: 'PASS', detail: 'chromium', evidence: 'tr/' },
    { name: 'webkit', status: 'NOT TESTED', detail: 'offline' },
    { name: 'cart', status: 'FAIL', detail: 'total', fix: 'money.ts' }],
    retest: ['cart FAIL→PASS'] }));
  const out = run('report', src, '--format', 'md,html', '--out', join(tmp, 'r.md'));
  ok(/r\.md\b/.test(out) && /r\.html\b/.test(out), 'no files');
  const md = readdirSync(tmp).filter(f => f.startsWith('r.md'));
  ok(md.length === 1, 'md missing');
  const h = readdirSync(tmp).filter(f => f.startsWith('r.html'));
  ok(h.length === 1, 'html missing');
});
t('report.non_destructive', () => {
  const src = join(tmp, 'results2.json');
  writeFileSync(src, JSON.stringify({ project: 'fx', results: [] }));
  writeFileSync(join(tmp, 'r.md'), 'ORIGINAL');
  run('report', src, '--format', 'md', '--out', join(tmp, 'r.md'));
  ok(readdirSync(tmp).some(f => f.startsWith('r-') && f.endsWith('.md')), 'no dated suffix');
  const first = readFileSync(join(tmp, 'r.md'), 'utf8');
  ok(first === 'ORIGINAL', 'overwrote existing report');
});
t('cli.bad_input_exits_nonzero', () => {
  let code = 0;
  try { run('report', join(tmp, 'nope.json')); } catch (e) { code = e.status; }
  ok(code === 2, `exit ${code} != 2`);
});

rmSync(tmp, { recursive: true, force: true });
console.log(`\n${pass + fail} checks: ${pass} pass, ${fail} fail`);
console.log(fail === 0 ? 'VERDICT PASS' : 'VERDICT FAIL');
process.exit(fail === 0 ? 0 : 1);
