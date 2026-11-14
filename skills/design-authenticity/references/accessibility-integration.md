# Accessibility Integration

Purpose: define the boundary and handoff between this skill and the project's
`accessibility` skill. A11y is a hard floor for original design, never a trade-off.

## Ownership boundary

- The `accessibility` skill owns WCAG interpretation, semantics, keyboard, focus,
  contrast math, SR behavior, and audit tooling. Do not restate or duplicate its
  rules; load it or run its tooling.
- This skill owns visual originality/coherence and ensures design choices keep
  a11y satisfiable (contrast-capable palettes, focus-visible-friendly layouts,
  motion with reduced-motion fallbacks).

## Hard floors for every design decision

Minimum WCAG 2.2 AA (AAA where realistic and stated). Concretely for design:

| Design choice | a11y obligation |
|---|---|
| Palette / effects | text + UI contrast computed at final values; effects never hide content or focus |
| Type scale | user text-scaling safe (rem/clamp), line-height ≥ 1.5 body, no clipped zoom |
| Layout | reflow at 320px without horizontal scroll; reading order = visual order |
| Interaction affordances | visible focus states designed as part of the look; targets ≥24px (44 touch) |
| Motion | reduced-motion variant for every non-essential animation |
| Color semantics | meaning always paired with text/icon/shape |
| Forms/data | labels + error messaging are design surface, not an afterthought |

## Originality budget

A "distinctive look" never blocks: keyboard traversal, announcements, contrast,
scaling, or focus visibility. If a direction conflicts, redesign the direction,
not the a11y. Editorial overlap that hides content, or glow that washes out text,
is failed design, not bold design.

## Verification handoff

- Automated: `accessibility` skill's tooling (axe+Playwright where available) can
  run the same surfaces this skill reviews; automated PASS ≠ conformance claim
  (that skill's rule, respected here).
- Manual: keyboard walk + contrast spot-check belong in this skill's quality gate
  "accessibility 10" line (`visual-quality-gates.md`); cite evidence, else NOT TESTED.
- Findings with contrast/focus observations are reported here AND in the gate;
  fix code in the project, not in this skill.

## Reading list for the a11y skill (do not copy)

`skills/accessibility/SKILL.md` mode gate; its `references/do-dont.md` for
surface rules; `tooling/a11y-audit` for runs. This skill never blocks on it; if
the a11y skill is unavailable (independent use), the floors above still apply
with the same severity.
