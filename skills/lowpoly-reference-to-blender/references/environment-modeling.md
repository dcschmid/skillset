# Environment and Prop Modeling

Buildings, track props, vegetation, rocks, machines, architecture, decor,
modular track pieces.

## Scale discipline

All environment pieces share the project unit plan (1 BU = 1 m) and a
documented grid. Track pieces join only at defined socket dimensions:

- Module widths snap to the project grid (e.g. 2 / 4 / 8 BU).
- Ground contact is flat: no floating props; the Z = 0 plane is the contact
  plane unless the project says otherwise.
- A reference human height (1.7 BU) is the sanity check: a door taller than
  the character is wrong, a rock knee-high to the character is knee-high.

## Modular pieces

- Build one master, duplicate for variants; keep names
  `<module>_<variant>_<n>`.
- Seams between modules: intentional join lines (bevel, material break),
  never accidental mismatched vertices.
- Pivots at grid-aligned corners or centers — the same rule for every module
  so engine snapping works.

## Vegetation and rocks

- Rocks: 20–80 tris, flat-shaded facets, designed silhouette, not
  randomized-sphere noise. Same lighting direction as the project.
- Trees: trunk + 1–3 foliage volumes, consistent stylization level with the
  project's props.
- Instancing-friendly: one object per unique asset; variants are separate
  files/instances in the engine, not unique meshes in one scene.

## Material reuse

Environment assets share a small material set (≤ 8 per module set). New
material = new atlas slot = draw-call cost. Document any new material.

## Performance notes (iGPU / weak systems)

- Static geometry merged or instanced where engine supports it.
- No per-prop textures where an atlas covers the set.
- Overdraw: avoid stacked transparent planes (foliage) beyond project limits.

## Open meshes are legal here

Walls without thickness, single-sided foliage planes, road strips — intentional
open geometry on environment pieces is a design choice, not a defect.
`validate_mesh.py` reports these as WARNING with the object name; they pass
when the report lists them as intentional.

## View gate

Environments verify against the reference from the gameplay camera plus one
ortho check (usually top or front) confirming layout, not full turntable.
