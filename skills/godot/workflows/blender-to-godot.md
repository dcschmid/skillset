# Workflow: Blender → Godot asset intake

Only for projects consuming Blender-authored 3D. Blender-side modeling =
`lowpoly-reference-to-blender` skill; this lane is the Godot contract
(`references/blender-integration.md`). Never assumed by the Godot skill.

## Steps

1. **Intake spec** — asset id, target scale (1 BU = 1 m), LOD policy,
   collision owner (Godot), material count budget.
2. **Delivery** — GLB (embedded textures) into `assets/models/<family>/`;
   never overwrite existing deliverables (dated suffix on collision);
   source `.blend` stored with the asset or asset repo link.
3. **Import** — drop files, `.import` committed, headless `--import` clean;
   `ImportLibrary` overrides only with measured need.
4. **Bind** — instantiate in owner scene, attach `CollisionShape3D`s,
   animations present (non-empty list), materials resolved.
5. **Gates** — IMPORTED warnings=0; RUNTIME bbox/lighting sanity; VISUAL vs
   reference art (style reference is the authority; substitute forbidden).
6. **Log** — asset table row: file, engine version, importer settings, gate.
