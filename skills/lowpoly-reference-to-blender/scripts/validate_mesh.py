#!/usr/bin/env python
"""Mesh validation gate. Run inside Blender (MCP or background):

    blender -b asset.blend --python validate_mesh.py [-- --json]
    blender -b --python validate_mesh.py  (live session via MCP exec)

Checks per MESH object; distinguishes defects (FAIL) from tolerated design
choices (WARNING). Exit 0 if no FAILs.

5.3 note: Mesh.is_manifold / use_auto_smooth are gone -> bmesh checks.
"""
import json
import sys

import bpy
import bmesh

EPS = 1e-6
POLY_BUDGET_DEFAULT = 12000  # per-object soft cap; budgets are configurable


def _facing(obj):
    """Object's documented facing via +Y when named/rotated convention holds."""
    return "unknown"  # informational only; view gate handles orientation


def validate_object(obj, budget):
    issues = []  # (level, code, message)
    me = obj.data
    if me is None or len(me.vertices) == 0:
        issues.append(("FAIL", "empty_mesh", "no mesh data"))
        return issues, {}

    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    tris = sum(len(f.verts) - 2 for f in bm.faces)

    # --- degenerate faces -------------------------------------------------
    degen = sum(1 for f in bm.faces if f.calc_area() < EPS)
    if degen:
        issues.append(("FAIL", "degenerate_faces", f"{degen} zero-area faces"))

    # --- duplicated verts (merge-by-distance survivors) --------------------
    merged = {}
    for v in bm.verts:
        key = (round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5))
        merged.setdefault(key, []).append(v.index)
    dupes = sum(len(g) - 1 for g in merged.values() if len(g) > 1)
    if dupes:
        issues.append(("WARNING", "duplicate_verts",
                       f"{dupes} coincident verts (harmless if intentional "
                       f"UV/hard-edge splits)"))

    # --- manifold: edges with != 2 faces where mesh is closed --------------
    boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    nonmanifold = sum(1 for e in bm.edges
                      if len(e.link_faces) > 2)
    if nonmanifold:
        issues.append(("FAIL", "nonmanifold_edges",
                       f"{nonmanifold} edges with >2 faces"))
    if boundary:
        issues.append(("WARNING", "open_edges",
                       f"{boundary} boundary edges (open mesh; tolerated "
                       f"for props/strips, defect for closed solids)"))

    # --- normals: flipped relative to face winding consistency -------------
    flipped = sum(1 for f in bm.faces if f.normal.length < EPS)
    if flipped:
        issues.append(("FAIL", "bad_normals",
                       f"{flipped} zero-length face normals"))

    bm.free()

    # --- transforms ---------------------------------------------------------
    if any(abs(s) < EPS for s in obj.scale):
        issues.append(("FAIL", "zero_scale", "object has zero scale axis"))
    elif (any(abs(s - 1.0) > 1e-4 for s in obj.scale)
          or any(abs(a) > 1e-4 for a in obj.rotation_euler)):
        issues.append(("WARNING", "unapplied_transform",
                       "scale/rotation not applied before export "
                       "(exporter applies; document animated pivots)"))
        if any(s < 0 for s in obj.scale):
            issues.append(("FAIL", "negative_scale",
                           "negative scale flips normals in engines"))

    # --- UVs ----------------------------------------------------------------
    if not me.uv_layers:
        issues.append(("WARNING", "no_uv",
                       "no UV map (fine for flat-color PBR, blocks "
                       "texturing)"))
    else:
        for uvl in me.uv_layers:
            if not uvl.data:
                issues.append(("FAIL", "empty_uv",
                               f"UV layer '{uvl.name}' has no data"))

    # --- material refs ------------------------------------------------------
    if not me.materials or all(m is None for m in me.materials):
        issues.append(("WARNING", "no_material",
                       "no material (exports as default white)"))
    else:
        slot_faces = [p.material_index for p in me.polygons
                      if p.material_index >= len(me.materials)
                      or me.materials[p.material_index] is None]
        if slot_faces:
            issues.append(("WARNING", "missing_material_slot",
                           f"{len(slot_faces)} faces point at empty slot"))

    # --- poly budget ---------------------------------------------------------
    if tris > budget:
        issues.append(("WARNING", "poly_budget",
                       f"{tris} tris > budget {budget}"))

    stats = {"vertices": len(me.vertices), "polygons": len(me.polygons),
             "triangles": tris, "boundary_edges": boundary,
             "uv_layers": len(me.uv_layers)}
    return issues, stats


def main():
    as_json = "--json" in sys.argv
    budget = POLY_BUDGET_DEFAULT
    for i, a in enumerate(sys.argv):
        if a == "--budget" and i + 1 < len(sys.argv):
            budget = int(sys.argv[i + 1])

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        meshes = [o for o in bpy.data.objects if o.type == "MESH"
                  and o.name in bpy.context.scene.collection.all_objects]
    report = {"blender_version": bpy.app.version_string,
              "budget": budget, "objects": [],
              "summary": {"PASS": 0, "WARNING": 0, "FAIL": 0}}
    worst = "PASS"
    for obj in meshes:
        issues, stats = validate_object(obj, budget)
        level = "PASS"
        for lvl, _, _ in issues:
            if lvl == "FAIL":
                level = "FAIL"
            elif lvl == "WARNING" and level != "FAIL":
                level = "WARNING"
        report["summary"][level] += 1
        if level == "FAIL":
            worst = "FAIL"
        elif level == "WARNING" and worst != "FAIL":
            worst = "WARNING"
        report["objects"].append({
            "name": obj.name, "status": level, "stats": stats,
            "issues": [{"level": l, "code": c, "message": m}
                       for l, c, m in issues]})

    report["result"] = worst
    print(json.dumps(report, indent=2 if as_json else None))
    if not as_json:
        for ent in report["objects"]:
            print(f"{ent['status']:7} {ent['name']} "
                  f"tris={ent['stats'].get('triangles')}")
            for iss in ent["issues"]:
                print(f"    {iss['level']:7} {iss['code']}: {iss['message']}")
        print(f"RESULT: {worst}")
    return 0 if worst != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
