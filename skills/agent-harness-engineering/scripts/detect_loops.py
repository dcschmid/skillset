#!/usr/bin/env python3
"""detect_loops.py — deterministic loop/anti-pattern detection over agent traces.

Input: JSON trace — a list of steps, {"steps": [...]}, or {"trace": [...]}.
Each step: {kind|type, tool|name, arguments|args|input, ok|success|status}.
Detects: identical-call repeats, delegation ping-pong, retry storms,
windowed no-progress cycles. Empty/unknown traces report honestly — never a
fabricated verdict of health.

Usage:
    python3 scripts/detect_loops.py trace.json [--window 8] [--min-repeats 3] [--format json|markdown]
Exit: 0 no loops, 1 loops found, 2 input/usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import detect_loops, parse_trace  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trace", help="JSON trace file")
    ap.add_argument("--window", type=int, default=8, help="no-progress block width (default 8)")
    ap.add_argument("--min-repeats", type=int, default=3, help="repetitions to call a loop (default 3)")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    if args.window < 2 or args.min_repeats < 2:
        print("error: --window and --min-repeats must be >= 2", file=sys.stderr)
        return 2
    try:
        raw = json.loads(Path(args.trace).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.trace}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {args.trace}: {e}", file=sys.stderr)
        return 2
    steps = parse_trace(raw)
    if not steps:
        print("trace contained no usable steps — verdict: UNKNOWN (not 'healthy')", file=sys.stderr)
        report = {"trace": str(args.trace), "steps": 0, "loops": [], "verdict": "UNKNOWN"}
        print(json.dumps(report, indent=2) if args.format == "json" else "# Loop detection\n0 steps. UNKNOWN.")
        return 2
    loops = detect_loops(steps, window=args.window, min_repeats=args.min_repeats)
    report = {"trace": str(args.trace), "steps": len(steps), "loops": loops,
              "verdict": "LOOPS_DETECTED" if loops else "PASS"}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"# Loop detection — {args.trace}\n{len(steps)} steps. Verdict: **{report['verdict']}**\n")
        for l in loops:
            print(f"- {l}")
    return 1 if loops else 0


if __name__ == "__main__":
    sys.exit(main())
