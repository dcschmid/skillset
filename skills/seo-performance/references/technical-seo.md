# Technical SEO — detector catalog

Each detector emits reproducible findings (evidence = bytes/response facts).
`scripts/seo.mjs technical <target>` runs this scope. Implementations:
`scripts/lib/detectors.mjs`.

## Crawling & status
| check | evidence | severity | notes |
|---|---|---|---|
| 5xx / 404 on linked routes | response status | critical/high | dead internal links too |
| soft-404 suspect | 200 + <600 chars + "not found" copy | medium | needs status-code confirmation |
| redirect chain >3 hops | chain length | medium | point links at final URL |
| redirect loop | repeated URL in chain | critical | break in server config |
| robots.txt Disallow hits indexable page | pattern match | high | robots ≠ index removal |
| non-standard robots directives | parse | medium | Google honors allow/disallow/sitemap/crawl-delay |

## Indexability
- meta robots / X-Robots-Tag noindex on important page → high (approval to
  remove: canonical-adjacent).
- indexable-vs-indexed honesty: without Search Console the report says
  "technically indexable", never "indexed by Google".

## Canonicals
- missing → low; points elsewhere → medium (verify intent); multiple → medium;
  scheme mismatch → medium; collision (N pages → 1 target) → medium;
  conflicts hreflang-self → medium.
- Approval gate: bulk canonical rewrites = content-structure change.

## Sitemaps
Parse XML, then fetch each loc: dead entries, non-canonical entries,
noindex-listed, future lastmod, index integrity, size structure.
Framework generators: @astrojs/sitemap, next/sitemap.ts|js, static generator
plugins — fix the generator, not the XML by hand.

## Page structure
title unique/10-70ch; description present/unique-per-template; h1==1;
heading nesting; viewport; charset; semantic landmarks; breadcrumb presence;
orphan pages (crawled, no internal inbound); duplicate descriptions;
URL params/funnels flagged for the project, not deleted.

## hreflang
absolutes only; valid BCP47 (xx / xx-YY / x-default); reciprocity required
across the group; language must agree with html lang and canonical.
i18n sites: run the group check (`analyzePages` i18n section) on every locale.

## JS SEO / rendering parity
Compare delivered HTML vs post-render DOM (playwrightRender when available):
content delta >2× with meaningful absolute size → content-js-only (high).
Without a browser: flag UNVERIFIED_RENDERING, recommend `serve` + audit,
or `--render` path when playwright exists in the project.

## Honesty matrix (offline)
| question | answerable offline? |
|---|---|
| is it crawlable | yes |
| is it indexed by Google | no — needs GSC |
| will it get rich results | no — needs Rich Results Test |
| INP value | no — needs CrUX/RUM |
| rendered parity | only with browser |
