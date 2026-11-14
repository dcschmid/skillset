# SEO & i18n — discoverability without hacks

## SEO (App Router-first; SPA variant noted)

- **Metadata API** (app-router.md): `generateMetadata` per route; title
  template; canonical via `metadata.alternates.canonical` / `metadataBase`;
  OG images via `opengraph-image.tsx` conventions; `sitemap.ts`, `robots.ts`,
  RSS per file conventions — read local docs before hand-writing `<head>`.
- Structured data: JSON-LD `<script type="application/ld+json">` rendered
  server-side from typed DTOs (recipe component; escape like JSON-in-HTML).
- Rendering for crawlers: SSR/static output by default (rendering.md) — a
  CSR-only SPA needs the host's prerender story or a framework switch note;
  never ship SEO pages as client-only renders.
- Indexing hygiene: one h1, semantic landmarks (a11y.md doubles), image alt,
  internal links as real anchors (`<Link>`), pagination rel, 301s via config.
- Audits: lint `<title>`/description per route; sitemap ↔ routes parity test.

## i18n (opt-in complexity — only where multilingual is a requirement)

- **Routing:** locale path prefix (`/[locale]/…`) or subdomain; middleware/
  proxy for locale detection + redirect; `generateStaticParams` per locale.
- **Strings:** typed message modules/JSON per locale; a thin `t()` over a
  record — libraries (next-intl, FormatJS) when pluralization/load-on-demand
  is real need (dependency rule 7).
- **Dates/numbers/timezones:** `Intl` built-ins with explicit locales and
  UTC-stored timestamps; display tz from user/locale, never server default.
- **RTL:** `dir` attribute per locale, logical CSS properties
  (`margin-inline-start`), mirrored icons via `transform: scaleX(-1)` under
  `[dir=rtl]`.
- **SEO×i18n:** hreflang alternates via `metadata.alternates.languages`,
  localized OG, per-locale sitemap entries, `lang` on `<html>` correct —
  test a locale switch keeps translations AND metadata.
- Small sites: 2 locales inline beat an i18n stack. Monolingual: install
  nothing.

## Verification

Metadata parity test (title/description present per route), sitemap test,
`hreflang` round-trip for one locale pair, Lighthouse SEO pass ≥ budget.
