#!/usr/bin/env python3
"""generate_report.py — render audit/benchmark/security JSON results as Markdown.

Accepts the JSON stdout/file of audit_harness.py, benchmark_agent.py, or
security_scan.py (auto-detected) and renders a human-readable report with the
honesty notes preserved (skipped categories, estimation caveats, mode labels).

Usage:
    python3 scripts/generate_report.py result.json [--out report.md]
Exit: 0 rendered, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import findings_to_markdown  # noqa: E402


def render(data):
    if "metrics" in data:  # benchmark
        m = data["metrics"]
        lines = [f"# Benchmark report — {data.get('suite', '?')} ({m.get('mode')}/{data.get('depth')})",
                 f"Verdict: **{data.get('verdict')}**\n",
                 "| metric | value |\n|---|---|"]
        for k, v in m.items():
            if k not in ("mode", "note"):
                lines.append(f"| {k} | {v} |")
        lines.append(f"\n_{m.get('note', '')}_\n\n_{data.get('honesty', '')}_")
        return "\n".join(lines) + "\n"
    if "findings" in data and "categories" not in data:  # security_scan
        lines = [f"# Security report — {data.get('path', '?')}",
                 f"Verdict: **{data.get('verdict')}** ({data.get('files_scanned')} files)\n"]
        for x in data["findings"]:
            lines.append(f"- [{x['severity']}] `{x['file']}` :: {x['check']} — {x['evidence']} → {x['fix']}")
        return "\n".join(lines) + "\n"
    if "categories" in data:  # audit
        lines = [f"# Audit report — {data.get('project', '?')}",
                 f"**Score {data['score']}/100** — verdict **{data.get('verdict')}**, "
                 f"{data.get('files_scanned')} files scanned (skipped categories excluded from score)\n"]
        lines.append("| category | earned/max | status | note |\n|---|---|---|---|")
        for c, v in data["categories"].items():
            lines.append(f"| {c} | {v.get('earned','–')}/{v.get('max','–')} | {v['status']} | {v['note']} |")
        lines.append("\n" + findings_to_markdown(data.get("findings", []), "Findings").lstrip("# \n").removeprefix("Harness Audit\n"))
        if data.get("fix_plan"):
            lines.append("\n## Fix plan")
            for fx in data["fix_plan"]:
                lines.append(f"- {fx['file']}: {fx['change']} (risk {fx['risk']})")
        return "\n".join(lines) + "\n"
    raise ValueError("unrecognized result shape (expected audit/benchmark/security result)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("result", help="result JSON from audit_harness/benchmark_agent/security_scan")
    ap.add_argument("--out", help="write markdown here (default: stdout)")
    args = ap.parse_args(argv)
    try:
        data = json.loads(Path(args.result).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.result}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    try:
        md = render(data)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
