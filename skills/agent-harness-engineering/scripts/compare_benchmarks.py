#!/usr/bin/env python3
"""compare_benchmarks.py — before/after comparison of two benchmark results.

Input: two results JSON files written by benchmark_agent.py (--out). Compares
metrics, flags regressions, verifies the modes are comparable (offline-vs-live
comparisons are reported as NOT COMPARABLE, not as improvement).

Usage:
    python3 scripts/compare_benchmarks.py before.json after.json [--format json|markdown]
Exit: 0 improved/neutral, 1 regression present, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HIGHER_IS_BETTER = {"task_completion_rate", "pass_at_1", "score"}
LOWER_IS_BETTER = {"retries_mean", "tool_calls_mean", "tool_error_rate", "loop_rate",
                   "duration_s_mean", "tokens_est_mean"}


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {p}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON {p}: {e}", file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before", help="results JSON (before)")
    ap.add_argument("after", help="results JSON (after)")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    a, b = load(args.before), load(args.after)
    ma, mb = a.get("metrics") or {}, b.get("metrics") or {}
    mode_a, mode_b = ma.get("mode"), mb.get("mode")
    comparable = mode_a == mode_b
    rows, regressions = [], 0
    for key in sorted(set(ma) & set(mb) - {"mode", "runs_per_task", "tasks", "scored",
                                           "unscored_unverified", "note"}):
        va, vb = ma.get(key), mb.get(key)
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)) or isinstance(va, bool):
            rows.append({"metric": key, "before": va, "after": vb, "delta": None, "verdict": "unavailable"})
            continue
        delta = round(vb - va, 4)
        if key in HIGHER_IS_BETTER:
            verdict = "improved" if delta > 0 else "regressed" if delta < 0 else "neutral"
        elif key in LOWER_IS_BETTER:
            verdict = "improved" if delta < 0 else "regressed" if delta > 0 else "neutral"
        else:
            verdict = "neutral"
        if verdict == "regressed" and comparable:
            regressions += 1
        rows.append({"metric": key, "before": va, "after": vb, "delta": delta, "verdict": verdict})
    report = {"before_mode": mode_a, "after_mode": mode_b, "comparable": comparable,
              "note": None if comparable else f"modes differ ({mode_a} vs {mode_b}) — delta is not an improvement claim",
              "rows": rows, "verdict": ("REGRESSION" if regressions else "PASS") if comparable else "NOT COMPARABLE"}
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"# Before/After — {args.before} → {args.after}")
        print(f"Modes: {mode_a} → {mode_b}. Verdict: **{report['verdict']}**\n")
        print("| metric | before | after | Δ | verdict |")
        print("|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['metric']} | {r['before']} | {r['after']} | {r['delta']} | {r['verdict']} |")
        if report["note"]:
            print(f"\n_{report['note']}_")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
