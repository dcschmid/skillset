#!/usr/bin/env node
/**
 * seo.mjs — seo-performance skill entrypoint. Node >=18.17, stdlib only.
 * Subcommands: audit | fix | performance | technical | content | schema |
 *              monitor | ci | report | compare | serve | tools
 * Network read-only + rate limited; local/fixture mode fully offline.
 */
import { createServer } from 'node:http';
import { readFileSync, existsSync, mkdirSync, writeFileSync, statSync } from 'node:fs';
import { join, extname, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { crawl, Robots } from './lib/crawler.mjs';
import { analyzePages, analyzeRobots, analyzeSitemap, analyzeSchema, analyzeBudgets, dedupe, sortBySeverity } from './lib/detectors.mjs';
import { validateSchemaHtml, crossCheckContent } from './lib/schema.mjs';
import { loadConfig, loadBudgets } from './lib/config.mjs';
import { detectProject } from './lib/project.mjs';
import { snapshot, saveSnapshot, renderMarkdown, compareSnapshots, loadSnapshot } from './lib/report.mjs';
import { planFixes, applyStaticHtmlFixes, gitStatus } from './lib/fix.mjs';
import { visibleSignature, stripTags, inspectHead, inspectBody, images, assets, jsonLdBlocks, normalizeUrl } from './lib/html.mjs';

const SKILL_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const HELP = `seo-performance — universal SEO & performance auditor
usage: node scripts/seo.mjs <command> [target] [flags]
commands:
  audit <dir|url>        full audit (default). dir = project root, url = external site
  fix <dir|url>          audit + remediation (safe classes; --apply writes, default dry-run)
  performance <target>   metrics + budgets only
  technical <target>     crawl/indexability/metadata/canonical/sitemap
  content <target>       headings/metadata/content-quality evidence
  schema <target>        JSON-LD validation (3-tier verdict)
  monitor <dir>          recurring-audit assets (weekly GH Action; snapshots trend)
  ci <dir>               budget gate, exit 1 on error breach; --init writes LHCI config
  compare <a.json> <b.json>  before/after diff, noise vs regression
  serve <dir> [--port N] local static server (offline integration testing)
  tools                  installed measurement-tool versions
flags: --profile default|strict --level 1|2|3 --max-pages N --apply
       --out DIR --source-dist DIR (audit built output) --port N --init`;

function parseArgs(argv) {
  const cmds = ['audit', 'fix', 'performance', 'technical', 'content', 'schema', 'monitor', 'ci', 'compare', 'serve', 'tools', 'help'];
  const flags = {}, positional = [];
  let command = 'audit';
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const name = a.slice(2), next = argv[i + 1];
      if (next != null && !next.startsWith('--')) { flags[name] = next; i++; } else flags[name] = true;
    } else if (positional.length === 0 && cmds.includes(a)) command = a;
    else positional.push(a);
  }
  return { command, positional, flags };
}

const { command: cmd, positional, flags } = parseArgs(process.argv.slice(2));
const flag = (n, d) => (n in flags ? flags[n] : d);
const bool = (n) => flags[n] === true || flags[n] === 'true';

