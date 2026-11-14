# Performance & profiling (4.7 baseline)

Measure → fix → re-measure. No folklore budgets; every number below is a
starting question, not a promise.

## Protocol (report per templates in testing.md)

1. Editor: Project > Tools > Profiler (CPU functions, renderer frames, memory).
2. Runtime overlays: `Engine.get_frames_per_second()`, `Performance.get_monitor`
   (draw calls, primitives, node counts, video mem).
3. `--print-fps`, `--gpu-profile`, `--extra-gpu-memory-tracking` (debug builds).
4. Fixed-fps capture: `--fixed-fps 60 --write-movie out.avi` for reproducible
   frame timing.

## Hot areas → first probe → common real fix

| Area | Probe | Fix shape |
|---|---|---|
| CPU script | Profiler function table | cache refs, `set_process(false)`, data over nodes |
| Draw calls | `Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME` | atlases, `MultiMeshInstance`, merge statics |
| Texture VRAM | memory monitor / `--extra-gpu-memory-tracking` | VRAM compression, mipmaps, size tiers |
| Shader | `--gpu-profile` | fewer variants/toggles, simpler fills |
| Physics | profiler physics row | fewer bodies, layers/masks tight, fixed steps |
| 2D batching | canvas items + texture splits | texture atlas, material sharing |
| Loads | frame spikes on scene swap | threaded `ResourceLoader`, pre-warm |

## Style-specific first checks

- Pixel: integer scale + snap on (shimmer ≠ perf but both are style bugs);
  atlas everything; no mips.
- Voxel: chunk mesh size vs frustum; collision rebuild cadence
  (`voxel-art.md`).
- 3D: LOD coverage, light counts per cell, occluders on big levels.
- Realistic: renderer tier down before art down (`realistic-rendering.md`).

## Platform floors

Define one lowest-spec machine (iGPU/phone) and profile THERE last.
Web: shared-thread vs worker-thread budget differs (verify per version).

## Deliverable

Performance notes in project README: platform, scene, before/after numbers,
tool used. Unmeasured claims → UNVERIFIED.
