# Workflow: Performance Pass

Measure → change one lever → re-measure. No "feels faster". Report in
`templates/performance-report.md`.

1. **Baseline on target hardware** — release build, profiler on
   (`references/performance.md` protocol): frame time p50/p99, draw calls,
   tris, memory. Without a baseline there is no optimization, only guessing.
2. **Classify the bottleneck** — CPU (scripts/physics/load) vs GPU (draw
   calls/pixels/overdraw) vs IO/load. Levers differ completely.
3. **CPU** — Lua: allocation churn (per-frame tables/strings/hashing),
   hot loops, `pairs()` in frame paths; physics step count and query volume;
   async loading scheduling.
4. **GPU** — batching/atlas consolidation, texture formats+compression,
   shader cost (1.14.1 GLES2 opt-out matters for WebGL1 targets), overdraw
   from layered sprites, light count on 3D scenes.
5. **Memory/load** — pooled instantiation via factories, proxy-driven scene
   streaming, asset compression profiles, texture budgets per platform.
6. **One lever at a time** — apply, re-measure with the same capture, keep
   only what moved the numbers; revert the rest.
7. **Deliver** — completed report (before/after, level reached). Platform
   budgets come from the project/profile, never from engine folklore.