async function main() {
  if (cmd === 'help') { console.log(HELP); return 0; }
  if (cmd === 'tools') { const { toolVersions } = await import('./lib/perf.mjs');
    console.log(JSON.stringify(toolVersions(process.cwd()), null, 2)); return 0; }
  if (cmd === 'compare') return compare(String(flag('noise', 10)));
  if (cmd === 'serve') return serve();

  const target = positional[0] ?? process.cwd();
  const isUrl = /^https?:\/\//.test(target);
  const projectDir = isUrl ? null : resolve(target);
  const config = loadConfig({ profile: flag('profile', 'default'), projectDir,
    flags: { level: parseInt(flag('level', flag('profile', 'default') === 'strict' ? 3 : 2), 10),
      ...(flag('max-pages') ? { crawl: { maxPages: parseInt(flag('max-pages'), 10) } } : {}) } });
  const budgets = loadBudgets(projectDir);
  const outDir = resolve(projectDir ?? process.cwd(), String(flag('out', '.seo-report')));
  const project = projectDir ? detectProject(projectDir) : null;

  // ---- evidence ----
  let pages = [], robots = new Robots(''), sitemap = { sitemaps: [], indexes: [] }, sitemapUrls = [];
  if (isUrl) {
    pages = await crawl({ startUrl: target, maxPages: config.crawl.maxPages, delayMs: config.crawl.delayMs,
      timeoutMs: config.crawl.timeoutMs, respectRobotsTxt: config.crawl.respectRobotsTxt, render: null });
    if (pages.__robots) robots = pages.__robots;
    const sm = await tryFetch(new URL('sitemap.xml', new URL(target).origin).toString());
    if (sm) ({ sitemap, sitemapUrls } = parseSitemap(sm, new URL('sitemap.xml', new URL(target).origin).toString()));
  } else if (project) {
    const dist = flag('source-dist', null) ? resolve(String(flag('source-dist'))) : distFor(project, projectDir);
    if (dist) {
      pages = await crawl({ startUrl: '/', rootDir: dist,
        maxPages: config.crawl.maxPages, respectRobotsTxt: false, render: null });
      const rb = join(dist, 'robots.txt'); if (existsSync(rb)) robots = new Robots(readFileSync(rb, 'utf8'));
      const sm = findSitemapFile(dist); if (sm) ({ sitemap, sitemapUrls } = parseSitemap(readFileSync(sm, 'utf8'), 'file://' + sm));
    } else pages = sourceAudit(projectDir, project);
  }

  // enrich sitemap entries with real status (measured, never guessed)
  for (const sm of sitemap.sitemaps ?? []) for (const u of sm.urls ?? []) {
    const hit = pages.find((p) => normalizeUrl(p.finalUrl) === normalizeUrl(u.loc));
    if (hit) { u.status = hit.status ?? null; u.metaRobots = hit.head?.robotsMeta ?? null; continue; }
    if (isUrl) { const r = await tryFetch(u.loc); if (r != null) u.status = 200; }
    else if (project) {
      const dist = flag('source-dist', null) ? resolve(String(flag('source-dist'))) : distFor(project, projectDir);
      if (dist) {
        const pth = decodeURIComponent(new URL(u.loc).pathname).replace(/^\/+/, '');
        const exists = [join(dist, pth), join(dist, pth + '.html'), join(dist, pth, 'index.html')].some((f) => existsSync(f));
        u.status = exists ? 200 : 404;
      }
    }
  }

  // ---- findings ----
  let findings = [];
  if (pages.length) {
    const rich = pages.map(enrich);
    findings = analyzePages(rich, { config, robots, sitemap, sitemapUrls });
    findings.push(...analyzeRobots(robots, sitemapUrls[0], rich.filter((p) => p.path)));
    findings.push(...analyzeSitemap(sitemap, rich));
    findings.push(...analyzeSchema(rich.filter((p) => p.jsonLd?.length).map((p) => ({ url: p.url, blocks: p.jsonLd })), config));
  }
  findings = dedupe(findings);
  const scope = { technical: ['crawling', 'indexability', 'canonical', 'sitemap', 'metadata', 'rendering'],
    content: ['content', 'structured-data', 'i18n', 'metadata'] }[cmd];
  if (scope) findings = findings.filter((f) => scope.includes(f.category));

  const measurements = pages.filter((p) => p.ttfbMs != null).map((p) => ({ url: p.finalUrl,
    'ttfb-ms': p.ttfbMs, 'page-total-kb': Math.round((p.transferBytes ?? 0) / 1024) }));
  const budgetFindings = analyzeBudgets(measurements.length ? measurements : null, budgets);
  if (cmd === 'performance') findings = [...findings, ...budgetFindings];
  else findings = [...findings, ...budgetFindings];

  // ---- commands ----
  if (cmd === 'fix') return doFix({ findings, config, projectDir, outDir, project });
  if (cmd === 'ci') return doCI({ findings, config, projectDir, outDir });
  if (cmd === 'monitor') return doMonitor({ projectDir });
  if (cmd === 'schema') return doSchema({ pages });

  return finish({ cmd, pages, findings, project, projectDir, isUrl, target, config, outDir, measurements });
}

