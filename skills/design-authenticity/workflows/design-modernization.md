# Workflow: DESIGN_MODERNIZATION

Modernize an existing design WITHOUT destroying brand identity or features.
"Better, not merely different." Inherits AUDIT_AND_FIX phases; emphasis differs.

1. **Identity lock.** Existing brand tokens, type, imagery, tone = authority to
   evolve, not replace. What must survive verbatim goes on the preservation
   list (`safe-auto-fix.md`). Direction: evolve current direction
   (`design-directions.md`) toward product/audience fit — do NOT paste a new
   template or a fresh AI default.
2. **Modernize within**, in this order (each = targeted diff, verified):
   typography (fit, hierarchy, scale, leading, responsive type) → spacing/
   rhythm → color usage (consistency, states, contrast; effects earn place) →
   visual hierarchy/IA → layout composition → components (variants at shared
   source) → navigation → responsive behavior → interaction/state design
   (hover/focus/loading/empty/error).
3. **Generic-output guard:** result passes `anti-ai-patterns.md` (no new
   interchangeable hero/feature-card/gradient defaults) and the name-swap test.
4. **Preservation regression:** features, routes, content, tokens consumers
   intact; visual regression pairs prove intended-only change
   (`visual-regression.md`); a11y never regresses (floors hold, tool rerun).
5. **Gate:** before/after rubric table (`visual-quality-gates.md`), target ≥90
   where project constraints + change budget allow; report + open issues per
   `audit-report-format.md`.
