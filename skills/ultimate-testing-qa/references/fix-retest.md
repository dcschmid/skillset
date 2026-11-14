# Fix-retest protocol (Workflow E — the skill's core)

A defect without a fix + retest is an unfinished task. Source editable?
Run the loop. Not editable (third-party host, deployed site you don't own)?
Stop at reproduce + diagnose + handoff packet.

## 1. Reproduce as a test

Defect becomes an executable artifact: failing Vitest case (logic/UI unit)
or failing Playwright spec (browser/flow). No artifact → not confirmed;
"looks like a bug" → NEEDS REVIEW with repro steps, never FAIL.
Smallest surface: single route, single input, deterministic data.

## 2. Isolate

- Vitest: `vitest related <suspect>` → which sources cover the test; stack
  frames → file:line.
- Playwright: trace (`npx playwright show-trace`) → network tab, console,
  DOM at failure frame.
- Bisection when new: `git bisect run npx vitest run <file>`.
- Classify first: source bug vs test bug vs environment. Environment (missing
  browser, offline, port) → fix the env, don't patch source to appease it.

## 3. Locate the root cause

Fix where the defect originates, not where it surfaces. Symptom patches
(guard clause hiding an undefined, `try/catch` swallowing, `await sleep()`
in tests) are banned: name the invariant broken, show which caller violates
it. If root cause is a dependency: pin/upgrade with lockfile diff shown, or
wrap at the boundary + regression test for the wrapper.

## 4. Minimal fix

Smallest diff restoring the invariant; no drive-by refactors. Preserve
design intent and existing conventions (naming, structure, style of the
file being fixed). Exported-signature changes → LSP/grep references, update
every caller in the same change.

## 5. Retest ladder (all four, in order)

1. the failing test → green (was red: proves fix, `vitest run <file>` /
   `npx playwright test <spec>`)
2. its suite → no collateral (`vitest run` / project's e2e script)
3. build/type gate the project already has (`tsc --noEmit`, framework build)
4. live re-audit for browser defects: re-run the Workflow C health test

Then regression lock: no test existed → write the one that locks the fix
(it fails without the patch — that is the whole point).

## 6. Before/after evidence

Report rows move FAIL → PASS with evidence pointers (trace file, vitest
output, screenshot pair). qa.mjs report renders both snapshots; never
overwrite the before-file (dated suffix).

## Handoff packet (source not editable)

repro steps · failing artifact (spec file) · observed vs expected · located
origin (file/endpoint/version) · suggested patch · affected-user scope.
Status NEEDS REVIEW with the packet, not silent FAIL.

## Flaky triage (honesty rules)

`retries: 1` in CI is transport insurance, not a fix. Two green runs after
a fix + the trace clean → PASS. Intermittent → trace the failing attempt,
fix timing by waiting on state (web-first assertions), not wall time.
Quarantine = `test.fixme` + issue link + re-run date, listed in reports.
