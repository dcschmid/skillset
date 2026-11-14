# Core Web Vitals & measurement discipline

Thresholds verified 2026-11-14 (web.dev/articles/vitals, Google CWV docs):
good = **LCP ≤ 2500ms · INP ≤ 200ms · CLS ≤ 0.1** at p75, mobile and
desktop evaluated **separately**. INP replaced FID (final since Mar 2024).
Supporting lab metrics: TTFB ≤ 800ms, FCP ≤ 1800ms, TBT ≤ 200ms, SI ≤ 3400ms.

## Four data sources — never merge them silently
| source | answers | has INP? | reproducible in CI? | tool |
|---|---|---|---|---|
| RUM (own field) | what users feel | yes | no | own pipeline |
| CrUX | population p75 field | **yes (only here + RUM)** | API yes, volatile | PSI API |
| Lighthouse lab | one-load diagnosis | no (TBT proxy only) | yes (2 runs + tolerance) | lighthouse 13.x |
| Playwright interaction | scripted interaction latency | estimate | yes | playwright 1.6x |

Report rule: `metric @ source @ device @ timestamp` or it doesn't ship.
Lab score ≠ ranking report; CrUX p75 ≠ lab value; missing = UNAVAILABLE.

## INP specifics
INP = worst plausible interaction delay (of all interactions, page load
→ idle). Lab substitute: TBT (load-phase blocking) + long-task counts.
For interaction truth: playwright script a representative click/typing and
measure response (templates show the seam; `perf.playwrightRender` captures
jsErrors). Do NOT report TBT as "INP (lab)" — label the metric by its name.

## LCP pipeline & typical causes
request → TTFB → resource → render. Bottleneck attribution from waterfall:
TTFB: server render/cold start/no CDN cache. Resource: oversized/uncompressed
hero image, lazy-loaded LCP image, missing preload. Render: render-blocking
CSS, font swap, hydration blocking paint. Fix in that order — measurement
before code.

## CLS: images without dims, injected banners, font swap, late CSS,
animations on layout props. INP long tasks: hydration storms (CSR-heavy
Next/React), third-party tags, sync island hydration.

## Skill integration points
- budgets: `config/performance-budgets.json` → `ci` gate (lab-safe metrics only)
- snapshots: `.seo-report/snapshot-*.json` carry `metrics[]` with source tags
- `compare`: classifies delta vs `tolerancePct` → noise|regression|improvement
  + `environmentChanged` flag when test env changed (framework/Node diff)
- optional live: `perf.psiFieldData()` (network; graceful UNAVAILABLE offline),
  `perf.lighthouseRun()` (local Chrome; form-factor split)

## Measurement protocol (repeatable)
1. Same conditions both sides: same build mode, device emulation, network,
   repeat count (≥2), cold/warm stated.
2. Fixed pages: pick representative routes by type (home, content, listing)
   and pin them in config — drift between runs is environment, not regression.
3. Record page load budget + interaction budget separately.
4. Report p75 language for field, raw ms + repeat median for lab.