const sevRank = (s) => ({ critical: 0, high: 1, medium: 2, low: 3 })[s] ?? 4;

function finish({ cmd, pages, findings, project, projectDir, isUrl, target, config, outDir, measurements }) {
  const metrics = measurements.map((m) => ({ url: m.url, metric: 'ttfb-ms', value: m['ttfb-ms'], lowerIsBetter: true }));
  const dataGaps = [
    'INP: field metric — needs CrUX/RUM source (UNAVAILABLE offline, not zero)',
    'Google indexation status: needs Search Console (UNAVAILABLE)',
    'rich-result award: needs Rich Results Test (UNDETERMINED offline)',
    ...(isUrl ? [] : ['served metrics: run `serve` + audit URL for TTFB/waterfalls of live output']),
  ];
  const snap = snapshot({ root: outDir, name: isUrl ? new URL(target).origin : (project?.framework ?? 'site') + ':' + (projectDir ?? ''),
    pages, findings, metrics, project, tools: { node: process.version }, dataGaps });
  mkdirSync(outDir, { recursive: true });
  const snapFile = saveSnapshot(outDir, snap);
  writeFileSync(join(outDir, 'report.md'), renderMarkdown({ snap, compare: null }));
  writeFileSync(join(outDir, 'report.json'), JSON.stringify({ ...snap, findings: sortBySeverity(findings) }, null, 2));
  const c = snap.counts;
  const gate = config.failOnSeverity;
  const fail = gate ? findings.some((f) => sevRank(f.severity) <= sevRank(gate)) : false;
  console.log(`seo-performance ${cmd} @ ${isUrl ? new URL(target).origin : projectDir}`);
  console.log(`pages: ${pages.length} · findings: ${findings.length} (critical ${c.critical} · high ${c.high} · medium ${c.medium} · low ${c.low})`);
  for (const f of sortBySeverity(findings).slice(0, 25)) console.log(`  [${f.severity}] ${f.id} ${(f.urls ?? [])[0] ?? ''} — ${String(f.evidence).slice(0, 110)}`);
  if (findings.length > 25) console.log(`  … ${findings.length - 25} more in report.md`);
  console.log(`report: ${join(outDir, 'report.md')} · snapshot: ${snapFile}`);
  return fail ? 1 : 0;
}

