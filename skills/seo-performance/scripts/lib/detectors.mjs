/**
 * detectors.mjs — deterministic checks over collected page evidence.
 * Every finding: {id, category, severity, urls, evidence, cause, fix, effort,
 * risk, verify, autoFixable}. Severity is impact-based, not score-based.
 * Class taxonomy in references/remediation-guide.md.
 */
import { normalizeUrl } from './html.mjs';

const SEV_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };
export const compareSeverity = (a, b) => SEV_ORDER[a] - SEV_ORDER[b];

const F = (o) => ({
  id: `${o.category}:${o.slug}`,
  category: o.category, slug: o.slug, severity: o.severity,
  urls: o.urls ?? [], files: o.files ?? [],
  evidence: o.evidence, cause: o.cause, fix: o.fix,
  effort: o.effort ?? 'S', risk: o.risk ?? 'low',
  verify: o.verify, autoFixClass: o.autoFixClass ?? null,
  status: 'confirmed',
});

/** @param {Array<{url:string,finalUrl:string,status:number,chain:Array,html:string,headers:Object,depth:number,skipped?:boolean}>} pages
 *  @param {{config:Object, robots?:Object, sitemap?:Object, sitemapUrls?:Array}} ctx */
export function analyzePages(pages, ctx) {
  const findings = [];
  const push = (f) => findings.push(f);
  const live = pages.filter((p) => !p.skipped && p.html != null);
  const cfg = ctx.config ?? {};

  // ---------- status & redirects ----------
  for (const p of pages) {
    if (p.error) {
      push(F({ category: 'crawling', slug: 'fetch-error', severity: 'high', urls: [p.url],
        evidence: `fetch failed: ${p.error}`, cause: 'host/timeout/DNS', fix: 'verify route + server', effort: 'S', risk: 'low',
        verify: 're-crawl URL', }));
      continue;
    }
    const chain = p.chain ?? [{ url: p.url, status: p.status }];
    if (chain.length > 3)
      push(F({ category: 'crawling', slug: 'redirect-chain-long', severity: 'medium', urls: [p.url],
        evidence: `${chain.length} hops: ${chain.map((c) => c.status).join('->')}`,
        cause: 'unnecessary redirect hops', fix: 'point links at final URL', effort: 'S', risk: 'low',
        verify: 'chain length <= 2' }));
    const loop = new Set(chain.map((c) => normalizeUrl(c.url)));
    if (chain.some((c) => c.status >= 300 && c.status < 400) && loop.size < chain.length)
      push(F({ category: 'crawling', slug: 'redirect-loop', severity: 'critical', urls: [p.url],
        evidence: `loop: ${chain.map((c) => c.url).join(' -> ')}`, cause: 'cyclic redirect rules',
        fix: 'break cycle in server/redirect config', effort: 'S', risk: 'medium', verify: 'no repeated URL in chain' }));
    if (p.status >= 500)
      push(F({ category: 'crawling', slug: 'server-error', severity: 'critical', urls: [p.url],
        evidence: `HTTP ${p.status}`, cause: 'server/route failure', fix: 'fix route', effort: 'M', risk: 'low', verify: 'status 200' }));
    if (p.status === 404)
      push(F({ category: 'crawling', slug: 'not-found', severity: 'high', urls: [p.url],
        evidence: 'HTTP 404', cause: 'missing route or stale link', fix: 'add route or fix inbound links', effort: 'S', risk: 'low',
        verify: 'status 200 or removed link' }));
    if (p.status === 200 && softNotFound(p))
      push(F({ category: 'crawling', slug: 'soft-404-suspect', severity: 'medium', urls: [p.url], status: 200,
        evidence: `status 200 but ${p.bodyChars} visible chars and "not found" wording`,
        cause: 'page renders 404 copy with 200 status', fix: 'return real 404 status', effort: 'S', risk: 'medium',
        verify: 'server response code 404' }));
  }

  // ---------- per page checks ----------
  for (const p of live) {
    const h = p.head, b = p.body, a = p.assets;

    // indexability
    const robotsHdr = (p.headers['x-robots-tag'] ?? '').toLowerCase();
    if ((h.robotsMeta ?? '').toLowerCase().includes('noindex') || robotsHdr.includes('noindex')) {
      const important = /(^|\/)(index|about|blog|products?|contact)?$/.test(new URL(p.finalUrl).pathname);
      push(F({ category: 'indexability', slug: `noindex-${important ? 'important' : 'page'}`,
        severity: important ? 'high' : 'low', urls: [p.url],
        evidence: `noindex via ${h.robotsMeta ? 'meta' : 'X-Robots-Tag'}="${h.robotsMeta ?? robotsHdr}"`,
        cause: important ? 'noindex on a page meant for search' : 'intentional exclusion (verify)',
        fix: 'remove noindex or block via robots.txt only if also removing links', effort: 'S', risk: 'medium',
        verify: 'meta/X-Robots-Tag free of noindex', autoFixClass: 'static-html-meta' }));
    }

    // title / description
    if (!h.titlePresent || !h.title) push(F({ category: 'metadata', slug: 'title-missing', severity: 'medium', urls: [p.url],
      evidence: 'no <title> or empty', cause: 'layout/SEO component gap', fix: 'add unique title', effort: 'S', risk: 'low',
      verify: 'crawl shows title', autoFixClass: 'static-html-meta' }));
    else if (h.title.length < 10) push(F({ category: 'metadata', slug: 'title-short', severity: 'low', urls: [p.url],
      evidence: `"${h.title}" (${h.title.length} ch)`, cause: 'template truncation', fix: 'descriptive 30-60 ch title', effort: 'S', risk: 'low', verify: 're-crawl' }));
    else if (h.title.length > 70) push(F({ category: 'metadata', slug: 'title-long', severity: 'low', urls: [p.url],
      evidence: `${h.title.length} ch`, cause: 'title stuffing', fix: 'shorten; move detail to description', effort: 'S', risk: 'low', verify: 're-crawl' }));
    const dup = (h.metaDescription ?? '').length;
    if (dup === 0 && !p.headingsMentionDescription) push(F({ category: 'metadata', slug: 'description-missing', severity: 'low', urls: [p.url],
      evidence: 'no meta description', cause: 'missing from layout', fix: 'add 80-160 ch summary; Google may rewrite it', effort: 'S', risk: 'low',
      verify: 're-crawl', autoFixClass: 'static-html-meta' }));

    // canonical
    if (h.canonical) {
      const cu = normalizeUrl(new URL(h.canonical, p.finalUrl).toString());
      const self = normalizeUrl(p.finalUrl);
      if (cu !== self) push(F({ category: 'canonical', slug: 'canonical-points-elsewhere', severity: 'medium', urls: [p.url],
        evidence: `canonical ${cu} != delivered ${self}`, cause: 'copy-paste template or missing per-page override',
        fix: 'per-page canonical matching intended URL', effort: 'S', risk: 'low', verify: 'canonical == self for indexables' }));
      if (/^http:/i.test(h.canonical) && /^https:/i.test(p.finalUrl))
        push(F({ category: 'canonical', slug: 'canonical-scheme-mismatch', severity: 'medium', urls: [p.url],
          evidence: `canonical http:// while page served https`, cause: 'stale base URL config', fix: 'scheme-aware absolute URL', effort: 'S', risk: 'low', verify: 'scheme match' }));
      if (p.hreflangSelf && p.hreflangSelf !== cu)
        push(F({ category: 'canonical', slug: 'canonical-hreflang-conflict', severity: 'medium', urls: [p.url],
          evidence: `self hreflang ${p.hreflangSelf} != canonical ${h.canonical}`, cause: 'language switching vs canonical drift',
          fix: 'canonical must match the active hreflang target', effort: 'S', risk: 'medium', verify: 'hreflang self == canonical' }));
    } else {
      push(F({ category: 'canonical', slug: 'canonical-missing', severity: 'low', urls: [p.url],
        evidence: 'no canonical link', cause: 'not emitted by layout', fix: 'absolute self-referencing canonical', effort: 'S', risk: 'low',
        verify: 'crawl shows canonical', autoFixClass: 'static-html-meta' }));
    }
    const canonicalDupes = [];
    const reC = /<link[^>]+rel=["']?canonical["']?[^>]*>/gi;
    let mc; while ((mc = reC.exec(p.html ?? '')) !== null) canonicalDupes.push(mc[0]);
    if (canonicalDupes.length > 1)
      push(F({ category: 'canonical', slug: 'canonical-multiple', severity: 'medium', urls: [p.url],
        evidence: `${canonicalDupes.length} canonical links: ${canonicalDupes.join(' | ').slice(0, 300)}`,
        cause: 'duplicate emission (layout + page)', fix: 'single canonical', effort: 'S', risk: 'low', verify: 'count==1' }));

    // language
    if (!h.htmlLang) push(F({ category: 'content', slug: 'html-lang-missing', severity: 'low', urls: [p.url],
      evidence: '<html> without lang', cause: 'root layout', fix: 'add lang per locale', effort: 'S', risk: 'low', verify: 're-crawl', autoFixClass: 'static-html-lang' }));
    else if (h.hreflangs.length && !h.hreflangs.some((x) => x.hreflang.startsWith((h.htmlLang ?? '').split('-')[0])))
      push(F({ category: 'i18n', slug: 'lang-hreflang-mismatch', severity: 'low', urls: [p.url],
        evidence: `lang=${h.htmlLang} but hreflang set [${h.hreflangs.map((x) => x.hreflang).join(',')}] has no match`,
        cause: 'template locale drift', fix: 'sync html lang with active hreflang', effort: 'S', risk: 'low', verify: 'prefix match' }));

    // viewport / charset
    if (!h.viewport) push(F({ category: 'mobile', slug: 'viewport-missing', severity: 'medium', urls: [p.url],
      evidence: 'no meta viewport', cause: 'layout gap', fix: 'add width=device-width', effort: 'S', risk: 'low', verify: 're-crawl', autoFixClass: 'static-html-meta' }));
    if (!h.charsetPresent) push(F({ category: 'technical', slug: 'charset-missing', severity: 'low', urls: [p.url],
      evidence: 'no charset', cause: 'layout gap', fix: '<meta charset="utf-8">', effort: 'S', risk: 'low', verify: 're-crawl' }));

    // headings
    const h1s = b.headings.h1;
    if (h1s === 0) push(F({ category: 'content', slug: 'h1-missing', severity: 'medium', urls: [p.url],
      evidence: 'no <h1>', cause: 'component markup gap', fix: 'one H1 with primary topic', effort: 'S', risk: 'low', verify: 're-crawl' }));
    else if (h1s > 1) push(F({ category: 'content', slug: 'h1-multiple', severity: 'low', urls: [p.url],
      evidence: `${h1s} H1 elements`, cause: 'nested components each adding H1', fix: 'keep single H1; demote rest', effort: 'S', risk: 'low', verify: 'h1==1' }));
    if (b.headings.h2 === 0 && b.visibleText.wordCount > 200)
      push(F({ category: 'content', slug: 'heading-structure-thin', severity: 'low', urls: [p.url],
        evidence: `${b.visibleText.wordCount} words with no H2`, cause: 'flat content model', fix: 'structure sections with headings', effort: 'M', risk: 'low', verify: 're-crawl' }));

    // hreflang
    for (const x of h.hreflangs) {
      const valid = /^[a-z]{2}(?:-[a-z]{2})?(?:-[a-z]{4})?$|^x-default$/i.test(x.hreflang);
      if (!valid) push(F({ category: 'i18n', slug: 'hreflang-invalid-code', severity: 'medium', urls: [p.url],
        evidence: `hreflang="${x.hreflang}"`, cause: 'invalid BCP47', fix: 'ISO639(+ISO3166) or x-default', effort: 'S', risk: 'low', verify: 'validator passes' }));
      if (x.href && !x.href.startsWith('http')) push(F({ category: 'i18n', slug: 'hreflang-relative-url', severity: 'medium', urls: [p.url],
        evidence: `href="${x.href}"`, cause: 'relative URLs in link alternates', fix: 'absolute URLs', effort: 'S', risk: 'low', verify: 're-crawl' }));
    }

    // images
    const imgs = p.images ?? [];
    for (const im of imgs.slice(0, 30)) {
      if (im.alt === undefined) push(F({ category: 'accessibility', slug: 'img-alt-missing', severity: 'low', urls: [p.url], files: p.files ?? [],
        evidence: `img src=${im.src} has no alt attribute`, cause: 'component lacks alt prop', fix: 'descriptive alt or alt="" for decorative', effort: 'S', risk: 'low', verify: 're-crawl a11y pass' }));
      if (im.lazy && (p.lcpCandidates ?? []).includes(im.src))
        push(F({ category: 'performance', slug: 'lcp-image-lazy', severity: 'medium', urls: [p.url],
          evidence: `loading=lazy on LCP candidate ${im.src}`, cause: 'blanket lazy loading', fix: 'eager + fetchpriority=high for LCP image', effort: 'S', risk: 'low', verify: 'LCP element not lazy' }));
      if (!im.width || !im.height)
        push(F({ category: 'performance', slug: 'img-dimensions-missing', severity: 'low', urls: [p.url],
          evidence: `img ${im.src} without width/height`, cause: 'no intrinsic size', fix: 'set width/height or aspect-ratio', effort: 'S', risk: 'low', verify: 'CLS-friendly markup' }));
    }

    // blocking resources
    if (a.blockingScripts > 0)
      push(F({ category: 'performance', slug: 'render-blocking-script', severity: 'medium', urls: [p.url],
        evidence: `${a.blockingScripts} sync external script(s)`, cause: 'script without defer/async/module',
        fix: 'defer/async or module; inline critical path', effort: 'S', risk: 'low', verify: 'blockingScripts==0' }));
    if (p.ttfbMs && p.ttfbMs > (cfg.cwv?.ttfbMs ?? 800))
      push(F({ category: 'performance', slug: 'ttfb-slow', severity: p.ttfbMs > 1800 ? 'high' : 'medium', urls: [p.url],
        evidence: `TTFB ${p.ttfbMs}ms (HTTP-only sample; lab threshold ${cfg.cwv?.ttfbMs ?? 800}ms)`,
        cause: 'server render time / cold start / no cache', fix: 'caching, CDN, static output', effort: 'M', risk: 'medium', verify: 're-measure' }));
    if ((p.transferBytes ?? 0) > 1500 * 1024)
      push(F({ category: 'performance', slug: 'page-too-heavy', severity: 'medium', urls: [p.url],
        evidence: `${Math.round((p.transferBytes ?? 0) / 1024)}KB delivered HTML`, cause: 'inline payloads/bloat', fix: 'externalize+compress', effort: 'M', risk: 'low', verify: 'budget pass' }));

    // JS-only content suspicion (CSR gap): meaningful text appears only after render
    if (p.rendered && p.rendered.rendered) {
      const pre = p.head.__pre?.visibleText, post = p.rendered.visibleText;
      if (pre && post && post.textLength > pre.textLength * 2 && post.textLength > 800)
        push(F({ category: 'rendering', slug: 'content-js-only', severity: 'high', urls: [p.url],
          evidence: `pre-render ${pre.textLength}ch vs post-render ${post.textLength}ch`,
          cause: 'main content generated client-side', fix: 'SSR/SSG the route or pre-render', effort: 'M', risk: 'medium',
          verify: 'pre/post text parity for SEO content' }));
    }
  }

  // ---------- cross-page ----------
  const canon = new Map();
  for (const p of live) if (p.head.canonical) {
    const c = normalizeUrl(new URL(p.head.canonical, p.finalUrl).toString());
    if (!canon.has(c)) canon.set(c, []); canon.get(c).push(p.url);
  }
  for (const [c, src] of canon) if (src.length > 1)
    push(F({ category: 'canonical', slug: 'canonical-collision', severity: 'medium', urls: src,
      evidence: `${src.length} pages canonicalize to ${c}`, cause: 'template canonical not per-page',
      fix: 'per-page canonicals', effort: 'S', risk: 'low', verify: 'injective canonical map on indexables' }));

  const desc = new Map();
  for (const p of live) if (p.head.metaDescription) {
    const d = p.head.metaDescription.trim();
    if (!desc.has(d)) desc.set(d, []); desc.get(d).push(p.url);
  }
  for (const [d, src] of desc) if (src.length > 2)
    push(F({ category: 'metadata', slug: 'duplicate-descriptions', severity: 'low', urls: src,
      evidence: `${src.length} pages share one meta description`, cause: 'global description', fix: 'per-page summaries', effort: 'M', risk: 'low', verify: 'uniqueness on key templates' }));

  // orphan detection: no inbound internal links among crawled set
  const inbound = new Set();
  for (const p of live) for (const l of p.internalLinks ?? []) inbound.add(normalizeUrl(l));
  const orphans = live.filter((p) => !inbound.has(normalizeUrl(p.finalUrl)) && p.depth > 1 && !/\/$/.test(new URL(p.finalUrl).pathname));
  if (orphans.length)
    push(F({ category: 'architecture', slug: 'orphan-pages', severity: 'low', urls: orphans.map((p) => p.url).slice(0, 20),
      evidence: `${orphans.length} crawled pages without internal inbound link`, cause: 'nav/sitemap-only discovery',
      fix: 'link from relevant hub pages', effort: 'M', risk: 'low', verify: 'crawl graph inbound >=1 (non-landing)' }));

  // hreflang reciprocity
  const recip = new Map();
  for (const p of live) for (const x of p.head.hreflangs) if (x.href) {
    const key = normalizeUrl(new URL(x.href, p.finalUrl).toString());
    if (!recip.has(key)) recip.set(key, []); recip.get(key).push({ from: p.finalUrl, lang: x.hreflang });
  }
  for (const [target, entries] of recip) {
    const t = live.find((p) => normalizeUrl(p.finalUrl) === target);
    if (!t || !t.head.hreflangs.length) continue;
    const missing = entries.filter((e) => !t.head.hreflangs.some((x) => normalizeUrl(new URL(x.href, target).toString()) === normalizeUrl(e.from)));
    if (missing.length)
      push(F({ category: 'i18n', slug: 'hreflang-not-reciprocal', severity: 'medium', urls: [target, ...missing.map((m) => m.from)].slice(0, 10),
        evidence: `${target} does not link back to [${missing.map((m) => m.from + ' (' + m.lang + ')').join(', ')}]`,
        cause: 'one-sided hreflang block', fix: 'bidirectional hreflang groups', effort: 'S', risk: 'medium', verify: 'reciprocity check passes' }));
  }

  return findings;
}

function softNotFound(p) {
  if (p.status !== 200 || !p.html) return false;
  const t = p.body?.visibleText?.textLength ?? 0;
  return t < 600 && /(not found|404|doesn.t exist)/i.test(p.html.slice(0, 4000));
}

/** robots.txt analysis. @param {{raw:string, disallow:Array, allow:Array, sitemaps:Array, error?:string}} robots */
export function analyzeRobots(robots, sitemapUrl, pages) {
  const findings = [];
  const push = (o) => findings.push(F(o));
  if (robots.error) {
    push({ category: 'crawling', slug: 'robots-unavailable', severity: 'low', urls: ['/robots.txt'],
      evidence: robots.error, cause: 'no robots.txt (permitted; default allow-all)', fix: 'optional: explicit file with Sitemap: line', effort: 'S', risk: 'low', verify: 'file serves 200', autoFixClass: 'robots-txt' });
    return findings;
  }
  if (sitemapUrl && !robots.sitemaps.length)
    push({ category: 'crawling', slug: 'robots-missing-sitemap-reference', severity: 'low', urls: ['/robots.txt'],
      evidence: `no "Sitemap:" line (sitemap found at ${sitemapUrl})`, cause: 'manual file not updated', fix: 'add Sitemap: <abs url>', effort: 'S', risk: 'low', verify: 'Sitemap line present', autoFixClass: 'robots-txt' });
  const blockedIndexables = (pages ?? []).filter((p) => robots.disallow.some((d) => matchesPath(p.path ?? '/', d)));
  for (const p of blockedIndexables.slice(0, 10))
    push({ category: 'crawling', slug: 'robots-blocks-important-page', severity: 'high', urls: [p.url],
      evidence: `Disallow blocks ${p.path} but page is linked/indexable`, cause: 'over-broad Disallow',
      fix: 'narrow Disallow; robots.txt does not remove pages from the index — use noindex for removal', effort: 'S', risk: 'medium', verify: 'page fetchable by crawler', autoFixClass: 'robots-txt' });
  if (/noindex/i.test(robots.raw ?? ''))
    push({ category: 'crawling', slug: 'robots-noindex-misuse', severity: 'medium', urls: ['/robots.txt'],
      evidence: 'robots.txt uses non-standard directive: ' + (robots.raw.match(/noindex.*/i)?.[0] ?? '').slice(0, 120),
      cause: 'Google does not honor noindex in robots.txt', fix: 'move removal to meta noindex / X-Robots-Tag', effort: 'S', risk: 'low', verify: 'directives limited to Google-standard set' });
  return findings;
}

function matchesPath(path, pattern) {
  const re = new RegExp('^' + pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\$/g, '') + '(?:$|/)');
  return re.test(path);
}

