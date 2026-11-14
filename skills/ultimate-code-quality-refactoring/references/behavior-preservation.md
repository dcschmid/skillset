# Behavior Preservation

The core quality goal: improve code without unnoticed regressions. A green
suite is necessary, not sufficient — enumerate what must stay stable, then
verify each class you can.

## Behavior inventory (before any edit)

Capture per touched module: function signatures · return values · error
behavior (types/orderings) · API response shapes · serialization formats ·
persisted data · side effects & ordering · event order · async timing ·
state transitions · UI behavior · performance envelope · platform compat.

Anything you cannot enumerate is residual risk — say so in the report.

## Category discipline (never mix silently)

- **REFACTOR** — behavior identical; verification target = old vs new.
- **BUG FIX** — behavior intentionally changes; verification target = new
  behavior matches spec; label every changed output.
- **FEATURE CHANGE** — additive; verification target = old behavior still
  reachable.

A refactor that "needs" a behavior change is not a refactor — split it.

## Legacy / untested code

Before touching untested code: write **characterization tests** that pin
current output (documenting the status quo, not endorsing it). If you cannot
run the code, do not edit it blind — mark UNVERIFIED and propose the tests
as the first work package.

## Techniques by need

| Need | Technique |
|---|---|
| No tests exist | characterization tests on public entry points |
| Complex invariant | property-based tests |
| Cross-service contract | contract tests against captured responses |
| Legacy output | golden master (record → edit → byte-compare) |
| Numeric/simulation | differential test old vs new on same inputs |

## Post-change verification ladder

syntax → format/lint → typecheck → unit (affected) → integration (affected)
→ contract/snapshot → build → full relevant suite → compare vs baseline.
Each unavailable rung is reported UNVERIFIED, not skipped silently
(`scripts/verify_changes.py`).
