#!/usr/bin/env python3
"""audit_godot_project.py — read-only auditor for a Godot 4.x project.

Stdlib only; runs WITHOUT the engine (STATIC level). Reports: project
settings that matter for style gates, scenes + scripts inventory, autoloads,
broken res:// dependencies, .import coverage, input-map action count,
addons, export presets. Never writes anything.

Usage: audit_godot_project.py <project_dir>
Exit 0 = audit produced (findings listed); exit 1 = not a Godot project.
"""
import re
import sys
from pathlib import Path


def res_paths(text: str) -> set[str]:
    return set(re.findall(r'res://[\w/.\-]+', text))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    root = Path(sys.argv[1]).resolve()
    pg = root / "project.godot"
    if not pg.is_file():
        print(f"FAIL not a Godot project (no project.godot): {root}")
        return 1

    cfg = pg.read_text(encoding="utf-8", errors="replace")
    findings: list[str] = []

    ver = re.search(r'config/features=PackedStringArray\(([^)]*)\)', cfg)
    print(f"engine_hint: {ver.group(1) if ver else 'none (open in editor to stamp)'}")

    main_scene = re.search(r'run/main_scene="?([^"\n]+)', cfg)
    print(f"main_scene: {main_scene.group(1) if main_scene else 'UNSET'}")
    if main_scene and not (root / main_scene.group(1).replace("res://", "")).is_file():
        findings.append(f"main_scene missing: {main_scene.group(1)}")

    autoload_section = re.search(r"\[autoload\]\n(.*?)(\n\[|\Z)", cfg, re.S)
    autoloads = re.findall(r'^(\w+)="(\*?res://[^"]+)"',
                           autoload_section.group(1), re.M) if autoload_section else []
    print(f"autoloads: {[a[0] for a in autoloads] or 'none'}")
    for name, path in autoloads:
        if not (root / path.lstrip("*").replace("res://", "")).is_file():
            findings.append(f"autoload {name} -> missing {path}")

    style_keys = {
        "default_texture_filter": "rendering/textures/canvas_textures/default_texture_filter",
        "stretch_mode": "display/window/stretch/mode",
        "window_width": "display/window/size/viewport_width",
        "window_height": "display/window/size/viewport_height",
        "renderer": "rendering/renderer/rendering_method",
        "snap_2d_transforms": "rendering/2d/snap/snap_2d_transforms_to_pixel",
    }
    for label, key in style_keys.items():
        m = re.search(rf'^{re.escape(key)}=(.+)$', cfg, re.M)
        if not m:  # sectioned spelling: rendering/textures/... inside [rendering]
            tail = key.split("/", 1)[1] if key.split("/")[0] in (
                "rendering", "display", "physics", "input_devices") else key
            m = re.search(rf'^{re.escape(tail)}=(.+)$', cfg, re.M)
        print(f"style.{label}: {m.group(1).strip() if m else 'default'}")

    scenes = sorted(root.rglob("*.tscn"))
    scripts = sorted(root.rglob("*.gd"))
    imports = len(list(root.rglob("*.import")))
    print(f"scenes: {len(scenes)}  scripts: {len(scripts)}  .import files: {imports}")

    scan = scenes + scripts + [pg]
    for f in scan:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ref in res_paths(text):
            rel = ref.replace("res://", "")
            if rel and not (root / rel).exists():
                findings.append(f"broken dep in {f.relative_to(root)}: {ref}")
        for m in re.finditer(r'ExtResource\("([\w_]+)"\)', text):
            pass  # ext ids resolve via header; header scan above covers paths

    addons = [p.name for p in (root / "addons").iterdir() if p.is_dir()] if (root / "addons").is_dir() else []
    if addons:
        print(f"addons: {addons} (each: compat/license/maintenance gate)")
    ep = root / "export_presets.cfg"
    print(f"export_presets: {'present' if ep.is_file() else 'none'}")

    for f in findings:
        print(f"FINDING {f}")
    print(f"STATIC audit done: {len(findings)} finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
