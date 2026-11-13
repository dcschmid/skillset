#!/usr/bin/env python3
"""Environment detection for the lowpoly-reference-to-blender skill.

Runs in SYSTEM Python (no bpy). Reports the real Blender install found on this
machine - binary, version, build hash, embedded Python version, glTF exporter
availability, and live MCP addon status if reachable.

Usage:  python3 detect_blender.py [--json]
Exit:   0 = Blender usable, 1 = Blender not usable.
"""
import json
import shutil
import subprocess
import sys

PROBE = """
import bpy, sys, json
out = {
    "blender_version": bpy.app.version_string,
    "build_hash": (bpy.app.build_hash.decode()
                   if isinstance(bpy.app.build_hash, bytes)
                   else str(bpy.app.build_hash)),
    "python_version": sys.version.split()[0],
}
try:
    import addon_utils
    out["gltf_addon"] = any(m.__name__ == "io_scene_gltf2"
                            for m in addon_utils.modules())
except Exception as e:
    out["gltf_addon_error"] = str(e)
try:
    from addon_utils import enable
    enable("io_scene_gltf2", default_set=True)
    props = {p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
    out["gltf_export_props"] = {k: (k in props) for k in
                                ("export_format", "export_yup", "use_selection")}
except Exception as e:
    out["gltf_ops_error"] = str(e)
print("PROBE_JSON::" + json.dumps(out))
"""


def run_blender_probe(blender_bin):
    """Run the in-Blender probe; return dict or None."""
    try:
        proc = subprocess.run(
            [blender_bin, "-b", "--factory-startup", "--python-expr", PROBE],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    for line in proc.stdout.splitlines():
        if line.startswith("PROBE_JSON::"):
            return json.loads(line[len("PROBE_JSON::"):]), None
    return None, (proc.stderr or proc.stdout)[-400:]


def mcp_configured():
    """Detect BlenderMCP server config files (config presence, not liveness)."""
    from pathlib import Path
    hits = []
    home = Path.home()
    candidates = [
        home / ".config" / "blender" / "blendermcp.json",
        home / ".blender-mcp.json",
        home / ".cursor" / "mcp.json",
        home / ".config" / "Claude" / "claude_desktop_config.json",
        home / ".claude" / "mcp.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
                if "blender" in text.lower():
                    hits.append(str(path))
            except OSError:
                pass
    return hits


def main():
    as_json = "--json" in sys.argv
    report = {"ok": False, "blender_bin": None, "errors": []}

    blender_bin = shutil.which("blender")
    if not blender_bin:
        report["errors"].append("no blender binary on PATH")
    else:
        report["blender_bin"] = blender_bin
        probe, err = run_blender_probe(blender_bin)
        if probe:
            report.update(probe)
            report["ok"] = bool(probe.get("blender_version"))
            report["gltf_ready"] = bool(probe.get("gltf_export_props", {})
                                        .get("export_format"))
        else:
            report["errors"].append(f"blender probe failed: {err}")

    report["mcp_config_files"] = mcp_configured()

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        for key in ("blender_bin", "blender_version", "build_hash",
                    "python_version", "gltf_ready", "mcp_config_files"):
            if key in report:
                print(f"{key}: {report[key]}")
        for e in report.get("errors", []):
            print(f"error: {e}")
        print(f"usable: {report['ok']}  (MCP liveness: check via live "
              f"get_addon_status tool, not file presence)")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
