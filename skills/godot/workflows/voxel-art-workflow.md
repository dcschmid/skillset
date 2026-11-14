# Workflow: Voxel look / voxel-world setup

Style gate says voxel. FIRST classify: aesthetic (authored voxel models) or
editable worlds (runtime chunks). Applies `references/voxel-art.md`.

## Aesthetic branch

1. Model pipeline chosen (MagicaVoxel/Blockbench/Blender+addon) — NOT a
   Blender requirement.
2. Export GLB/mesh → `assets/models/`, `.import` committed, NEAREST + no mips
   on blocky textures, simple collision authored in Godot.
3. Gates: IMPORTED clean, bbox 1 BU=1 m, VISUAL seam check.

## Editable-world branch

1. Data model: chunk size, id table, `Dictionary[Vector3i, Chunk]` world,
   seeded generation — deterministic.
2. Meshing: greedy same-id+same-normal merge → `ArrayMesh`; collision rebuild
   on chunk commit, not per block edit.
3. Streaming: LRU cache, background-thread generate, unload policy, dirty flush.
4. Persistence: per-chunk `user://` files + versioned header; save/load →
   byte-equality test (AUTOTEST).
5. Gates: STATIC seed test; AUTOTEST mesh>0 + save/load equal; RUNTIME chunk
   border walk smooth; VISUAL seams invisible.

## Plugin branch (only if hand-rolled budget exceeded)

Candidate addons gated per `references/godot-versions.md` check: engine compat,
license, maintenance; pinned in project README on adoption.
