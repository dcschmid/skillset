# Performance Report — <project> — <date>

Engine version (sha): ______ · Platform/hardware: ______ · Build: debug|release
Measurement method: on-device profiler / on_screen_profiler / frame capture
(all numbers below are measurements or marked UNMEASURED).

## Frame budget

| Metric | Target | Measured | Where measured | Level |
|---|---:|---:|---|---|
| Frame time p50 (ms) | | | | RUNTIME |
| Frame time p99 (ms) | | | | RUNTIME |
| Draw calls | | | | RUNTIME |
| Triangles | | | | RUNTIME |
| Texture memory (MB) | | | | RUNTIME |
| App memory (MB) | | | | RUNTIME |

## Hotspots (from profiler, ranked)

| # | System/script | Cost | Fix lever | Status |
|---|---|---|---|---|
| 1 | | | | open |

## Levers applied

- [ ] batching/atlas consolidation (draw calls)
- [ ] Lua allocation: scratch tables, no per-frame hash/string churn
- [ ] physics: fixed step, group filtering, fewer queries
- [ ] asset: compression profiles, mipmaps, resolution scale
- [ ] load: async/proxy preload, pooled instantiation

## Before/after

| Metric | Before | After | Evidence |
|---|---:|---:|---|
| | | | |

## Verdict

Build: BUILT/RUNTIME/VISUAL level reached: ______. Remaining risk: ______.
Unmeasured claims must stay UNMEASURED.
