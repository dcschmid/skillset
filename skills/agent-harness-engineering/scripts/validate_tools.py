#!/usr/bin/env python3
"""validate_tools.py — audit agent tool definitions against the portable contract.

Reads a JSON file holding a tool list, a single tool, or a platform wrapper
({"tools": [...]} / {"functions": [...]}). Reports per-tool contract errors
plus set-level findings (duplicates, overlap, oversized namespace).

Usage:
    python3 scripts/validate_tools.py tools.json [--format json|markdown]
Exit: 0 clean, 1 findings present, 2 input/usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import audit_tool, audit_tool_set  # noqa: E402


def extract_tools(data):
    if isinstance(data, dict):
        for key in ("tools", "functions"):
            if isinstance(data.get(key), list):
                return data[key]
        if data.get("name") or (isinstance(data.get("function"), dict)):
            return [data]
    if isinstance(data, list):
        return data
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="JSON file with tool definitions")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    try:
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {args.file}: {e}", file=sys.stderr)
        return 2
    tools = extract_tools(data)
    if tools is None:
        print("error: no tool list found (expected list, {tools:[...]}, or single tool object)", file=sys.stderr)
        return 2
    per_tool = {}
    problems = []
    for i, t in enumerate(tools):
        name = (t or {}).get("name", f"<index {i}>") if isinstance(t, dict) else f"<index {i}>"
        errs = audit_tool(t)
        if errs:
            per_tool[str(name)] = errs
            problems.extend(f"{name}: {e}" for e in errs)
    set_findings = audit_tool_set([t for t in tools if isinstance(t, dict)])
    problems.extend(set_findings)
    report = {"file": str(args.file), "tools_checked": len(tools),
              "per_tool_errors": per_tool, "set_findings": set_findings,
              "verdict": "PASS" if not problems else "FAIL"}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"# Tool validation — {args.file}")
        print(f"{len(tools)} tool(s) checked. Verdict: **{report['verdict']}**\n")
        for name, errs in per_tool.items():
            print(f"## {name}")
            for e in errs:
                print(f"- {e}")
        for f in set_findings:
            print(f"- (set) {f}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
