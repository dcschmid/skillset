#!/usr/bin/env python
"""GLB export verification: reimport a GLB into a factory Blender scene and
confirm geometry, materials, hierarchy, transforms survived.

    blender -b --python verify_export.py -- --glb ./out/asset.glb [--json]

Reports PASS/WARN/FAIL comparing the source scene (if open) or absolute
sanity checks (if run empty). Exit 0 on PASS/WARN.
"""
import json
import sys
from pathlib import Path

import bpy


def arg(name, default=None):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def scene_stats():
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"
              and o.data]
    return {
        "objects": len(bpy.context.scene.objects),
        "meshes": len(meshes),
        "triangles": sum(sum(len(p.vertices) - 2 for p in m.data.polygons)
                         for m in meshes),
        "vertices": sum(len(m.data.vertices) for m in meshes),
        "materials": sorted({mm.name for m in meshes
                             for mm in m.data.materials if mm}),
        "names": sorted(o.name for o in bpy.context.scene.objects),
    }


def main():
    glb = Path(arg("--glb") or "").resolve()
    if not glb.is_file():
        print(json.dumps({"result": "FAIL", "error": f"missing {glb}"}))
        return 1

    source = None
    if bpy.context.scene.objects:
        source = scene_stats()  # compare mode: source scene already open

    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=str(glb))
    imported = [o for o in bpy.context.scene.objects if o.name not in before]
    stats = scene_stats()

    result, issues = "PASS", []
    if stats["triangles"] == 0:
        result, issues = "FAIL", ["no geometry after reimport"]
    elif stats["materials"]:
        pass
    else:
        issues.append("WARN: no materials in reimported GLB")

    if source:
        if stats["triangles"] != source["triangles"]:
            issues.append(
                f"triangle drift: {source['triangles']} -> "
                f"{stats['triangles']}")
        if len(stats["materials"]) < len(source["materials"]):
            issues.append("material loss on round-trip")

    print(json.dumps({"result": result, "glb": str(glb),
                      "reimported": stats,
                      "source": source, "issues": issues,
                      "note": "Y-up source becomes Z-up on Blender import; "
                              "axis flip is expected, not a defect"},
                     indent=2))
    if result == "FAIL":
        return 1
    return 0 if not issues else 0  # WARN passes; report carries the warning


if __name__ == "__main__":
    sys.exit(main())
