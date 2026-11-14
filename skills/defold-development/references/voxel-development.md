# Voxel Development — Defold 1.14.1 baseline

Load when the project is voxel-shaped. The first section decides *which*
voxel game you're building; the rest assumes you got past it. Engine
extension path: `/manuals/extensions/`. Lua patterns: `lua-engineering.md`.

## Suitability — read before committing

| You want | Defold verdict |
|---|---|
| Voxel **look**: static or authored voxel-style meshes (Minecraft-ish props, low-poly blocky scenes) rendered as ordinary models | Fine today. Export glTF/glb, import, done. Draco/Meshopt-compressed glTF is read **at import time only**; KTX2 textures apply to gltf/glb import (see `version-compatibility.md`). |
| Voxel **look with per-instance animation** (attach/destroy blocks rarely, pre-baked variants) | Fine: model variants + factory, or a handful of mesh components. |
| **Fully dynamic, editable voxel world** (Minecraft-class: mine/build anywhere, meshing every frame-ish, huge streaming worlds) | **Not an engine feature.** No voxel terrain, no runtime chunk mesher, no voxel collision in the engine. You build the data structures, mesher, culling, and streaming in Lua or a native extension. Achievable — budget it as systems engineering, not configuration. |

Decision rule: if the world is authored, it's an asset pipeline question
(gltf). If the world is simulated and mutable, it's an engine-programming
question; prototype one chunk (gen → mesh → collide → unload) before
authoring anything else.

## Voxel assets as meshes (the easy path)

- Author in MagicaVoxel/Blockbench/Blender → export glb → drop in `assets/`.
  Import is edit-time; runtime loads a normal `.model` (`/manuals/models/`).
- Keep voxel props on shared materials so they batch; atlas the palette
  (one texture, nearest filter for hard edges — `2d-pixel-art.md` rules
  apply to voxel textures too).
- Scale discipline: define 1 block = 1 world unit in project docs; import
  scaling surprises are the top voxel-asset bug.

## Block world data (dynamic path — all yours)

No engine type exists; the boring shape that works:

```lua
-- chunk of 16x16xH, flat array, index arithmetic — not nested tables
local function idx(x, y, z) return x + y * SZ + z * SZ * SZ end
-- plain preallocated array of small-int block ids
local block_grid = {}
```

- Block ids: small integers + a module-level registry table (id → mesh,
  material, collision kind). Static keys, `lua-engineering.md` rules.
- Chunk key = `"cx,cz,cy"` string built at chunk boundaries only, cached in
  a chunk map; per-block string keys are fatal.

## Chunks: load/unload streaming

- Chunk = GO spawned via factory from a pooled id list, or a mesh component
  per chunk on one owner GO. Pool; don't create/destroy per frame
  (architecture.md factory rule).
- Load: distance/ring queue, N chunks/rate-limited ticks. Unload:
  serialize block deltas (see budget below) then destroy. This is your
  streaming — there is no engine world-streamer.
- Async: chunk generation in Lua is synchronous CPU; budget ms/tick and
  profile (`profiler` in editor). Heavy gen/meshing belongs in a native
  extension (`/manuals/extensions/`, C/C++ via native extensions) if Lua
  can't hit frame budget — be honest about that effort estimate up front.

## Runtime mesh generation

Two engine-side routes, both real, neither voxel-aware:

1. **Mesh component** (`/manuals/meshes/`, `/ref/mesh-lua`): CPU-side
   vertex data you write per chunk-mesh rebuild. Right for
   modest vertex counts; check current API surface in the ref page before
   coding.
2. **Buffer API** (`/ref/buffer-lua`) + `render`/model swap: build
   `buffer.buffer` with your vertex declaration, hand to a mesh/model.
   Verify field-creation calls in the ref, don't paste from memory.

Algorithms you implement (documented, standard, not engine features):

- **Face culling**: emit a face only where the neighbor is air — kills ~80%
  of naive geometry. Pure array reads; Lua-fine at chunk scale.
- **Greedy meshing**: merge coplanar same-material faces into quads;
  second-biggest win. Boring nested loops; write tests for the merge rules.
- Both operate on the chunk array; output is one vertex stream per material.

## Voxel collision

Physics does **not** consume voxel grids. Compile to engine shapes:

- Static: bake per-chunk collision as convex shapes/boxes approximating the
  surface (a column of boxes per exposed column is the cheap version) into
  a `.collisionobject` (`/manuals/physics-go/` for 3D collision object
  docs — verify current doc names before citing to users).
- Editable worlds: re-bake only the touched chunk's collider; full-chunk
  rebuild is your cost unit.
- Or skip the physics engine for characters: voxel raycasts/AABB-vs-grid in
  Lua over the chunk array — deterministic, cheap, `lua-engineering.md`
  determinism notes apply.

## Procedural + large worlds

Terrain generation is `procedural-generation.md`'s job (when that reference
exists in this skill): seeded noise in Lua, deterministic per chunk
(chunk-coords → seed), data-only handoff to the mesher above. Streaming =
the chunk ring queue; "infinite" = unbounded chunk map + unload policy +
save deltas (version-tagged, architecture.md save rules).

## Budget table (honest numbers to plan against)

| Concern | Budget reality |
|---|---|
| Chunk 16×16×H(H=64) greedy-meshed | rebuild in Lua: ms-scale, tune H/queue |
| Draw calls | per-material chunk mesh; 1-3 per visible chunk |
| Memory | block grids cheap (ints); vertex buffers dominate — cap resident chunks |
| Save size | deltas over generated base, not full grids |

## Checklist

- [ ] Authored-vs-simulated decision made and written down
- [ ] One chunk prototype: gen → cull → greedy mesh → collide → unload
- [ ] Meshing output one stream per material; atlas + nearest filtering
- [ ] Collider rebake scoped to edited chunks
- [ ] Extension (C++) path priced if Lua misses frame budget — not assumed
