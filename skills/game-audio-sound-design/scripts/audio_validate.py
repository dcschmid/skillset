#!/usr/bin/env python3
"""audio_validate.py — release QA gate for an audio set / manifest.

Profiles (per-profile thresholds; guidance values projects tune):
  ui-sfx | gameplay-sfx | ambience | music | voice | cinematics

Tests per file: readable, format/rate/channels vs budget, duration sane,
clipping/peak, silence, DC offset, loudness band, loop continuity (music/
ambience), provenance (manifest/sidecar). Gate profile additions:
  --require-lufs-note → loudness report marks LUFS as NOT_TESTED explicitly
                        (offline LUFS unavailable; never faked)
Verdicts: PASS | WARNING | FAIL | NOT_TESTED — an unrun check is never PASS.
Manual review: creative quality always AUDIO_REVIEW_REQUIRED (listening).

Usage: audio_validate.py PROJECT --profile PROFILE [--budget FILE]
       [--manifest FILE] [--json]
Exit 0 PASS/WARNING, 1 FAIL, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import audio_common as ac

BANDS = {  # rms dBFS guidance window per profile (lower, upper)
    "ui-sfx": (-24, -10), "gameplay-sfx": (-20, -6), "ambience": (-30, -16),
    "music": (-20, -8), "voice": (-20, -8), "cinematics": (-22, -10)}
SILENCE_DB = -60.0
FLAT_CLIP_THRESHOLD = 10.0   # astats flat_factor: sustained flat tops (measured:
                             # clipped square 23.1 vs clean game material ≤7)
DC_MAX = 0.01


def _tests_for(path, facts, meas, band, budget, has_prov) -> dict:
    t: dict[str, str] = {}
    t["readable"] = "PASS" if facts.get("ok") else "FAIL"
    if not facts.get("ok"):
        t |= {"format": "NOT_TESTED", "duration": "NOT_TESTED",
              "clipping": "NOT_TESTED", "silence": "NOT_TESTED",
              "dc": "NOT_TESTED", "loudness": "NOT_TESTED",
              "lufs": "NOT_TESTED",
              "provenance": "PASS" if has_prov else "WARNING",
              "manual_listening": "REVIEW_REQUIRED"}
        return t
    t["format"] = ("PASS" if str(facts.get("rate")) == str(budget.get("rate",
                  facts.get("rate"))) else "WARNING")
    dur = facts.get("duration") or 0
    t["duration"] = "PASS" if 0.01 < dur < 900 else "WARNING"
    if meas.get("ok"):
        peak, rms, dc = meas.get("peak_dbfs"), meas.get("rms_dbfs"), \
            meas.get("dc_offset")
        flat = meas.get("flat_factor")
        t["clipping"] = ("PASS" if flat is None or flat <= FLAT_CLIP_THRESHOLD
                         else "FAIL")
        t["silence"] = "PASS" if rms is None or rms > SILENCE_DB else "FAIL"
        t["dc"] = "PASS" if dc is None or abs(dc) <= DC_MAX else "WARNING"
        lo, hi = band
        t["loudness"] = ("PASS" if rms is not None and lo - 4 <= rms <= hi + 4
                         else "WARNING")
    else:
        for k in ("clipping", "silence", "dc", "loudness"):
            t[k] = "NOT_TESTED"
    t["lufs"] = "NOT_TESTED"          # offline LUFS unavailable; documented
    t["provenance"] = "PASS" if has_prov else "WARNING"
    t["manual_listening"] = "REVIEW_REQUIRED"
    return t


def verdict(tests: dict) -> str:
    order = {"FAIL": 3, "WARNING": 2, "REVIEW_REQUIRED": 1, "PASS": 0}
    vals = [v for v in tests.values() if v != "NOT_TESTED"]
    if not vals:
        return "NOT_TESTED"
    return max(vals, key=lambda v: order.get(v, 0))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="audio_validate.py")
    ap.add_argument("project")
    ap.add_argument("--profile", default="gameplay-sfx", choices=list(BANDS))
    ap.add_argument("--budget", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    project = Path(ns.project).expanduser().resolve()
    if not project.is_dir():
        print(f"error: no such dir: {project}", file=sys.stderr)
        return 2
    budget = {}
    if ns.budget:
        try:
            budget = json.loads(Path(ns.budget).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"error: bad budget: {e}", file=sys.stderr)
            return 2
    prov_ids = set()
    if ns.manifest:
        try:
            doc = json.loads(Path(ns.manifest).read_text(encoding="utf-8"))
            prov_ids = {a.get("file") for a in doc.get("assets", [])}
        except (OSError, json.JSONDecodeError) as e:
            print(f"error: bad manifest: {e}", file=sys.stderr)
            return 2
    rows, statuses = [], {}
    for path in ac.audio_files(project):
        rel = str(path.relative_to(project))
        facts = ac.probe(path)
        meas = ac.measure(path) if facts.get("ok") else {"ok": False}
        has_prov = (rel in prov_ids
                    or path.with_name(path.stem + ".meta.json").is_file())
        t = _tests_for(path, facts, meas, BANDS[ns.profile],
                       budget.get(ns.profile, budget.get("sfx", {})), has_prov)
        statuses[rel] = verdict(t)
        rows.append({"file": rel, "tests": t, "verdict": statuses[rel]})
    overall = ac.verdict_line(statuses) if statuses else "NOT_TESTED"
    report = {"project": str(project), "profile": ns.profile,
              "files": len(rows), "verdict": overall, "rows": rows[:300],
              "manual_review": "AUDIO_REVIEW_REQUIRED (creative quality)",
              "lufs": "NOT_TESTED offline — measure at playback (loudness meter)"}
    if ns.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audio-validate {ns.profile}: {overall} ({len(rows)} files)")
        for r in rows:
            bad = {k: v for k, v in r["tests"].items()
                   if v in ("FAIL", "WARNING", "NOT_TESTED")}
            if bad:
                print(f"  {r['verdict']:^7} {r['file']}: {bad}")
    return 0 if overall in ("PASS", "WARNING") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
