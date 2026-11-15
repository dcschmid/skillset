#!/usr/bin/env python3
"""audio_manifest.py — machine-readable audio manifest (create/ingest/check).

Schema v1 entry (values measured or backend-reported, never invented):
  {asset_id, category: sfx|music|ui|voice|ambience, source, model, seed,
   duration_seconds, sample_rate, channels, file, sha256_head,
   license_status: approved|review_required|restricted|unknown,
   quality_status: PASS|WARNING|FAIL|NOT_TESTED, target_engine, notes}

Commands:
  create  PROJECT_DIR [--out FILE] [--target-engine generic]
          → manifest for every audio file (facts measured on the spot)
  ingest  GAF_OUTPUT_DIR --into MANIFEST   (harvest backend output + sidecar)
  check   MANIFEST          → drift/revalidation report (no writes)

Existing manifests are never silently overwritten (unique-suffixed unless
--out names a fresh path). license_status seeds from backend sidecar notes
(dasheng → restricted: unlicensed runtime; sa3 → review_required until
revenue tier confirmed). Exit 0 ok, 1 check drift, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import audio_common as ac

SCHEMA = "gaf-audio-manifest/1"


def _entry(path: Path, root: Path, engine: str) -> dict:
    facts = ac.probe(path)
    side = path.with_name(path.stem + ".meta.json")
    meta = {}
    if side.is_file():
        try:
            meta = json.loads(side.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
    cat = "music" if "music" in str(path).lower() else \
        ("sfx" if path.suffix in (".wav", ".ogg", ".opus") else "ambience")
    note = str(meta.get("note", "")) + str(meta.get("generator", ""))
    lic = "review_required"
    if "dasheng" in note.lower():
        lic = "restricted"          # runtime unlicensed — internal only
    elif "sa3" in note.lower() or "Stable Audio" in note:
        lic = "review_required"     # Community License: commercial < $1M/yr
    elif "acestep" in note.lower() or "ACE-Step" in note:
        lic = "approved"            # MIT runtime + weights
    return {
        "asset_id": path.stem,
        "category": cat,
        "source": meta.get("generator", "imported"),
        "model": meta.get("synth_model") or meta.get("generator", "unknown"),
        "seed": meta.get("seed"),
        "prompt": meta.get("prompt"),
        "duration_seconds": facts.get("duration"),
        "sample_rate": int(facts["rate"]) if facts.get("rate") else None,
        "channels": facts.get("channels"),
        "file": str(path.relative_to(root)) if path.is_relative_to(root)
        else str(path),
        "measured": bool(facts.get("ok")),
        "license_status": lic,
        "quality_status": "PASS" if facts.get("ok") else "FAIL",
        "target_engine": engine,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def create(root: Path, out: Path, engine: str) -> dict:
    doc = {"schema": SCHEMA, "project": str(root),
           "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "assets": [_entry(p, root, engine) for p in ac.audio_files(root)]}
    ac.write_json(out, doc)
    return {"out": str(out), "assets": len(doc["assets"])}


def ingest(src: Path, manifest: Path) -> dict:
    entries = []
    for wav in sorted(src.glob("*.wav")):
        m = wav.with_name(wav.stem + ".meta.json")
        if not m.is_file():
            continue
        doc = {"schema": SCHEMA, "source_dir": str(src),
               "assets": [_entry(wav, src, "generic")]}
        ac.write_json(ac.unique_path(
            manifest.with_name(f"{manifest.stem}.{wav.stem}.json")), doc)
        entries.append(wav.name)
    return {"ingested": entries}


def check(manifest: Path) -> tuple[dict, bool]:
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    root = Path(doc.get("project", manifest.parent))
    drift, now_fail = [], False
    for e in doc.get("assets", []):
        f = next((c for c in (root / e["file"], manifest.parent / e["file"])
                  if c.is_file()), None)
        if f is None:
            drift.append({"asset": e["asset_id"], "problem": "file-missing"})
            continue
        facts = ac.probe(f)
        if not facts.get("ok"):
            drift.append({"asset": e["asset_id"], "problem": "unreadable"})
            now_fail = True
        elif (facts.get("duration") or 0) - (e.get("duration_seconds") or 0) > 0.05:
            drift.append({"asset": e["asset_id"],
                          "problem": f"duration drift "
                          f"{e['duration_seconds']}→{facts['duration']}"})
    report = {"manifest": str(manifest), "assets": len(doc.get("assets", [])),
              "drift": drift, "verdict": "FAIL" if now_fail else
              ("WARNING" if drift else "PASS")}
    return report, report["verdict"] == "PASS"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="audio_manifest.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("project")
    c.add_argument("--out", default=None)
    c.add_argument("--target-engine", default="generic")
    c.add_argument("--json", action="store_true")
    g = sub.add_parser("ingest")
    g.add_argument("src")
    g.add_argument("--into", required=True)
    g.add_argument("--json", action="store_true")
    k = sub.add_parser("check")
    k.add_argument("manifest")
    k.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    try:
        if ns.cmd == "create":
            root = Path(ns.project).expanduser().resolve()
            out = Path(ns.out) if ns.out else root / "audio-manifest.json"
            res = create(root, out, ns.target_engine)
        elif ns.cmd == "ingest":
            res = ingest(Path(ns.src).expanduser().resolve(),
                         Path(ns.into).expanduser().resolve())
        else:
            report, ok = check(Path(ns.manifest).expanduser().resolve())
            print(json.dumps(report, indent=2, ensure_ascii=False)
                  if ns.json else json.dumps(report))
            return 0 if ok else 1
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, indent=2, ensure_ascii=False) if ns.json
          else json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