/** Sitemap findings. @param {{sitemaps:Array,indexes:Array,error?:string}} sm */
export function analyzeSitemap(sm, pages) {
  const findings = [];
  const push = (o) => findings.push(F({ category: 'sitemap', status: 'confirmed', ...o }));
  if (sm.error) {
    push({ slug: 'sitemap-missing', severity: 'medium', urls: ['/sitemap.xml'], evidence: sm.error,
      cause: 'sitemap not generated/served', fix: 'generate at build/serve time (@astrojs/sitemap, next/sitemap.ts, or static)', effort: 'S', risk: 'low', verify: 'fetch 200 valid XML' });
    return findings;
  }
  for (const s of sm.sitemaps ?? []) {
    if (s.parseError) push({ slug: 'sitemap-invalid-xml', severity: 'high', urls: [s.url], evidence: s.parseError,
      cause: 'malformed XML', fix: 'emit via framework module (xml escaping)', effort: 'S', risk: 'low', verify: 'XML parse + schema', autoFixClass: 'sitemap-cleanup' });
    const bad = (s.urls ?? []).filter((u) => u.status && u.status >= 400);
    if (bad.length) push({ slug: 'sitemap-dead-urls', severity: s.deathRatio > 0.3 ? 'high' : 'medium', urls: bad.map((u) => u.loc).slice(0, 10),
      evidence: `${bad.length}/${s.urls.length} entries non-2xx`, cause: 'stale build or renamed routes', fix: 'rebuild sitemap from route table', effort: 'S', risk: 'low', verify: 're-crawl: all 200', autoFixClass: 'sitemap-cleanup' });
    const nonCanonical = (s.urls ?? []).filter((u) => {
      const p = (pages ?? []).find((pp) => normalizeUrl(pp.finalUrl) === normalizeUrl(u.loc) && pp.head.canonical);
      return p && normalizeUrl(new URL(p.head.canonical, p.finalUrl).toString()) !== normalizeUrl(u.loc);
    });
    if (nonCanonical.length) push({ slug: 'sitemap-non-canonical-urls', severity: 'medium', urls: nonCanonical.map((u) => u.loc).slice(0, 10),
      evidence: `${nonCanonical.length} sitemap URLs canonicalize elsewhere`, cause: 'sitemap built from raw route list', fix: 'list canonical URLs only', effort: 'S', risk: 'low', verify: 'sitemap ∩ canonical map' });
    const noindexed = (s.urls ?? []).filter((u) => u.metaRobots?.includes('noindex'));
    if (noindexed.length) push({ slug: 'sitemap-includes-noindex', severity: 'medium', urls: noindexed.map((u) => u.loc).slice(0, 10),
      evidence: `${noindexed.length} noindex pages listed`, cause: 'sitemap from all routes', fix: 'filter noindex out', effort: 'S', risk: 'low', verify: 'sitemap has no noindex URLs', autoFixClass: 'sitemap-cleanup' });
    const future = (s.urls ?? []).filter((u) => u.lastmod && new Date(u.lastmod) > new Date());
    if (future.length) push({ slug: 'sitemap-lastmod-future', severity: 'low', urls: future.map((u) => u.loc).slice(0, 5),
      evidence: `${future.length} lastmod in future`, cause: 'build timestamp vs content date', fix: 'lastmod = content modified', effort: 'S', risk: 'low', verify: 'lastmod <= now' });
  }
  for (const ix of sm.indexes ?? []) for (const err of ix.errors ?? [])
    push({ slug: 'sitemap-index-invalid', severity: 'high', urls: [ix.url], evidence: err, cause: 'index file broken', fix: 'regenerate index', effort: 'S', risk: 'low', verify: 'index parses' });
  return findings;
}

