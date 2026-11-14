# Workflow: Debug a Godot project / feature

`references/debugging.md` detail. Reproduce → isolate → fix → re-verify.

## Steps

1. **Reproduce headless** — `godot --headless --path . --quit-after N`
   (or the failing scene); capture stdout/stderr tail — script errors,
   import errors, leak counts are the first evidence.
2. **Classify** — parse error? missing resource? runtime exception in a
   signal chain? style bug (filter/scale) vs logic bug vs perf bug.
3. **Isolate** — smallest booting scene; `--recovery-mode` if plugins/editor
   crash; `--debug-collisions`/`--debug-navigation`/
   `--debug-canvas-item-redraw` per domain; `--single-threaded-scene` to rule
   out threading (verify flag availability per build).
4. **Bisect** — VCS between known-good and broken; audit script for dep drift.
5. **Fix** — at the cause, not the symptom: no swallowing errors, no
   `await`-spaghett over races, no filter-toggles masking shimmering.
6. **Re-verify** — same reproduction command green + the ladder
   (STATIC→IMPORTED→RUNTIME); gameplay bug → AUTOTEST added/extended if a
   harness exists; VISUAL if appearance was involved.

Report: LEVEL + command + observed tail + ruled-out list. No engine on host →
hand user the exact commands; UNVERIFIED, never invented PASS.
