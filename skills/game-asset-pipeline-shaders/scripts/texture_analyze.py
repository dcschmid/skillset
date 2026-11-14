#!/usr/bin/env python3
"""texture_analyze.py — texture inventory, kind/class, color-space + sampler
advice, disk vs estimated-VRAM, optimization candidates (read-only).

Pixel-art/voxel profiles: no lossy suggestions, nearest/no-mip advice.
Uses Pillow when present for dims/alpha; falls back to header probes.
Usage: python3 scripts/texture_analyze.py DIR_OR_FILE [--config DIR] [--json OUT]
Exit 0 = analysis complete; findings may be any severity. 2 = usage/IO.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_lib import (DATA_MAP_RE, Report, file_vram_est, is_pixel_art,  # noqa: E402
                          load_config, sha1_head, vram_est_bytes)

TEXTURE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tga", ".exr", ".hdr",
               ".dds", ".ktx2", ".bmp"}
LOSSY_OK = {".jpg", ".jpeg"}
BPP = {".png": 32, ".tga": 32, ".bmp": 32, ".webp": 32, ".jpg": 24,
       ".jpeg": 24, ".dds": 8, ".ktx2": 8, ".exr": 64, ".hdr": 48}
LOSSLESS_FORMATS = {".png", ".tga", ".bmp"}


def classify(path):
    name = path.name.lower()
    for kind in ("normal", "rough", "metal", "occlusion|ao", "height|disp",
                 "emissive|glow", "opacity", "mask|orm"):
        import re as _re
        if _re.search(kind, name):
            return kind.split("|")[0], False
    return "albedo", DATA_MAP_RE.search(name) is not None


def analyze(path, cfg):
    size, w, h = file_vram_est(path, cfg)
    kind, _ = classify(path)
    pixel = is_pixel_art(cfg)
    out = {"file": str(path), "kind": kind, "ext": path.suffix.lower(),
           "disk_bytes": size, "width": w if w > 0 else None,
           "height": h if h > 0 else None, "hash": sha1_head(path)[:12]}
    bpp = BPP.get(out["ext"], 32)
    if w > 0:
        out["vram_est_bytes"] = vram_est_bytes(w, h, bpp,
                                               mips=not (pixel and kind == "albedo"))
        out["vram"] = "estimated"
    if pixel and out["ext"] in LOSSY_OK:
        out.setdefault("notes", []).append("pixel-art on lossy format: keep lossless source")
    cap = (cfg.get("texture_max_size") or {}).get(kind)
    if isinstance(cap, int) and w > cap:
        out.setdefault("findings", []).append(
            ("High", "oversized", f"{w}x{h} > profile cap {cap} for {kind}",
             "downsample on a copy; pixel-art: integer steps only"))
    if pixel:
        out["sampler"] = "nearest, no mipmaps"
    elif kind in ("normal", "rough", "metal", "occlusion", "height", "opacity", "mask"):
        out["sampler"] = "linear, color-space=LINEAR/data (never sRGB)"
    else:
        out["sampler"] = "linear+aniso per profile, color-space=sRGB"
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    root = Path(argv[0])
    cfg, notes, _ = load_config(argv[argv.index("--config") + 1]
                                if "--config" in argv else root.parent
                                if root.is_file() else root)
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    files = [root] if root.is_file() else sorted(
        p for p in root.rglob("*") if p.suffix.lower() in TEXTURE_EXT and p.is_file())
    if not files:
        print("textures: 0 found under", root)
        return 0
    rep = Report(f"textures:{root}")
    for n in notes:
        rep.note(n)
    rows, hashes = [], {}
    try:
        from PIL import Image  # optional, richer data
        pil = True
    except Exception:
        pil = False
        rep.note("Pillow absent: dims via headers only; no alpha/stats")
    for p in files:
        a = analyze(p, cfg)
        if pil and a.get("width"):
            try:
                with Image.open(p) as im:
                    a["mode"] = im.mode
                    if "A" in im.mode and im.mode not in ("RGB",):
                        al = im.getchannel("A")
                        ex = al.getextrema()
                        a["alpha"] = "full-opaque" if ex == (255, 255) else "used"
                        if ex == (255, 255):
                            rep.add(p, "texture", "Low", "alpha channel fully opaque — droppable",
                                    fix="strip alpha on a copy if engine import honors it",
                                    validation="STATIC")
            except Exception as e:
                rep.add(p, "texture", "Low", f"Pillow read failed: {e}", validation="STATIC")
        dup = hashes.setdefault(a["hash"], p)
        if dup is not None and dup != p:
            rep.add(p, "texture", "Medium", f"content-duplicate of {dup}",
                    fix="dedupe: keep one, repoint refs (auto_fix: dedupe-identical)",
                    validation="STATIC")
        rows.append(a)
    total_disk = sum(r["disk_bytes"] for r in rows)
    total_vram = sum(r.get("vram_est_bytes", 0) for r in rows)
    rep.note(f"textures={len(rows)} disk={total_disk}B vram_est={total_vram}B "
             f"(estimated; measure in profiler for truth) pixel_art={is_pixel_art(cfg)}")
    if out_json:
        Path(out_json).write_text(json.dumps({"rows": rows, **rep.to_json()}, indent=1),
                                  encoding="utf-8")
    print(rep.to_markdown())
    print("\n```json")
    print(json.dumps({"textures": len(rows), "disk_bytes_total": total_disk,
                      "vram_bytes_total_estimated": total_vram,
                      "pixel_art": is_pixel_art(cfg), "rows": rows}, indent=1))
    print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
