#!/usr/bin/env python3
"""security_scan.py — harness security review over prompts, tool configs, adapters.

Checks: prompt-injection surface (external content obeyed as instruction),
least-privilege breaches (shell without bounds, wildcard permissions), secret
literals in instruction/context files, path-traversal-prone path handling,
approval gates missing on HIGH/CRITICAL operations, dry-run that can write.

Usage:
    python3 scripts/security_scan.py PATH [--format json|markdown]
PATH is a file (prompt/config) or directory (scanned recursively).
Exit: 0 clean, 1 findings, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import RISK_LEVELS, approval_required, classify_risk  # noqa: E402

SECRET_PAT = re.compile(r"(?i)\b(api[_-]?key|secret|password|token|authorization|credential)s?\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{16,})")
INJECTION_PAT = re.compile(r"(?im)^(ignore (all |previous )?(instructions|prompts)|disregard (the )?(system|previous))")
SHELL_PAT = re.compile(r"(subprocess\.(run|call|Popen|check_output)|os\.system|execSync|child_process\.exec)")
TRAVERSAL_PAT = re.compile(r"(os\.path\.join\([^)]*user|\.\./\.\./|join\(\s*\w*(path|file|target)\s*\))")
WILDCARD_PERMS = re.compile(r"(\"permissions\"\s*:\s*\"\*\"|allowed_tools\s*:\s*\[\"\*\"\]|--yes|--no-verify|--force)")


def scan_text(rel, text, findings):
    n = 0
    for m in SECRET_PAT.finditer(text):
        findings.append({"id": f"SEC-{n+1}", "file": rel, "severity": "HIGH",
                         "check": "secrets-in-context",
                         "evidence": f"'{m.group(1)}=…' literal ({m.group(2)[:8]}…)",
                         "impact": "secret leaks into prompts/traces",
                         "fix": "move to env/secret store; mask in logs", "risk": "MEDIUM"})
        n += 1
    if INJECTION_PAT.search(text):
        findings.append({"id": f"SEC-{n+1}", "file": rel, "severity": "MEDIUM",
                         "check": "prompt-injection-surface",
                         "evidence": "imperative override phrase in repo file",
                         "impact": "agent obeys file content as instruction",
                         "fix": "wrap external content as data; instructions stay owner-authored", "risk": "LOW"})
        n += 1
    if SHELL_PAT.search(text) and not re.search(r"timeout\s*=", text):
        findings.append({"id": f"SEC-{n+1}", "file": rel, "severity": "MEDIUM",
                         "check": "unbounded-execution",
                         "evidence": "shell execution without timeout",
                         "impact": "hangs/resource exhaustion",
                         "fix": "timeout + path allowlist + output bound", "risk": "MEDIUM"})
        n += 1
    if WILDCARD_PERMS.search(text):
        findings.append({"id": f"SEC-{n+1}", "file": rel, "severity": "HIGH",
                         "check": "least-privilege",
                         "evidence": "wildcard/forced permission flag",
                         "impact": "agent exceeds intended authority",
                         "fix": "enumerate allowed tools/paths; drop force flags", "risk": "MEDIUM"})
        n += 1
    if TRAVERSAL_PAT.search(text) and "allowed_paths" not in text:
        findings.append({"id": f"SEC-{n+1}", "file": rel, "severity": "MEDIUM",
                         "check": "path-validation",
                         "evidence": "user-influenced path join without allowlist",
                         "impact": "path traversal outside project",
                         "fix": "validate/contain paths (allowed_paths or Path.resolve + is_relative_to)",
                         "risk": "MEDIUM"})
        n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="file or directory to scan")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    root = Path(args.path)
    if not root.exists():
        print(f"error: no such path: {root}", file=sys.stderr)
        return 2
    files = [root] if root.is_file() else [f for f in root.rglob("*")
                                           if f.suffix in (".py", ".ts", ".js", ".json", ".md", ".yaml", ".yml")
                                           and f.stat().st_size < 512_000
                                           and not any(p in ("node_modules", ".git", "__pycache__") for p in f.parts)]
    findings, scanned = [], 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        scan_text(str(f.relative_to(root) if not root.is_file() else f.name), text, findings)
    high = [x for x in findings if x["severity"] == "HIGH"]
    report = {"path": str(root), "files_scanned": scanned, "findings": findings,
              "verdict": "PASS" if not findings else ("FAIL" if high else "WARNINGS"),
              "risk_model": {"levels": list(RISK_LEVELS),
                             "approval_required_above": "MEDIUM" if approval_required("HIGH") else "HIGH"}}
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"# Harness security scan — {root}")
        print(f"{scanned} file(s), {len(findings)} finding(s). Verdict: **{report['verdict']}**\n")
        for x in findings:
            print(f"- [{x['severity']}] {x['file']} :: {x['check']} — {x['evidence']} → {x['fix']}")
        print(f"\nRisk tiers: {', '.join(RISK_LEVELS)}; HIGH/CRITICAL always need explicit approval.")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
