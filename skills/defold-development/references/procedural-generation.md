# Procedural Generation — Defold 1.14.1 baseline

Load when worlds/levels/shapes are generated at runtime or baked offline.
Genre-agnostic: dungeons, terrain, tracks, puzzle grids — same discipline.
Lua facts per `lua-engineering.md`; engine touchpoints cited inline.

## Seeded, reproducible RNG

`math.random` is global-state — hostile to saves and replays. Wrap it:

```lua
-- LCG-in-doubles: works on Lua 5.1 and 5.4 alike, deterministic.
local M = {}
local A, C, MOD = 6364136223846793005, 1442695040888963407, 2^64
function M.new(seed)
    assert(seed and seed ~= 0, "rng seed required")
    return setmetatable({ s = seed % MOD }, { __index = M })
end
function M:next()                      -- float [0,1)
    self.s = (self.s * A + C) % MOD    -- 5.1: emulate with mulmod-style doubles or ship C ext
    return self.s / MOD
end
function M:int(lo, hi) return lo + math.floor(self:next() * (hi - lo + 1)) end
return M
```

- Float precision caps useful range on 5.1 doubles; if the project runs
  5.4 (`game.project` `[script]`, see version-compatibility) integer ops
  are available. Read the project, don't guess the mode.
- Log the seed with the save; derive per-system children (`rng:derive
  ("caves")` pattern) so one system's edits don't cascade into another's
  stream. Never mix global `math.random` calls into world state.

## Noise in Lua

Value/simplex noise = pure functions over the seeded rng: hash integer
lattice, smoothstep-blend the corners. Keep it shippable:

- Integer lattice in, double interpolation out; same input → same float
  (fixed order, no `pairs()` dependence — `lua-engineering.md` determinism).
- Octave weights are module constants; noise per frame is a budget item —
  cache per-cell results in a bounded table with explicit eviction, not an
  ever-growing one.
- Boring choice: vendor one small pure-Lua module, no globals, seedable,
  testable headless.

## Shapes: grids & cellular automata

- Caves: 4-5 CA on a bounded grid; layouts: BSP split then connect. Both
  are pure Lua over fixed-size arrays — zero engine state.
- Emit **data first** (tile/prop tables), render second (tilemap/GO batch).
  Generation must run without the engine to stay unit-testable.
- Iteration order: ordered key lists, never `pairs()` for gameplay-relevant
  sequences — order is not stable across runs.

## Baking vs runtime generation

Prefer **baked** when the world is static per seed:

| Route | When | Touchpoint |
|---|---|---|
| Bake offline/editor-script | seed known at build/first boot | emits `.collection`/data; zero runtime gen cost; editor scripts: /manuals/editor-scripts/ |
| Boot gen, time-sliced | seed chosen at play | spread across frames; per-chunk budget |
| Streaming gen | infinite worlds | sliced in `update`; mind frame window |

Bake = cost paid once, inspectable output. Runtime gen = seed honesty,
paid on every platform including the slow ones.

## Chunk streaming & async

- Chunk = collection behind a **collection proxy** (async load/unload
  boundary, /manuals/collection-proxy/) or a **factory** pool for prop
  spam (`/manuals/factory/`; create/destroy per frame is banned).
- 1.14.1: resource loader scheduling moved to the job system (release
  notes) — async loads are cheaper, but policy is still yours: load radius
  > unload radius + hysteresis or borders thrash.
- Runtime-authored mesh output: `.buffer` resource + buffer/mesh component
  APIs (/manuals/buffer/, /manuals/mesh/) — verify exact 1.14.1 surface in
  /ref/buffer before writing (UNVERIFIED here). Model components consume
  glTF; they are not buildable from Lua — bake glTF or use buffers.

## Save / reproducibility contract

- Save = `{version, seed, rng_state, player_state, edited_cells}` — **not**
  the world. Regenerate from seed, overlay edits.
- Version tag + additive migration ladder (architecture.md convention);
  parse defensively (`pcall`, fallback + log); no `load()` on untrusted
  strings; disk format via json (`/ref/json`).
- Regression test: same seed + same gen-code version ⇒ identical cell dump;
  document float tolerance across save/load for edited values.

## Performance validation loop (run it, don't intend it)

1. Worst-case seed on the weakest target.
2. Measure: gen ms/chunk, gen ms/frame while streaming, added draw calls,
   Lua memory (/manuals/profiling/, /manuals/optimization-speed/).
3. Gate: per-frame gen budget (≤ 4 ms desktop / ≤ 8 ms mobile — **starting
   points to measure, not engine constants**).
4. Over budget → smaller chunks, deeper bake, fewer live chunks. Never
   close the loop by skipping the check.

## Honest limits

No built-in noise/terrain/voxel/mesh-generation systems; Lua is a single
VM — long gen loops hitch unless sliced; compute programs (/manuals/
compute/) exist but platform availability is not uniform, don't design
world gen around them without target verification. All of it is project
code or extensions; budget accordingly.
