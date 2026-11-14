#!/usr/bin/env python3
"""audit_defold_project.py — READ-ONLY audit of a Defold project.

Reports: layout, game.project sections worth attention, collections/scripts/
assets counts, render pipeline, physics config, extension usage, pixel-art
and 1.14.x-sensitive settings. Never writes, never "fixes".
Usage: python3 scripts/audit_defold_project.py <project_dir> [--json]
Exit 0 = audit produced; findings are informational, not pass/fail.
"""
import json
import re
import sys
from pathlib import Path

IGNORE = {".git", "build", "logs", "__pycache__", ".internal", ".cache", ".delta"}

def scan(root):
    counts, roots = {}, []
    for p in root.rglob("*"):
        if any(part in IGNORE for part in p.parts) or not p.is_file():
            continue
        ext = p.suffix.lower()
        counts[ext] = counts.get(ext, 0) + 1
        if ext in {".lua", ".script", ".gui_script"} and p.parent.name in {"modules", "shared", "main"}:
            roots.append(str(p.relative_to(root)))
    return counts, sorted(roots)

def ini(text):
    """Tiny INI reader good enough for game.project inspection."""
    out, sect = {}, None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            sect = line[1:-1]; out[sect] = {}
        elif "=" in line and sect:
            k, v = line.split("=", 1)
            out[sect][k.strip()] = v.strip()
    return out

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    root = Path(sys.argv[1]).resolve()
    as_json = "--json" in sys.argv
    gp = root / "game.project"
    if not gp.is_file():
        print(f"FAIL not a Defold project (no game.project): {root}"); return 1

    cfg = ini(gp.read_text(encoding="utf-8", errors="replace"))
    counts, module_roots = scan(root)
    report = {"project": str(root), "files_by_type": counts, "module_roots": module_roots}

    boot = cfg.get("bootstrap", {}).get("main_collection", "")
    # game.project stores built paths (.collectionc); check built AND source
    def present(p):
        if not p:
            return False
        for cand in (p, re.sub(r"c$", "", p) if p.endswith("c") else p + "c"):
            f = root / cand.lstrip("/")
            if f.is_file() or f.with_name(f.stem).with_suffix(
                    ".collection" if f.suffix == ".collectionc" else f.suffix).is_file():
                return True
        return False
    report["bootstrap_collection"] = boot
    report["bootstrap_present"] = present(boot)

    gates = {}
    shader_excl = cfg.get("shader", {}).get("exclude_gles_sm100")
    gates["gles2_webgl1_shaders"] = ("opt-in OFF (1.14.1 default)" if shader_excl in (None, "1")
                                     else "included (exclude_gles_sm100=0)")
    phys = cfg.get("physics", {})
    gates["2d_physics"] = phys.get("use_box2d", "unset")
    gates["3d_physics"] = phys.get("use_physics", phys.get("enabled", "unset"))
    report["engine_gates"] = gates

    style = []
    if counts.get(".png", 0) or counts.get(".tilesource", 0) or counts.get(".atlas", 0):
        style.append("2D/sprite assets present")
    if counts.get(".model", 0) or counts.get(".glb", 0) or counts.get(".gltf", 0):
        style.append("3D model assets present")
    if counts.get(".mesh", 0):
        style.append("mesh assets present")
    report["style_signals"] = style or ["no graphics assets yet"]
    report["render_scripts"] = counts.get(".render", 0)
    report["scripts_lua"] = counts.get(".lua", 0) + counts.get(".script", 0)

    if as_json:
        print(json.dumps(report, indent=2)); return 0
    print(f"# Audit {root}")
    print(f"bootstrap: {boot or 'MISSING'} (exists: {report['bootstrap_present']})")
    print(f"render scripts: {report['render_scripts']} | lua/script files: {report['scripts_lua']}")
    print("style signals: " + ", ".join(report["style_signals"]))
    for k, v in gates.items():
        print(f"gate {k}: {v}")
    print("module roots: " + (", ".join(module_roots[:12]) or "none detected"))
    print("(informational audit — no pass/fail; see workflows/existing-project.md)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
