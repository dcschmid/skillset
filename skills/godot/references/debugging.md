# Debugging (4.7 baseline)

## First moves (ordered)

1. Reproduce with headless: `godot --headless --path . --quit-after 300` —
   script errors surface in stdout; `-d` for the CLI debugger on interactive.
2. `--verbose` for full init log (drivers, extensions, shader cache).
3. Editor-run with overlays: `--debug-collisions`, `--debug-paths`,
   `--debug-navigation`, `--debug-canvas-item-redraw` (LOW-processor bugs).
4. Isolate: boot the smallest scene that fails (`godot scene.tscn`).
5. Bisect VCS; audit deps (`scripts/audit_godot_project.py`).

## Editor crash → `--recovery-mode` (disables tool scripts/plugins) — the
plugin/addon breakage triage; `--dap-port`/`--lsp-port` for external debuggers.

## Common failure patterns (verified shapes)

| Symptom | Likely cause | Probe |
|---|---|---|
| Blank screen, no errors | main scene/stretch/camera | `--print-fps`, camera current, layer masks |
| Flicker/shimmer pixel art | subpixel camera/positions | snap settings (pixel-art.md) |
| Missing-script errors | moved/renamed `.gd`, stale `.uid`-less refs | audit script paths |
| RID/ObjectDB leak warnings at exit | nodes alive on quit | benign at shutdown in 4.7.2 (observed); chase only if growing during play (`ObjectDB` leak count via `--verbose`) |
| First-frame hitch | shader compile | warm at load screen |
| Audio crackle CPU | undersized budget | `--audio-output-latency` |
| Web export black screen | renderer/platform | Compatibility vs WebGPU per version |

## Determinism bugs

`--fixed-fps 60 --write-movie out.avi` for identical replays; compare frames;
`--single-threaded-scene` to rule out threading (verify flag in target build).

## Report format

LEVEL + exact command + observed log tail + what was ruled out. Missing engine
→ exact commands for the user; never synthesize output.
