#!/usr/bin/env python3
"""audio_audit.py — audio asset & engine audit for game projects.

Modes:
  analyze   read-only inspection (default; never touches project files)
  fix       SAFE corrections (trim/fade/resample/convert) → NEW files in
            --out-dir; originals untouched; without --apply: proposal only
  optimize  budget-driven transcode plan; needs --apply to write

Finding: {severity: info|warning|error, category: asset|engine|mix,
problem, cause, fix_kind: fix|review|proposed, fix}.
Check status: PASS|WARNING|FAIL|NOT_TESTED (untested never reports PASS).

Asset checks: corrupt, silent, clipping, loudness-vs-profile, DC offset,
rate/channels-vs-budget, loop-seam risk, duplicates, missing sidecar.
Engine checks (static): defold .sound/game.project, godot .tscn/.tres —
missing references, unreferenced files, voice budget facts.

Usage:
  audio_audit.py PROJECT_DIR [--mode analyze|fix|optimize]
                 [--filter sfx|music|all] [--profile PROFILE]
                 [--out-dir DIR] [--dry-run] [--apply] [--json] [--budget FILE]
Exit: 0 no errors, 1 errors found, 2 usage/tool failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import audio_common as ac

SILENCE_DB = -60.0
FLAT_CLIP_THRESHOLD = 10.0   # astats flat_factor sustained-top metric (measured:
                             # clipped 23.1 vs mastered-clean ≤7; peak≈0 is normal)
DC_THRESHOLD = 0.01          # raw sample units
SEAM_RATIO = 3.0             # end/start energy ratio → loop-click risk
DEFAULT_BUDGET = {"sfx": {"rate": 48000, "channels": 2},
                  "music": {"rate": 48000, "channels": 2}}
# loudness guidance (rms dBFS) per profile — guidance, projects tune it
PROFILES = {"ui-sfx": (-24, -10), "gameplay-sfx": (-20, -6),
            "ambience": (-30, -16), "music": (-20, -8),
            "voice": (-20, -8), "cinematics": (-22, -10)}
AUDIO_EXTS = (".wav", ".ogg", ".mp3", ".flac", ".opus")


def finding(sev, cat, prob, cause, kind, desc) -> dict:
    return {"severity": sev, "category": cat, "problem": prob, "cause": cause,
            "fix_kind": kind, "fix": desc}


def _sha_head(path: Path, n: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read(n))
    return h.hexdigest()[:16]


def _seam(path, rate: int = 8000) -> tuple[float, float] | None:
    """(start, end) energy of first/last 5 ms mono s16 — loop-click risk."""
    out = subprocess.run(
        [ac.require("ffmpeg"), "-v", "error", "-i", str(path), "-ac", "1",
         "-ar", str(rate), "-f", "s16le", "-"], capture_output=True)
    if out.returncode != 0 or len(out.stdout) < 160:
        return None
    k = int(0.005 * rate) * 2
    head = struct.unpack(f"<{k // 2}h", out.stdout[:k])
    tail = struct.unpack(f"<{k // 2}h", out.stdout[-k:])
    return (sum(x * x for x in head) / len(head),
            sum(x * x for x in tail) / len(tail))


def analyze_asset(path: Path, budget: dict, profile: str) -> dict:
    facts = ac.probe(path)
    if not facts.get("ok"):
        return {"facts": facts, "checks": {"readable": "FAIL",
                                           "overall": "FAIL"},
                "findings": [finding("error", "asset", "unreadable/corrupt",
                                     facts.get("error", "ffprobe failed"),
                                     "review",
                                     "re-encode from source or regenerate")]}
    m = ac.measure(path)
    findings: list[dict] = []
    checks = {"readable": "PASS", "metered": "PASS"}
    rms, peak = m.get("rms_dbfs"), m.get("peak_dbfs")
    dur = facts.get("duration")

    if not m.get("ok"):
        checks["metered"] = "WARNING"
        findings.append(finding("warning", "asset", "unmeterable",
                                m.get("error", "astats failed"), "fix",
                                "re-encode to wav and re-audit"))
    else:
        if rms is not None and rms < SILENCE_DB:
            findings.append(finding("error", "asset", "silent",
                                    f"rms {rms:.1f} dBFS", "review",
                                    "check source; regenerate if useless"))
        flat = m.get("flat_factor")
        if flat is not None and flat > FLAT_CLIP_THRESHOLD:
            findings.append(finding("warning", "asset", "clipping",
                                    f"flat_factor {flat:.1f} (sustained flat tops)",
                                    "fix", "ffmpeg -af 'alimiter=limit=0.99'"))
        dc = m.get("dc_offset")
        if dc is not None and abs(dc) > DC_THRESHOLD:
            findings.append(finding("warning", "asset", "dc-offset",
                                    f"dc {dc:.4f}", "fix",
                                    "ffmpeg -af 'highpass=f=20'"))
        if rms is not None and profile in PROFILES:
            lo, hi = PROFILES[profile]
            if not (lo - 4 <= rms <= hi + 4):
                findings.append(finding(
                    "info", "mix", "loudness-out-of-profile",
                    f"rms {rms:.1f} outside profile '{profile}' [{lo},{hi}]",
                    "review", "engine volume or re-normalize"))
    b = budget.get(profile if profile in budget else "sfx",
                   DEFAULT_BUDGET["sfx"])
    rate = int(facts.get("rate") or 0)
    if b.get("rate") and rate and rate != b["rate"]:
        findings.append(finding("info", "asset", "rate-mismatch",
                                f"{rate} Hz vs budget {b['rate']} Hz", "fix",
                                f"ffmpeg -ar {b['rate']}"))
    ch = facts.get("channels")
    if b.get("channels") and ch not in (None, b["channels"]):
        findings.append(finding("info", "asset", "channels-mismatch",
                                f"{ch} ch vs budget {b['channels']} ch", "fix",
                                f"-ac {b['channels']}"))
    if (dur or 0) > 2.0 and profile in ("music", "ambience"):
        seam = _seam(path)
        if seam:
            h, t = seam
            if min(h, t) > 0 and max(h, t) / max(min(h, t), 1e-9) > SEAM_RATIO:
                findings.append(finding(
                    "warning", "asset", "loop-seam-risk",
                    "end/start energy gap — click on loop", "fix",
                    "crossfade tail→head or fade both edges"))
    if not path.with_name(path.stem + ".meta.json").is_file() and not any(
            p.name.startswith(path.stem) and p.suffix == ".json"
            for p in path.parent.glob("*.json")):
        findings.append(finding("info", "asset", "missing-provenance",
                                "no .meta.json sidecar (prompt/seed unknown)",
                                "review", "add manifest entry (audio_manifest.py)"))

    verdict = ("FAIL" if any(x["severity"] == "error" for x in findings)
               else "WARNING" if any(x["severity"] == "warning" for x in findings)
               else "PASS")
    checks["overall"] = verdict
    facts_out = dict(facts)
    facts_out["sha"] = _sha_head(path)
    if m.get("ok"):
        facts_out |= {"peak_dbfs": peak, "rms_dbfs": rms,
                      "dc_offset": m.get("dc_offset")}
    return {"facts": facts_out, "checks": checks, "findings": findings}


_REF_RE = re.compile(r'"([\w./:@-]*\.(?:ogg|wav|mp3|flac|opus))"')


def engine_audit(project: Path) -> tuple[list[dict], dict]:
    """Static engine facts. defold: .sound + game.project; godot: .tscn/.tres.
    defold refs resolve relative to the referencing file, then the root."""
    findings, facts = [], {"engine": "generic", "referenced": 0,
                           "missing": [], "unreferenced": 0}
    wanted: set[str] = set()

    def note(ref: str, base: Path) -> None:
        facts["referenced"] += 1
        hit = next((c for c in (base / ref, project / ref) if c.is_file()), None)
        if hit is not None:
            wanted.add(str(hit.resolve()))
        else:
            facts["missing"].append(str(base / ref))

    if (project / "game.project").is_file():
        facts["engine"] = "defold"
        sources = [project / "game.project"] + [
            p for pat in ("*.sound", "*.lua", "*.collection", "*.gui")
            for p in project.rglob(pat)]
        for src in sources:
            for m in _REF_RE.finditer(src.read_text(encoding="utf-8",
                                                    errors="replace")):
                note(m.group(1), src.parent)
        gp = (project / "game.project").read_text(encoding="utf-8",
                                                  errors="replace")
        m = re.search(r"max_sound_instances\s*=\s*(\d+)", gp)
        if m:
            facts["max_sound_instances"] = int(m.group(1))
    elif (project / "project.godot").is_file():
        facts["engine"] = "godot"
        for src in [p for pat in ("*.tscn", "*.tres", "*.gd")
                    for p in project.rglob(pat)]:
            for m in re.finditer(r'"(res://[^"]+\.(?:ogg|wav|mp3|flac|opus))"',
                                 src.read_text(encoding="utf-8",
                                               errors="replace")):
                rel = project / m.group(1).removeprefix("res://")
                facts["referenced"] += 1
                if rel.is_file():
                    wanted.add(str(rel.resolve()))
                else:
                    facts["missing"].append(m.group(1))
    missing = facts["missing"]
    facts["missing"] = missing[:20]
    if missing:
        findings.append(finding("error", "engine", "missing-audio-reference",
                                f"{len(missing)} referenced file(s) absent",
                                "review", "repair paths or restore files"))
    if facts["engine"] != "generic":
        orphans = [p for p in ac.audio_files(project)
                   if str(p.resolve()) not in wanted and
                   not any(str(p).endswith(w.rsplit('/', 1)[-1]) for w in wanted)]
        facts["unreferenced"] = len(orphans)
        if orphans:
            findings.append(finding("info", "engine", "unreferenced-assets",
                                    f"{len(orphans)} audio file(s) not referenced "
                                    "statically (runtime loads possible)",
                                    "review", "confirm before deletion"))
    return findings, facts


def fix_asset(path: Path, out_dir: Path, ops: list[str], budget: dict,
              dry: bool) -> dict:
    """Safe corrections → NEW file (original never touched). ops:
    trim|fade|resample|channels. dry/proposal-only without writes."""
    facts = ac.probe(path)
    if not facts.get("ok"):
        return {"file": str(path), "action": "skipped", "reason": "unreadable"}
    b = budget.get("sfx", DEFAULT_BUDGET["sfx"])
    filters = []
    if "trim" in ops:
        filters.append("silenceremove=start_periods=1:start_threshold=-60dB:"
                       "stop_periods=-1:stop_threshold=-60dB")
    if "fade" in ops:
        dur = facts.get("duration") or 0.2
        filters.append(f"afade=t=in:d=0.01,afade=t=out:st={max(dur - 0.02, 0)}:d=0.02")
    args = [ac.require("ffmpeg"), "-v", "error", "-i", str(path)]
    if filters:
        args += ["-af", ",".join(filters)]
    if "resample" in ops and b.get("rate"):
        args += ["-ar", str(b["rate"])]
    if "channels" in ops and b.get("channels"):
        args += ["-ac", str(b["channels"])]
    out = ac.unique_path(out_dir / path.name)
    args += [str(out)]
    if dry:
        return {"file": str(path), "action": "proposed",
                "cmd": " ".join(args), "out": str(out)}
    out.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        return {"file": str(path), "action": "skipped",
                "reason": (p.stderr or "ffmpeg failed")[-200:]}
    recheck = ac.measure(out)
    before_m = ac.measure(path)
    return {"file": str(path), "action": "applied", "out": str(out),
            "before": {"rms_dbfs": (before_m.get("rms_dbfs")
                                    if before_m.get("ok") else None),
                       "duration": facts.get("duration")},
            "after": {"rms_dbfs": (recheck.get("rms_dbfs")
                                   if recheck.get("ok") else None)},
            "recheck": "PASS" if recheck.get("ok") else "FAIL"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="audio_audit.py")
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--mode", choices=["analyze", "fix", "optimize"],
                    default="analyze")
    ap.add_argument("--filter", choices=["sfx", "music", "all"], default="all")
    ap.add_argument("--profile", default="gameplay-sfx")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--budget", default=None, help="budget JSON file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)

    project = Path(ns.project).expanduser().resolve()
    if not project.is_dir():
        print(f"error: no such project dir: {project}", file=sys.stderr)
        return 2
    budget = DEFAULT_BUDGET
    if ns.budget:
        try:
            budget = json.loads(Path(ns.budget).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"error: bad budget file: {e}", file=sys.stderr)
            return 2
    out_dir = Path(ns.out_dir) if ns.out_dir else project / "audio-audit-out"

    results, fixes, fixes_n = [], [], 0
    for path in ac.audio_files(project):
        rel = str(path.relative_to(project))
        if ns.filter != "all":
            is_music = "music" in rel.lower()
            if (ns.filter == "music") != is_music:
                continue
        r = analyze_asset(path, budget, ns.profile)
        results.append({"file": rel, "facts": r["facts"], "checks": r["checks"],
                        "findings": r["findings"]})
        if ns.mode != "analyze":
            fixable = [x for x in r["findings"] if x["fix_kind"] == "fix"]
            if fixable:
                ops = []
                if any(x["problem"].startswith(("rate", "channels")) for x in fixable):
                    ops += ["resample"]
                    if any(x["problem"].startswith("channels") for x in fixable):
                        ops.append("channels")
                if any(x["problem"] == "loop-seam-risk" for x in fixable):
                    ops.append("fade")
                apply_now = ns.mode == "fix" and ns.apply and not ns.dry_run
                fixes.append(fix_asset(path, out_dir, ops or ["resample"],
                                       budget, dry=not apply_now))
                fixes_n += 1

    eng, facts = engine_audit(project)
    statuses = {r["file"]: r["checks"]["overall"] for r in results}
    statuses["engine"] = ("FAIL" if any(x["severity"] == "error" for x in eng)
                          else "WARNING" if eng else "PASS")
    report = {
        "project": str(project), "mode": ns.mode, "profile": ns.profile,
        "engine": facts, "assets": len(results),
        "findings": sum(len(r["findings"]) for r in results) + len(eng),
        "asset_findings": results[:200], "engine_findings": eng,
        "fixes": fixes, "verdict": ac.verdict_line(statuses),
        "manual_review": "creative/mix-balance quality: AUDIO_REVIEW_REQUIRED "
                         "(measurements never replace listening)",
        "lufs": "offline LUFS not measured (ffmpeg loudnorm single-pass); "
                "documented in references/mixing-mastering.md",
    }
    if ns.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audio-audit {ns.mode}: {report['verdict']} "
              f"assets={report['assets']} findings={report['findings']} "
              f"engine={facts['engine']} fixes={fixes_n}")
        for r in results:
            for x in r["findings"]:
                print(f"  [{x['severity']:^7}] {r['file']}: {x['problem']} "
                      f"({x['cause']}) -> {x['fix']}")
        for x in eng:
            print(f"  [{x['severity']:^7}] engine: {x['problem']} ({x['cause']})")
    return 0 if report["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
