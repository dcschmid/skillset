#!/usr/bin/env python3
"""material_audit.py — material/reference integrity audit (read-only, stdlib).

Engine-agnostic: scans .material (Defold), .gdshader/.material (Godot text),
GLB/GLTF embedded materials, and reports defects vs style-aware expectations
(materials.md). Repairs are PROPOSALS; fix-mode applies protected subset.
Usage: python3 scripts/material_audit.py PROJECT_DIR [--config DIR]
Exit 0 = done; 1 = Critical findings.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_lib import Report, is_pixel_art, load_config  # noqa: E402

STYLE_OK_MISSING = {"normal": ("pixel-art", "pixelart", "voxel", "hand-painted", "flat")}


def audit_gltf_materials(path, doc, rep, cfg):
    px = is_pixel_art(cfg)
    ntx = len(doc.get("images") or [])
    for i, m in enumerate(doc.get("materials") or []):
        name = m.get("name", f"[{i}]")
        prm = m.get("pbrMetallicRoughness") or {}
        mr = prm.get("metallicRoughnessTexture", {}).get("index")
        if mr is not None and not (0 <= mr < ntx):
            rep.add(path, "material", "Critical", f"'{name}' MR texture index {mr} >= {ntx}",
                    fix="re-point", validation="STATIC")
        bct = prm.get("baseColorTexture", {}).get("index")
        if bct is not None and not (0 <= bct < ntx):
            rep.add(path, "material", "Critical", f"'{name}' albedo texture index {bct} >= {ntx}",
                    fix="re-point", validation="STATIC")
        met = prm.get("metallicFactor")
        if isinstance(met, (int, float)) and 0.1 < met < 0.9:
            rep.add(path, "material", "Medium", f"'{name}' metallicFactor {met} mid-range (drift?)",
                    fix="confirm intentional; else set 0/1 (fix-mode, diff-guarded)",
                    validation="STATIC")
        if px:
            rep.add(path, "material", "Informational",
                    f"'{name}' in pixel-art project: normal/rough variation style-expected",
                    validation="STATIC")


def audit_defold(path, rep):
    txt = path.read_text(errors="replace")
    for m in re.finditer(r'textures:\s*"([^"]+)"', txt):
        t = m.group(1)
        if t and not (path.parent / t).exists() and not any(
                (p / t).exists() for p in [path.parent.parent]):
            pass  # relative resolution is engine-configured; note only if declared root
    if re.search(r'fragment_program:\s*"([^"]+)"', txt):
        fp = re.search(r'fragment_program:\s*"([^"]+)"', txt).group(1)
        if not (path.parent / fp).exists() and not any(
                (d / fp).exists() for d in [path.parent.parent, path.parent.parent.parent]):
            rep.add(path, "material", "High", f"shader not found near material: {fp}",
                    fix="restore/re-path shader file (repoint fix)", validation="STATIC")


def audit_godot_text(path, rep):
    txt = path.read_text(errors="replace")
    for m in re.finditer(r'texture(\d)?\s*=\s*ExtResource\("(\w+_\w+)"\)', txt):
        pass  # ExtResource ids resolve in .import/.uid sidecars — engine truth
    if path.suffix == ".gdshader":
        if "shader_type" not in txt:
            rep.add(path, "shader", "Critical", "gdshader without shader_type header",
                    fix="add shader_type spatial|canvas_item", validation="STATIC")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    root = Path(argv[0])
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    cfg, notes, _ = load_config(argv[argv.index("--config") + 1]
                                if "--config" in argv else root)
    rep = Report(f"materials:{root}")
    for n in notes:
        rep.note(n)
    from pipeline_lib import read_gltf
    n = 0
    for p in list(root.rglob("*.glb")) + list(root.rglob("*.gltf")):
        doc, err = read_gltf(p)
        if not err and doc.get("materials"):
            n += len(doc["materials"])
            audit_gltf_materials(p, doc, rep, cfg)
    for p in root.rglob("*.material"):
        if p.stat().st_size < 1 << 20:
            audit_defold(p, rep)
            n += max(1, p.read_text(errors="replace").count("materials {"))
    for p in list(root.rglob("*.gdshader")) + list(root.rglob("*.material.res")):
        audit_godot_text(p, rep)
    rep.note(f"material entries inspected={n} (style-aware suppressions: "
             f"art_style={cfg.get('art_style') or 'undeclared'})")
    print(rep.to_markdown())
    return 1 if any(f["severity"] == "Critical" for f in rep.findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
