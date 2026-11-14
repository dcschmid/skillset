# Refactoring Plan — {{SCOPE}}

Intent class: REFACTOR | BUG FIX | FEATURE CHANGE (one per package; split otherwise)

## Behavior inventory (what must not change)
signatures · returns · error types/order · API shapes · serialization ·
persisted data · side-effect order · event order · async timing · state
transitions · UI behavior · perf envelope · platform compat.
Unlistable → residual risk, stated.

## Baseline
- commands: {{CHECK_CMDS}} (verify_changes.py --save-baseline)
- failing-before: {{TEST_IDS}} (attributed to baseline)
- characterization tests added: {{YES/NO — required before MEDIUM/HIGH edits}}

## Packages (each: one pattern, one commit-sized diff, verified, revertible)
| # | Pattern | Files | Precondition check | Verification | Risk | Status |

## Rollback unit
own hunks only; user's dirty files untouched; mixed files → manual revert or stop.

## Exit gate
no NEW failures vs baseline · no unintended API change · no new P0/P1 ·
behavior diffs labeled · UNVERIFIED list explicit.