/** Schema.org findings. @param {Array<{url:string, blocks:Array}>} schemaPages */
export function analyzeSchema(schemaPages, cfg) {
  const findings = [];
  const push = (o) => findings.push(F({ category: 'structured-data', status: 'confirmed', ...o }));
  for (const p of schemaPages) {
    for (const b of p.blocks.filter((b) => !b.ok))
      push({ slug: 'jsonld-invalid', severity: 'high', urls: [p.url], evidence: `JSON.parse: ${b.error}`,
        cause: 'hand-written JSON-LD broken', fix: 'programmatic construction / template serializer', effort: 'S', risk: 'low',
        verify: 'node schema-check passes', autoFixClass: 'static-html-meta' });
    for (const b of p.blocks.filter((b) => b.ok)) {
      const nodes = nodeList(b.data);
      const types = new Set(nodes.map((n) => n['@type']).filter(Boolean).flat());
      for (const n of nodes) {
        const t = Array.isArray(n['@type']) ? n['@type'] : [n['@type']].filter(Boolean);
        for (const ty of t) {
          const req = REQUIRED[ty];
          if (!req) continue;
          for (const field of req) if (!(field in n))
            push({ slug: `schema-missing-field-${ty.toLowerCase()}`, severity: 'medium', urls: [p.url],
              evidence: `${ty} lacks "${field}"`, cause: 'partial template', fix: `add ${field} from visible content`, effort: 'S', risk: 'low',
              verify: 'validator: no missing required' });
        }
        if (n.datePublished && n.dateModified && new Date(n.dateModified) < new Date(n.datePublished))
          push({ slug: 'schema-date-inverted', severity: 'low', urls: [p.url], evidence: `${n.dateModified} < ${n.datePublished}`,
            cause: 'field swap', fix: 'fix dates from content', effort: 'S', risk: 'low', verify: 'dates ordered' });
      }
      const seenTypes = [...types];
      if (seenTypes.length > 8)
        push({ slug: 'schema-bloat', severity: 'low', urls: [p.url], evidence: `${seenTypes.length} root types: ${seenTypes.join(',')}`,
          cause: 'shotgun markup', fix: 'types for what the page is, nothing else', effort: 'M', risk: 'low', verify: 'minimal type set' });
    }
  }
  return findings;
}
const REQUIRED = {
  Article: ['headline', 'datePublished', 'author'], BlogPosting: ['headline', 'datePublished', 'author'],
  Organization: ['name', 'url'], LocalBusiness: ['name', 'address'], BreadcrumbList: ['itemListElement'],
  Event: ['name', 'startDate', 'location'], Product: ['name', 'description'],
  VideoObject: ['name', 'uploadDate', 'thumbnailUrl'], WebSite: ['url'],
};
function nodeList(data) {
  const out = [];
  const walk = (n) => { if (!n || typeof n !== 'object') return;
    if (Array.isArray(n)) { n.forEach(walk); return; }
    if (n['@type']) out.push(n);
    for (const v of Object.values(n)) if (v && typeof v === 'object') walk(v); };
  walk(data); return out;
}

