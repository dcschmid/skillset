# Game Engine Export

## Targets

Primary: **Defold**. The pipeline stays engine-neutral: any engine consuming
glTF 2.0 / GLB can take the output; engine-specific notes are additive.

## Units and orientation

- Blender: +Z up, meters. glTF: +Y up, meters — handled by the exporter's
  `export_yup=True` (verified present on 5.3.0's `io_scene_gltf2`).
- After export, engines see Y-up. Document in the delivery note which axis is
  "forward" for animated parts (wheels, steering wheels) so engine code
  rotates on the right axis.

## Defold specifics

- Defold imports GLB via its model import pipeline: meshes, materials
  (base color / metallic-roughness), transforms, hierarchy survive.
- Not guaranteed through Defold's import: complex node graphs, custom blend
  modes, drivers, constraints, lights/cameras (prefer excluding them or
  stripping per project). Keep export to geometry + PBR materials + textures.
- Skeletal animation and morph targets are later workflows for this project
  family (Riff Racers: "individuelle Animationen als späterer Workflow") —
  do not ship half-bound rigs.
- For per-part control in engine (wheels!), export GLB with `use_selection`
  hierarchies preserved; verify pivots survive reimport.

## LOD

Optional, only when the project requests:
- LOD0: deliverable as scored.
- LOD1: ~50% tris, same silhouette primitives, no bevels.
- LOD2: ~25%, billboard-grade blockout.
Only emit if the target engine consumes them (Defold: manual swap or
component-level; document the choice).

## Export checklist (mechanical part in export_glb.py)

1. Selection = asset objects only (no helper cameras/lights unless requested).
2. Transforms applied except intentional pivot parents.
3. Names stable, ASCII, no trailing duplicates (`object.name` cleaned).
4. Materials use exported Principled inputs; textures packed.
5. `export_format='GLB'`, `export_yup=True`, `export_apply=True` where safe.
6. BLEND saved first — the .blend is always a deliverable, not an afterthought.

## Post-export verification

`verify_export.py` reimports the GLB into a factory scene and checks object
count, mesh totals, material presence, transform delta. Report goes with the
delivery.

## File naming

`<asset>.blend`, `<asset>.glb` — no version suffixes in filenames; version
history lives in git. Outputs land in the project's `output_dir`; never
overwrite a previous delivery without moving it to a dated subfolder.
