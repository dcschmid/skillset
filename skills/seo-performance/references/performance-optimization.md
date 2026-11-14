# Performance optimization playbook

Order of operations: measure → attribute → smallest root-cause fix in the
project's own stack → re-measure. Never delete features/functionality or
degrade a11y for numbers. Framework-native solutions beat new dependencies.

## Images
- modern formats via framework asset pipeline (astro:assets AVIF/WebP,
  next/image); explicit width/height or aspect-ratio (CLS).
- LCP image: eager + `fetchpriority=high` + preload; NOT lazy. Other images:
  lazy. Responsive srcset/sizes; no CSS-upscaled small bitmaps.
- detectors: img-dimensions-missing, lcp-image-lazy; budget: image-total-kb.

## JavaScript
- payload: js-transfer-kb budget; route-level code-splitting; dynamic import
  for below-fold/interaction-only components; dedupe double deps
  (`npm dedupe`/resolutions, not new libs).
- hydration: Astro islands minimal client JS (only interactive components
  get client:load/idle); Next: Server Components default, 'use client'
  surgical; React/Vite: consider pre-render/SSR when SEO demands (react.md).
- third-party: load after interaction where possible; tag-manager audit.

## CSS: inline critical path (framework does it: Astro compress, Next
auto-extract); AVOID import-on-demand bloat; expensive selectors/deep
`:has()` chains rare; animate transform/opacity only.

## Fonts: subset, ≤2 families/weights, woff2, preload only LCP-visible
font, font-display swap + metric-compatible fallback (size-adjust) to kill
shift. Astro Fonts API/next/font handle most — prefer them.

## Server/network: compression (brotli), cache-control, HTTP/2+, CDN,
static where possible (TTFB detector → ttfb-slow findings route here).

## Controlled workflow (fix mode)
1 baseline snapshot → 2 attribute (waterfall/long-tasks, name the file) →
3 fix (framework-native, no new deps unless user approves) → 4 verify:
build + tests + browser spot-check + lighthouse re-run + `compare` →
5 document (delta + residuals + risks).
Approval gates: architecture changes, redirect migrations, canonical
rewrites, content removal.
Regressions: budgets in `config/performance-budgets.json` + CI gate.
