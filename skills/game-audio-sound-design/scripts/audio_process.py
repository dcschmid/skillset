#!/usr/bin/env python3
"""audio_process.py — deterministic ffmpeg processing of one audio file.

Originals are NEVER modified: output goes to --out (unique-suffixed when it
exists). Every op is a documented ffmpeg filter — no invented DSP.

Ops (--op, repeatable; order = application order):
  fade              10 ms in + out at edges (loop-click safety)
  trim              strip leading/trailing silence (< -60 dBFS)
  normalize TARGET  peak-normalize to TARGET dBFS (e.g. -1.0)
  resample RATE     → RATE Hz (s16 wav)
  mono | stereo     channel layout
  loop-xfade        crossfade tail into head (seamless loop material)
  atempo FACTOR     time-preserving tempo change 0.5–2.0 (music layers)
  gain DB           fixed dB gain (variation without regeneration)

Usage:
  audio_process.py FILE --op fade --op "normalize -1.0" [--out DIR|FILE]
                      [--dry-run] [--json]
Exit 0 ok (dry-run prints the plan), 1 processing failed, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import audio_common as ac


def filters_for(ops: list[str], duration: float) -> tuple[list[str], dict]:
    """Map skill ops → ffmpeg filter chain + encode overrides."""
    chain: list[str] = []
    enc: dict = {}
    for op in ops:
        parts = op.split()
        name = parts[0].lower()
        if name == "fade":
            d = max(duration - 0.01, 0.0)
            chain += [f"afade=t=in:d=0.01,afade=t=out:st={d}:d=0.01"]
        elif name == "trim":
            chain += ["silenceremove=start_periods=1:start_threshold=-60dB:"
                      "stop_periods=-1:stop_threshold=-60dB"]
        elif name == "normalize":
            target = float(parts[1])
            chain.append(f"alimiter=limit={10 ** (target / 20):.4f}")
        elif name == "resample":
            enc["ar"] = int(float(parts[1]))
        elif name == "mono":
            enc["ac"] = 1
        elif name == "stereo":
            enc["ac"] = 2
        elif name == "loop-xfade":
            half = round(min(duration, 1.0) / 2, 4)
            chain.append(f"afade=t=out:st={max(half, 0.0)}:d={half}")
        elif name == "atempo":
            f = float(parts[1])
            if not (0.5 <= f <= 2.0):
                raise ValueError(f"atempo {f} outside 0.5–2.0")
            chain.append(f"atempo={f}")
        elif name == "gain":
            chain.append(f"volume={float(parts[1])}dB")
        else:
            raise ValueError(f"unknown op: {op!r}")
    return chain, enc


def cmd_for(src: Path, out: Path, ops: list[str]) -> list[str]:
    facts = ac.probe(src)
    if not facts.get("ok"):
        raise ValueError(f"unreadable: {facts.get('error')}")
    chain, enc = filters_for(ops, facts.get("duration") or 0.0)
    cmd = [ac.require("ffmpeg"), "-y", "-v", "error", "-i", str(src)]
    if chain:
        cmd += ["-af", ",".join(chain)]
    if enc.get("ar"):
        cmd += ["-ar", str(enc["ar"])]
    if enc.get("ac"):
        cmd += ["-ac", str(enc["ac"])]
    if out.suffix.lower() == ".wav":
        cmd += ["-c:a", "pcm_s16le"]
    return cmd + [str(out)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="audio_process.py")
    ap.add_argument("file")
    ap.add_argument("--op", action="append", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    src = Path(ns.file).expanduser().resolve()
    if not src.is_file():
        print(f"error: no such file: {src}", file=sys.stderr)
        return 2
    if ns.out:
        out = Path(ns.out).expanduser().resolve()
        out = ac.unique_path(out / src.name) if out.is_dir() or not out.suffix \
            else out
    else:
        out = ac.unique_path(src.with_name(f"{src.stem}.proc{src.suffix}"))
    try:
        cmd = cmd_for(src, out, ns.op)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if ns.dry_run:
        plan = {"file": str(src), "out": str(out), "cmd": " ".join(cmd),
                "action": "proposed"}
        print(json.dumps(plan, indent=2) if ns.json else " ".join(cmd))
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(cmd, capture_output=True, text=True)
    ok = p.returncode == 0 and out.is_file()
    before, after = ac.measure(src), (ac.measure(out) if ok else {})
    res = {"file": str(src), "out": str(out),
           "action": "applied" if ok else "failed",
           "before": {"rms_dbfs": before.get("rms_dbfs")},
           "after": {"rms_dbfs": after.get("rms_dbfs")},
           "recheck": "PASS" if ok and after.get("ok") else "FAIL",
           "error": None if ok else (p.stderr or "")[-300:]}
    print(json.dumps(res, indent=2, ensure_ascii=False) if ns.json
          else f"{res['action']}: {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
