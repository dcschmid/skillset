# Blender integration (5.3.0 on this machine, hash 02f0899d)

Runs: `detect` style checks on system Python; anything importing `bpy` runs
inside Blender (`blender -b --python script.py` or MCP exec). Bundled Python
3.13; system Python has no `bpy`. Removed in 5.3: `Mesh.is_manifold`,
`Mesh.use_auto_smooth`, `mathutils.geometry.area_tri_loop` — do not emit.
Convention: **+Z up, +Y facing, 1 BU = 1 m**. Lookup nodes by `type`, never
name (localized). `diffuse_color` is viewport-only; colors go on shader
inputs.

## Export preflight (`scripts/blender_preflight.py`, run in Blender)

scale applied · transforms applied · pivot correct · normals (no flip/no
auto_smooth call) · tangents (recompute or bake normal map) · UVs (no
overlaps where atlas, no zero-islands, seam count reported) · vertex colors
real CD attribute · material slots resolve · single skeleton, deform counts
· animations on actions · morphs as shape keys with basis intact.

## Procedural → portable

Blender node trees are NOT glTF/engine-compatible by default. Export
candidates: baked textures (diffy/normal/rough via bake ops), simplified
principled inputs, or engine-side rebuild. Baking = new deliverables, dated
suffix on collision, never overwrite source. `io_scene_gltf2` flags verified
present: `export_format/export_yup/use_selection/export_apply` — read enums,
don't hardcode; `BLENDER_WORKBENCH` assign by string in try/except.

## Batch export + gate

batch per collection → `gltf_validate.py` → engine headless import.
Blender-side quality: manifold check replacement (5.3: bmesh edge-count
walk), UV area distortion report, material count vs profile.
Handoff to design work (modeling, rigging, look-dev) →
`lowpoly-reference-to-blender`; this file only covers the technical
export/validate boundary.
