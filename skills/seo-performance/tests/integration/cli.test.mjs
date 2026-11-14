/**
 * Integration: spawns scripts/seo.mjs against fixture sites. Deterministic,
 * offline (local serve only). Scenario numbers map to the skill spec tests.
 * NOTE: audits run against the skill's own `serve` subprocess — an
 * in-process http server deadlocks against the synchronous spawnSync audit.
 */
import { spawnSync, spawn } from 'node:child_process';
import { readFileSync, existsSync, rmSync, mkdirSync, writeFileSync, cpSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const SKILL = new URL('../..', import.meta.url).pathname;
const SEO = join(SKILL, 'scripts', 'seo.mjs');
const FIX = join(SKILL, 'tests', 'fixtures', 'site');
const run = (args, cwd = process.cwd()) => spawnSync('node', [SEO, ...args], { encoding: 'utf8', timeout: 60000, cwd });
const mk = (p) => { mkdirSync(p, { recursive: true }); return p; };
const tmp = (name) => mk(join(tmpdir(), `seoperf-it-${name}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`));
const jsonOf = (dir) => JSON.parse(readFileSync(join(dir, 'report.json'), 'utf8'));

async function serveFixtures(port) {
  const child = spawn('node', [SEO, 'serve', FIX, '--port', String(port)], { stdio: 'ignore' });
  const t0 = Date.now();
  for (;;) {
    try { const r = await fetch(`http://127.0.0.1:${port}/`); if (r.ok) break; } catch { /* starting */ }
    if (Date.now() - t0 > 8000) { child.kill(); throw new Error('serve did not start'); }
    await new Promise((r) => setTimeout(r, 150));
  }
  return { url: `http://127.0.0.1:${port}/`, close: () => child.kill() };
}

export default function (t) {
  // --- Scenario 4: technically broken website (broken links, sitemap, canonicals) ---
  t('IT4 broken-site fixture produces expected detector findings', () => {
    const dir = tmp('broken');
    const r = run(['audit', FIX, '--source-dist', FIX, '--out', dir]);
    const out = r.stdout + r.stderr;
    for (const probe of ['fetch-error', 'canonical', 'viewport-missing', 'sitemap-dead-urls', 'lastmod-future', 'description-missing'])
      if (!out.includes(probe)) throw new Error(`missing ${probe} in:\n${out}`);
    if (!/report: .*report\.md/.test(out)) throw new Error('no report path');
    const j = jsonOf(dir);
    if (!(j.findings.length > 5)) throw new Error('too few findings: ' + j.findings.length);
    rmSync(dir, { recursive: true, force: true });
  });

  // --- Scenario 9: no external APIs — offline run still finishes ---
  t('IT9 offline run completes with dataGaps and no fabricated numbers', () => {
    const dir = tmp('offline');
    const r = run(['audit', FIX, '--source-dist', FIX, '--out', dir, '--profile', 'strict']);
    if (r.status > 1) throw new Error('crashed: ' + r.stderr);
    const j = jsonOf(dir);
    if (!j.dataGaps.some((g) => /INP/.test(g))) throw new Error('INP gap not declared');
    if (!j.dataGaps.some((g) => /Search Console|rich/i.test(g))) throw new Error('offline tiers not declared');
    if (j.metrics.some((m) => m.metric === 'inp')) throw new Error('INP fabricated');
    rmSync(dir, { recursive: true, force: true });
  });

  // --- Scenario 6: structured data correct vs broken + content mismatch ---
  t('IT6 schema command flags broken JSON-LD and content mismatch', () => {
    const r = run(['schema', FIX, '--source-dist', FIX]);
    if (r.status !== 0) throw new Error(r.stderr);
    const j = JSON.parse(r.stdout.slice(r.stdout.indexOf('{')));
    const broken = j.results.find((x) => /schema-broken/.test(x.url));
    if (!broken || broken.verdict.tiers['valid-schema'] !== false) throw new Error('broken jsonld not caught:\n' + r.stdout.slice(0, 600));
    if (!broken.cross.length) throw new Error('content mismatch not caught');
  });

  // --- Scenario 7: i18n hreflang/Canonical group (de page = one-sided, must flag) ---
  t('IT7 i18n fixture: de page carries hreflang group, en reciprocal', async () => {
    const srv = await serveFixtures(8941);
    const dir = tmp('i18n');
    try {
      const r = run(['audit', srv.url, '--out', dir, '--max-pages', '10']);
      const out = r.stdout + r.stderr;
      const j = jsonOf(dir);
      if (j.findings.some((f) => f.id === 'i18n:hreflang-invalid-code')) throw new Error('false invalid hreflang on valid codes');
      if (!/pages: [2-9]|pages: 1[0-9]/.test(out)) throw new Error('crawl did not traverse:\n' + out);
      const urls = j.findings.flatMap((f) => f.urls ?? []);
      if (!urls.some((u) => /about/.test(u)) || !urls.some((u) => /schema-broken/.test(u)))
        throw new Error('locale/child pages not reached through server crawl');
    } finally { srv.close(); rmSync(dir, { recursive: true, force: true }); }
  });

  // --- Scenario 8: external URL read-only boundary ---
  t('IT8 local-server crawl respects same-host + max-pages', async () => {
    const srv = await serveFixtures(8942);
    const dir = tmp('ext');
    try {
      const r = run(['audit', srv.url, '--out', dir, '--max-pages', '2']);
      if (r.status > 1) throw new Error('crashed: ' + r.stderr);
      const j = jsonOf(dir);
      if (!(j.pagesMeasured <= 2)) throw new Error('max-pages exceeded: ' + j.pagesMeasured);
      if (!(j.pagesMeasured >= 1)) throw new Error('nothing crawled');
    } finally { srv.close(); rmSync(dir, { recursive: true, force: true }); }
  });

  // --- Scenario 5: performance regression detection through snapshots ---
  t('IT5 compare detects injected perf regression, hides noise within tolerance', () => {
    const dir = tmp('cmp');
    const snap = (lcp, t2) => ({ schema: 'seo-performance-snapshot/1', capturedAt: t2, name: 'n', project: {}, tools: { node: 'n' },
      pagesMeasured: 1, metrics: [{ url: 'u', metric: 'lcp', value: lcp, lowerIsBetter: true }],
      findings: [], counts: { critical: 0, high: 0, medium: 0, low: 0 }, dataGaps: [] });
    const a = join(dir, 'a.json'), b = join(dir, 'b.json');
    writeFileSync(a, JSON.stringify(snap(1000, '2026-01-01T00:00:00Z')));
    writeFileSync(b, JSON.stringify(snap(5000, '2026-01-02T00:00:00Z')));
    const reg = run(['compare', a, b]);
    if (!/regression/.test(reg.stdout)) throw new Error('regression not flagged:\n' + reg.stdout);
    writeFileSync(b, JSON.stringify(snap(1010, '2026-01-02T00:00:00Z')));
    if (/regression/.test(run(['compare', a, b]).stdout)) throw new Error('noise mislabeled regression');
    rmSync(dir, { recursive: true, force: true });
  });

  // --- Scenario 2/10: existing project fix flow keeps design/function intact ---
  t('IT2/10 fix dry-run proposes, apply edits only safe classes; diff reviewable', () => {
    const dir = tmp('fix');
    cpSync(FIX, dir, { recursive: true });
    const dry = run(['fix', dir, '--source-dist', dir, '--out', join(dir, '.rep')]);
    const dryJ = JSON.parse(dry.stdout.slice(dry.stdout.indexOf('{')));
    if (dryJ.mode !== 'dry-run') throw new Error('not dry-run:\n' + dry.stdout.slice(0, 400));
    if (readFileSync(join(dir, 'about.html'), 'utf8') !== readFileSync(join(FIX, 'about.html'), 'utf8'))
      throw new Error('dry-run wrote files');
    const ap = run(['fix', dir, '--source-dist', dir, '--out', join(dir, '.rep'), '--apply']);
    if (ap.status !== 0) throw new Error('apply failed: ' + ap.stderr.slice(0, 400));
    const aboutAfter = readFileSync(join(dir, 'about.html'), 'utf8');
    if (!aboutAfter.includes('viewport')) throw new Error('apply changed nothing (viewport should be injected)');
    if (!aboutAfter.includes('<h1>About the fixture</h1>') || !aboutAfter.includes('Deliberately broken'))
      throw new Error('content damaged by fix');
    if (!existsSync(join(dir, '.rep', 'fixes-applied.patch'))) throw new Error('no patch artifact');
    rmSync(dir, { recursive: true, force: true });
  });

  // --- ci gate + budgets ---
  t('CI gate exits non-zero on high-severity fixture breakage; budgets honored', () => {
    const dir = tmp('ci');
    const r = run(['ci', FIX, '--source-dist', FIX, '--out', dir]);
    if (r.status !== 1) throw new Error('expected fail exit on broken fixture, got ' + r.status + ':\n' + r.stdout);
    rmSync(dir, { recursive: true, force: true });
    const base = tmp('ciinit');
    writeFileSync(join(base, 'package.json'), '{"scripts":{"build":"true"}}');
    const init = run(['ci', base, '--init']);
    if (init.status !== 0 || !existsSync(join(base, 'lighthouserc.cjs')) || !existsSync(join(base, '.github/workflows/seo-performance.yml')))
      throw new Error('ci --init incomplete');
    if (!/module.exports/.test(readFileSync(join(base, 'lighthouserc.cjs'), 'utf8'))) throw new Error('lighthouserc not LHCI format');
    rmSync(base, { recursive: true, force: true });
  });

  // --- Scenario 3: React/Vite style CSR boundary detected (source-level honesty) ---
  t('IT3 source-level run on framework project stays honest (no built HTML => no fabricated findings)', () => {
    const dir = tmp('csr');
    writeFileSync(join(dir, 'package.json'), JSON.stringify({ dependencies: { react: '19.0.0', vite: '6.0.0' } }));
    const r = run(['audit', dir, '--out', join(dir, '.rep')]);
    const j = jsonOf(join(dir, '.rep'));
    if (!/source-level|serve|dist/.test(JSON.stringify(j.dataGaps)) && !/dist|serve|source/i.test(r.stdout))
      throw new Error('source-level honesty note missing:\n' + JSON.stringify(j.dataGaps) + r.stdout);
    rmSync(dir, { recursive: true, force: true });
  });

  // --- Scenario 1: new static site baseline stays clean-ish on good fixture ---
  t('IT1 good fixture home produces no false positives on core tags', () => {
    const dir = tmp('clean');
    run(['technical', FIX, '--source-dist', FIX, '--out', dir]);
    const j = jsonOf(dir);
    const home = j.findings.filter((f) => (f.urls || []).some((u) => /\/$|index\.html$/.test(u) && !/about|schema|de\//.test(u)));
    for (const falsePos of ['title-missing', 'description-missing', 'viewport-missing', 'charset-missing', 'h1-missing', 'canonical-missing', 'html-lang-missing'])
      if (home.some((f) => f.id.endsWith(falsePos))) throw new Error('false positive: ' + falsePos + ' on clean home');
    rmSync(dir, { recursive: true, force: true });
  });

  // --- monitor scaffolding ---
  t('monitor writes weekly workflow with cron', () => {
    const dir = tmp('mon');
    const r = run(['monitor', dir]);
    if (r.status !== 0) throw new Error(r.stderr);
    const wf = readFileSync(join(dir, '.github/workflows/seo-performance-weekly.yml'), 'utf8');
    if (!/cron:/.test(wf)) throw new Error('no cron in monitor workflow');
    rmSync(dir, { recursive: true, force: true });
  });

  // --- serve roundtrip: the skill's own static server hosts fixtures for audits ---
  t('serve command hosts fixtures end-to-end (spawn -> audit -> kill)', async () => {
    const srv = await serveFixtures(8943);
    const dir = tmp('serve');
    try {
      const r = run(['audit', srv.url, '--out', dir, '--max-pages', '6']);
      const j = jsonOf(dir);
      if (!(j.pagesMeasured >= 2)) throw new Error('serve+audit crawl found ' + j.pagesMeasured + ' pages');
      if (!j.findings.length) throw new Error('broken fixture through server yielded no findings');
      rmSync(dir, { recursive: true, force: true });
    } finally { srv.close(); }
  });
}
