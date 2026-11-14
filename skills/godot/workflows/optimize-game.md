# Workflow: Performance pass (Godot, measured)

`references/performance.md` protocol. No optimization without a measurement;
no FPS promises.

## Steps

1. **Baseline** — lowest target hardware (or closest local proxy), fixed
   scene + `--fixed-fps 60 --write-movie` capture; record fps, draw calls,
   primitives, video mem, script time (Profiler + `Performance` monitors).
2. **Attribute** — hot table in `performance.md`: CPU-script / draw / VRAM /
   shader / physics / batching / load-spikes; style-specific first checks
   (pixel atlas, voxel chunk cadence, LOD/occluders, realistic renderer tier).
3. **Fix smallest** — one change per commit: cache, batch, atlas, tier-down,
   cull; each maps to a probe re-run.
4. **Re-measure** — same capture command; delta table in commit/PR notes.
5. **Lock in** — profiler regression check in CI where runnable
   (`references/testing.md`); budgets in project README.

Deliverable: before/after numbers + tool output per fix. Unmeasured → UNVERIFIED.
