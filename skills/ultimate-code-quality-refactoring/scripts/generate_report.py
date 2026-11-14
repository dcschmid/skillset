#!/usr/bin/env python3
"""
generate_report.py — render an audit bundle JSON into a Markdown report.

Input: quality-audit.json from run_audit.py (and optionally a verification
report from verify_changes.py and a delta from compare_baseline.py). Output:
structured Markdown with the sections an engineer acts on. Every number is
traceable to a bundle field; unavailable data renders as N/A or
NOT MEASURED — never a fabricated score.

Usage:
    python3 generate_report.py AUDIT.json [-o OUT.md]
              [--verify VERIFY.json] [--delta DELTA.md]

Exit codes: 0 ok | 1 bad args | 2 unreadable input.
"""
import argparse
import json
import sys
from pathlib import Path


def load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {p}: {exc}", file=sys.stderr)
        sys.exit(2)


def section(title):
    return [f"## {title}", ""]


def fmt(v):
    return "N/A" if v is None else str(v)


def main() -> int:
    ap = argparse.ArgumentParser(description="render audit report (read-only inputs)")
    ap.add_argument("audit", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--verify", type=Path, help="verify_changes.py JSON")
    ap.add_argument("--delta", type=Path, help="compare_baseline.py markdown")
    a = ap.parse_args()
    if not a.audit.is_file():
        print(f"error: not a file: {a.audit}", file=sys.stderr)
        return 1
    b = load(a.audit)
    d, m = b.get("detection", {}), b.get("metrics", {})
    dupes = b.get("duplicates", {})
    out = [f"# Quality Audit — `{b.get('project', 'unknown')}`",
           f"_Generated {fmt(b.get('generated'))} · read-only audit · "
           f"complexity values are proxies_", ""]

    out += section("1. Executive Summary")
    langs = ", ".join(f"{k} ({v} files)" for k, v in
                      list(d.get("languages", {}).items())[:8]) or "unknown"
    t = m.get("totals", {})
    out += [f"- Languages: **{langs}**",
            f"- Frameworks detected: {', '.join(d.get('frameworks', [])) or 'none'}",
            f"- Monorepo: {d.get('monorepo', {}).get('detected', 'unknown')} "
            f"({d.get('monorepo', {}).get('kind', 'unknown')})",
            f"- Files measured: {fmt(m.get('files_measured'))} "
            f"(skipped: {fmt(m.get('files_skipped'))})",
            f"- Complexity hotspots: {len(m.get('hotspots', []))}",
            f"- Clone candidate groups: "
            f"{fmt(dupes.get('clone_group_count') if isinstance(dupes, dict) else 'skipped')}",
            ""]

    out += section("2. Complexity Hotspots (measured proxies)")
    out += ["| File | Lines | Nesting | CC-proxy | Long>50 | Debt |", "|---|---|---|---|---|---|"]
    for h in m.get("hotspots", [])[:20]:
        out.append(f"| `{h.get('file')}:{h.get('language', '?')}` | {h.get('lines')} "
                   f"| {h.get('max_nesting_depth')} | {h.get('complexity_proxy')} "
                   f"| {h.get('long_functions_over_50')} | {h.get('debt_markers')} |")
    if not m.get("hotspots"):
        out.append("| (none above threshold) | | | | | |")
    out.append("")

    out += section("3. Duplicate Candidates")
    if isinstance(dupes, dict) and dupes.get("groups"):
        for g in dupes["groups"][:15]:
            sites = " · ".join(f"`{s['file']}:{s['start_line']}`"
                               for s in g["sites"][:5])
            kind = "cross-file" if g["cross_file"] else "intra-file"
            out.append(f"- [{kind}] {sites}")
        out.append("")
        out.append("_Candidates: merge only when the sites change together._")
    else:
        out.append("No groups or scan skipped — see bundle `duplicates.status`.")
    out.append("")

    out += section("4. Verification Status")
    if a.verify:
        v = load(a.verify)
        out += [f"- Verdict: **{fmt(v.get('verdict'))}**",
                f"- Checks run: {', '.join(v.get('checks_run', [])) or 'none'}",
                f"- New failures vs baseline: "
                f"{len(v.get('new_failures_vs_baseline', []))}",
                f"- Baseline (pre-existing) failures now passing: "
                f"{len(v.get('baseline_failures_now_passing', []))}"]
    else:
        out.append("NOT VERIFIED — no verification report supplied. "
                   "Run project checks per references/testing-strategy.md.")
    out.append("")

    if a.delta:
        out += section("5. Before / After")
        try:
            out += a.delta.read_text(encoding="utf-8").splitlines()
        except OSError:
            out.append("delta unreadable")
        out.append("")

    out += section("Gates & Caveats")
    out += [f"- Method: {fmt(m.get('method'))}"]
    for c in m.get("metric_caveats", []):
        out.append(f"- {c}")
    missing = [t for t, p in (b.get("external_tools") or {}).items() if p == "missing"]
    out += [f"- External tools missing (documented, not faked): "
            f"{', '.join(missing) or 'none'}",
            "- Quality gate: no new check failures vs baseline; no unmeasured "
            "value presented as measured."]
    text = "\n".join(out) + "\n"
    if a.out:
        try:
            a.out.parent.mkdir(parents=True, exist_ok=True)
            n, target = 1, a.out
            while target.exists():
                target = a.out.with_name(f"{a.out.stem}-{n}{a.out.suffix}")
                n += 1
            target.write_text(text, encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {target}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
