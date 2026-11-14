#!/usr/bin/env python3
"""
compare_baseline.py — before/after metric delta from two metrics JSON files.

Input: two JSON files written by collect_metrics.py (same project, pre/post
refactoring). Output: markdown delta table with only MEASURED values; anything
not present in both inputs is N/A. Never invents a delta, never scores.

Usage:
    python3 compare_baseline.py BEFORE.json AFTER.json [--format md|json]

Exit codes: 0 ok | 1 bad args/files | 2 unreadable JSON.
"""
import argparse
import json
import sys
from pathlib import Path

METRICS = [  # (label, key-path, better)
    ("files measured", ("files_measured",), "neutral"),
    ("avg complexity proxy", ("totals", "avg_complexity_proxy"), "lower"),
    ("total branch points", ("totals", "branch_points"), "lower"),
    ("debt markers (TODO/FIXME)", ("totals", "debt_markers"), "lower"),
    ("code lines", ("totals", "code_lines"), "neutral"),
    ("comment lines", ("totals", "comment_lines"), "neutral"),
]


def load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read {p}: {exc}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON {p}: {exc}", file=sys.stderr)
        sys.exit(2)


def get(doc, path):
    cur = doc
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur if isinstance(cur, (int, float)) and not isinstance(cur, bool) else None


def hotspots(doc):
    return {h["file"]: h for h in doc.get("hotspots", []) if "file" in h}


def main() -> int:
    ap = argparse.ArgumentParser(description="before/after metrics delta")
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    b, af = load(a.before), load(a.after)

    rows = []
    for label, path, better in METRICS:
        vb, va = get(b, path), get(af, path)
        if vb is None or va is None:
            delta = "N/A"
        else:
            d = va - vb
            trend = ("->" if d == 0 else "down" if d < 0 else "up")
            good = better == "neutral" or (d <= 0) == (better == "lower")
            delta = f"{d:+g} ({trend})" + ("" if good or d == 0 else " REGRESSION")
        rows.append((label, vb, va, delta))

    hb, ha = hotspots(b), hotspots(af)
    resolved = sorted(set(hb) - set(ha))
    added = sorted(set(ha) - set(hb))

    if a.format == "json":
        print(json.dumps({"rows": [
            {"metric": m, "before": vb, "after": va, "delta": d}
            for m, vb, va, d in rows],
            "hotspots_resolved": resolved, "hotspots_added": added,
            "note": "measured values only; N/A = no measurement base"},
            indent=2))
        return 0
    out = ["# Before / After", "",
           "| Metric | Before | After | Delta |",
           "|---|---|---|---|"]
    out += [f"| {m} | {vb if vb is not None else 'N/A'} "
            f"| {va if va is not None else 'N/A'} | {d} |"
            for m, vb, va, d in rows]
    out += ["", f"Hotspots resolved ({len(resolved)}): "
            + (", ".join(f"`{f}`" for f in resolved[:20]) or "none"),
            f"Hotspots added ({len(added)}): "
            + (", ".join(f"`{f}`" for f in added[:20]) or "none"),
            "", "Only measured values appear; unmeasured metrics are N/A."]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
