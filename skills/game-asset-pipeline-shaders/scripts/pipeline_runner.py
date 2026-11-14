#!/usr/bin/env python3
"""pipeline_runner.py — mode dispatcher: audit|validate|fix|optimize|compare|benchmark.

fix = DRY RUN by default (--apply to write; .orig backups; protected globs
skipped; manifest for reversal). compare = Pillow metrics when two images
given, else NOT_RUN honestly. Estimates always labeled estimated.
Usage:
  python3 scripts/pipeline_runner.py MODE TARGET [--config DIR] [--json OUT]
        [--apply] [--before A --after B]
Exit 0 = ok; 1 = blocking findings; 2 = usage.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_lib import (Report, find_assets, is_pixel_art, load_config,  # noqa: E402
                          sha1_head)

HERE = Path(__file__).resolve().parent
MODES = ("audit", "validate", "fix", "optimize", "compare", "benchmark")


def _sub(cmd):
    r = subprocess.run([sys.executable, str(HERE / cmd[0]), *cmd[1:]],
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def mode_audit(target, args):
    rc, out, err = _sub(["asset_audit.py", str(target),
                         *( ["--config", args["config"]] if args["config"] else []),
                         *(["--json", str(Path(args["json"]).with_suffix(".audit.json"))]
                           if args["json"] else [])])
    print(out, end="")
    if err:
        print(err, file=sys.stderr)
    return rc


def mode_validate(target, args):
    files = [target] if target.is_file() else [p for k, p in
             find_assets(target, load_config(target)[0])]
    worst = 0
    for p in files[:200]:
        if p.suffix.lower() in (".glb", ".gltf"):
            rc, out, _ = _sub(["gltf_validate.py", str(p)])
            print(f"— {p.name}: {'ok' if rc == 0 else 'blocking'}")
            worst = max(worst, rc)
        elif p.suffix.lower() == ".material" or p.suffix == ".gdshader":
            rc, _, _ = _sub(["material_audit.py", str(target)])
            worst = max(worst, rc)
    rc, out, _ = _sub(["texture_analyze.py", str(target if target.is_dir()
                                               else target.parent)])
    print(out, end="")
    return worst


def mode_fix(target, args):
    """Dry-run default: enumerate protected-safe repairs as diff-style plan."""
    cfg, notes, _ = load_config(Path(args["config"] or target))
    allowed = set(cfg.get("auto_fix", {}).get("enabled") or [])
    protect = [str(g) for g in cfg.get("auto_fix", {}).get("protect") or []]
    rep = Report(f"fix-plan:{target}")
    rep.note(f"apply={'yes' if args['apply'] else 'DRY-RUN (pass --apply, .orig backups written)'}"
             f" allowed_fixes={sorted(allowed)} protect={protect}")
    root = Path(target)
    files = find_assets(root, cfg)
    # candidate 1: dedupe identical (content hash) — reversible via manifest
    by_hash = {}
    for kind, p in files:
        h = sha1_head(p)
        by_hash.setdefault(h, []).append(p)
    for h, group in by_hash.items():
        if len(group) > 1 and "dedupe-identical" in allowed:
            keep, rest = group[0], group[1:]
            if any(_protected(p, protect) for p in group):
                rep.add(keep, "fix", "Informational", "duplicate set under protect paths — skipped",
                        validation="STATIC")
                continue
            plan = {"fix": "dedupe-identical", "keep": str(keep),
                    "remove_or_repoint": [str(p) for p in rest],
                    "backup": "true (.orig before rewrite; manifest: fix-manifest.json)"}
            if args["apply"]:
                _write_manifest(root, plan)
                for p in rest:
                    bak = p.with_name(p.name + ".orig")
                    if not bak.exists():
                        bak.write_bytes(p.read_bytes())
                rep.add(keep, "fix", "Informational",
                        f"applied: {len(rest)} dup(s) backed up, repoint refs pending "
                        f"(manual confirm per engine import file)", validation="STATIC")
            else:
                rep.add(keep, "fix-plan", "Medium",
                        f"dedupe-identical: keep {keep.name}, repoint {len(rest)} copy(ies)",
                        fix="approve then rerun --apply", impact="one less file, refs must update",
                        validation="STATIC")
    # candidate 2: missing-texture repoint via same-name asset elsewhere
    idx = {}
    for kind, p in files:
        idx.setdefault(p.name, []).append(p)
    for manifest in list(root.rglob("*.import"))[:300]:
        try:
            txt = manifest.read_text(errors="replace")
        except OSError:
            continue
        import re
        for m in re.finditer(r'"([^"]+/\.(png|jpg|jpeg|webp|tga|glb|gltf))"', txt):
            src = Path(m.group(1))
            if (manifest.parent / src).exists() or (root / str(src)).exists():
                continue
            cands = idx.get(src.name, [])
            if cands and "repoint-missing-texture" in allowed:
                rep.add(manifest, "fix-plan", "High",
                        f"missing {src} -> unique same-name candidate {cands[0]}",
                        fix=f"rewrite path to {cands[0]} (backup first)" if len(cands) == 1
                        else f"{len(cands)} candidates — needs choice, report-only",
                        validation="STATIC")
    print(rep.to_markdown())
    return 0


def _protected(p, globs):
    s = str(p)
    return any(g.rstrip("/") in s or s.endswith(g.strip("*")) for g in globs)


def _write_manifest(root, plan):
    m = Path(root) / "asset-reports" / "fix-manifest.json"
    m.parent.mkdir(parents=True, exist_ok=True)
    rows = json.loads(m.read_text()) if m.is_file() else []
    rows.append(plan)
    m.write_text(json.dumps(rows, indent=1))


def mode_compare(args):
    a, b = args.get("before"), args.get("after")
    if not (a and b):
        print("NOT_RUN: compare needs --before A --after B images "
              "(no render env assumed); engine render then rerun")
        return 0
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("NOT_RUN: Pillow absent — install Pillow or use engine-side compare")
        return 0
    ia, ib = Image.open(a).convert("RGBA"), Image.open(b).convert("RGBA")
    if ia.size != ib.size:
        ib = ib.resize(ia.size)
    diff = ImageChops.difference(ia.convert("RGB"), ib.convert("RGB"))
    db = diff.tobytes()  # RGB bytes; avoids getdata() deprecation on Pillow 12+
    n = max(1, len(db) // 3)
    diffpct = sum(1 for i in range(0, len(db) - 2, 3)
                  if db[i] + db[i + 1] + db[i + 2] > 12) / n * 100
    # grayscale SSIM, uniform 8x8 blocks (estimate-grade metric)
    ab, bb = ia.convert("L").tobytes(), ib.convert("L").tobytes()
    w = ia.size[0]
    blocks, ssim_n = 0, 0.0
    for y in range(0, ia.size[1] - 7, 8):
        for x in range(0, w - 7, 8):
            ia_ = [ab[(y + j) * w + x + i] for j in range(8) for i in range(8)]
            ib_ = [bb[(y + j) * w + x + i] for j in range(8) for i in range(8)]
            ma, mb = sum(ia_) / 64, sum(ib_) / 64
            va = sum((v - ma) ** 2 for v in ia_) / 64
            vb = sum((v - mb) ** 2 for v in ib_) / 64
            cov = sum((u - ma) * (v - mb) for u, v in zip(ia_, ib_)) / 64
            c1, c2 = 6.5025, 58.5225
            ssim_n += ((2 * ma * mb + c1) * (2 * cov + c2)) / \
                      ((ma * ma + mb * mb + c1) * (va + vb + c2))
            blocks += 1
    ssim = ssim_n / blocks if blocks else 1.0
    print(f"## compare {Path(a).name} vs {Path(b).name}\n"
          f"- pixel_diff: {diffpct:.2f}% pixels changed\n"
          f"- SSIM: {ssim:.4f} (8x8 block estimate; full-window lib if project installs one)\n"
          "- no single metric decides: use both + perceptual review; thresholds from "
          "asset-pipeline.yaml quality_thresholds")
    return 0


def mode_optimize(target, args):
    cfg, notes, _ = load_config(Path(args["config"] or target))
    rc, out, _ = _sub(["texture_analyze.py", str(target),
                       *(["--config", args["config"]] if args["config"] else [])])
    print(out, end="")
    print("\n# optimize = plan mode: suggestions above require approval before "
          "any write; originals protected; pixel-art: lossy/format changes forbidden")
    return rc


def main(argv):
    if len(argv) < 2 or argv[0] not in MODES:
        print(__doc__)
        return 2
    mode, target_s = argv[0], argv[1]
    args = {"config": argv[argv.index("--config") + 1] if "--config" in argv else None,
            "json": argv[argv.index("--json") + 1] if "--json" in argv else None,
            "apply": "--apply" in argv,
            "before": argv[argv.index("--before") + 1] if "--before" in argv else None,
            "after": argv[argv.index("--after") + 1] if "--after" in argv else None}
    target = Path(target_s)
    if not target.exists():
        print(f"error: target missing: {target}", file=sys.stderr)
        return 2
    return {"audit": lambda: mode_audit(target, args),
            "validate": lambda: mode_validate(target, args),
            "fix": lambda: mode_fix(target, args),
            "optimize": lambda: mode_optimize(target, args),
            "compare": lambda: mode_compare(args),
            "benchmark": lambda: mode_optimize(target, args)}[mode]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
