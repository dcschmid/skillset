# Next.js — SEO/perf layer (skill `react-nextjs` owns framework depth)

Detection: `next` dep; app vs pages router detected by dir. Baseline:
Next 16.x (2026-11-14).

## Metadata (app router): Metadata API + generateMetadata per route;
exportMetadata absolute URLs; `metadataBase` set. Pages router: next/head
per page. Missing ⇒ detector title-missing/description-missing.
`app/robots.ts` + `app/sitemap.ts` emit both (dynamic, route-table accurate —
beats static files drift). OG images: ImageResponse/opengraph-image files.

## Rendering & SEO risk matrix
- Server Components default: content in delivered HTML (good for crawlers
  incl. no-JS AI crawlers). 'use client boundary = hydration payload: keep
  surgical; SEO content ABOVE boundary.
- Full CSR client pages / large client components ⇒ content-js-only risk
  (rendering parity detector fires). dynamic/ssr:false only with reason.
- Streaming/Suspense: streamed shell + late content is delivered bytes
  (fine); useEffect-fetch rendered content is not (flag).
- generateStaticParams/ISR: static where content is static; TTFB findings
  on server routes route to caching/CDN work, not content deletion.

## Perf seams
next/image (dims+formats automatic); next/font (no shift, no requests);
bundle: route-level code splitting automatic — audit heavy client deps via
js-transfer budget; double deps from client/server split; revalidation
strategy affects TTFB not correctness.
Fix seam: edit app/ files from finding evidence; audit via built output
(.next/standalone or export) or serve + URL.
