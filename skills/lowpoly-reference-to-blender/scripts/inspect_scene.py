#!/usr/bin/env python
"""Scene state snapshot. Run inside Blender (MCP execute-code or
`blender -b file.blend --python inspect_scene.py [-- --json]`).

Non-destructive: reads only. Prints a JSON snapshot of objects, transforms,
mesh totals and materials - the "before" picture for any build or the report's
scene section.
"""
import json
import sys

import bpy


def snapshot():
    data = {
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "file": bpy.data.filepath or None,
        "objects": [],
        "materials": sorted(m.name for m in bpy.data.materials),
    }
    for obj in bpy.context.scene.objects:
        entry = {
            "name": obj.name,
            "type": obj.type,
            "location": list(round(v, 4) for v in obj.location),
            "rotation": [round(a, 4) for a in obj.rotation_euler],
            "scale": list(round(v, 4) for v in obj.scale),
            "parent": obj.parent.name if obj.parent else None,
            "children": [c.name for c in obj.children],
            "visible": not obj.hide_get(),
        }
        if obj.type == "MESH" and obj.data:
            me = obj.data
            entry["mesh"] = me.name
            entry["vertices"] = len(me.vertices)
            entry["polygons"] = len(me.polygons)
            entry["triangles"] = sum(len(p.vertices) - 2 for p in me.polygons)
            entry["uv_layers"] = [u.name for u in me.uv_layers]
            entry["materials"] = [m.name if m else None
                                  for m in me.materials]
            entry["unapplied_transform"] = (
                any(abs(v - 1.0) > 1e-5 for v in obj.scale)
                or any(abs(v) > 1e-5 for v in obj.rotation_euler)
                or any(abs(v) > 1e-5 for v in obj.location)
            )
        data["objects"].append(entry)
    return data


def main():
    as_json = "--json" in sys.argv or "--json" in sys.argv[1:]
    data = snapshot()
    print(json.dumps(data, indent=2 if as_json else None,
                     default=str))


if __name__ == "__main__":
    main()
