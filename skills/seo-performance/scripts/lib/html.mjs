/**
 * html.mjs — small deterministic HTML inspection layer (stdlib only).
 * Regex tokenizer tuned for auditing heuristics, not spec-complete parsing.
 * Every check downstream treats these results as evidence about delivered
 * bytes, which is exactly what we want for SEO (crawlers see bytes too).
 */

const VOID_TAGS = new Set(['area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr']);

/** Parse a subset of attributes from a tag-open string. */
export function parseAttrs(str) {
  const attrs = {};
  const re = /([a-zA-Z:@][\w:.-]*)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g;
  let m;
  while ((m = re.exec(str))) {
    const name = m[1].toLowerCase();
    attrs[name] = m[2] ?? m[3] ?? m[4] ?? '';
  }
  return attrs;
}

/** All tags (open + self-closing) with positions. Comments stripped first. */
export function tags(html) {
  const clean = html.replace(/<!--[\s\S]*?-->/g, (c) => ' '.repeat(c.length));
  const out = [];
  const re = /<([a-zA-Z][\w:-]*)((?:\s+[^<>]*?)?)(\/?)>/g;
  let m;
  while ((m = re.exec(clean))) {
    out.push({
      tag: m[1].toLowerCase(),
      attrs: parseAttrs(m[2] || ''),
      selfClosing: m[3] === '/' || VOID_TAGS.has(m[1].toLowerCase()),
      start: m.index,
      openEnd: m.index + m[0].length,
      raw: m[0],
    });
  }
  out.__clean = clean;
  return out;
}

