# Blender integration (OPTIONAL lane, 4.7 baseline)

Blender is NOT a Godot-skill dependency: pixel/voxel/vector projects skip this
file entirely. Load it only when the project consumes Blender-authored meshes.
Blender-side modeling guidance belongs to the
`lowpoly-reference-to-blender` skill — do not duplicate it here; this file is
the Godot-side contract only.

## Export contract (Blender → Godot)

- Convention (repo-wide): **+Z up, +Y facing, +X right, 1 BU = 1 m**;
  Blender is Z-up natively → Godot importer handles Y-up GLB; keep transforms
  applied, scale 1, origin at feet/pivot.
- GLB (embedded textures) single-file delivery; GLTF+bin+textures when a DCC
  round-trip continues; verify `io_scene_gltf2` export keys against the live
  Blender (5.3) before scripting batch export.
- Materials: Principled BSDF exports as `StandardMaterial3D`; UVs required
  for textures; physics/collision authored in Godot, not imported from Blender.

## Godot-side import

Drop GLB in `assets/models/`; `.import` committed; re-import headless
(`--headless --import`) in CI; `ImportLibrary` for library-level overrides
(LOD generation, compression) — verify keys in 4.7 docs at first use.

## Validation gates (per asset)

IMPORTED: no import warnings; RUNTIME: `GlobalPosition`/bbox sane (1 BU=1 m),
animations list non-empty, materials bound; VISUAL: scale/lighting match
reference. Dated-suffix on collision — never overwrite delivered GLBs.

## When Blender is the wrong tool

Pure 2D/pixel, pure vector UI, engine-procedural (`SurfaceTool`) props:
skip Blender, no apology.
