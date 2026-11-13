# Modeling Workflow

General procedure for any asset. Category docs override details here.

## Axis and unit convention

- **+Z = up, +Y = forward (subject facing), +X = right.**
- 1 BU = 1 meter. Characters ~1.5–2.0 BU tall. Karts ~2.0–2.5 BU long.
- All build code and cameras follow this convention. Mixed conventions are
  the top cause of "back view shows the front" failures.

## Session start

1. `scripts/inspect_scene.py` → capture pre-existing objects. Never modify or
   delete objects not in your build scope.
2. Create a root Empty named after the asset. Parent all parts to it.
   The root is the export and pivot anchor.
3. Name everything: `<asset>_<part>` (`riffdriver_helmet`, `kart_chassis`).
   No `Cube.003` in deliverables.

## Build order

1. Blockout — largest forms at final scale and facing. Check silhouette from
   front + side immediately, not at the end.
2. Structural forms — the parts that define the category (head, chassis, roof).
3. Secondary forms — limbs, wheels, panels, trim.
4. Detail — bevels, hard edges, small props. Only after 1–3 match the reference.

Apply transformations (`object.select_all` → apply) before detail passes so
later ops work on clean data.

## Low-poly discipline

- Spend triangles on silhouette and identity features; save them on surfaces
  never seen in gameplay framing.
- A bevel that catches a highlight is worth 50 tris; a subdivision of a flat
  panel is worth 0.
- Hard edges are a design tool: shade flat where the reference shows a facet,
  smooth where it shows a curve. Set via
  `polygons[].use_smooth` + autosmooth replacement (see
  `topology-and-optimization.md` for the 5.3 API).
- No uncontrolled `subdivision_surface` on a low-poly deliverable.

## Iteration loop (every pass ends here)

1. Render the named ortho views: `scripts/render_reference_views.py`.
2. Place each render next to the matching reference view.
3. List deviations: silhouette / feature / proportion / color.
4. Fix the single largest deviation.
5. Re-render. Repeat until the view gate passes.

A pass is not "done" because it looks good in the viewport. It is done when
the rendered views match the reference within tolerance.

## Blender 5.3 API notes (verified on 5.3.0 / 02f0899d)

- `Mesh.validate()` exists; `Mesh.is_manifold` and `Mesh.use_auto_smooth` are
  gone. Manifold checks via bmesh (`bm.edges.ensure_lookup_table()`,
  count linked faces per edge) — see `validate_mesh.py`.
- `mathutils.geometry.area_tri_loop` removed; use
  `bmesh.types.BMFace.calc_area()` or numpy cross products.
- `BLENDER_WORKBENCH` is not in `engine` enum_items but assigns successfully
  and renders correctly — use it for fast test renders.
- Embedded Python is 3.13; `bpy` is not importable from system python.
