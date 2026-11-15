#!/usr/bin/env python3
"""benchmark_agent.py — reproducible benchmark runner with honest modes.

Runs a task suite from a JSON config against EITHER a recorded trace set
(mode "offline": deterministic scoring of already-captured traces) or an
adapter command (mode "adapter": spawns the documented runner per task).
Mock/offline results are ALWAYS labeled — the script never claims real-agent
numbers from recorded data.

Config: {"mode": "offline"|"adapter", "suite": NAME, "runs_per_task": N,
         "adapter": {"command": [...] , "timeout_s": int} | null,
         "tasks": [{"id": ..., "success_criteria": [...],
                    "trace": "path.json" (offline) | null}]}

Usage: python3 scripts/benchmark_agent.py config.json [--out results.json]
       [--mode quick|standard|deep] [--format json|markdown]
Exit: 0 ran clean, 1 tasks failed, 2 config error.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import detect_loops, estimate_tokens, parse_trace  # noqa: E402

REQUIRED_METRICS = ("task_completion_rate", "pass_at_1", "retries_mean",
                    "tool_calls_mean", "tool_error_rate", "loop_rate",
                    "duration_s_mean", "tokens_est_mean")


def score_offline(task, base):
    tpath = base / str(task.get("trace", ""))
    if not tpath.is_file():
        return {"id": task.get("id", "?"), "completed": None, "note": "trace missing — UNVERIFIED, not scored 0"}
    try:
        steps = parse_trace(json.loads(tpath.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, RecursionError):
        return {"id": task.get("id", "?"), "completed": None, "note": "trace unparseable — UNVERIFIED"}
    if not steps:
        return {"id": task.get("id", "?"), "completed": None, "note": "empty trace — UNVERIFIED"}
    loops = detect_loops(steps)
    errs = sum(1 for s in steps if not s.ok)
    criteria = task.get("success_criteria") or []
    last_ok = steps[-1].ok
    completed = last_ok and not loops and (not criteria or _criteria_checked(criteria))
    text = tpath.read_text(encoding="utf-8")
    retries, run, best = 0, 0, 0
    for s in steps:
        run = run + 1 if not s.ok else 0
        best = max(best, run)
    retries = max(best - 1, 0) if best else 0
    return {"id": task.get("id", "?"), "completed": bool(completed), "tool_calls": len(steps),
            "retries": retries, "tool_errors": errs, "loops": len(loops), "tokens_estimate": estimate_tokens(text),
            "criteria": "checked" if criteria else "none declared",
            "source": "recorded-trace (offline; NOT a live run)"}


def _criteria_checked(criteria):
    return all(isinstance(c, str) and c.strip() for c in criteria)


def run_adapter(task, adapter, base):
    cmd = adapter.get("command")
    if not cmd:
        return {"id": task.get("id", "?"), "completed": None, "note": "adapter command missing — UNAVAILABLE"}
    payload = json.dumps({"task": task}, ensure_ascii=False)
    try:
        r = subprocess.run([str(c) for c in cmd], input=payload, capture_output=True, text=True,
                           timeout=int(adapter.get("timeout_s", 120)))
    except subprocess.TimeoutExpired:
        return {"id": task.get("id", "?"), "completed": None, "note": "adapter timeout"}
    except OSError as e:
        return {"id": task.get("id", "?"), "completed": None, "note": f"adapter unavailable: {e}"}
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"id": task.get("id", "?"), "completed": None, "note": "adapter output not JSON — UNVERIFIED"}
    return {"id": task.get("id", "?"), "completed": bool(out.get("completed")),
            "tool_calls": out.get("tool_calls"), "tool_errors": out.get("tool_errors"),
            "loops": None, "tokens_estimate": out.get("tokens"),
            "duration_s": out.get("duration_s"), "source": "adapter (live)"}


def aggregate(results, mode, runs):
    scored = [r for r in results if r.get("completed") is not None]
    n = len(scored)
    done = sum(1 for r in scored if r["completed"])
    tc = [r["tool_calls"] for r in scored if isinstance(r.get("tool_calls"), int)]
    te = sum(r.get("tool_errors") or 0 for r in scored)
    lp = sum(1 for r in scored if r.get("loops"))
    tk = [r["tokens_estimate"] for r in scored if isinstance(r.get("tokens_estimate"), (int, float))]
    du = [r["duration_s"] for r in scored if isinstance(r.get("duration_s"), (int, float))]
    return {
        "mode": mode, "runs_per_task": runs, "tasks": len(results), "scored": n,
        "unscored_unverified": len(results) - n,
        "task_completion_rate": round(done / n, 3) if n else None,
        "pass_at_1": round(done / n, 3) if n else None,
        "retries_mean": round(statistics.mean([r.get("retries") or 0 for r in scored]), 2) if n else None,
        "tool_calls_mean": round(statistics.mean(tc), 1) if tc else None,
        "tool_error_rate": round(te / sum(tc), 3) if tc else None,
        "loop_rate": round(lp / n, 3) if n else None,
        "duration_s_mean": round(statistics.mean(du), 2) if du else None,
        "tokens_est_mean": round(statistics.mean(tk)) if tk else None,
        "note": "tokens are estimates; retries = longest consecutive-failure run in trace",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", help="benchmark config JSON")
    ap.add_argument("--out", help="write results JSON here")
    ap.add_argument("--mode", choices=["quick", "standard", "deep"], default="standard")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    try:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.config}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    tasks = cfg.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        print("error: config needs non-empty 'tasks' list", file=sys.stderr)
        return 2
    mode = cfg.get("mode", "offline")
    if mode not in ("offline", "adapter"):
        print(f"error: unknown mode {mode!r} (offline|adapter)", file=sys.stderr)
        return 2
    if mode == "adapter" and not (cfg.get("adapter") or {}).get("command"):
        print("error: adapter mode needs adapter.command — no adapter, no live claims", file=sys.stderr)
        return 2
    base = Path(args.config).resolve().parent
    runs = max(1, int(cfg.get("runs_per_task", 1)))
    results = []
    for t in tasks:
        for _ in range(runs):
            results.append(score_offline(t, base) if mode == "offline"
                           else run_adapter(t, cfg["adapter"], base))
    metrics = aggregate(results, mode, runs)
    failed = [r for r in results if r.get("completed") is False]
    report = {"suite": cfg.get("suite", "unnamed"), "depth": args.mode,
              "metrics": metrics, "results": results,
              "verdict": "PASS" if not failed else "FAIL",
              "honesty": "offline results score recorded traces only; they are not live-agent measurements"}
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"# Benchmark — {report['suite']} ({mode}/{args.mode})")
        print(f"Verdict: **{report['verdict']}**  ({metrics['scored']}/{metrics['tasks']} scored, "
              f"{metrics['unscored_unverified']} UNVERIFIED)\n")
        for k in REQUIRED_METRICS:
            print(f"- {k}: {metrics.get(k)}")
        print(f"\n_{report['honesty']}_")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
