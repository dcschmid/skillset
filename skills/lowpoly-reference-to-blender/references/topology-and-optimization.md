# Topology and Optimization

## Polygon budget is a contract, not a suggestion

Budgets come from the project profile (polygon_budget parameter or
`profiles/<project>.md`). No universal fixed limits exist; per-type starting
points for stylized real-time assets:

| Type | Range | Priority when trimming |
|---|---|---|
| Character | 1500–6000 tris | torso/limb loops last-first |
| Face region | 300–1500 | cut last |
| Kart/vehicle | 1200–4000 | wheel segments, panel loops |
| Prop | 100–800 | interior geometry |
| Environment module | 300–2000 | hidden contact geometry |

Budget exceeded → fix is remove loops that don't affect silhouette, not
"export and optimize later".

## Controlled distribution

Silhouette edges and identity features get geometry; surfaces never seen in
gameplay camera ranges get none. A flat panel stays flat.

## Bevels

Bevels exist to catch highlights on readable edges. Rules:
- Character helmets, kart body edges, prop corners: small bevel (0.5–2% of
  part size), 1–2 segments.
- Bevels are applied and real at low poly — no bevel modifier with 6
  segments shipped inside a low-poly deliverable.

## Hard vs soft shading (Blender 5.3)

`Mesh.use_auto_smooth` is removed in 5.3. The replacement pattern:
- Per-face: `polygons[i].use_smooth = False` for facets, `True` for curves.
- Edge split where a smooth region meets a flat one is achieved by keeping
  faces flat and faces flat — flat-shaded low-poly needs no autosmooth.
- For the rare smooth-object-with-hard-edge case, use `bpy.ops.mesh.mark_...`
  equivalents via bmesh or addGeometry by-weight before export.

## Normals

- Consistent outward orientation after every modeling session:
  `bpy.ops.mesh.normals_make_consistent(inside=False)` in edit mode on all
  closed meshes; open meshes get face-normal direction checked by hand.
- Negative object scale is banned before export — apply scale.

## Common defects (validation targets)

- Duplicated vertices at seams that shading won't hide — merge by distance.
- Degenerate faces (zero area) — delete.
- N-gons on exported low-poly: fine for flat panels in Defold, split to
  tris/quads only if shading breaks.
- Unapplied transforms — apply location/rotation/scale on the export root
  unless the hierarchy intentionally carries transforms (animated pivots).

## Mesh data hygiene

- One mesh per logical object; no loose data blocks in the delivered file.
- Names stable and meaningful — the export validator checks them.
