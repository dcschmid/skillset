#!/usr/bin/env python3
"""audio_batch.py — batch operations over audio file sets.

Sub-commands:
  process  PROJECT --op OP... [--filter ...]   apply audio_process ops per
           file; originals untouched (unique-suffixed outputs); resumable:
           files with an existing *.proc-report.json sidecar are skipped
           (idempotent re-runs)
  convert  PROJECT --to wav|ogg|flac|mp3 [--rate N] [--channels N]
           transcode set into --out-dir (never overwrites)
  report   PROJECT [--json]                    measured facts table for every
           audio file (no writes)

All outputs land under --out-dir (default PROJECT/audio-batch-out). GPU
generation is NOT this script's job: use gaf_adapter / the backend.
Exit 0 all ok, 1 some file failed, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import audio_common as ac

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio_process  # noqa: E402


def _out(out_dir: Path, src: Path, suffix: str = "") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    return ac.unique_path(out_dir / f"{src.stem}{suffix}{src.suffix}")


def process(project: Path, ops: list[str], out_dir: Path, dry: bool) -> list[dict]:
    results = []
    for path in ac.audio_files(project):
        report = path.with_name(path.stem + ".proc-report.json")
        if report.is_file():                       # idempotent: already done
            results.append({"file": str(path), "action": "skipped",
                            "reason": "already processed"})
            continue
        out = _out(out_dir, path)
        try:
            cmd = audio_process.cmd_for(path, out, ops)
        except ValueError as e:
            results.append({"file": str(path), "action": "skipped",
                            "reason": str(e)})
            continue
        if dry:
            results.append({"file": str(path), "action": "proposed",
                            "cmd": " ".join(cmd)})
            continue
        p = subprocess.run(cmd, capture_output=True, text=True)
        ok = p.returncode == 0 and out.is_file()
        rec = {"file": str(path), "action": "applied" if ok else "failed",
               "out": str(out), "recheck": "PASS" if ok else "FAIL",
               "error": None if ok else (p.stderr or "")[-200:]}
        report.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        results.append(rec)
    return results


def convert(project: Path, out_dir: Path, fmt: str, rate: int | None,
            ch: int | None) -> list[dict]:
    results = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in ac.audio_files(project):
        out = ac.unique_path(out_dir / f"{path.stem}.{fmt}")
        cmd = [ac.require("ffmpeg"), "-y", "-v", "error", "-i", str(path)]
        if rate:
            cmd += ["-ar", str(rate)]
        if ch:
            cmd += ["-ac", str(ch)]
        if fmt == "wav":
            cmd += ["-c:a", "pcm_s16le"]
        results.append({"file": str(path), "out": str(out),
                        "cmd": " ".join(map(str, cmd + [str(out)])),
                        "_argv": list(map(str, cmd)) + [str(out)]})
    for r in results:                                # run after planning
        p = subprocess.run(r.pop("_argv"), capture_output=True, text=True)
        r["action"] = "applied" if p.returncode == 0 else "failed"
        r["recheck"] = "PASS" if p.returncode == 0 else "FAIL"
    return results


def report(project: Path) -> list[dict]:
    rows = []
    for path in ac.audio_files(project):
        facts = ac.probe(path)
        m = ac.measure(path) if facts.get("ok") else {}
        rows.append({"file": str(path), "duration": facts.get("duration"),
                     "rate": facts.get("rate"), "channels": facts.get("channels"),
                     "peak_dbfs": m.get("peak_dbfs"), "rms_dbfs": m.get("rms_dbfs"),
                     "status": "PASS" if facts.get("ok") and m.get("ok") else
                               ("WARNING" if facts.get("ok") else "FAIL")})
    return rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="audio_batch.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("process")
    p.add_argument("project")
    p.add_argument("--op", action="append", required=True)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    c = sub.add_parser("convert")
    c.add_argument("project")
    c.add_argument("--to", required=True, choices=["wav", "ogg", "flac", "mp3"])
    c.add_argument("--rate", type=int)
    c.add_argument("--channels", type=int)
    c.add_argument("--out-dir", default=None)
    c.add_argument("--json", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("project")
    r.add_argument("--json", action="store_true")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    project = Path(ns.project).expanduser().resolve()
    if not project.is_dir():
        print(f"error: no such dir: {project}", file=sys.stderr)
        return 2
    out_dir = (Path(ns.out_dir).expanduser().resolve()
               if getattr(ns, "out_dir", None) else project / "audio-batch-out")
    try:
        if ns.cmd == "process":
            rows = process(project, ns.op, out_dir, ns.dry_run)
        elif ns.cmd == "convert":
            rows = convert(project, out_dir, ns.to, ns.rate, ns.channels)
        else:
            rows = report(project)
    except (RuntimeError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    fails = [x for x in rows if x.get("action") == "failed"
             or x.get("recheck") == "FAIL" or x.get("status") == "FAIL"]
    print(json.dumps({"files": len(rows), "failed": len(fails), "rows": rows},
                     indent=2, ensure_ascii=False) if ns.json
          else f"batch {ns.cmd}: {len(rows)} files, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
