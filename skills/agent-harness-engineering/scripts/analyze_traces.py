#!/usr/bin/env python3
"""analyze_traces.py — structured trace diagnosis: timeline, tool-call stats, error history.

Input: JSON trace (list, {"steps": [...]}, or {"trace": [...]}). Produces an
agent-step/tool-call timeline, per-tool counts, error history with retry
runs, and redaction of secret-looking literals in the printed evidence.
Observability concepts follow OpenTelemetry vocabulary (span ~ step, trace id
passthrough) without requiring an OTel runtime.

Usage:
    python3 scripts/analyze_traces.py trace.json [--format json|markdown]
Exit: 0 analyzed, 2 unusable input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import detect_loops, parse_trace  # noqa: E402

SECRET_PAT = re.compile(r"([A-Za-z0-9_\-\.]{16,})(?=[\"'\s,}]|$)")


def redact(text):
    """Strip long opaque literals that follow secret-looking keys (best effort)."""
    out = []
    for chunk in re.split(r"([A-Za-z0-9_\-\.]{20,})", str(text)):
        out.append("***REDACTED***" if len(chunk) >= 20 and re.fullmatch(r"[A-Za-z0-9_\-\.]+", chunk) else chunk)
    return "".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trace", help="JSON trace file")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    try:
        raw = json.loads(Path(args.trace).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.trace}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    steps = parse_trace(raw)
    if not steps:
        print("trace has no usable steps — no diagnosis fabricated", file=sys.stderr)
        return 2
    per_tool, errors, timeline = {}, [], []
    for s in steps:
        per_tool[s.name or s.kind] = per_tool.get(s.name or s.kind, 0) + 1
        if not s.ok:
            errors.append({"index": s.index, "step": redact(s.name or s.kind),
                           "args_digest": redact(s.args_key[:80])})
        timeline.append({"i": s.index, "kind": s.kind, "step": redact((s.name or s.kind)[:60]),
                         "ok": s.ok})
    loops = detect_loops(steps)
    report = {"trace": str(args.trace), "steps": len(steps), "per_tool": per_tool,
              "error_history": errors, "loops": loops,
              "redaction": "secret-looking literals masked in output",
              "timeline": timeline[:200]}
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"# Trace diagnosis — {args.trace}\n{len(steps)} steps, {len(errors)} failed, {len(loops)} loop findings\n")
        print("| tool/kind | calls |")
        print("|---|---|")
        for k, v in sorted(per_tool.items(), key=lambda x: -x[1]):
            print(f"| {k} | {v} |")
        if errors:
            print("\nError history:")
            for e in errors[:20]:
                print(f"- step {e['index']}: {e['step']} args={e['args_digest']}")
        for l in loops:
            print(f"- loop: {l}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
