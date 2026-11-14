# Performance — measure, then ship

Astro's default is fast; performance work = protecting that default and
measuring the deltas you add. No claimed numbers without a before/after run.

## Budgets (start values, tune per project)

| Metric | Static content pages | SSR pages |
|---|---|---|
| JS per route (gz) | 0 KB ideal, < 20 KB with island | same + island |
| CSS per route (gz) | < 15 KB | < 15 KB |
| LCP (4G) | < 2.5 s | < 2.5 s |
| CLS | < 0.1 | < 0.1 |
| INP | < 200 ms | < 200 ms |
| Build | watch `--verbose`; flag regressions > 20% |

## The levers (Astro-specific, in order of payoff)

1. **Zero-JS by default**: audit every `client:*` and `<script>` — is the
   island required? Delete the hydration before optimizing the bundle.
2. **Static where possible**: on-demand routes only for per-request data;
   server islands keep the page cacheable (rendering-routing.md).
3. **Route caching (7+)**: `Astro.cache`/`routeRules` on on-demand routes;
   SWR for list pages (caching.md rules).
4. **Images**: `astro:assets` on all raster; dimensions on every tag; AVIF/WebP;
   hero `fetchpriority="high"`, rest lazy; alt+width+height → CLS.
5. **Fonts**: self-host subset woff2, `font-display: swap`, preload LCP font,
   metric-compatible fallback; Fonts API (7+) for provider-based loading.
6. **Build timings**: Rust compiler + Sätteri are the baseline; slow builds →
   `astro build --verbose` + Build Timing Diagnostics (7.4+): identify slow
   collections/pages/plugins; MD count → loader parallelism; remote fetches in
   `getStaticPaths`/loaders → batch or move to islands.
7. **Caching headers/CDN**: hashed assets immutable; HTML per adapter/host
   (deployment.md headers).
8. **Third-party**: analytics/an embeds behind islands or `client:idle`;
   preconnect hosts; delete unused ones.

## Measure (the commands, honest reporting)

```bash
astro build --verbose                 # timings; dist/ inspection
npx lighthouse http://localhost:4321 --preset=perf   # SERVED: before/after
node scripts/audit_astro_project.mjs .               # JS-heavy route census
du -sh dist/_astro/*.js | sort -h                   # bundle census (gz aware)
```
Report: command → number → interpretation. A "faster" without numbers is
UNVERIFIED.

## Streaming & TTFB (SSR)

Early HTML flush then await (Astro renders streamed by default on 7) — put
slow data fetches after above-fold markup or in a server island; measure TTFB
and LCP separately.
