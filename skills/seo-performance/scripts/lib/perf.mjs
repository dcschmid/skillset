/**
 * perf.mjs — optional integrations with local measurement tools.
 * Strategy: prefer project-local deps, then npx --no-install pinned calls,
 * never system installs. Without tools: structured UNAVAILABLE results —
 * the audit continues on HTTP-only data and says so (never fabricates).
 */
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const run = (cmd, args, opts = {}) => {
  try {
    const r = spawnSync(cmd, args, { encoding: 'utf8', timeout: opts.timeout ?? 180000, maxBuffer: 20 * 1024 * 1024, shell: false, ...opts });
    return { code: r.status, out: (r.stdout ?? '') + (r.stderr ?? '') };
  } catch (e) { return { code: -1, out: String(e.message) }; }
};

export function toolVersions(cwd = process.cwd()) {
  const installed = (name) => { try {
    const p = join(cwd, 'node_modules', name, 'package.json');
    return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')).version : null; } catch { return null; } };
  const v = (cmd, args) => { const r = run(cmd, args, { timeout: 30000 }); return r.code === 0 ? r.out.trim().split('\n')[0] : null; };
  return {
    node: process.version,
    lighthouse: installed('lighthouse') ?? v('npx', ['--no-install', 'lighthouse', '--version'], ),
    lhci: installed('@lhci/cli') ?? v('npx', ['--no-install', 'lhci', '--version']),
    unlighthouse: v('npx', ['--no-install', 'unlighthouse', '--version']),
    playwright: installed('playwright') ?? installed('@playwright/test'),
  };
}

/** One Lighthouse lab run, JSON out. Scores are lab data — labelled as such. */
export function lighthouseRun(url, { cwd = process.cwd(), formFactor = 'mobile', outPath = null, chromePath = null } = {}) {
  const args = [url, '--output=json', '--only-categories=seo,best-practices,performance', '--chrome-flags=--headless --no-sandbox --disable-gpu', `--form-factor=${formFactor}`, `--output-path=${outPath ?? '/tmp/lh-' + Date.now() + '.json'}`];
  if (chromePath) args.push(`--chrome-path=${chromePath}`);
  const r = run('npx', ['--no-install', 'lighthouse', ...args], { cwd, timeout: 240000 });
  if (r.code !== 0) return { available: false, reason: 'lighthouse failed: ' + r.out.slice(-400) };
  try {
    const file = args.find((a) => a.startsWith('--output-path=')).split('=')[1];
    const j = JSON.parse(readFileSync(file, 'utf8'));
    const a = (id) => j.audits?.[id]?.numericValue ?? null;
    return { available: true, source: 'lighthouse-lab', formFactor,
      scores: { performance: j.categories?.performance?.score, seo: j.categories?.seo?.score },
      metrics: { lcp: a('largest-contentful-paint'), fcp: a('first-contentful-paint'), cls: a('cumulative-layout-shift'),
        tbt: a('total-blocking-time'), speedIndex: a('speed-index'), ttfb: j.audits?.['server-response-time']?.details?.items?.[0]?.responseEnd },
      failedAudits: Object.values(j.audits ?? {}).filter((x) => x.score !== null && x.score < 0.9).map((x) => ({ id: x.id, title: x.title, delta: x.displayValue })).slice(0, 25),
      note: 'lab metrics; INP not lab-reproducible (field metric) — reported separately' };
  } catch (e) { return { available: false, reason: 'parse: ' + e.message }; }
}

/** Playwright: delivered HTML + JS-error capture for rendering-parity checks. */
export async function playwrightRender(url, { cwd = process.cwd() } = {}) {
  let pw; try { pw = (await import(join(cwd, 'node_modules/playwright/index.mjs'))).default ?? await import('playwright'); }
  catch { try { pw = await import('playwright'); } catch { return { available: false, reason: 'playwright not resolvable' }; } }
  let browser;
  try {
    browser = await pw.chromium.launch({ args: ['--no-sandbox'] });
    const page = await (await browser.newContext({ javaScriptEnabled: true })).newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 200)));
    const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    const html = await page.content();
    return { available: true, html, status: resp?.status() ?? 200, jsErrors: errors };
  } catch (e) { return { available: false, reason: String(e.message) }; }
  finally { try { await browser?.close(); } catch {} }
}

/** Unlighthouse sitewide lab sweep — opt-in via config/CLI (heavier). */
export function unlighthouseRun(url, { cwd = process.cwd(), maxPages = 10 } = {}) {
  const r = run('npx', ['--no-install', 'unlighthouse', `--site=${url}`, `--max-pages=${maxPages}`, '--output-file'], { cwd, timeout: 600000 });
  if (r.code !== 0) return { available: false, reason: 'unlighthouse: ' + r.out.slice(-300) };
  try {
    const outDir = join(cwd, '.unlighthouse');
    return { available: true, source: 'unlighthouse', note: 'aggregate lab; see .unlighthouse/ for per-page', hint: outDir };
  } catch (e) { return { available: false, reason: String(e.message) }; }
}

/** Field data: PSI API / CrUX need network + keyless PSI call; graceful otherwise. */
export async function psiFieldData(url) {
  try {
    const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 15000);
    const res = await fetch('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=' + encodeURIComponent(url) + '&category=performance', { signal: ctrl.signal });
    clearTimeout(t);
    if (!res.ok) return { available: false, reason: `PSI HTTP ${res.status}` };
    const j = await res.json();
    const crux = j.loadingExperience?.metrics ?? {};
    const p75 = (m) => crux[m]?.percentiles?.p75 ?? null;
    return { available: true, source: 'crux-field', percentile: 75,
      lcp: p75('LARGEST_CONTENTFUL_PAINT_MS'), inp: p75('INTERACTION_TO_NEXT_PAINT'), cls: p75('CUMULATIVE_LAYOUT_SHIFT_SCORE'),
      origin: j.loadingExperience?.origin ?? url, note: 'CrUX p75 — the only INP source here' };
  } catch (e) { return { available: false, reason: String(e.message) }; }
}
