#!/usr/bin/env python3
"""validate_observations.py — check tool outputs against the observation contract.

Reads a JSON file holding one observation, a list of observations, or a
{"observations": [...]} wrapper. Checks status vocabulary, one-line summary,
and the error contract (category, cause, retryable bound, stop condition).
Existing tool protocols don't have to change — use this on adapter output.

Usage:
    python3 scripts/validate_observations.py observations.json [--format json|markdown]
Exit: 0 valid, 1 violations, 2 input/usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import audit_observation  # noqa: E402


def extract_items(data):
    if isinstance(data, dict) and isinstance(data.get("observations"), list):
        return data["observations"]
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "status" in data:
        return [data]
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="JSON file with observation object(s)")
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
    items = extract_items(data)
    if items is None:
        print("error: no observation found (expected object with 'status', list, or {observations:[...]})",
              file=sys.stderr)
        return 2
    results = []
    bad = 0
    for i, obs in enumerate(items):
        errs = audit_observation(obs)
        results.append({"index": i, "status": (obs or {}).get("status") if isinstance(obs, dict) else None,
                        "errors": errs})
        bad += bool(errs)
    report = {"file": str(args.file), "checked": len(items), "invalid": bad,
              "results": results, "verdict": "PASS" if not bad else "FAIL"}
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"# Observation validation — {args.file}")
        print(f"{len(items)} observation(s), {bad} invalid. Verdict: **{report['verdict']}**\n")
        for r in results:
            for e in r["errors"]:
                print(f"- [{r['index']}:{r['status']}] {e}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
