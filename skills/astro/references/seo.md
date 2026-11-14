# SEO — technical, per-route, verifiable

Prerequisite: `site: 'https://...'` set in config — canonical/sitemap/OG URLs
break without it. SEO here = mechanics; no ranking guarantees.

## Head contract (every route, via layout)

Per-route inputs: `title` (≤~60ch, unique), `description` (≤~160ch, unique),
canonical (self-URL; `Astro.url` with `site`), `og:` (title/description/
image/type/url), `twitter:card`, `robots` (default index,follow; drafts/noindex
utility pages opt out), `hreflang` clusters on i18n sites.

```astro
<!-- BaseLayout.astro, props: { title, description, ogImage?, noindex? } -->
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={new URL(Astro.url.pathname, Astro.site)} />
  <meta property="og:type" content="website" />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:url" content={new URL(Astro.url.pathname, Astro.site)} />
  <meta property="og:image" content={new URL(ogImage, Astro.site)} />
  <meta name="twitter:card" content="summary_large_image" />
  {noindex && <meta name="robots" content="noindex" />}
  <slot name="head" />   <!-- route-specific: JSON-LD, hreflang -->
</head>
```
(Content collections feed title/description/date → pass into layout props;
no page-level `<head>` sprawl.)

## Structured data (JSON-LD, in `slot="head"`)

Blog page → `Article`/`BlogPosting` (headline, datePublished/Modified, author,
image); docs → `BreadcrumbList` + `Article`; org → `Organization`; product →
`Product`+`Offer` where applicable. Emit from data, not literals; JSON-LD
`<script type="application/ld+json">` uses `set:html` from `JSON.stringify`.
Validate at `MEASURED` stage (Rich Results / schema.org validator) on sampled
templates.

## Discovery files

- `sitemap-index.xml` / `sitemap-0.xml`: `@astrojs/sitemap` integration or an
  endpoint built from the actual route list; `lastmod` from collection dates;
  every listed URL returns 200.
- `robots.txt`: `Sitemap:` line + allow-all default; per-route `X-Robots-Tag`
  for auth/noindex areas (middleware/endpoint header).
- RSS: `/rss.xml` endpoint from collections (`@astrojs/rss` or raw XML).
- `404.astro` real page, site-styled, links to key sections, HTTP 404 status
  (`Astro.response.status = 404` where applicable).

## URL hygiene

Lowercase, hyphenated, consistent `trailingSlash` config; one canonical casing
per resource; redirects (config `redirect` map) for renamed routes. Pagination
pages self-canonical.

## i18n sites

`hreflang` alternates + `x-default` from the locale route set (see
internationalization.md); localized titles/descriptions from collections.

## Verification (MEASURED, not claimed)

- `dist/` crawl: unique titles, all internal links 200, sitemap URLs resolve.
- Lighthouse SEO lane (testing.md); spot `curl` + `grep` per template.
