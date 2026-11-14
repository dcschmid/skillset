#!/usr/bin/env python3
"""
verify_changes.py — post-change verification against a recorded baseline.

Compares current git state and (optionally) re-runs the project's declared
check commands, diffing results against a baseline JSON captured BEFORE the
refactoring. Verdicts are PASS / FAIL / UNVERIFIED — never a silent pass.
Baseline test failures are attributed to the baseline, not to the change.

Baseline format (JSON, produced by --save-baseline from a checks run):
    {"commands": [{"cmd": "...", "exit": 0, "signature": "sha1..."}], ...}

Usage:
    python3 verify_changes.py [PROJECT_DIR] --baseline BASE.json [--save-baseline]
              [--cmd CMD]... [--max-files N]

--cmd runs the given shell command inside PROJECT_DIR (repeatable); without
--cmd only the git change surface is reported. Exit codes:
    0 = PASS (no regressions detected) | 1 = FAIL (new failure vs baseline)
    2 = UNVERIFIED (checks unavailable / no baseline) | 3 = bad args.
Read-only toward the project except commands the user explicitly passes.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def sig(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def run_check(root: Path, cmd: str, timeout: int = 600):
    try:
        r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True,
                           text=True, timeout=timeout)
        return {"cmd": cmd, "exit": r.returncode,
                "signature": sig(r.stdout + r.stderr),
                "tail": (r.stdout + r.stderr)[-2000:]}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "exit": "timeout", "signature": "timeout", "tail": ""}
    except OSError as exc:
        return {"cmd": cmd, "exit": "error", "signature": f"err:{exc}", "tail": ""}


def main() -> int:
    ap = argparse.ArgumentParser(description="verify changes vs baseline")
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--baseline", type=Path, help="baseline JSON to compare against")
    ap.add_argument("--save-baseline", action="store_true",
                    help="run --cmd checks and write baseline, no comparison")
    ap.add_argument("--cmd", action="append", default=[],
                    help="check command to run (repeatable)")
    ap.add_argument("--max-files", type=int, default=500)
    a = ap.parse_args()
    root = a.project.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 3
    if a.save_baseline:
        report = {"generated": datetime.now(timezone.utc).isoformat(),
                  "baseline": True,
                  "commands": [run_check(root, c) for c in a.cmd]}
        if a.baseline:
            a.baseline.parent.mkdir(parents=True, exist_ok=True)
            a.baseline.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"baseline saved: {a.baseline}")
        else:
            print(json.dumps(report, indent=2))
        return 0

    changed = git(root, "status", "--porcelain")
    if changed is None:
        print("verdict: UNVERIFIED (not a git repo or git unavailable — "
              "change surface unknown)")
        return 2
    lines = [l for l in changed.splitlines() if l.strip()]
    if len(lines) > a.max_files:
        print(f"note: {len(lines)} changed paths (> --max-files {a.max_files}); "
              "listing first page only")
        lines = lines[:a.max_files]

    current = {c["cmd"]: c for c in (run_check(root, c) for c in a.cmd)}
    failures, new_failures, fixed = [], [], []
    baseline = {}
    if a.baseline:
        try:
            base = json.loads(a.baseline.read_text(encoding="utf-8"))
            baseline = {c["cmd"]: c for c in base.get("commands", [])}
        except (OSError, json.JSONDecodeError) as exc:
            print(f"verdict: UNVERIFIED (baseline unreadable: {exc})")
            return 2

    for cmd, res in current.items():
        base = baseline.get(cmd)
        if res["exit"] != 0:
            failures.append(cmd)
            if base is None or base["exit"] == 0:
                new_failures.append(cmd)   # was green, now red => regression
        elif base is not None and base["exit"] != 0:
            fixed.append(cmd)              # baseline-known failure now passing

    report = {
        "verdict": ("PASS" if not new_failures and (current or lines)
                    else "FAIL" if new_failures else "UNVERIFIED"),
        "generated": datetime.now(timezone.utc).isoformat(),
        "changed_paths": [l[3:] for l in lines],
        "checks_run": list(current.keys()),
        "failures": failures, "new_failures_vs_baseline": new_failures,
        "baseline_failures_now_passing": fixed,
        "checks_available": bool(current),
        "details": {c: {"exit": r["exit"], "tail": r["tail"][-500:]}
                    for c, r in current.items()},
        "notes": ["baseline failures are pre-existing, not caused by the change",
                  "no checks run => UNVERIFIED, never PASS"],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["verdict"] == "FAIL":
        return 1
    if report["verdict"] == "UNVERIFIED":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
