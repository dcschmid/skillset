#!/usr/bin/env python
"""End-to-end pipeline test: build test geometry -> validate -> ortho renders
-> GLB export -> GLB reimport. Runs fully inside Blender background mode.

    blender -b --python tests/test_e2e_pipeline.py

Exit 0 = pipeline intact (technical gates only; visual reference fidelity is
a separate human/visual step and is NOT asserted here).
Writes artifacts under tests/.artifacts/ — disposable.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import bpy
import bmesh

HERE = Path(__file__).resolve().parent
ART = HERE / ".artifacts"
SCRIPTS = HERE.parent / "scripts"


def build_test_asset():
    """Deliberate test geometry: named, parented, transformed — exercises
    the validator (applied root, animated-pivot child, one flat facet)."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    root = bpy.data.objects.new("testdriver_root", None)  # EMPTY pivot
    bpy.context.scene.collection.objects.link(root)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new("testdriver_body")
    bm.to_mesh(me)
    bm.free()
    body = bpy.data.objects.new("testdriver_body", me)
    bpy.context.scene.collection.objects.link(body)
    body.parent = root

    head = bpy.data.objects.new("testdriver_head",
                                bpy.data.meshes.new("testdriver_head"))
    bmesh.new().free()
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.35)
    bm.to_mesh(head.data)
    bm.free()
    bpy.context.scene.collection.objects.link(head)
    head.parent = body
    head.location = (0, 0.1, 0.8)  # intentional: pivot offset (animated pivot)

    wheel = bpy.data.objects.new("testdriver_wheel",
                                 bpy.data.meshes.new("testdriver_wheel"))
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.2)
    bm.to_mesh(wheel.data)
    bm.free()
    bpy.context.scene.collection.objects.link(wheel)
    wheel.parent = root
    wheel.location = (0.5, -0.4, -0.4)

    mat = bpy.data.materials.new("testdriver_body_blue")
    mat.use_nodes = True
    for m in (body.data.materials, head.data.materials):
        m.append(mat)
    return ["testdriver_root", "testdriver_body", "testdriver_head",
            "testdriver_wheel"]


def run_blender_script(script, *args):
    cmd = [os.environ.get("BLENDER_BIN", "blender"), "-b",
           "--python", str(script), "--", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return proc


def main():
    ART.mkdir(exist_ok=True)
    failures, checks = [], []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            failures.append(f"{name}: {detail}")

    names = build_test_asset()
    check("build.test_asset", len(bpy.data.objects) == 4,
          f"{len(bpy.data.objects)} objects")

    sys.path.insert(0, str(SCRIPTS))
    import validate_mesh as vm
    report = {"objects": []}
    for n in names:
        obj = bpy.data.objects[n]
        if obj.type != "MESH":
            continue
        issues, stats = vm.validate_object(obj, vm.POLY_BUDGET_DEFAULT)
        fails = [i for i in issues if i[0] == "FAIL"]
        report["objects"].append({"name": n, "fails": len(fails),
                                  "warns": len(issues) - len(fails)})
    check("validate.no_fails",
          all(o["fails"] == 0 for o in report["objects"]),
          json.dumps(report["objects"]))

    # ortho render gate (child process = real background-mode render path)
    blend = ART / "e2e.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    proc = run_blender_script(
        SCRIPTS / "render_reference_views.py",
        "--", "--out", str(ART), "--asset", "e2e",
        "--views", "front,side,back", "--size", "128")
    renders_ok = all((ART / f"e2e_{v}.png").exists()
                     for v in ("front", "side", "back"))
    if renders_ok:  # real gate: views must differ (catches camera bugs)
        import hashlib
        digests = {(ART / f"e2e_{v}.png").read_bytes() and
                   hashlib.md5((ART / f"e2e_{v}.png").read_bytes())
                   .hexdigest() for v in ("front", "side", "back")}
        renders_ok = len(digests) == 3
    check("render.ortho_views", renders_ok, proc.stderr[-200:])

    # GLB export via the real script, inside this session's data
    proc = subprocess.run(
        [os.environ.get("BLENDER_BIN", "blender"), "-b", str(blend),
         "--python", str(SCRIPTS / "export_glb.py"), "--",
         "--out", str(ART / "e2e.glb"), "--root", "testdriver_root"],
        capture_output=True, text=True, timeout=300)
    glb = ART / "e2e.glb"
    check("export.glb", glb.exists() and glb.stat().st_size > 200,
          proc.stdout[-300:] or proc.stderr[-200:])

    # GLB reimport verification (verify_export runs empty -> absolute check)
    proc = subprocess.run(
        [os.environ.get("BLENDER_BIN", "blender"), "-b",
         "--python", str(SCRIPTS / "verify_export.py"), "--",
         "--glb", str(glb)],
        capture_output=True, text=True, timeout=300)
    try:
        verdict = json.loads(proc.stdout[
            proc.stdout.index("{"):proc.stdout.rindex("}") + 1])
    except ValueError:
        verdict = {"result": "PARSE_FAIL", "raw": proc.stdout[-300:]}
    check("verify.reimport_pass", verdict.get("result") == "PASS",
          json.dumps(verdict)[:300])
    tris = verdict.get("reimported", {}).get("triangles", 0)
    check("verify.geometry_survives", tris > 0, f"tris={tris}")

    out = {"pipeline": "lowpoly-reference-to-blender/e2e",
           "blender": bpy.app.version_string,
           "checks": checks,
           "result": "PASS" if not failures else "FAIL",
           "note": "technical gates only; visual reference fidelity "
                   "requires render-vs-reference human/visual review"}
    (ART / "e2e-report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
