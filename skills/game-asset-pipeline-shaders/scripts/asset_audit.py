#!/usr/bin/env python3
"""asset_audit.py — whole-project asset inventory + pipeline findings (read-only).

Walks a project, detects engine (probed), classifies assets, runs texture and
glTF lanes, aggregates findings by severity for audit mode. CI-safe/headless.
Usage: python3 scripts/asset_audit.py PROJECT_DIR [--json OUT] [--md OUT.md]
Exit 0 = audit complete (findings may exist); 1 = blocking (Critical) findings.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_lib import (Report, detect_engine, find_assets,  # noqa: E402
                          load_config)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    root = Path(argv[0])
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    out_md = argv[argv.index("--md") + 1] if "--md" in argv else None
    cfg, notes, _ = load_config(root)
    engine, ver = detect_engine(root)
    rep = Report(f"audit:{root}")
    for n in notes:
        rep.note(n)
    rep.note(f"engine={engine or 'undetected (adapters stay generic)'} version={ver or '?'} "
             f"(probed from project files; style={cfg.get('art_style') or 'undeclared'})")
    assets = find_assets(cfg_root := root, cfg)
    rep.note(f"assets={len(assets)} ({sum(1 for k,_ in assets if k=='texture')} textures, "
             f"{sum(1 for k,_ in assets if k=='model')} models)")
    if not assets:
        rep.note("no known asset extensions found — check exclude_dirs swallowing paths")

    tex = [p for k, p in assets if k == "texture"]
    models = [p for k, p in assets if k == "model"]
    # texture lane: dedupe + missing-by-reference
    hashes = {}
    for p in tex:
        import hashlib
        h = hashlib.sha1()
        try:
            h.update(p.read_bytes()[:65536])
        except OSError:
            rep.add(p, "io", "High", "unreadable", fix="permissions/repo state",
                    validation="STATIC")
            continue
        key = h.hexdigest()
        if key in hashes:
            rep.add(p, "texture", "Medium", f"content-duplicate of {hashes[key]}",
                    fix="dedupe candidate (fix-mode, protected paths respected)",
                    validation="STATIC")
        else:
            hashes[key] = p
    # model lane: structural parse
    from pipeline_lib import read_gltf
    for p in models:
        try:
            doc, err = read_gltf(p)
            if err:
                rep.add(p, "model", "Critical", f"parse: {err}",
                        fix="re-export from source; do not hand-edit GLB",
                        validation="STATIC")
            else:
                ext = set(map(str, (doc.get("extensionsRequired") or [])))
                if ext and engine in (None, "multi"):
                    rep.add(p, "model", "Medium",
                            f"required extensions {sorted(ext)} with engine undetected",
                            fix="declare engine in asset-pipeline.yaml; adapter-gate codecs",
                            validation="STATIC")
        except Exception as e:
            rep.add(p, "model", "High", f"validator error: {e}", validation="STATIC")
    # reference lane: engine import manifests naming missing files
    for manifest in list(root.rglob("*.import"))[:400]:
        try:
            txt = manifest.read_text(errors="replace")
        except OSError:
            continue
        for src in _source_paths(txt):
            sp = (manifest.parent / src)
            if src and not sp.is_file() and not (root / src).is_file():
                rep.add(manifest, "reference", "High", f"import source missing: {src}",
                        fix="restore file or repoint (auto_fix: repoint-missing-texture)",
                        validation="STATIC")
    blocking = sum(1 for f in rep.findings if f["severity"] == "Critical")
    counts = rep.counts()
    rep.note(f"severities: {counts} — gate honesty: all checks STATIC "
             f"(engine import=HEADLESS, pixels=RENDER require the engine; "
             f"NOT_RUN there unless run separately)")
    if out_json:
        Path(out_json).write_text(json.dumps(rep.to_json(), indent=1), encoding="utf-8")
    md = rep.to_markdown()
    if out_md:
        Path(out_md).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 1 if blocking else 0


def _source_paths(txt):
    import re
    for m in re.finditer(r'(?:importer|path|src_file|source_file)\s*=?\s*"([^"]+\.(?:png|jpg|jpeg|webp|tga|exr|hdr|dds|ktx2|glb|gltf|fbx))"', txt):
        yield m.group(1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
