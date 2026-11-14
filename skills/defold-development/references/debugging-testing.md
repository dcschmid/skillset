# Debugging & Testing — Defold 1.14.1 baseline

Load for bug hunts, test design, or CI wiring. Levels of verification claims:
SKILL.md truth ladder. Facts: `/manuals/debugging-game-logic` (editor debugger
+ DAP), `/manuals/debugging-game-and-system-logs`, `/manuals/automated-testing`,
`/manuals/profiling`, `/ref/profiler`.

## Lua debugger (editor + DAP)

The editor ships a debugger for game logic: breakpoints, step, inspect script
instances, live in the running app; it speaks DAP, so external clients (VS
Code et al.) attach — `/manuals/debugging-game-logic`. Use it for state
questions ("what is hp *now*"), not for timing — stepping changes frame
behavior; timing goes to the profiler (`performance.md`). Native (C++) bugs:
`/manuals/debugging-native-code` (+ Android/iOS variants).

## Logs

Engine + game logs: console in editor; on device enable
**Write Log File** (`[log] write_log_file = 1`) — file location per
`/manuals/debugging-game-and-system-logs` (mobile via dev app / platform
tooling). `print()`/`pprint()` are the built-ins; tag lines
`[module] what/why` (`lua-engineering.md`). Log spam is a bug: unknown
message ids log once, per-frame paths log nothing.

## Unit tests for pure Lua logic

There is **no engine `unit_test` module** at 1.14.1 — not in the manuals, not
in the Lua API list. Two honest routes:

1. **Plain harness** (zero deps, default): modules are pure
   (`architecture.md`) so drive them outside the engine or in a headless
   bundle; `assert` + tiny runner is enough.

```lua
-- tests/test_damage.lua — runs under plain lua OR headless dmengine
local damage = require("game.shared.damage")
assert(damage.apply({hp = 10}, {amount = 3}).hp == 7)
assert(pcall(damage.apply, {}, {amount = 1}) == false, "validates input")
print("TEST {\"event\":\"suite_end\",\"status\":\"pass\"}")
```

2. **Community lib** (DefTest etc., asset portal `?tag=testing`): suites,
   teardown, mocks for selected engine APIs, LuaCov. Extension of the
   ecosystem, not the engine — pin its version like any dependency.

Structured results for automation: `TEST`-prefixed JSON lines, run id per
run, one terminal event per suite (`/manuals/automated-testing`). Collector
parses lines independently, ignores engine noise.

## Integration tests (running collection)

Behavior needing GOs/messages/physics: dedicated test collection as bootstrap
(`[bootstrap] main_collection = /test/test.collectionc` via a
`--settings test/test.settings` overlay to bob — never commit a test
bootstrap). Pattern per test: known state → one behavior → assert →
cleanup → emit result. "Dev room" collections (blockouts + scenarios) make
mechanics reproducible without playing to them.

## Headless CI

`--variant headless` bundle, run with a process controller: exit status +
timeout + terminal event required (`/manuals/automated-testing`,
`/manuals/bob`):

```sh
java -jar bob.jar --root . --settings test/test.settings \
  --platform x86_64-linux --variant headless --archive \
  --bundle-output build/test-bundle resolve build bundle
# then: run executable, enforce timeout, grep TEST lines, require pass
```

HTML5: external browser drivers (Playwright/Puppeteer) hit the canvas;
input flows through normal `on_input`; JS↔Lua bridge via `html5.run()` +
your JS side (`/manuals/html5` custom template). Runtime inspection of a
debug engine: engine service / Automation Bridge (**extension**, not core).
Visual checks: editor preview + runtime screenshot for image diff;
prefer deterministic assertions over pixel diffs where expressible.

## Deterministic repro harness (pattern)

1. Seed + log: every RNG seeded, seeds printed as one line (`lua-engineering`).
2. Fixed step: sim in `fixed_update`; no `os.clock`/`dt` in state.
3. Input tape: timestamped input list replayed into `on_input` equivalent.
4. Snapshot: dump state at frame N; assert equal across runs.
5. Artifact: seed + tape + engine version committed with the failing case.

```
repro/case_042/  seed.txt  inputs.json  expected.json  run.sh
```

## Failure diagnosis loop

**Reproduce** → smallest tape/scene that fails every time (no flaky base).
**Isolate** → binary-search the tape, then the module set; profiler +
debugger split CPU-vs-state. **Minimize** → dev-room collection with just
the suspect GOs. **Fix** → root cause; symptom patches (swallow error,
widen tolerance) are findings, not fixes. **Regression** → minimized case
becomes a permanent test (`/manuals/automated-testing` levels). Then
re-measure if the fix touched a hot path (`performance.md`).

Engine crashes (not Lua errors): read the crash/log tail for the assert,
note engine sha (`--version`), reduce to a minimal project before filing —
90% of "engine bugs" are data or step-order.
