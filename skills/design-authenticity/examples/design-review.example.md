# Design review — example report (REVIEW mode, fictional "harbor-ferry" dashboard)

render: screenshots/harbor-2026-11-14/{desktop,light,dark}.png (Playwright)
context: tokens at src/styles/tokens.css (marine navy brand), direction=industrial
gate: identity 16/20 · type 12/15 · layout 11/15 · fit 13/15 · components 7/10
content 9/10 · responsive 4/5 · a11y 8/10 => 80/100 (heuristic; < 90, refactors listed)

## Findings (schema: severity/component/observation/rationale/fix)

C1 major — schedules page
  component: src/routes/schedules/+page.astro (sections L40-120)
  observation: 4 equal stat-cards + centered hero H1 + 2 CTAs, identical to any
    SaaS starter; departures table already answers the same task.
  rationale: repeatable-template layout that does not serve the ferry task
    (find next departure, platform, status); content differs, layout says "same".
  fix: replace card row with one status strip (next departure, platform, delay);
    table becomes primary element.

A2 minor — tokens
  component: src/styles/tokens.css:12
  observation: --accent = #6366f1 (default indigo) beside brand navy #0f3a5c.
  rationale: brand is marine; indigo is an unexamined default, competes with brand.
  fix: --accent -> signal yellow #f2b134 (wayfinding read), verify 4.5:1 on navy.

J1 minor — components
  observation: 3 button radii in use (4/8/16px) across sibling toolbars.
  fix: one radius token per size step; migrate consumers.

## Non-findings (classification filter fired)

- 3 cards on pricing page: genuinely parallel plans, equal weight correct — no finding.
- backdrop-blur on map overlay: deliberate glass per existing brand doc — no finding.
- dense 12-col grid on admin: project constraint (data density) — no finding.

## Blockers

none (a11y tooling: 0 AA violations, keyboard walk ok; focus rings pass on navy)

## Refactor priorities

1 (C1) -> retest schedules route -> re-gate. 2 (A2) -> contrast recheck. 3 (J1).