export function analyzeBudgets(measurements, budgets) {
  const findings = [];
  for (const m of measurements ?? []) for (const r of budgets.rules ?? []) {
    const v = m[r.metric] ?? m[mapping[r.metric]];
    if (v == null) { findings.push(F({ category: 'budgets', slug: `budget-no-data-${r.metric}`, severity: 'low', urls: [m.url ?? 'project'],
      evidence: `${r.metric} unavailable (${r.source ?? 'lab'}); skipped, not passed`, cause: 'no RUM/CrUX wired', fix: 'optional: connect PSI/CrUX or RUM', effort: 'S', risk: 'low', verify: 'snapshot has value' })); continue; }
    if (v > (r.error ?? Infinity)) findings.push(F({ category: 'budgets', slug: `budget-exceeded-${r.metric}`, severity: 'high', urls: [m.url ?? 'project'],
      evidence: `${r.metric} ${v} > error ${r.error}`, cause: 'budget breach', fix: `reduce below ${r.warn}`, effort: 'M', risk: 'low', verify: 're-measure' }));
    else if (v > (r.warn ?? Infinity)) findings.push(F({ category: 'budgets', slug: `budget-warn-${r.metric}`, severity: 'medium', urls: [m.url ?? 'project'],
      evidence: `${r.metric} ${v} > warn ${r.warn}`, cause: 'approaching limit', fix: 'trim before it becomes error', effort: 'M', risk: 'low', verify: 're-measure' }));
  }
  return findings;
}
const mapping = { 'lcp-ms': 'lcp', 'cls': 'cls', 'tbt-ms': 'tbt', 'inp-ms': 'inp', 'ttfb-ms': 'ttfb' };

export function dedupe(findings) {
  const map = new Map();
  for (const f of findings) {
    const k = f.id + '|' + (f.urls[0] ?? '');
    const prev = map.get(k);
    if (!prev || compareSeverity(f.severity, prev.severity) < 0) map.set(k, f);
  }
  return [...map.values()].sort((a, b) => compareSeverity(a.severity, b.severity) || a.id.localeCompare(b.id));
}
export const sortBySeverity = (fs) => [...fs].sort((a, b) => compareSeverity(a.severity, b.severity));
