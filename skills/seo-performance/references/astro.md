# Astro — SEO/perf layer (skill: `astro` owns framework depth)

Detection: `astro` dep. Baseline verified: Astro 7.4.x (2026-11-14).
If an `astro` skill is installed, delegate internals; this is the audit seam.

## Layout-level SEO (the SEO component pattern)
`src/components/SEO.astro` or head slot in layouts: `<title>` + description
propagated per route (no global constants); `site:` set in astro.config →
canonical/sitemap absolute; `<html lang>` per locale.

## Canonical & sitemap
`@astrojs/sitemap` in integrations (excludes prerender:false by default);
sitemap in robots via config or generated file. `astro.config.site` missing
⇒ relative canonicals (detector: canonical-missing/points-elsewhere noise).

## Islands = performance strategy
client:* only on interactive components (detector counts islands vs files);
server:defer for slow non-critical blocks; zero client JS on content routes.
INP: hydrate-on-visible for below-fold, avoid client:load carousels.

## Images: astro:assets (AVIF/WebP + dims automatic). Hero: `preload`/
priority equivalents — no lazy on LCP (detector catches lcp-image-lazy).
Fonts: Fonts API (subset+swap automatic).
Content Collections: content dates flow to lastmod/schema dates.
Route caching & on-demand rendering: prerender:false routes need adapter +
are sitemap-excluded — verify intentional.
Fix seam safety: templates edit .astro source; built dist edits (fix mode)
land in dist only until next build — prefer source edits from findings'
`files` evidence.
