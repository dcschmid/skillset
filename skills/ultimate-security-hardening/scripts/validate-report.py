#!/usr/bin/env python3
"""validate-report.py — schema validator for skill security reports.

Validates security-findings.json (+ report presence) so fabricated or
malformed reports fail loudly. Usage:
    python3 validate-report.py --dir <project>/security-reports [--fix-hint]
    python3 validate-report.py --file findings.json
Exit: 0 valid, 1 invalid/missing, 2 usage error.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime
from pathlib import Path

SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"}
STATUSES = {"Confirmed", "Likely", "Needs Manual Review", "False Positive", "Not Applicable"}
FIX_STATES = {"FIXED", "PARTIALLY FIXED", "REQUIRES REVIEW", "NOT FIXED", "FALSE POSITIVE"}
VERDICTS = {"PASS", "PASS WITH WARNINGS", "BLOCKED", "INCOMPLETE"}
SECRET_KEYS = {"password", "secret", "token", "api_key", "apikey", "key", "authorization", "credential"}
MASK_MARK = "***MASKED***"

def _mask_leak_check(obj, path="root", leaks=None):
    """Secret values must never land in reports verbatim."""
    leaks = leaks if leaks is not None else []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 16 and MASK_MARK not in v \
               and any(sk in k.lower() for sk in SECRET_KEYS) and not v.startswith("$"):
                leaks.append(f"{path}.{k} looks like an unmasked secret value")
            _mask_leak_check(v, f"{path}.{k}", leaks)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _mask_leak_check(v, f"{path}[{i}]", leaks)
    return leaks

def validate_findings(data) -> list[str]:
    errs = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    for field in ("project", "commit", "generated_at", "findings", "verdict"):
        if field not in data:
            errs.append(f"missing required field: {field}")
    if not isinstance(data.get("findings"), list):
        errs.append("findings must be a list")
        return errs
    ids = set()
    for i, f in enumerate(data["findings"]):
        base = f"findings[{i}]"
        if not isinstance(f, dict):
            errs.append(f"{base}: object required"); continue
        for field in ("id", "severity", "category", "location", "evidence", "status", "fix_status"):
            if not f.get(field):
                errs.append(f"{base}: missing {field}")
        if f.get("id") in ids:
            errs.append(f"{base}: duplicate id {f.get('id')}")
        ids.add(f.get("id"))
        if f.get("severity") and f["severity"] not in SEVERITIES:
            errs.append(f"{base}.severity '{f['severity']}' not in {sorted(SEVERITIES)}")
        if f.get("status") and f["status"] not in STATUSES:
            errs.append(f"{base}.status '{f['status']}' not in {sorted(STATUSES)}")
        if f.get("fix_status") and f["fix_status"] not in FIX_STATES:
            errs.append(f"{base}.fix_status '{f['fix_status']}' not in {sorted(FIX_STATES)}")
        if f.get("status") == "Confirmed" and not f.get("evidence"):
            errs.append(f"{base}: Confirmed without evidence")
    v = data.get("verdict")
    if v and v not in VERDICTS:
        errs.append(f"verdict '{v}' not in {sorted(VERDICTS)}")
    for leak in _mask_leak_check(data):
        errs.append(f"secret-leak: {leak}")
    # verdict consistency: PASS requires no open critical/high confirmed
    if v == "PASS":
        open_ch = [f.get("id") for f in data["findings"]
                   if f.get("severity") in ("CRITICAL", "HIGH")
                   and f.get("status") == "Confirmed"
                   and f.get("fix_status") not in ("FIXED", "FALSE POSITIVE")]
        if open_ch:
            errs.append(f"PASS with open CRITICAL/HIGH: {open_ch} (use BLOCKED or fix statuses)")
    if v == "PASS" and data.get("coverage_gaps"):
        errs.append("PASS with documented coverage_gaps (use INCOMPLETE)")
    ts = data.get("generated_at", "")
    if ts:
        try: datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError: errs.append(f"generated_at not ISO8601: {ts}")
    return errs

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", help="security-reports directory")
    ap.add_argument("--file", help="single findings.json path")
    a = ap.parse_args()
    targets = []
    if a.file: targets = [Path(a.file)]
    elif a.dir:
        d = Path(a.dir)
        if not d.is_dir():
            print(f"FAIL: no such dir {d}", file=sys.stderr); return 1
        targets = sorted(d.glob("security-findings*.json"))
        for req in ("security-report.md",):
            if not list(d.glob(req.replace(".md", "*.md"))):
                print(f"WARN: missing {req} (report file expected alongside findings)")
        if not targets:
            print("FAIL: no security-findings*.json found — nothing to validate", file=sys.stderr); return 1
    else:
        print("error: --dir or --file required", file=sys.stderr); return 2
    failed = 0
    for t in targets:
        try:
            data = json.loads(t.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"FAIL {t.name}: unreadable: {e}", file=sys.stderr); failed += 1; continue
        errs = validate_findings(data)
        if errs:
            failed += 1
            print(f"FAIL {t.name}:")
            for e in errs: print(f"  - {e}", file=sys.stderr)
        else:
            n = len(data.get("findings", []))
            print(f"OK   {t.name}: {n} findings, verdict={data.get('verdict')}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
