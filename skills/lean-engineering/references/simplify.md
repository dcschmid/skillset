# /lean simplify — behavior-preserving simplification

Goal: less complexity, identical behavior. Applies to named files or the
touched area; never opportunistic rewrites of code the task didn't touch.

## Sequence (binding)

1. **Understand the current behavior.** Read the code, its callers, its
   tests, its fixtures. If behavior is uncertain and untested, write a
   characterization check first (a few asserts on real inputs) — that file
   is the contract for steps 3–6.
2. **Identify the checks.** Which tests/lint/typecheck cover this area?
   Record their current state (pass/fail) as the baseline; pre-existing
   failures stay attributed to the baseline, never blamed on this change.
3. **Small, reversible steps.** One idea per edit; each commit-sized. No
   full rewrites without a stated reason the increment cannot carry it.
   The public API stays: signatures, return shapes, data formats, error
   types the outside world reads — untouched unless the user asked.
4. **Preserve by category.** Security-relevant validation stays; error handling
   stays — handling of data-loss risk is never deleted
   (moving it is fine); invariants, locks, and platform quirks the code
   comments carry stay. Deletion applies to pass-through layers, unused
   knobs, dead branches — never to the floor list in
   engineering-ladder.md.
5. **Verify after each step** with the project's own commands
   (baseline from step 2). Green ≠ done: re-read the diff for side effects
   the tests don't cover (ordering, logging, telemetry, defaults).
6. **Unexpected effect → revert or fix now.** Revert own hunks only; the
   user's uncommitted work is untouchable.

## Git is the review surface

`git diff` after every step is the audit trail: hunks stay small enough to
read in one pass; format-noise is never mixed with behavior change.
Before destructive or hard-to-reverse operations (deleting a file, mass
rename, dropping a layer others consume) → explicit user approval first.

## Definition of done

- same observable behavior (tests + baseline diff clean, or deltas listed
  and explained)
- measurable delta stated honestly: lines, deps, concepts, round-trips —
  measured numbers only, N/A when unmeasured, nothing invented
- the simplify pass added no dependency, no framework, no new abstraction
- new non-trivial logic that survived the pass keeps its check