function doFix({ findings, config, projectDir, outDir }) {
  const apply = bool('apply');
  const dist = projectDir
    ? (flag('source-dist', null) ? resolve(String(flag('source-dist')))
      : distFor(detectProject(projectDir), projectDir)
        ?? (existsSync(join(projectDir, 'index.html')) ? projectDir : null)) // static site rooted at project
    : null;
  const plans = planFixes(findings, { autoFixClasses: config.fix.autoFixClasses, approvals: {}, projectDir });
  const safe = findings.filter((f) => f.autoFixClass && config.fix.autoFixClasses.includes(f.autoFixClass));
  const result = { mode: apply ? 'applied' : 'dry-run', planned: plans.length, autoFixable: safe.length,
    manual: findings.filter((f) => !f.autoFixClass).map((f) => ({ id: f.id, fix: f.fix })).slice(0, 40) };
  if (dist) { const r = applyStaticHtmlFixes(dist, { apply, reportDir: outDir });
    result.staticHtml = { status: r.status, files: r.files, changed: r.changed.slice(0, 20) };
    if (apply) result.gitDiffStat = gitStatus(projectDir); }
  else result.staticHtml = { status: 'NO_DIST', note: 'build the project first (fix targets built HTML) or audit a URL' };
  mkdirSync(outDir, { recursive: true });
  result.next = apply ? 'verify: build, tests, re-audit' : 'rerun with --apply to write (git-tracked)';
  writeFileSync(join(outDir, 'fix-plan.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  return 0;
}

function doCI({ findings, config, projectDir, outDir }) {
  if (bool('init')) {
    const base = projectDir ?? process.cwd();
    writeFileSync(join(base, 'lighthouserc.cjs'), readFileSync(join(SKILL_ROOT, 'templates', 'lighthouse-ci.config.cjs'), 'utf8'));
    mkdirSync(join(base, '.github/workflows'), { recursive: true });
    writeFileSync(join(base, '.github/workflows/seo-performance.yml'), readFileSync(join(SKILL_ROOT, 'templates', 'github-actions-example.yml'), 'utf8'));
    console.log('wrote lighthouserc.cjs + .github/workflows/seo-performance.yml — set budgets to project reality');
    return 0;
  }
  const blocking = findings.filter((f) => (f.severity === 'critical' || f.severity === 'high')
      && !['robots-blocks-important-page', 'soft-404-suspect', 'robots-noindex-misuse', 'robots-unavailable'].includes(f.slug))
    .concat(findings.filter((f) => f.category === 'budgets' && f.severity === 'high'));
  for (const f of blocking) console.log(`[${f.severity}] ${f.id} ${(f.urls ?? []).join(' ')} — ${f.evidence}`);
  console.log(`ci gate: ${blocking.length ? 'FAIL' : 'PASS'} (${blocking.length} blocking of ${findings.length} findings)`);
  return blocking.length ? 1 : 0;
}

function doMonitor({ projectDir }) {
  const dir = join(projectDir ?? process.cwd(), '.github/workflows');
  mkdirSync(dir, { recursive: true });
  const wf = readFileSync(join(SKILL_ROOT, 'templates', 'github-actions-example.yml'), 'utf8')
    .replace('on:\n  push:\n    branches: [main]\n  pull_request:\n    branches: [main]\n',
      'on:\n  schedule:\n    - cron: "0 6 * * 1"  # weekly Monday 06:00 UTC — tune cadence\n  workflow_dispatch:\n');
  writeFileSync(join(dir, 'seo-performance-weekly.yml'), wf);
  console.log(`monitor ready: ${join(dir, 'seo-performance-weekly.yml')} · trend snapshots land in .seo-report/ · classify drift with \`compare\``);
  return 0;
}

function doSchema({ pages }) {
  const results = pages.filter((p) => p.html).map((p) => ({ url: p.url,
    verdict: validateSchemaHtml(p.html), cross: crossCheckContent(p.html, stripTags(p.html)).slice(0, 10) }));
  console.log(JSON.stringify({ policy: 'valid-schema ≠ google-conform ≠ rich-result-award (undetermined offline)',
    pages: results.length, results: results.slice(0, 20) }, null, 2));
  return 0;
}

function compare(noise) {
  const [a, b] = positional.slice(0, 2).map((f) => loadSnapshot(f));
  const r = compareSnapshots(a, b, { noisePct: Number(noise) });
  console.log(renderMarkdown({ snap: b ?? { name: 'n/a', counts: { critical: 0, high: 0, medium: 0, low: 0 }, findings: [], capturedAt: '?' }, compare: r }));
  return 0;
}

function serve() {
  const dir = resolve(positional[0] ?? process.cwd());
  const port = parseInt(flag('port', 8123), 10);
  const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.xml': 'application/xml', '.txt': 'text/plain',
    '.webp': 'image/webp', '.avif': 'image/avif', '.woff2': 'font/woff2', '.ico': 'image/x-icon' };
  const server = createServer((req, res) => {
    let p = join(dir, decodeURIComponent((req.url ?? '/').split('?')[0]));
    if (!existsSync(p)) return void (res.writeHead(404), res.end('not found'));
    if (statSync(p).isDirectory()) p = join(p, 'index.html');
    if (!existsSync(p)) return void (res.writeHead(404), res.end('not found'));
    res.writeHead(200, { 'content-type': MIME[extname(p)] ?? 'application/octet-stream' });
    res.end(readFileSync(p));
  });
  server.listen(port, '127.0.0.1', () => console.log(`serving ${dir} → http://127.0.0.1:${port} (Ctrl-C to stop)`));
  process.on('SIGTERM', () => server.close(() => process.exit(0)));
  process.on('SIGINT', () => server.close(() => process.exit(0)));
  return new Promise(() => {}); // hold the event loop; killed externally
}

// ---------- shared helpers ----------
function enrich(p) {
  if (p.skipped || p.html == null) return { ...p, head: p.head ?? { hreflangs: [] }, body: p.body ?? { headings: { h1: 0 }, visibleText: { textLength: 0, wordCount: 0 } } };
  const head = p.head?.titlePresent != null ? p.head : inspectHead(p.html);
  return { ...p, head, body: p.body?.headings ? p.body : inspectBody(p.html), images: p.images ?? images(p.html),
    assets: p.assets ?? assets(p.html), jsonLd: p.jsonLd ?? jsonLdBlocks(p.html),
    hreflangSelf: (p.head?.hreflangs ?? []).find((x) => x.href && normalizeUrl(new URL(x.href, p.finalUrl).toString()) === normalizeUrl(p.finalUrl))?.href ?? null };
}
function distFor(pr, dir) {
  for (const d of ['dist', 'out', '_site', 'build']) if (existsSync(join(dir, d, 'index.html'))) return join(dir, d);
  return null;
}
function findSitemapFile(dir) { for (const p of ['sitemap-index.xml', 'sitemap.xml']) if (existsSync(join(dir, p))) return join(dir, p); return null; }
function parseSitemap(xml, url) {
  const urls = [...xml.matchAll(/<url>([\s\S]*?)<\/url>/gi)].map((m) => ({
    loc: /<loc>([\s\S]*?)<\/loc>/i.exec(m[1])?.[1]?.trim(),
    lastmod: /<lastmod>([\s\S]*?)<\/lastmod>/i.exec(m[1])?.[1]?.trim() ?? null })).filter((u) => u.loc);
  const error = /<urlset|<sitemapindex/.test(xml) ? null : 'no urlset/sitemapindex root — not XML sitemap';
  const indexes = /<sitemapindex/i.test(xml) ? [{ url, errors: [] }] : [];
  return { sitemap: { sitemaps: urls.length ? [{ url, urls, parseError: error }] : [], indexes, error: urls.length || indexes.length ? error : 'empty sitemap' },
    sitemapUrls: urls.map((u) => u.loc) };
}
async function tryFetch(u) { try { const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 15000);
  const r = await fetch(u, { headers: { 'user-agent': 'seo-performance-skill/1.0 (audit; read-only)' }, signal: ctrl.signal });
  clearTimeout(t); return r.ok ? await r.text() : null; } catch { return null; } }
function sourceAudit(dir, pr) {
  const read = (p) => { try { return readFileSync(join(dir, p), 'utf8'); } catch { return null; } };
  const out = [];
  for (const [f, txt] of [['index.html', read('index.html') ?? read('public/index.html')], ['robots.txt', read('public/robots.txt') ?? read('robots.txt')]] ) {
    if (!txt) continue;
    out.push({ url: 'file://' + join(dir, f), finalUrl: 'file://' + join(dir, f), status: 200, headers: {}, depth: 0,
      html: f.endsWith('.html') ? txt : `<html><head><title>robots</title></head><body></body></html>`, htmlRaw: txt, files: [f], path: '/' + f, sourceLevel: true });
  }
  if (!out.length && pr.framework !== 'static-html') out.push({ url: 'file://' + dir, finalUrl: 'file://' + dir, status: 200, headers: {},
    depth: 0, html: `<html lang=""><head><title>${pr.framework} source-level audit — build output not found</title></head><body><p>source-level evidence; run build or serve for delivered-HTML checks</p></body></html>`,
    files: ['package.json'], path: '/', sourceLevel: true });
  return out;
}

main().then((code) => process.exit(code)).catch((e) => { console.error('seo-performance error:', e.stack ?? e); process.exit(2); });
