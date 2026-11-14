import assert from 'node:assert/strict';
import { analyzePages, analyzeRobots, analyzeSitemap, analyzeSchema, analyzeBudgets, dedupe } from '../../scripts/lib/detectors.mjs';
import { Robots } from '../../scripts/lib/crawler.mjs';
import { inspectHead, inspectBody, images, assets, jsonLdBlocks } from '../../scripts/lib/html.mjs';

const page = (url, html, extra = {}) => {
  const p = { url, finalUrl: extra.finalUrl ?? url, status: extra.status ?? 200, headers: extra.headers ?? {},
    chain: extra.chain ?? [{ url, status: extra.status ?? 200 }], html, depth: extra.depth ?? 1, path: extra.path ?? new URL(url).pathname,
    head: inspectHead(html), body: inspectBody(html), images: images(html), assets: assets(html), jsonLd: jsonLdBlocks(html),
    internalLinks: extra.internalLinks ?? [], ttfbMs: extra.ttfbMs ?? null, transferBytes: html.length, files: extra.files ?? [] };
  return p;
};
const html = (o) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${o.title ?? 'A perfectly reasonable page title'}</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="${o.desc ?? 'A fixture description of adequate length for the audit to accept.'}">
${o.canonical ? `<link rel="canonical" href="${o.canonical}">` : ''}${o.hreflang ?? ''}${o.ld ? `<script type="application/ld+json">${o.ld}</script>` : ''}
</head><body>${o.body ?? '<main><h1>Head</h1><p>body</p></main>'}</body></html>`;

const cfg = { config: { cwv: { ttfbMs: 800 } } };

export default function (t) {
  t('clean page yields no metadata/canonical findings', () => {
    const fs = analyzePages([page('https://x.test/', html({ canonical: 'https://x.test/' }))], cfg);
    const bad = fs.filter((f) => ['metadata', 'canonical', 'mobile', 'content'].includes(f.category) && f.category !== 'canonical');
    assert.equal(fs.filter((f) => f.slug.startsWith('title') || f.slug.startsWith('description') || f.slug === 'viewport-missing' || f.slug === 'charset-missing' || f.slug === 'h1-missing' || f.slug === 'canonical-missing').length, 0, JSON.stringify(fs.map((f) => f.id)));
    assert.ok(bad.every((f) => f.severity !== 'critical'));
  });
  t('noindex page + X-Robots-Tag detected', () => {
    const fs = analyzePages([page('https://x.test/', html({}), { headers: { 'x-robots-tag': 'noindex' } })], cfg);
    assert.ok(fs.some((f) => f.slug.startsWith('noindex-')));
  });
  t('canonical mismatch + collision + hreflang conflict', () => {
    const fs = analyzePages([
      page('https://x.test/a', html({ canonical: 'https://x.test/b' })),
      page('https://x.test/c', html({ canonical: 'https://x.test/b' })),
    ], cfg);
    assert.ok(fs.some((f) => f.slug === 'canonical-points-elsewhere'));
    assert.ok(fs.some((f) => f.slug === 'canonical-collision'));
  });
  t('redirect chain long + loop detected', () => {
    const chain = [1, 2, 3, 4, 5].map((i) => ({ url: `https://x.test/r${i}`, status: 301 }));
    assert.ok(analyzePages([page('https://x.test/r1', html({}), { chain })], cfg).some((f) => f.slug === 'redirect-chain-long'));
    const loop = [{ url: 'https://x.test/a', status: 301 }, { url: 'https://x.test/b', status: 301 }, { url: 'https://x.test/a', status: 301 }];
    assert.ok(analyzePages([page('https://x.test/a', html({}), { chain: loop, status: 301 })], cfg).some((f) => f.slug === 'redirect-loop'));
  });
  t('robots: sitemap ref missing + blocks indexable + noindex misuse', () => {
    const robots = Object.assign(new Robots('User-agent: *\nDisallow: /\nnoindex: /x\n'), { raw: 'User-agent: *\nDisallow: /\nnoindex: /x' });
    const fs = analyzeRobots(robots, 'https://x.test/sitemap.xml', [{ url: 'https://x.test/', path: '/' }]);
    assert.ok(fs.some((f) => f.slug === 'robots-missing-sitemap-reference'));
    assert.ok(fs.some((f) => f.slug === 'robots-blocks-important-page'));
    assert.ok(fs.some((f) => f.slug === 'robots-noindex-misuse'));
    assert.ok(fs.every((f) => !/sitemap/ig.test('x') || f.urls.includes('/robots.txt') || f.urls.includes('/')));
  });
  t('robots disallow matching honors allow override + wildcards', () => {
    const r = new Robots('User-agent: *\nDisallow: /admin/\nAllow: /admin/public.html');
    assert.equal(r.allowed('https://x.test/admin/secret.html'), false);
    assert.equal(r.allowed('https://x.test/admin/public.html'), true);
    assert.equal(r.allowed('https://x.test/'), true);
  });
  t('sitemap: dead, non-canonical, noindex, future lastmod', () => {
    const sm = { sitemaps: [{ url: 'https://x.test/sitemap.xml', urls: [
      { loc: 'https://x.test/dead/', status: 404 }, { loc: 'https://x.test/a/', lastmod: '2030-01-01' },
    ] }], indexes: [] };
    const pages = [page('https://x.test/a', html({ canonical: 'https://x.test/a/', desc: 'x' }))];
    pages[0].head.robotsMeta = null;
    const fs = analyzeSitemap(sm, pages);
    assert.ok(fs.some((f) => f.slug === 'sitemap-dead-urls'));
    assert.ok(fs.some((f) => f.slug === 'sitemap-lastmod-future'));
  });
  t('orphan page detection', () => {
    const p1 = page('https://x.test/', html({}), { internalLinks: [], depth: 0 });
    const p2 = page('https://x.test/orphan.html', html({}), { internalLinks: [], depth: 2 });
    assert.ok(analyzePages([p1, p2], cfg).some((f) => f.slug === 'orphan-pages'));
  });
  t('hreflang reciprocity + invalid code', () => {
    const en = page('https://x.test/', html({ canonical: 'https://x.test/', hreflang: '<link rel="alternate" hreflang="en" href="https://x.test/"><link rel="alternate" hreflang="de" href="https://x.test/de/">' }));
    const de = page('https://x.test/de/', html({ canonical: 'https://x.test/de/', hreflang: '<link rel="alternate" hreflang="de" href="https://x.test/de/">' }));
    assert.ok(analyzePages([en, de], cfg).some((f) => f.slug === 'hreflang-not-reciprocal'));
    const bad = page('https://x.test/', html({ canonical: 'https://x.test/', hreflang: '<link rel="alternate" hreflang="deutsch" href="/x">' }));
    assert.ok(analyzePages([bad], cfg).some((f) => f.slug === 'hreflang-invalid-code'));
  });
  t('lcp-image-lazy + render blocking + ttfb slow', () => {
    const p = page('https://x.test/', html({ body: '<main><h1>H</h1><img src="hero.png" width="1" height="1" alt="" loading="lazy"><script src="j.js"></script></main>' }), { ttfbMs: 1500 });
    p.lcpCandidates = ['hero.png'];
    const fs = analyzePages([p], cfg);
    assert.ok(fs.some((f) => f.slug === 'lcp-image-lazy'));
    assert.ok(fs.some((f) => f.slug === 'render-blocking-script'));
    assert.ok(fs.some((f) => f.slug === 'ttfb-slow'));
  });
  t('schema: broken json + missing required fields', () => {
    const fs = analyzeSchema([{ url: 'https://x.test/', blocks: [
      { ok: false, error: 'bad' }, { ok: true, data: { '@type': 'Article', headline: 'H' } },
    ] }], {});
    assert.ok(fs.some((f) => f.slug === 'jsonld-invalid'));
    assert.ok(fs.some((f) => f.slug === 'schema-missing-field-article'));
  });
  t('budgets: warn/error/no-data honesty', () => {
    const b = { rules: [{ metric: 'lcp-ms', warn: 100, error: 200 }], tolerancePct: 10 };
    assert.ok(analyzeBudgets([{ url: 'u', lcp: 250 }], b).some((f) => f.slug === 'budget-exceeded-lcp-ms'));
    assert.ok(analyzeBudgets([{ url: 'u' }], b).some((f) => f.slug === 'budget-no-data-lcp-ms'));
    assert.equal(analyzeBudgets([{ url: 'u', lcp: 50 }], b).length, 0);
  });
  t('dedupe keeps worst severity per id+url', () => {
    const fs = dedupe([{ id: 'a:b|u', severity: 'low', urls: ['u'], category: 'x' }, { id: 'a:b|u', severity: 'high', urls: ['u'], category: 'x' }]);
    assert.equal(fs.length, 1); assert.equal(fs[0].severity, 'high');
  });
}
