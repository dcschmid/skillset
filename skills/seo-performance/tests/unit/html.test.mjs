import assert from 'node:assert/strict';
import { parseAttrs, tags, innerHtml, stripTags, visibleSignature, inspectHead, inspectBody, images, assets, jsonLdBlocks, normalizeUrl } from '../../scripts/lib/html.mjs';

export default function (t) {
  t('parseAttrs quoted/unquoted/boolean', () => {
    const a = parseAttrs(' rel="canonical" href=\'/x\' data-n=3 async');
    assert.equal(a.rel, 'canonical'); assert.equal(a.href, '/x'); assert.equal(a['data-n'], '3'); assert.equal(a.async, '');
  });
  t('tags finds void + self-closing + attrs', () => {
    const ts = tags('<div><img src="a.png" alt="x"><br/><p>hi</p></div>');
    assert.deepEqual(ts.map((x) => x.tag), ['div', 'img', 'br', 'p']);
    assert.equal(ts[1].attrs.alt, 'x');
  });
  t('stripTags removes scripts/styles', () => {
    assert.equal(stripTags('<p>a</p><script>var x="<b>";</script>'), 'a');
  });
  t('visibleSignature deterministic + diff-sensitive', () => {
    const a = visibleSignature('<p>hello world</p>'), b = visibleSignature('<p>hello world</p>'), c = visibleSignature('<p>hello worlds more</p>');
    assert.equal(a.textHash, b.textHash); assert.notEqual(a.textHash, c.textHash);
    assert.ok(a.textLength > 0);
  });
  t('inspectHead extracts canonical/hreflang/lang/meta', () => {
    const h = inspectHead(`<html lang="de"><head><title>T</title><meta name="robots" content="noindex">
      <link rel="canonical" href="https://x.test/"><link rel="alternate" hreflang="EN" href="/en/">
      <meta property="og:title" content="o"><meta name="description" content="d"></head><body>`);
    assert.equal(h.title, 'T'); assert.equal(h.canonical, 'https://x.test/');
    assert.equal(h.hreflangs[0].hreflang, 'en'); assert.equal(h.htmlLang, 'de');
    assert.equal(h.metaDescription, 'd'); assert.equal(h.robotsMeta, 'noindex'); assert.equal(h.ogTags, 1);
  });
  t('inspectBody heading count + landmarks', () => {
    const b = inspectBody('<nav></nav><main><h1>a</h1><h1>b</h1><h2>c</h2></main>');
    assert.equal(b.headings.h1, 2); assert.equal(b.headings.h2, 1); assert.equal(b.semanticTags.main, 1);
  });
  t('images flags lazy/eager/missing dims', () => {
    const [im] = images('<img src="h.png" loading="lazy"><img src="a.png" width="1" height="2" alt="">');
    assert.equal(im.lazy, true); assert.equal(im.alt, undefined);
    assert.equal(images('<img src="a.png" alt="">')[0].alt, '');
  });
  t('assets: blocking scripts counted, jsonld typed', () => {
    const a = assets('<script src="s.js"></script><script src="d.js" defer></script><script type="application/ld+json">{}</script><link rel="stylesheet" href="c.css">');
    assert.equal(a.blockingScripts, 1);
    assert.equal(a.scripts.filter((s) => s.jsonLd).length, 1);
    assert.equal(a.styles.length, 1);
  });
  t('jsonLdBlocks parses multi + reports broken', () => {
    const bs = jsonLdBlocks('<script type="application/ld+json">{"@type":"A"}</script><script type="application/ld+json">{bad</script>');
    assert.equal(bs.length, 2); assert.equal(bs[0].ok, true); assert.equal(bs[1].ok, false);
  });
  t('normalizeUrl: scheme/host case, trailing slash, hash', () => {
    assert.equal(normalizeUrl('HTTPS://X.Test/A/#frag'), 'https://x.test/A');
    assert.equal(normalizeUrl('https://x.test/a/'), normalizeUrl('https://x.test/a'));
  });
}
