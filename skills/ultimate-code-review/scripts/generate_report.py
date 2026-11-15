#!/usr/bin/env python3
"""generate_report.py — render a validated findings bundle as Markdown/JSON.

generate_report.py VALIDATED.json [--scope scope.json] [--context ctx.json]
                       [--format md|json|both] [-o DIR] [--title T]

Reads only what validate_findings.py emitted (verdict VALID/PARTIAL) plus the
optional scope/context JSONs from git_review.py / collect_context.py.
Never invents content: absent data renders as "not checked" / N/A.
Standards and Spec stay SEPARATE sections; no cross-axis score is computed.
Writes code-review.md / code-review.json (into -o DIR when given).
Exit 0 rendered; 1 bad input; 2 usage.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AXIS_TITLES = {
    "standards": "Standards Review", "spec": "Specification Review",
    "bugs": "Bugs & Regression Risks", "security": "Security Review",
    "testing": "Testing & Verification", "performance": "Performance & Architecture",
}
SEV_ORDER = ["critical", "high", "medium", "low", "info"]


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8")) if p else None
    except (OSError, json.JSONDecodeError):
        return None


def render_md(rep, scope, ctx, title):
    L = [f"# {title}", "",
         f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} · "
         f"verdict {rep.get('verdict','?')}_", ""]
    L += ["## Review Context"]
    if scope:
        L += [f"- Repository: `{scope.get('repo','?')}`",
              f"- Branch: `{(ctx or {}).get('branch','?')}`",
              f"- Mode: `{scope.get('mode','?')}` · status `{scope.get('status','?')}`",
              f"- Base: `{scope.get('base') or '-'}` @ "
              f"`{(scope.get('base_sha') or '-')[:12]}`",
              f"- Target: `{scope.get('target') or '-'}` @ "
              f"`{(scope.get('target_sha') or '-')[:12]}`",
              f"- Merge-base: `{(scope.get('merge_base_sha') or '-')[:12]}`",
              f"- Diff command: `{scope.get('diff_command','-')}`",
              f"- Files reviewed: {len(scope.get('files', []))}",
              f"- Untracked: {', '.join(scope.get('untracked_files', [])) or '-'}",
              f"- Excluded: {', '.join(scope.get('excluded_patterns', [])[:6])} …"]
    else:
        L += ["- scope bundle not provided"]
    if ctx:
        specs = ctx.get("spec_candidates") or []
        L += [f"- Spec status: `{ctx.get('spec_status','?')}`"
              + (f" ({', '.join(specs[:3])})" if specs else ""),
              f"- Standards sources: {', '.join(ctx.get('standards_sources', [])[:5]) or '-'}",
              f"- Stack: {', '.join(ctx.get('languages', [])) or 'unclear'}"]
    open_f = [f for f in rep.get("findings", []) if f.get("status") == "open"]
    L += ["", "## Executive Summary",
          f"- Open findings: {rep.get('open', len(open_f))}",
          " · ".join(f"{s.upper()}: {rep.get('by_severity', {}).get(s, 0)}"
                     for s in SEV_ORDER),
          ""]
    g = rep.get("gate")
    if g:
        L += [f"**Gate {g.get('level')}: "
              f"{'PASS' if g.get('pass') else 'FAIL'}** — blocking: "
              f"{', '.join(g.get('blocking', [])) or 'none'}; "
              f"skipped axes (gaps, not passes): "
              f"{', '.join(g.get('skipped_axes', [])) or 'none'}", ""]
    for axis in ("standards", "spec", "bugs", "security", "testing",
                 "performance"):
        L += [f"## {AXIS_TITLES[axis]}", ""]
        axis_f = [f for f in open_f if f.get("axis") == axis]
        if rep.get("skipped_axes") and axis in rep["skipped_axes"]:
            L += ["SKIPPED — documented gap, not a pass.", ""]
            continue
        if not axis_f:
            L += ["No open findings on this axis (checked scope only).", ""]
            continue
        for f in sorted(axis_f, key=lambda x: SEV_ORDER.index(x["severity"])):
            loc = f"{f['file']}" + (f":{f.get('line_start','')}"
                                    if f.get("line_start") else "")
            L += [f"### {f['id']} · {f['severity']} · {f['confidence']} — "
                  f"{f['title']}",
                  f"- Location: `{loc}`",
                  f"- Impact: {f.get('impact','—')}",
                  f"- Evidence: {f.get('evidence','—')}",
                  f"- Recommendation: {f.get('recommendation','—')}",
                  f"- Verify: {f.get('verification','—')}",
                  (f"- Also flagged by: {', '.join(f['also_flagged_by'])}"
                   if f.get("also_flagged_by") else ""), ""]
    if ctx and ctx.get("check_commands"):
        L += ["## Verification Evidence",
              "Declared project checks (run them; unrun = not asserted):"]
        L += [f"- `{c.get('cmd')}` ({c.get('tool')}/{c.get('script')}) — "
              "NOT EXECUTED by this report" for c in ctx["check_commands"][:8]]
        L += [""]
    L += ["## Limitations",
          "- Axes/axes-skipped and unexecuted checks above are coverage gaps, "
          "never passes.",
          "- Findings below `confirmed`/`strong-evidence` confidence are "
          "flagged as such; treat `suspected`/`needs-verification` as leads."]
    return "\n".join(x for x in L if x is not None) + "\n"


def main():
    ap = argparse.ArgumentParser(prog="generate_report.py")
    ap.add_argument("input")
    ap.add_argument("--scope"), ap.add_argument("--context")
    ap.add_argument("--format", choices=["md", "json", "both"], default="md")
    ap.add_argument("-o", "--out", default=".")
    ap.add_argument("--title", default="Code Review Report")
    a = ap.parse_args()
    rep = load(a.input)
    if not rep or rep.get("verdict") not in ("VALID", "PARTIAL"):
        print(json.dumps({"error": "input is not a VALID/PARTIAL findings "
                                   "bundle from validate_findings.py"}))
        sys.exit(1)
    scope, ctx = load(a.scope), load(a.context)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    wrote = []
    if a.format in ("md", "both"):
        p = out / "code-review.md"
        p.write_text(render_md(rep, scope, ctx, a.title), encoding="utf-8")
        wrote.append(str(p))
    if a.format in ("json", "both"):
        bundle = {"report": rep, "scope": scope, "context": ctx}
        p = out / "code-review.json"
        p.write_text(json.dumps(bundle, indent=1, ensure_ascii=False),
                     encoding="utf-8")
        wrote.append(str(p))
    print(json.dumps({"wrote": wrote, "open": rep.get("open")}))


if __name__ == "__main__":
    main()
