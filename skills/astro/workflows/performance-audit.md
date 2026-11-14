# Workflow: Performance & SEO Audit Pass

Measure → fix → re-measure. Every claim gets a number.

1. **Baseline (run, don't assume)**:
   - `astro build` duration + `--verbose`; `du -sh dist/_astro/*` (JS/CSS census)
   - Lighthouse on `/` + 2 representative routes (mobile preset): LCP/CLS/INP,
     save JSON artifacts
   - Route census: which routes are static vs on-demand (audit script /
     `astro build` log)
   - SEO crawl sanity: titles unique, canonicals absolute, sitemap 200s,
     images have dimensions+alt
2. **Rank findings by payoff** (performance.md levers): delete unrequested
   JS first, then image/font/caching, micro-optimizations last.
3. **Fix one lever at a time**, ordered list in the report: change → expected
   metric → command.
4. **Re-measure** identically; per-metric table before/after/delta. Build-time
   claims cite the timing output; perf claims cite Lighthouse JSONs.
5. **Ship gate**: check + build + preview smoke; budgets (performance.md)
   green or consciously relaxed with reason noted.
6. Report: table of metrics, list of changes, remaining slow spots + why
   deferred.
