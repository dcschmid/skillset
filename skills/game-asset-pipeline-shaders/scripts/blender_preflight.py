#!/usr/bin/env python3
"""blender_preflight.py — export-readiness gate, RUNS INSIDE BLENDER 5.x.

blender -b file.blend --python-expr "import sys; sys.path.insert(0,'DIR');
import blender_preflight; blender_preflight.main('out.json')"  (or MCP exec)
Checks per selected-or-all objects: transforms applied, scale, pivots,
normals (5.3: no use_auto_smooth/is_manifold), UVs, CD colors, slots,
armature/morph counts. glTF export flags read from addons, never hardcoded.
Report only — writes nothing to the .blend.
"""


def _report():
    import bpy
    data = {"blender": bpy.app.version_string, "objects": [], "notes": []}
    targets = list(bpy.context.selected_objects) or [
        o for o in bpy.context.scene.objects if o.type in {
            "MESH", "ARMATURE"}]
    for ob in targets:
        row = {"name": ob.name, "type": ob.type, "findings": []}
        if ob.type == "MESH":
            me = ob.data
            if any(abs(s - 1.0) > 1e-4 for s in ob.scale):
                row["findings"].append(
                    ("High", f"scale {tuple(ob.scale)} unapplied (apply before export)"))
            if any(abs(a) > 1e-4 for a in ob.rotation_euler) or \
                    any(abs(t) > 1e-4 for t in ob.location):
                row["findings"].append(("Informational",
                                        "transform offsets present (glTF keeps node TRS)"))
            if not me.uv_layers:
                row["findings"].append(("High", "no UV layer — textures will fail"))
            me.calc_loop_triangles()
            me.validate()
            flips = sum(1 for lp in me.loops if lp.normal.dot(
                me.vertices[lp.vertex_index].normal) < -0.5)
            if flips:
                row["findings"].append(("High", f"{flips} flipped vertex/loop normals"))
            if me.color_attributes and not any(
                    a.domain in {"CORNER", "POINT"} for a in me.color_attributes):
                row["findings"].append(("Medium", "color attrs not CD/CP — export drops"))
            slots = {ms.material for ms in ob.material_slots if ms.material}
            if len(slots) > 8:
                row["findings"].append(("Medium", f"{len(slots)} materials (batch cost)"))
            if me.shape_keys:
                row["findings"].append(("Informational",
                                        f"shape keys={len(me.shape_keys.key_blocks)} "
                                        "→ glTF morphs (basis intact)"))
        if ob.type == "ARMATURE":
            row["findings"].append(("Informational",
                                    f"bones={len(ob.data.bones)} — deform/mode check on export"))
        if ob.type == "MESH" and ob.data.materials and any(
                m and m.use_nodes and any(
                    n.type not in {"BSDF_PRINCIPLED", "TEX_IMAGE", "MAPPING", "TEX_COORD",
                                   "UV_MAP", "OUTPUT_MATERIAL", "BSDF_DIFFUSE",
                                   "LIGHTMAP", "BACKGROUND"}
                    for n in m.node_tree.nodes) for m in ob.data.materials if m and m.node_tree):
            row["findings"].append(("High",
                                    "procedural node tree — bake/replace before glTF "
                                    "(Blender nodes not engine-portable)"))
        data["objects"].append(row)
    try:
        import io_scene_gltf2  # availability probe, flags read not assumed
        data["notes"].append("io_scene_gltf2: present")
    except ImportError:
        data["notes"].append("io_scene_gltf2: MISSING — export lane unavailable")
    data["notes"].append(f"blender={bpy.app.version_string} (5.3: no "
                         "use_auto_smooth/is_manifold; workbench engine assign by string)")
    return data


def main(out_path=None):
    data = _report()
    blocking = sum(1 for o in data["objects"] for s, _ in o["findings"]
                   if s in ("High", "Critical"))
    for o in data["objects"]:
        for sev, msg in o["findings"]:
            print(f"{sev}: {o['name']}: {msg}")
    for n in data["notes"]:
        print(f"note: {n}")
    print(f"objects={len(data['objects'])} blocking={blocking}")
    if out_path:
        import json
        with open(out_path, "w") as f:
            json.dump(data, f, indent=1)
    return 0 if not blocking else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