/** Inner content of the first element with given tag (naive but stable). */
export function innerHtml(html, tag) {
  const m = new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)</${tag}>`, 'i').exec(html);
  return m ? m[1] : null;
}

export function stripTags(html) {
  return html
    .replace(/<script[\s\S]*?<\/script\s*>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style\s*>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Signature of *visible* content for pre/post-render diffing. */
export function visibleSignature(html) {
  const text = stripTags(html);
  return {
    textLength: text.length,
    wordCount: text ? text.split(' ').length : 0,
    textHash: hash(text.slice(0, 8000)),
    linkCount: (html.match(/<a\s/gi) || []).length,
    imageCount: (html.match(/<img\s/gi) || []).length,
    headingCount: (html.match(/<h[1-6][\s>]/gi) || []).length,
  };
}

function hash(s) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

/** Head metadata extracted from raw delivered HTML. */
export function inspectHead(html) {
  const head = innerHtml(html, 'head') ?? html.slice(0, 60000);
  const t = tags(html);
  const meta = [];
  for (const x of t) {
    if (x.tag !== 'meta') continue;
    meta.push({
      name: x.attrs.name?.toLowerCase() ?? null,
      property: x.attrs.property?.toLowerCase() ?? null,
      httpEquiv: x.attrs['http-equiv']?.toLowerCase() ?? null,
      content: x.attrs.content ?? null,
    });
  }
  const title = innerHtml(html, 'title');
  const canonical = t.find((x) => x.tag === 'link' && x.attrs.rel === 'canonical');
  const hreflangs = t
    .filter((x) => x.tag === 'link' && x.attrs.rel === 'alternate' && x.attrs.hreflang)
    .map((x) => ({ hreflang: x.attrs.hreflang.toLowerCase(), href: x.attrs.href ?? '' }));
  const htmlTag = t.find((x) => x.tag === 'html');
  return {
    title: title ? stripTags(title) : null,
    titlePresent: title != null,
    metaDescription: meta.find((m) => m.name === 'description')?.content ?? null,
    robotsMeta: meta.find((m) => m.name === 'robots')?.content ?? null,
    viewport: meta.find((m) => m.name === 'viewport')?.content ?? null,
    charsetPresent: meta.some((m) => m.name === 'charset' || m.httpEquiv === 'content-type') || /<meta[^>]+charset=/i.test(head),
    canonical: canonical?.attrs.href ?? null,
    hreflangs,
    htmlLang: htmlTag?.attrs.lang ?? null,
    ogTags: meta.filter((m) => m.property?.startsWith('og:')).length,
    twitterTags: meta.filter((m) => m.name?.startsWith('twitter')).length,
  };
}

export function inspectBody(html) {
  const t = tags(html);
  const headings = {};
  for (let i = 1; i <= 6; i++) headings[`h${i}`] = 0;
  for (const x of t) if (x.tag in headings) headings[x.tag]++;
  const body = innerHtml(html, 'body') ?? html;
  return {
    headings,
    semanticTags: {
      nav: (body.match(/<nav[\s>]/gi) || []).length,
      main: (body.match(/<main[\s>]/gi) || []).length,
      header: (body.match(/<header[\s>]/gi) || []).length,
      footer: (body.match(/<footer[\s>]/gi) || []).length,
      article: (body.match(/<article[\s>]/gi) || []).length,
    },
    visibleText: visibleSignature(html),
    breadcrumb: /breadcrumb/i.test(html.slice(0, 60000)),
  };
}

export function images(html) {
  return tags(html)
    .filter((x) => x.tag === 'img')
    .map((x) => ({
      src: x.attrs.src ?? x.attrs['data-src'] ?? null,
      srcset: x.attrs.srcset ?? null,
      alt: 'alt' in x.attrs ? x.attrs.alt : undefined,
      width: x.attrs.width ?? null,
      height: x.attrs.height ?? null,
      loading: x.attrs.loading ?? 'eager(default)',
      fetchpriority: x.attrs.fetchpriority ?? 'auto(default)',
      decoding: x.attrs.decoding ?? null,
      sizes: x.attrs.sizes ?? null,
      lazy: x.attrs.loading === 'lazy',
    }));
}

export function assets(html) {
  const t = tags(html);
  const scripts = t
    .filter((x) => x.tag === 'script')
    .map((x) => ({
      src: x.attrs.src ?? null,
      inline: !x.attrs.src && !(x.attrs.type || '').includes('json'),
      jsonLd: (x.attrs.type || '').includes('ld+json'),
      defer: 'defer' in x.attrs,
      async: 'async' in x.attrs,
      type: x.attrs.type ?? null,
    }));
  const styles = t
    .filter((x) => x.tag === 'link' && (x.attrs.rel === 'stylesheet' || x.attrs.rel === 'preload'))
    .map((x) => ({ href: x.attrs.href ?? null, rel: x.attrs.rel, media: x.attrs.media ?? null, as: x.attrs.as ?? null }));
  const links = t
    .filter((x) => x.tag === 'a' && x.attrs.href)
    .map((x) => x.attrs.href);
  const fonts = (html.match(/@font-face/gi) || []).length + (html.match(/\.(woff2?|ttf|otf)(["'?])/gi) || []).length;
  const inlineStyleBytes = (innerHtml(html, 'style') ?? '').length + (innerHtml(html, 'head')?.match(/<style/gi) || []).length;
  return { scripts, styles, links, fonts, inlineStyleBytes, blockingScripts: scripts.filter((s) => s.src && !s.defer && !s.async && !(s.type || '').includes('module')).length };
}

export function jsonLdBlocks(html) {
  const re = /<script[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script\s*>/gi;
  const out = [];
  let m;
  while ((m = re.exec(html))) {
    const raw = m[1].trim();
    try { out.push({ raw, ok: true, data: JSON.parse(raw) }); }
    catch (e) { out.push({ raw, ok: false, error: e.message }); }
  }
  return out;
}

/** Absolute-ize and normalize for identity/duplication logic. */
export function absUrl(href, baseUrl) {
  try { return new URL(href, baseUrl); } catch { return null; }
}

export function normalizeUrl(u) {
  try {
    const url = new URL(u);
    url.hash = '';
    url.host = url.host.toLowerCase();
    if (url.pathname.length > 1 && url.pathname.endsWith('/')) url.pathname = url.pathname.slice(0, -1);
    return url.toString();
  } catch { return u; }
}
