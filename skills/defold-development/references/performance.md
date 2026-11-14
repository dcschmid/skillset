# Performance — Defold 1.14.1 baseline

Load for profiling passes, budgets, or "it stutters". Facts:
`/manuals/profiling`, `/manuals/optimization*`, `/ref/profiler/`. Measure on
target hardware; every number below is a template, not a constant.

## Protocol (order matters)

1. **Capture baseline** frame time + draw calls on the worst scene, target
   device (not the dev box).
2. **Locate**: visual profiler (`profiler.enable_ui(true)` — verified
   `/manuals/profiling` / `/ref/profiler`; modes via `profiler.set_ui_mode`,
   views via `profiler.set_ui_view_mode`, `profiler.view_recorded_frame`).
   Remotery web frame profiler: `Debug ▸ Open Web Profiler` (desktop/mobile;
   **not** HTML5). Scope names → CPU owner.
3. **Counters**: Global Properties view (draw calls, component counts) +
   `LuaMem` (Lua VM) vs `Memory` (engine) in KB.
4. **Fix one lever**, re-measure same scene. Keep the report.
5. HTML5: browser Performance panel — enable
   `profiler.performance_timeline_enabled` in game.project; Remotery
   unavailable there. macOS Metal debug builds: GPU traces via engine service
   `/profiler/gputrace` → Xcode (`METAL_CAPTURE_ENABLED=1` at launch).

Profiler presence is decided at build time by the **App Manifest Profiler**
setting (default Debug Only / None / Always); `game.project [profiler]`
controls runtime only — `Track CPU` toggles CPU sampling separately.
Mobile on-device: the dev app surface shows the same runtime profiler.
Pure-Lua profilers (ProFi): counting profiles ok, timing profiles inflate —
hook overhead is real.

## CPU budget

Split frame: engine scopes vs your scripts vs Sound thread (Remotery
timelines). Lua rules from `lua-engineering.md` apply: no per-frame
`require`/hash/string keys, scratch vectors reused, dispatch tables not
chains. Physics cadence = `fixed_update` (`physics-ai.md`); a hitch at scene
start is an architecture bug (`architecture.md`), fix with async loads:
`factory.load` / collection proxy async load / `resource`-level loads per
`/ref/factory`, `/ref/collectionproxy` — verify exact names before use.
Resource load timing: `[resource] profile = 1` + resource profiler
(Capture → Show load times; Load/Preload/Read/Create columns; don't sum —
nested double-count).

## GPU budget

- **Draw calls**: shrink via atlases (one texture → batched sprites;
  `/manuals/atlas`), shared materials, static-batchable tilemaps. Watch the
  draw-call counter before/after each atlas merge. N atlases + N materials ≈
  floor of N batches — verify with the counter, not intuition.
- **Fill rate** (mobile/HTML5): overdraw from full-screen GUI/particles is
  the usual iGPU killer; cap `html5.min/max_pixel_ratio` + High-DPI
  (`html5.md`), scale particle counts by resolution tier.
- **Textures**: compressed via texture profiles (`/manuals/texture-profiles`,
  bob `--texture-compression`); mipmaps for 3D, none for pixel art
  (`2d-pixel-art.md`). Sizing table = measure per platform tier:
  record observed VRAM at the worst scene; budgets come from that, not blogs.
- **Particles/meshes**: levers = count, overdraw layers, shader cost, mesh
  vertex counts; particlefx component cost shows as its own scope — halve
  counts first, shader tricks last.

## Memory

Lua GC: preallocate tables at init, reuse, no per-frame closures in hot
loops; watch `LuaMem` slope over a minute of play — a ramp is a leak, not
garbage. Engine side: resource profiler Resources view (size + refcounts);
unload via proxies/factories destroyed, not assumed. Asset streaming:
proxies unload old scenes behind you; large audio streamed (`audio.md`);
KTX2/Draco are **import-time** wins, not runtime levers.

## Load times & size

Build report (`report.html`, editor bundle checkbox or bob
`--build-report-html`) → per-resource size ranking. Optimize biggest first:
audio, atlases, archives. HTML5 heap: `html5.heap_size` (MB) sized to fit
measured peak, not the default.

## Templates — fill with measurements, then stop guessing

```
Scene: ____   Device: ____   Build: debug|release  Engine: 1.14.1
Frame ms p50/p95: CPU ____/____  GPU ____/____  Draw calls ____
LuaMem ____ KB  Memory ____ KB  Textures ____ MB
Action: ____   Result (same scene re-measure): ____
```

Record into `templates/performance-report.md` — every perf claim in a commit
or PR points at a filled row. "Feels faster" is not a result.
