# Voxel art & voxel worlds (4.7 baseline)

Two distinct asks — identify which one the project has before writing code:

1. **Voxel aesthetic** (static look): authored voxel models (MagicaVoxel,
   Blockbench, Blender+addon) exported as mesh or texture; engine treats them
   like any GLB/mesh. No runtime voxel system needed.
2. **Editable voxel worlds** (Minecraft-like): runtime chunk generation,
   editing, persistence. Engine-side systems + (optionally) a GDExtension.

## Aesthetic path (default, no plugin)

- Model in voxel tool → export GLB/FBX → standard import
  (`references/asset-pipelines.md`). Flat-shaded, palettes:
  `references/low-poly.md` guidance applies (few materials, vertex colors).
- Texture filter NEAREST + no mipmaps for blocky texel crispness.
- Collision: authored as simple convex shapes, not per-voxel; or merged
  `CollisionShape3D` boxes for static props.

## Editable worlds (engine-side building blocks)

- **Data**: `PackedByteArray`/`packed` 3D array per chunk; block id `uint8`;
  chunk 16³ or 32³ fixed; world = `Dictionary[Vector3i, Chunk]`.
- **Meshing**: greedy merge same-id runs → `SurfaceTool`/`ArrayMesh`
  (`ArrayMesh.create_from_arrays`); per-chunk one `MeshInstance3D`; material =
  one `StandardMaterial3D` atlas or vertex colors.
- **Collision**: `ConcavePolygonShape3D` built from mesh triangles, or
  column/box simplification — remesh collision ONLY when chunk edits, not
  per-block edits (budget!).
- **Streaming**: `Dictionary` cache LRU; generate on background threads
  (`WorkerThreadPool`, verify API 4.7); unload far chunks; visible-range from
  camera chunk coord.
- **Persistence**: per-chunk file `user://world/x_z.bin` (`store_var`/
  `get_var` on the packed array + edits overlay); world header file with
  seed/version. Dirty-chunk flush on leave-chunk.
- **Player edits**: sparse `Dictionary[Vector3i -> block_id]` overlay on top
  of generated base — regeneration + edits merge deterministic.

## Plugin decision (Zylann Voxel Tools etc.)

Only when world size/edit-frequency exceeds hand-rolled budget. Gate: engine
compatibility with pinned version (4.7.x), license, maintenance, GDExtension
build per platform. Evaluate via `references/godot-versions.md` routine; pin
the addon version in project README.

## Verification gates

1. STATIC: chunk code compiles; deterministic seed test.
2. AUTOTEST: generate chunk → mesh vertex count > 0, manifold-ish (no
   interior faces), collision built; save→load→byte-identical.
3. RUNTIME: walk across chunk border — no hitches (frame log), no gaps.
4. VISUAL: seams between chunks invisible; texel alignment stable.

## Anti-rules

- No per-voxel `Node`s; no `MultiMesh` for full worlds (draw-call flood) —
  merged chunk meshes are the unit.
- Greedy meshing without normals merge = lighting seams; merge only
  same-normal faces.
