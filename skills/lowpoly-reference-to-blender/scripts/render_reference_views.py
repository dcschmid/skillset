#!/usr/bin/env python
"""Orthographic multi-view render gate. Run inside Blender (MCP or background):

    blender -b asset.blend --python render_reference_views.py \
        -- --out ./out --asset myasset [--views front,side,back,top,hero]

Axis convention (project contract): +Z up, +Y = subject facing, +X = subject
right. "Front" shows the subject's face; "side" is the exact left side; "back"
shows the back — never a 3/4. Cameras are orthographic; helper cameras are
removed after render.

Renders use BLENDER_WORKBENCH (assignable on 5.3 even though the enum list
hides it) for fast deterministic comparison images.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

DEFAULT_VIEWS = ("front", "side", "back")
CHARACTER_VIEWS = ("front", "side", "back")
VEHICLE_VIEWS = ("front", "side", "back", "top")

# camera direction = vector from subject center to camera (world space)
VIEW_DIRS = {
    "front": Vector((0.0, -1.0, 0.0)),          # subject faces +Y, camera sees face
    "side":  Vector((-1.0, 0.0, 0.0)),          # exact LEFT side
    "rside": Vector((1.0, 0.0, 0.0)),           # right side if requested
    "back":  Vector((0.0, 1.0, 0.0)),
    "top":   Vector((0.0, 0.0, 1.0)),
    "hero":  Vector((-0.8, -1.0, 0.45)),        # 3/4 upper-left, optional
}


def arg(name, default=None):
    for i, a in enumerate(sys.argv):
        if a == name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def scene_bounds(objects):
    mins = [math.inf] * 3
    maxs = [-math.inf] * 3
    for obj in objects:
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            for i in range(3):
                mins[i] = min(mins[i], w[i])
                maxs[i] = max(maxs[i], w[i])
    if mins[0] == math.inf:
        return Vector((-1, -1, -1)), Vector((1, 1, 1))
    return Vector(mins), Vector(maxs)


def main():
    out_dir = arg("--out", "./out")
    asset = arg("--asset", "asset")
    views = (arg("--views") or ",".join(DEFAULT_VIEWS)).split(",")
    size = int(arg("--size", "512"))
    os.makedirs(out_dir, exist_ok=True)

    targets = [o for o in bpy.context.scene.objects
               if o.type in {"MESH", "EMPTY"} and not o.hide_render
               and o.name not in {c.name for c in
                                  bpy.data.objects if c.type == "CAMERA"}]
    if not targets:
        targets = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not targets:
        print(json.dumps({"error": "no mesh objects to render"}))
        return 1

    mins, maxs = scene_bounds(targets)
    center = (mins + maxs) / 2.0
    radius = max((maxs - mins).length / 2.0, 0.5)

    prev_engine = bpy.context.scene.render.engine
    try:
        bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
    except TypeError:
        pass  # stays on prior engine; render still valid

    results = []
    for view in views:
        if view not in VIEW_DIRS:
            results.append({"view": view, "status": "unknown_view"})
            continue
        direction = VIEW_DIRS[view]
        dist = radius * 3.5
        cam_data = bpy.data.cameras.new(f"gatecam_{view}")
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = radius * 2.4
        cam = bpy.data.objects.new(f"gatecam_{view}", cam_data)
        bpy.context.scene.collection.objects.link(cam)
        cam.location = center + direction.normalized() * dist
        # camera looks along -Z: point -Z from camera toward subject center
        cam.rotation_mode = "QUATERNION"
        cam.rotation_quaternion = (center - cam.location).to_track_quat(
            "-Z", "Y")

        name = f"{asset}_{view}"
        path = os.path.join(out_dir, f"{name}.png")
        bpy.context.scene.camera = cam
        bpy.context.scene.render.resolution_x = size
        bpy.context.scene.render.resolution_y = size
        bpy.context.scene.render.filepath = path
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(write_still=True)
        results.append({"view": view, "status": "rendered", "file": path,
                        "ortho": True,
                        "camera_dir": list(direction.normalized())})
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_data)

    bpy.context.scene.render.engine = prev_engine
    print(json.dumps({"asset": asset, "convention": "+Z up +Y facing",
                      "views": results}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
