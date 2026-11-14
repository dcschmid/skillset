# React + Vite (CSR) — SEO/perf layer

Detection: react+vite deps; rendering=csr-default. The delivered HTML is a
shell — SEO checks MUST run against post-render DOM or pre-rendered output.

## Rendering-parity discipline (the core finding class)
`seo.mjs` pre/post comparison (needs playwright; else UNVERIFIED_RENDERING).
content-js-only = high when SEO body exists only post-render. Recommended
order (never forced migration):
1. keep CSR, add `vite-plugin-ssr`-free options first: **pre-render**
   (vite-plugin-prerender/similar) if routes are enumerable;
2. static meta in index.html + react-helmet-async per route (title/meta/
   canonical in DOM before hydration snapshot);
3. SSR via framework only if content scale/intent justifies (approval:
   framework-migration class) — Astro/Next suggestion is a PROPOSAL with
   evidence, never an auto-move.

## Perf seams (CSR specifics)
bundle: route-level dynamic import (`React.lazy` + router split); js-transfer
budget on dist/assets; lazy below-fold; heavy deps (date/moment/icon sets)
tree-shaken or swapped inside existing stack; double deps deduped.
Third-party after interaction; CLS: Suspense skeletons with reserved height.
`npm run build && serve dist` then audit URL for honest lab numbers.
