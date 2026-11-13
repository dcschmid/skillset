#!/usr/bin/env python
"""GLB export with pre-flight checks. Run inside Blender (MCP/background):

    blender -b asset.blend --python export_glb.py -- --out ./out/myasset.glb \
        [--root myasset_root] [--blend ./out/myasset.blend]

Never overwrites an existing GLB: dated suffix on collision.
Refuses export when any target object FAILS validate_mesh checks.
5.3 verified props: export_format, export_yup, use_selection, export_apply.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import bpy

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "validate_mesh", Path(__file__).with_name("validate_mesh.py"))
_vm = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_vm)


def arg(name, default=None):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def unique(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_name(f"{path.stem}-{stamp}{path.suffix}")


def main():
    out = Path(arg("--out", "./out/asset.glb")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    root_name = arg("--root")
    save_blend = arg("--blend")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if root_name:
        root = bpy.data.objects.get(root_name)
        if root is None:
            print(json.dumps({"error": f"root '{root_name}' not found"}))
            return 1
        keep = {root.name} | {c.name for c in root.children_recursive}
        meshes = [m for m in meshes if m.name in keep]
    if not meshes:
        print(json.dumps({"error": "no mesh objects in scope"}))
        return 1

    # Gate 1: validation must pass
    fails = []
    for obj in meshes:
        issues, _ = _vm.validate_object(obj, _vm.POLY_BUDGET_DEFAULT)
        bad = [i for i in issues if i[0] == "FAIL"]
        if bad:
            fails.append({"object": obj.name,
                          "issues": [f"{c}: {m}" for _, c, m in bad]})
    if fails:
        print(json.dumps({"exported": False, "blocked_by_validation": fails},
                         indent=2))
        return 1

    # BLEND deliverable first, never destructive
    if bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    if save_blend:
        blend_path = unique(Path(save_blend).resolve())
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    for obj in bpy.context.scene.objects:
        obj.select_set(obj in meshes)
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]

    target = unique(out)
    kwargs = dict(filepath=str(target), export_format="GLB",
                  use_selection=True, export_yup=True,
                  export_apply=True, export_materials="EXPORT")
    try:
        bpy.ops.export_scene.gltf(**kwargs)
    except TypeError:
        kwargs.pop("export_materials", None)
        bpy.ops.export_scene.gltf(**kwargs)

    size = target.stat().st_size if target.exists() else 0
    print(json.dumps({"exported": True, "glb": str(target), "bytes": size,
                      "objects": [m.name for m in meshes],
                      "blend": bpy.data.filepath or None}, indent=2))
    return 0 if size > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
