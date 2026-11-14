# Workflow: CREATE

New surfaces: pages, apps, dashboards, design systems, game menus. Spine = 8
phases; proportional effort (small component = phases 1,2,6 compressed to
minutes; full site = all phases, real reviews).

1. **Product Understanding.** Discovery per SKILL.md: product, audience, tasks,
   existing brand/tokens/components, constraints, must-keep. Read files first;
   ask only what the project cannot answer. Output: 3–8 line brief.
2. **Visual Direction.** Shortlist from `references/design-directions.md`; pick
   one (or 2–3 distinct candidates → pick with a one-line why). Write the 3
   concrete decisions it forces (type pair, color strategy, layout rhythm).
   Existing system present → direction must extend it, not replace.
3. **Design System.** Author/extend tokens + component contracts:
   `typography.md`, `color-and-composition.md`, `design-principles.md`. In an
   existing system: additions over replacements; token-value edits need a reason.
4. **Implementation.** In the project's stack, per
   `references/framework-integration.md`. No new deps, no parallel systems.
   Every visual element traces to phase 2/3 decisions; IA before decoration.
5. **Visual Review (render).** If a browser/preview exists: render the real
   surface across configured viewports/states (`scripts/screenshot_audit.sh`,
   repo browser tooling) and LOOK at it. No browser → state source-only review;
   never claim a visual pass.
6. **Authenticity Review.** Run `references/anti-ai-patterns.md` A–J over the
   result; classify findings; fix `major`+, log `minor`/`nit`.
7. **Refinement.** Targeted fixes from findings; cap
   `max_refine_iterations` (default 2); re-render when cheap.
8. **Final Gate.** `references/visual-quality-gates.md` rubric; report per-axis
   + total + blockers + evidence level. >= configured minimum (default 90) or
   "delivered with open issues: …". Never loop forever.

## Binding for every step

- Proportional: trivial change → skip 2/3/7 internally, still respect GUARD
  floors while coding; do not run full discovery for a button tweak.
- Redesign ≠ default: existing working designs survive unless tasked otherwise.
- Report honesty: what was rendered vs inferred is stated per axis.
