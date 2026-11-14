# Visual Quality Gates — 100-point rubric + evidence rules

Purpose: the final gate for CREATE/REFACTOR and the report frame for REVIEW.
A structured heuristic, not an objective proof of quality. Target: **>=90**
(configurable minimum). Scores cite concrete observations or are not emitted.

## Scoring rubric

| Axis | Pts | 4-level shorthand (full→none) |
|---|---|---|
| Distinct visual identity | 20 | product-recognizable after name-swap; direction coherent → indistinguishable-from-template |
| Typography & hierarchy | 15 | chosen family/scale/ranks survive squint + reading → unchosen/flat |
| Layout & composition | 15 | rhythm/whitespace/grid serve tasks and content → uniform template grid |
| Product & audience fit | 15 | every section answers a real task/audience need → generic marketing skeleton |
| Component quality & consistency | 10 | components derived from function, one language → card-per-section, drifting variants |
| Content credibility | 10 | real/specific copy, no invented data → filler, fable metrics, lorem |
| Responsive design | 5 | verified across target viewports, states hold → desktop-only assumption |
| Accessibility | 10 | AA floor met with evidence (contrast, focus, scale, motion) → unverified or blocked |

**100 total.** Score each axis from observations; round-half honest. Report per-axis
lines, not just the total.

## Gate rules (binding)

1. **Blockers outrank points.** a11y blockers, broken interaction, real responsive
   failure, invented content → status "needs fixes" even at score 95. Fix, then rescore.
2. **No render, no visual score.** Without an actual render (or supplied
   screenshots), visual axes emit `VISUAL_REVIEW_REQUIRED`; deliver code-level
   findings only. Never fabricate a passing number.
3. **Score ≠ claim.** Report "gate 92/100 (heuristic, evidence: …)", never
   "objective quality 92".
4. **Iteration cap**: after `max_refine_iterations` (default 2) passes, deliver
   best + open-issues list. No silent loops.

## Evidence levels per axis

- identity/typography/layout/fit/components/content: render (screenshot/source of
  truth) + finding refs from `anti-ai-patterns.md` categories.
- responsive: renders or tests at the configured viewport set.
- accessibility: `accessibility-integration.md` handoff evidence (tool run,
  keyboard walk) or explicit NOT TESTED + reason.

## Report template

```
## Design gate — <surface> — <date>
render: <screenshot path | source-only | VISUAL_REVIEW_REQUIRED>
identity 18/20 · typography 13/15 · layout 12/15 · fit 14/15 · components 9/10
content 9/10 · responsive 4/5 · a11y 9/10  =>  88/100 (< 90 → refine)
blockers: none | <list>
findings: A1(minor, …), C2(major, …)   fixes: applied: …  open: …
```

Full worked example: `examples/design-review.example.md`.

## Tooling (preferred: existing repo tools)

- Screenshots: `scripts/screenshot_audit.sh` wraps an available browser
  (Playwright from `accessibility/tooling/a11y-audit` when installed; otherwise
  any CLI browser). Viewport matrix + states per invocation config.
- Structure: DOM inspection (the a11y tool's page handles) for heading order,
  landmark count, duplicate ids.
- Diff-only evidence rule: screenshot diffs flag CHANGE, never quality; judge
  with the rubric.
- Missing browser → say so; emit `VISUAL_REVIEW_REQUIRED`; do NOT output a
  passed screenshot audit. `scripts/validate_config.mjs` validates an optional
  project config; absence of config is not a failure.
