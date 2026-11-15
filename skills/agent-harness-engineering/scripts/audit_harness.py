#!/usr/bin/env python3
"""audit_harness.py — audit an existing agent harness in a project.

Scans a project for harness artifacts (tool definitions, agent loops, prompts,
delegation configs, traces, harness tests), runs category audits, and reports
findings + a transparent 0..100 score. Categories with no observable material
are SKIPPED — they never distort the score, never fake a pass.

Usage:
    python3 scripts/audit_harness.py --project PATH [--format markdown|json]
                                     [--fix] [--apply] [--only CAT,...]
    --fix        print the fix plan (dry-run; default, writes nothing)
    --apply      apply only deterministic LOW-risk JSON fixes (code is never rewritten)
Exit: 0 no findings, 1 findings present, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import (ScoreCard, approval_required, audit_observation,  # noqa: E402
                         audit_tool, audit_tool_set, classify_risk,
                         detect_loops, estimate_tokens, parse_trace)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".tox"}
CATEGORIES = ("architecture", "tools", "context", "reliability", "recovery",
              "security", "performance", "multi-agent", "observability", "test-coverage")
AGENT_HINT = re.compile(r"\b(agent|react|tool_call|function_call|handoff|supervisor|"
                        r"planner|executor|max_turns|max_steps|max_iterations)\b", re.I)
SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
_fnd_seq = [0]


def finding(category, severity, component, evidence, cause, impact, fix, fixable, risk):
    _fnd_seq[0] += 1
    return {"id": f"AHE-{_fnd_seq[0]:03d}", "category": category, "severity": severity,
            "component": str(component), "evidence": evidence, "cause": cause,
            "impact": impact, "fix": fix, "fixable": fixable, "risk": risk}


def walk(root: Path, limit=4000):
    files, seen = [], 0
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir())
        except OSError:
            continue
        for e in entries:
            seen += 1
            if seen > limit:
                return files
            if e.is_dir():
                if e.name not in SKIP_DIRS and not e.name.startswith("."):
                    stack.append(e)
            elif e.suffix in (".py", ".ts", ".js", ".json", ".md", ".yaml", ".yml", ".toml"):
                if e.stat().st_size < 512_000:
                    files.append(e)
    return files


def read(f: Path):
    try:
        return f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# ------------------------------------------------------------- per-category

def scan_tool_files(files):
    """JSON files that look like tool/observation payloads."""
    out = []
    for f in files:
        if f.suffix != ".json":
            continue
        raw = read(f)
        if raw is None:
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, RecursionError):
            out.append(("broken-json", f, None))
            continue
        if isinstance(data, dict) and isinstance(data.get("tools"), list):
            out.append(("tools", f, data["tools"]))
        elif isinstance(data, dict) and isinstance(data.get("functions"), list):
            out.append(("tools", f, data["functions"]))
        elif isinstance(data, dict) and "status" in data and "summary" in data:
            out.append(("observation", f, [data]))
        elif isinstance(data, list) and data and isinstance(data[0], dict) and "name" in data[0]:
            out.append(("tools", f, data))
    return out


def audit_tools_category(root, scanned, findings):
    tool_sets = [(f, t) for kind, f, t in scanned if kind == "tools" and t is not None]
    broken = [(f) for kind, f, _ in scanned if kind == "broken-json"]
    for f in broken:
        findings.append(finding("tools", "MEDIUM", f.relative_to(root), "unparseable JSON",
                                "invalid JSON", "tool loader fails or silently drops tools",
                                "repair JSON syntax", "yes", "LOW"))
    if not tool_sets:
        return None
    points = max_points = 0
    for f, tools in tool_sets:
        tools = [t for t in tools if isinstance(t, dict)]
        for t in tools:
            name = t.get("name", "<unnamed>")
            for e in audit_tool(t):
                findings.append(finding("tools", "MEDIUM", f"{f.relative_to(root)}::{name}",
                                        e, "contract violation", "unreliable tool selection/execution",
                                        f"fix: {e}", "yes" if "description" in e or "name" in e else "review",
                                        "LOW"))
            points += 1
        for e in audit_tool_set(tools):
            findings.append(finding("tools", "HIGH", f.relative_to(root), e,
                                    "set-level defect", "selection ambiguity / context bloat",
                                    f"fix: {e}", "review", "MEDIUM"))
        points += 2
        if points:
            max_points = points
        max_points = points
    return (min(points, max_points), max_points)


SECRET_PAT = re.compile(r"(?i)\b(api[_-]?key|secret|password|token|authorization)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{16,})")


def audit_code_files(root, files, findings):
    """Architecture/reliability/recovery/security evidence from agent code."""
    agent_files = []
    for f in files:
        if f.suffix not in (".py", ".ts", ".js") or "test" in f.name.lower():
            continue
        text = read(f)
        if text and AGENT_HINT.search(text):
            agent_files.append((f, text))
    if not agent_files:
        return None
    card_pts = rel_pts = rec_pts = sec_pts = cmax = rmax = recmax = secmax = 0
    for f, text in agent_files:
        rel = str(f.relative_to(root))
        has_loop = re.search(r"while\s+|for\s+.*range|recursion", text)
        bounded = re.search(r"(max_turns|max_steps|max_iterations|max_retries|range\(\s*\d+\)|timeout|while\s+\w+\s*<=?\s*\d+)", text)
        if has_loop and not bounded:
            findings.append(finding("reliability", "HIGH", rel, "agent loop without step/turn bound",
                                    "no max_turns/max_steps/timeout", "infinite planning/tool loops possible",
                                    "add explicit step budget + stop condition", "yes", "MEDIUM"))
        if has_loop:
            cmax += 1
            if bounded:
                card_pts += 1
        retries = re.findall(r"(?:for|range)\(?\s*(\d+)\s*\)?[^:]*:\s*\n\s*try", text) or \
            re.findall(r"max_retries\s*=\s*(\d+)", text)
        for m in re.finditer(r"while\s+True\s*:", text):
            if "break" not in text[m.start():m.start() + 2500]:
                findings.append(finding("recovery", "MEDIUM", rel, "while True without visible break in block",
                                        "unbounded retry", "retry storm risk",
                                        "bound iterations + stop condition", "review", "MEDIUM"))
            recmax += 1
            if "break" in text[m.start():m.start() + 2500]:
                rec_pts += 1
        if re.search(r"except[^:]*:\s*\n\s*(pass|continue)\s*$", text, re.M):
            findings.append(finding("reliability", "MEDIUM", rel, "silent exception swallow",
                                    "except: pass/continue", "silent failure — agent proceeds on garbage",
                                    "log + classify + surface status", "review", "MEDIUM"))
        rmax += 1
        if re.search(r"prompt\s*=.*f['\"].*\{[^}]*\b[A-Z_]*(API_?KEY|SECRET|TOKEN|PASSWORD)", text) \
           or re.search(r"f['\"][^'\"]*\{[^}]*\b(API_?KEY|SECRET|TOKEN|PASSWORD)", text):
            findings.append(finding("security", "HIGH", rel, "secret interpolated into prompt string",
                                    "env secret concatenated into model input",
                                    "secret exposed in every trace/context",
                                    "pass via adapter header or mask before logging", "review", "MEDIUM"))
        leaks = SECRET_PAT.findall(text)
        for k, v in leaks[:2]:
            findings.append(finding("security", "HIGH", rel, f"possible secret literal for '{k}' ({v[:8]}…)",
                                    "credential in source/prompt", "secret exposure in traces/context",
                                    "move to env/secret store; mask in logs", "yes", "MEDIUM"))
        secmax += 1
        sec_pts += 1 if not leaks else 0
        shell = re.search(r"(subprocess\.(run|call|Popen|shell)|os\.system|execSync|child_process)", text)
        if shell and not re.search(r"timeout\s*=", text):
            findings.append(finding("security", "MEDIUM", rel, "shell execution without timeout",
                                    "uncontrolled execution", "hangs / resource exhaustion",
                                    "add timeout + path allowlist", "review", "MEDIUM"))
        if rel_pts == 0 and cmax:
            rel_pts = cmax - sum(1 for x in findings if x["component"] == rel and x["category"] == "reliability")
    if recmax:
        recmax = max(recmax, 1)
    return dict(architecture=(card_pts, max(cmax, 1)), reliability=(max(rel_pts, 0), max(rmax + len(agent_files), 1)),
                recovery=(rec_pts, recmax or 1), security=(sec_pts, max(secmax + len(agent_files), 1)))


PROMPT_FILES = re.compile(r"(AGENTS\.md|CLAUDE\.md|SKILL\.md|SYSTEM.*\.md|prom?ompts?/.*\.md|\.prompt)$", re.I)


def audit_prompts_category(root, files, findings):
    prompts = [(f, read(f)) for f in files if PROMPT_FILES.search(str(f))]
    prompts = [(f, t) for f, t in prompts if t]
    if not prompts:
        return None
    pts = mx = 0
    for f, t in prompts:
        rel = str(f.relative_to(root))
        tok = estimate_tokens(t)
        mx += 2
        if tok > 4000:
            findings.append(finding("context", "MEDIUM", rel, f"prompt inlines ~{tok} estimated tokens",
                                    "no progressive disclosure", "context budget burned every invocation",
                                    "split depth into references/ loaded on demand", "review", "MEDIUM"))
        else:
            pts += 1
        if re.search(r"(ignore (all |previous )?instructions|disregard previous)", t, re.I):
            findings.append(finding("security", "MEDIUM", rel, "injection-style imperative in repo prompt file",
                                    "external content treated as instruction source",
                                    "model may obey file-embedded instructions",
                                    "wrap external content as data, not instructions", "review", "LOW"))
        else:
            pts += 1
    return (pts, mx)


def audit_traces_category(root, files, findings):
    traces = []
    for f in files:
        if f.suffix != ".json" or "trace" not in f.name.lower():
            continue
        try:
            traces.append((f, parse_trace(json.loads(read(f) or ""))))
        except (json.JSONDecodeError, RecursionError):
            continue
    traces = [(f, s) for f, s in traces if s]
    if not traces:
        return None
    pts = mx = 0
    for f, steps in traces:
        mx += 1
        loops = detect_loops(steps)
        if loops:
            findings.append(finding("reliability", "HIGH", str(f.relative_to(root)),
                                    "; ".join(loops[:3]), "loop evidence in recorded trace",
                            "wasted budget, task failure", "add progress checks + stop conditions", "review", "MEDIUM"))
        else:
            pts += 1
        if all(not getattr(s, "args_key", "") for s in steps):
            findings.append(finding("observability", "LOW", str(f.relative_to(root)),
                                    "trace steps lack arguments — call not reconstructable",
                                    "thin tracing", "debugging blind spot",
                                    "log tool name + args + correlation id", "yes", "LOW"))
    return (pts, mx or 1)


def audit_tests_category(root, files):
    tests = [f for f in files if f.suffix == ".py" and ("test" in f.name.lower() or "tests/" in str(f))]
    if not tests:
        return None
    pts = min(len(tests), 4)
    return (pts, 4)


# ------------------------------------------------------------------ engine

def run_audit(root: Path, only=None):
    findings = []
    card = ScoreCard()
    files = walk(root)
    scanned = scan_tool_files(files)
    if only:
        wanted = set(only)
    else:
        wanted = set(CATEGORIES)

    if "tools" in wanted:
        r = audit_tools_category(root, scanned, findings)
        card.add("tools", *(r or (0, 0))) if r else card.skip("tools", "no tool definitions found")
    if {"architecture", "reliability", "recovery", "security"} & wanted:
        r = audit_code_files(root, files, findings)
        if r:
            for cat in ("architecture", "reliability", "recovery", "security"):
                if cat in wanted:
                    p, m = r[cat]
                    card.add(cat, min(p, m), m)
        else:
            for cat in ("architecture", "reliability", "recovery", "security"):
                if cat in wanted:
                    card.skip(cat, "no agent code found")
    if "context" in wanted:
        r = audit_prompts_category(root, files, findings)
        card.add("context", *r) if r else card.skip("context", "no prompt/instruction files found")
    if "observability" in wanted or "reliability" in wanted:
        r = audit_traces_category(root, files, findings)
        if r:
            card.add("observability", *(r[0], r[1])) if "observability" in wanted else None
    if "test-coverage" in wanted:
        r = audit_tests_category(root, files)
        card.add("test-coverage", *r) if r else card.skip("test-coverage", "no tests found")
    if not any(f["category"] in ("performance", "multi-agent") for f in findings):
        card.skip("performance", "no runtime metrics available (needs live trace; not fabricated)")
        card.skip("multi-agent", "no delegation config observed" if not re.search(
            "supervisor|handoff|worker", " ".join(read(f) or "" for f in files[:400]), re.I)
            else "delegation present but untestable offline")
    findings.sort(key=lambda f: SEV_ORDER.get(f["severity"], 9))
    return findings, card, len(files)


# --------------------------------------------------------------- fixes (safe)

def json_fixes(root, findings):
    """Deterministic, LOW-risk JSON-only fixes. Code files never rewritten."""
    fixes = []
    for kind, f, tools in scan_tool_files(walk(root)):
        if kind != "tools" or tools is None or not f.is_file():
            continue
        text = read(f)
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, RecursionError):
            continue
        tools_list = data.get("tools") if isinstance(data, dict) else data
        if not isinstance(tools_list, list):
            continue
        changed = False
        seen = set()
        kept = []
        for t in tools_list:
            if isinstance(t, dict) and isinstance(t.get("name"), str):
                if t["name"] in seen:
                    changed = True
                    continue
                seen.add(t["name"])
            kept.append(t)
        if changed and isinstance(data, dict):
            data["tools"] = kept
            fixes.append({"file": str(f), "change": f"removed {len(tools_list)-len(kept)} duplicate tool entr(ies)",
                          "new_content": json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                          "risk": "LOW", "approval": approval_required("LOW")})
        elif changed and isinstance(data, list):
            fixes.append({"file": str(f), "change": f"removed {len(tools_list)-len(kept)} duplicate tool entr(ies)",
                          "new_content": json.dumps(kept, indent=2, ensure_ascii=False) + "\n",
                          "risk": "LOW", "approval": False})
    return fixes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".", help="project root to audit (default: cwd)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--only", help="comma list of categories to run")
    ap.add_argument("--fix", action="store_true", help="print fix plan (dry-run, writes nothing)")
    ap.add_argument("--apply", action="store_true", help="apply deterministic LOW-risk JSON fixes")
    args = ap.parse_args(argv)
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    only = args.only.split(",") if args.only else None
    bad = set(only or ()) - set(CATEGORIES)
    if bad:
        print(f"error: unknown categories: {','.join(sorted(bad))}; valid: {','.join(CATEGORIES)}", file=sys.stderr)
        return 2
    findings, card, nfiles = run_audit(root, only)
    fixes = json_fixes(root, findings)
    applied = []
    if args.apply:
        for fx in fixes:
            p = Path(fx["file"])
            p.write_text(fx["new_content"], encoding="utf-8")
            applied.append(fx["file"])
    result = {"project": str(root), "files_scanned": nfiles, "findings": findings,
              **card.to_dict(), "fix_plan": fixes, "applied": applied,
              "verdict": "PASS" if not findings else "FINDINGS"}
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        from harness_lib import findings_to_markdown
        out = [findings_to_markdown(findings, f"Harness Audit — {root.name}"),
               f"**Score: {card.total}/100** over {len(files := [c for c in card.weights])} categories "
               f"(skipped categories excluded; see json for per-category status).",
               f"\nFiles scanned: {nfiles}. Verdict: **{result['verdict']}**"]
        if args.fix or args.apply:
            out.append("\n## Fix plan (dry-run)" if not args.apply else "\n## Applied fixes")
            for fx in fixes:
                out.append(f"- {fx['file']}: {fx['change']} (risk {fx['risk']}, approval={'yes' if fx['approval'] else 'no'})")
            if not fixes:
                out.append("- deterministic auto-fixes: none available (non-JSON fixes stay manual proposals)")
        print("\n".join(out))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
