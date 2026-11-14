/**
 * crawler.mjs — polite BFS crawler, Node stdlib only.
 * External URLs: read-only, robots-respecting, same-host, rate-limited.
 * Local/fixture mode: reads files from disk or an in-memory map (offline tests).
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { inspectHead, inspectBody, images, assets, jsonLdBlocks, visibleSignature, normalizeUrl, absUrl } from './html.mjs';

export class Robots {
  static parse(txt) {
    const r = { raw: txt, disallow: [], allow: [], sitemaps: [], crawlDelay: null, error: null };
    let applies = false;
    for (const line of txt.split('\n')) {
      const l = line.trim();
      if (/^user-agent:/i.test(l)) { const ua = l.split(':')[1].trim(); applies = ua === '*' || /node|googlebot|curl/i.test(ua); continue; }
      if (!applies && !/^sitemap:/i.test(l)) continue;
      const d = /^disallow:\s*(\S*)/i.exec(l); if (d && d[1]) r.disallow.push(d[1]);
      const a = /^allow:\s*(\S+)/i.exec(l); if (a) r.allow.push(a[1]);
      const s = /^sitemap:\s*(\S+)/i.exec(l); if (s) r.sitemaps.push(s[1]);
      const c = /^crawl-delay:\s*([\d.]+)/i.exec(l); if (c) r.crawlDelay = parseFloat(c[1]);
    }
    return r;
  }
  constructor(txt) { Object.assign(this, Robots.parse(txt ?? '')); }
  allowed(url) {
    const path = (() => { try { return new URL(url).pathname; } catch { return '/'; } })();
    const hits = (pats) => pats.some((p) => new RegExp('^' + p.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*')).test(path));
    if (this.allow.length && hits(this.allow)) return true;
    return !hits(this.disallow);
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function crawl(opts) {
  const { startUrl, rootDir = null, fixtures = null, maxPages = 40, delayMs = 250, timeoutMs = 10000, retries = 1,
    respectRobotsTxt = true, allowSameHostOnly = true, maxBodyBytes = 524288, render = null, onProgress = null } = opts;
  const fileMode = !!rootDir;                    // audit built output on disk
  const fixtureMode = !!fixtures;                // in-memory map (offline tests)
  const origin = fileMode ? 'http://local.site' : fixtureMode ? 'http://fixture.site' : new URL(startUrl).origin;
  const urlFor = (path) => origin + (path.startsWith('/') ? path : '/' + path);
  const queue = [{ url: startUrl.startsWith('http') ? startUrl : urlFor(startUrl), depth: 0 }];
  const seen = new Set(queue.map((q) => q.url));
  const results = [];
  let robots = new Robots('');
  let fetched = 0;

  const fetchText = async (absUrlStr) => {
    if (fixtureMode) {
      const key = decodeURIComponent(new URL(absUrlStr).pathname).replace(/^\/+/, '') || 'index.html';
      const hit = fixtures.get(key) ?? fixtures.get(key.replace(/\.html$/, '')) ?? fixtures.get(key + '.html')
        ?? fixtures.get('/' + key) ?? null;
      return hit != null ? { text: hit, status: 200, headers: {}, finalUrl: absUrlStr, transferBytes: hit.length } : null;
    }
    if (fileMode) {
      const pth = join(rootDir, decodeURIComponent(new URL(absUrlStr).pathname).replace(/^\/+/, ''));
      for (const f of [pth, pth + '.html', join(pth, 'index.html')])
        if (existsSync(f) && !statSync(f).isDirectory())
          return { text: readFileSync(f, 'utf8'), status: 200, headers: {}, finalUrl: absUrlStr, transferBytes: readFileSync(f).byteLength };
      return null;
    }
    for (let i = 0; i <= retries; i++) {
      try {
        const ctrl = new AbortController();
        const t = setTimeout(() => ctrl.abort(), timeoutMs);
        const res = await fetch(absUrlStr, { signal: ctrl.signal, redirect: 'follow',
          headers: { 'user-agent': 'seo-performance-skill/1.0 (audit; read-only)', accept: 'text/html,application/xhtml+xml' } });
        clearTimeout(t);
        const buf = await res.arrayBuffer();
        const clipped = buf.byteLength > maxBodyBytes ? buf.slice(0, maxBodyBytes) : buf;
        const headers = {}; res.headers.forEach((v, k) => (headers[k] = v));
        return { text: new TextDecoder().decode(clipped), status: res.status, headers, finalUrl: res.url,
          transferBytes: buf.byteLength, chain: [{ url: absUrlStr, status: res.status }] };
      } catch (e) { if (i === retries) return { error: String(e.message ?? e) }; await sleep(300 * (i + 1)); }
    }
  };
  // robots.txt first (live mode only; file/fixture mode passes it in via context)
  if (!fileMode && !fixtureMode) {
    const rb = await fetchText(origin + '/robots.txt');
    if (rb && !rb.error && rb.status === 200) robots = new Robots(rb.text);
  }

  while (queue.length && results.length < maxPages) {
    const item = queue.shift();
    if (respectRobotsTxt && robots.raw && !robots.allowed(item.url)) {
      results.push({ url: item.url, depth: item.depth, skipped: true, reason: 'robots.txt Disallow' });
      continue;
    }
    const res = await fetchText(item.url);
    fetched++;
    if (!res || res.error) { results.push({ url: item.url, depth: item.depth, error: res?.error ?? '404-or-missing', status: null }); continue; }
    if (delayMs && fetched % 5 === 0) await sleep(delayMs);
    onProgress?.(results.length, item.url);
    const html = res.text;
    const finalUrl = res.finalUrl ?? item.url;
    const page = {
      url: item.url, finalUrl, depth: item.depth, status: res.status ?? 200, headers: res.headers ?? {},
      chain: res.chain ?? [{ url: item.url, status: res.status ?? 200 }], transferBytes: res.transferBytes ?? html.length,
      html, head: inspectHead(html), body: inspectBody(html), images: images(html), assets: assets(html),
      jsonLd: jsonLdBlocks(html), rendered: null,
      ttfbMs: res.ttfbMs ?? null, path: (() => { try { return new URL(finalUrl).pathname; } catch { return '/'; } })(),
      internalLinks: [], files: [],
    };
    page.head.__pre = page.head;
    page.body = page.body;

    if (render) { try { page.rendered = await render(finalUrl, html); } catch { page.rendered = null; } }
    const post = page.rendered?.html ? inspectBody(page.rendered.html) : page.body;
    page.visibleAfterRender = post?.visibleText;

    // internal links for BFS + link checks
    const internal = [];
    for (const raw of page.assets.links) {
      const u = absUrl(raw, finalUrl);
      if (!u || (u.protocol !== 'http:' && u.protocol !== 'https:')) continue;
      if (u.hash) { continue; }
      const same = u.origin === origin || !allowSameHostOnly;
      if (!same) continue;
      const clean = normalizeUrl(u.toString());
      internal.push(clean);
      if (!seen.has(clean) && !raw.startsWith('#')) { seen.add(clean); queue.push({ url: clean, depth: item.depth + 1 }); }
    }
    page.internalLinks = internal;
    results.push(page);
  }
  results.__robots = robots;
  results.__fetched = fetched;
  return results;
}
