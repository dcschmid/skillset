# Safe Auto-Fix — rules for changing existing code

Binding in AUDIT_AND_FIX, DESIGN_MODERNIZATION, ANTI_AI_SLOP_CLEANUP and any
fix-on-findings work. An audit NEVER silently becomes a refactor when only a
review was requested.

## Never (without explicit task mandate)

- remove working features · change APIs/data models · break auth · restructure
  routing · delete existing content · replace brand identity · add dependencies
  "for convenience" · overwrite uncommitted/foreign changes (check `git status`
  baseline first; build ON TOP) · delete tests to silence failures · ignore
  critical warnings.

## Prefer

- minimal, reversible, reviewable diffs · existing tokens before new literals ·
  existing components before new ones · consistent CSS architecture already in
  the project · semantic HTML · small changes over rewrites · fixes at the
  shared-source (token/variant) level when several surfaces drift identically.

## Risk gate (before each fix)

1. Blast radius: which consumers/routes read the touched token/component?
2. Behavior: does the fix alter logic, markup contract, or a11y semantics?
3. Reversibility: single commit-sized diff, no drive-by edits.
High technical risk → DOCUMENT the finding + proposed patch, do not apply.
Design-only task with functional P0 findings → document P0s, apply only
design-domain fixes; hand functional fixes back as recommendations.

## Verification per fix, not only at the end

project check/build/tests for the touched area after each batch; rendered diff
when browser available (`visual-regression.md`). Broken by a fix → revert that
fix, keep the rest. "Fixed" claims cite the command/output that proved it.

## Selectivity guarantee

scope from the request stays the scope: component audit → component fixes;
route fix → no site-wide rebuild; a small edit never triggers full design
discovery (`../workflows/guard.md` proportionality applies).
