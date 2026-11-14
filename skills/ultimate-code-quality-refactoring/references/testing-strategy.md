# Testing Strategy

The skill runs the project's tests, it does not invent parallel ones.

## Order of operations

1. Discover runners from manifests (`detect_project.py`
   `test_commands_declared`) — package.json scripts, pytest/go/cargo/
   gradle/dotnet conventions, Defold/Godot headless checks.
2. Run BEFORE edits → baseline (existing failures recorded per test id).
3. After each refactor step: affected subset only (fast loop).
4. End of work package: full relevant suite once.
5. Compare verdicts to baseline; classify failures NEW / PRE-EXISTING / FIXED.

Declared-but-never-executed commands stay "declared"; report UNVERIFIED
until actually run. Never claim a pass that was not executed.

## Missing test layer handling

| Situation | Action |
|---|---|
| No tests at all | characterization tests first work package; risky edits blocked until covered |
| Tests exist, failing | record as baseline; your diff may not add failures |
| Runner broken/flaky | flaky ≠ passing; report; rerun once, then report |
| No runner on machine | UNVERIFIED + exact command the user can run |

## Adding tests (only when needed and in project style)

Characterization pins existing output; regression tests pin the changed
contract. Place them where the project places tests; use its fixture
conventions; no new framework without approval.

## Evidence for web/game surfaces

Web: existing Playwright/cypress suite or headless browser check; visual
diff only where snapshots already exist. Games: engine headless validation
(Defold editor `--headless`, Godot `--headless --import`/`--quit-after`),
scene/resource load checks, deterministic sim replay — see
language-adapters.md.
