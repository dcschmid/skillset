#!/usr/bin/env python3
"""
run_audit.py — one-shot audit orchestrator (read-only).

Runs the skill's collectors against a project, writes ONE machine-readable
audit bundle (JSON) plus a short stdout summary, and classifies every finding
with a concrete file:line evidence pointer. Collectors it cannot run are
listed as missing capabilities, never faked.

Bundle = detection (languages/frameworks/commands) + metrics (complexity
proxies/hotspots) + duplicate candidates + available-tool inventory.

Usage:
    python3 run_audit.py [PROJECT_DIR] [-o OUT_DIR]
              [--limit N] [--window N] [--quick]

  --quick  skip duplicate scan (fast pre-merge pass)

Exit codes: 0 ok | 1 bad args/dir | 2 collector failure.
Never mutates PROJECT_DIR; writes only under OUT_DIR (default /tmp).
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = ["ast-grep", "jscpd", "rg", "eslint", "biome", "ruff", "mypy",
         "pyright", "cargo", "go", "sonar-scanner", "openrewrite", "npx"]


def run(script, project, extra):
    cmd = [sys.executable, str(HERE / script), str(project), *extra]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"collector {script} failed: {exc}"
    if r.returncode != 0:
        return None, f"collector {script} exit {r.returncode}: {r.stderr[:200]}"
    return r.stdout.strip(), None


def tool_inventory():
    return {t: shutil.which(t) or "missing" for t in TOOLS}


def main() -> int:
    ap = argparse.ArgumentParser(description="read-only audit orchestrator")
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("/tmp"))
    ap.add_argument("--limit", type=int, default=8000)
    ap.add_argument("--window", type=int, default=8)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    root = a.project.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1

    detection, err = run("detect_project.py", root, ["--limit", str(a.limit)])
    if detection is None:
        print(f"error: {err}", file=sys.stderr)
        return 2
    metrics, err = run("collect_metrics.py", root, ["--limit", str(a.limit)])
    if metrics is None:
        print(f"error: {err}", file=sys.stderr)
        return 2
    dupes = None
    if not a.quick:
        dupes, err = run("detect_duplicates.py", root,
                         ["--window", str(a.window), "--limit", str(a.limit)])
        if dupes is None:
            print(f"note: duplicates skipped: {err}", file=sys.stderr)

    bundle = {
        "kind": "quality-audit-bundle", "version": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": str(root), "read_only": True,
        "detection": json.loads(detection),
        "metrics": json.loads(metrics),
        "duplicates": json.loads(dupes) if dupes else {"status": "skipped"},
        "external_tools": tool_inventory(),
        "collector_failures": "none" if not a.quick else ["duplicates (quick)"],
        "reading_rules": [
            "complexity values are proxies, cite file:line when reporting",
            "duplicate groups are candidates; merging requires change-coupling",
            "audit mode: report only, change nothing",
        ],
    }
    try:
        a.out.mkdir(parents=True, exist_ok=True)
        out_file = a.out / "quality-audit.json"
        n = 1
        while out_file.exists():   # non-destructive: dated/numbered collision
            out_file = a.out / f"quality-audit-{n}.json"
            n += 1
        out_file.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot write bundle: {exc}", file=sys.stderr)
        return 2

    d, m = bundle["detection"], bundle["metrics"]
    langs = ", ".join(f"{k}:{v}" for k, v in list(d["languages"].items())[:6])
    print(f"audit: {root}")
    print(f"languages: {langs or 'unknown'}")
    print(f"frameworks: {', '.join(d['frameworks']) or 'none-detected'}")
    print(f"monorepo: {d['monorepo']['detected']} ({d['monorepo']['kind']})")
    print(f"files measured: {m['files_measured']} | hotspots: {len(m['hotspots'])}")
    if bundle["duplicates"] != "skipped":
        print(f"clone groups: {bundle['duplicates'].get('clone_group_count', 0)}")
    print(f"missing collectors/tools listed in bundle; no results were simulated")
    print(f"bundle: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
