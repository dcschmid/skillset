#!/usr/bin/env python3
"""validate_findings.py — validate/normalize/dedupe review findings.

Input: JSON file with {"findings": [...]} or a bare list. stdlib-only.
Enforces the finding schema (schemas/finding.schema.json is the contract;
this script is its executable form):

  required per finding: id, axis, severity, confidence, file, title,
                        description, impact, recommendation, status
  axis       standards | spec | bugs | security | testing | performance
  severity   critical | high | medium | low | info
  confidence confirmed | strong-evidence | suspected | needs-verification
  status     open | fixed | deferred | wontfix
  optional   line_start/line_end (int>=1), evidence, verification, refs

Rules enforced here (deterministic, so agents can't fake structure):
  * unknown/missing fields -> INVALID (finding dropped from gate math is
    NOT silent: it is reported in `invalid[]`).
  * file must be repo-relative: no leading '/', no '..'.
  * dedupe: same (file, axis-insensitive, overlapping lines, title-similar)
    -> merged into first, `also_flagged_by` records the other axes. The
    primary axis of the first finding is preserved (no axis laundering).
  * gate: --gate critical|high|security|all PASSES iff no open finding of
    that class has confidence confirmed/strong-evidence; unverified or
    skipped checks are reported, never counted as passes.

Exit: 0 gate pass / no gate; 1 gate fail or input invalid; 2 bad usage.
"""
import argparse
import json
import re
import sys
from pathlib import Path

AXES = {"standards", "spec", "bugs", "security", "testing", "performance"}
SEVS = ["critical", "high", "medium", "low", "info"]
SCHEMA = json.loads((Path(__file__).resolve().parent.parent / "schemas" /
                     "finding.schema.json").read_text(encoding="utf-8"))


def validate(f):
    errs = []
    for k in SCHEMA["required"]:
        if k not in f or f[k] in (None, ""):
            errs.append(f"missing {k}")
    for k, value in f.items():
        rule = SCHEMA["properties"].get(k)
        if rule is None:
            errs.append(f"unknown field {k}")
            continue
        kind = rule.get("type")
        correct = (kind is None or
                   (kind == "string" and isinstance(value, str)) or
                   (kind == "integer" and type(value) is int) or
                   (kind == "array" and isinstance(value, list)))
        if not correct:
            errs.append(f"bad type for {k}: expected {kind}")
            continue
        if "enum" in rule and value not in rule["enum"]:
            errs.append(f"bad {k}")
        if kind == "string":
            if len(value) < rule.get("minLength", 0):
                errs.append(f"{k} too short")
            if "pattern" in rule and not re.search(rule["pattern"], value):
                errs.append(f"bad {k} format")
        if kind == "integer" and value < rule.get("minimum", value):
            errs.append(f"bad {k}")
        if kind == "array":
            item = rule["items"]
            if any((item.get("type") == "string" and not isinstance(v, str))
                   or ("enum" in item and v not in item["enum"])
                   for v in value):
                errs.append(f"bad items in {k}")
    fn = f.get("file", "")
    if isinstance(fn, str) and (fn.startswith("/") or ".." in fn.split("/")):
        errs.append(f"file not repo-relative: {fn!r}")
    if (type(f.get("line_start")) is int and type(f.get("line_end")) is int
            and f["line_end"] < f["line_start"]):
        errs.append("line range inverted")
    return errs


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def overlaps(a, b):
    if a.get("file") != b.get("file"):
        return False
    a1, a2 = a.get("line_start"), a.get("line_end", a.get("line_start"))
    b1, b2 = b.get("line_start"), b.get("line_end", b.get("line_start"))
    if a1 is None or b1 is None:  # file-wide: same normalized title = same defect
        return norm_title(a.get("title")) == norm_title(b.get("title"))
    return a1 <= (b2 or b1) and b1 <= (a2 or a1)


def dedupe(findings):
    kept, dropped = [], []
    for f in findings:
        dup = next((k for k in kept
                    if overlaps(k, f) and norm_title(k["title"])
                    == norm_title(f["title"])), None)
        if dup is not None:  # link; first reporter keeps its axis
            dup.setdefault("also_flagged_by", [])
            if f["axis"] not in dup["also_flagged_by"]:
                dup["also_flagged_by"].append(f["axis"])
            dropped.append({"id": f["id"], "merged_into": dup["id"]})
        else:
            kept.append(f)
    return kept, dropped


def gate(findings, level):
    """Blocking = open + (confirmed|strong-evidence). Unverified/low-confidence
    never blocks but is listed. Skipped axes are reported by the caller."""
    def blocks(f):
        if f["status"] != "open":
            return False
        if f["confidence"] not in ("confirmed", "strong-evidence"):
            return False
        if level == "all":
            return True
        if level == "critical":
            return f["severity"] == "critical"
        if level == "high":
            return f["severity"] in ("critical", "high")
        if level == "security":
            return (f["axis"] == "security" or
                    "security" in f.get("also_flagged_by", []))
        return False
    blocking = [f for f in findings if blocks(f)]
    warn = [f for f in findings if f["status"] == "open" and f not in blocking]
    return blocking, warn


def main():
    ap = argparse.ArgumentParser(prog="validate_findings.py")
    ap.add_argument("input", help="findings JSON file")
    ap.add_argument("--gate", choices=["critical", "high", "security", "all"])
    ap.add_argument("--out", "-o", help="write normalized findings JSON")
    ap.add_argument("--skipped-axes", default="",
                    help="comma list of axes that were skipped (SPEC_NOT_"
                         "AVAILABLE, tools missing); gates stay honest")
    a = ap.parse_args()

    try:
        data = json.loads(Path(a.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"verdict": "INVALID", "error": str(e)[:200]}))
        sys.exit(1)
    findings = data.get("findings") if isinstance(data, dict) else data
    if not isinstance(findings, list):
        print(json.dumps({"verdict": "INVALID",
                          "error": "expected findings list"}))
        sys.exit(1)

    valid, invalid = [], []
    for f in findings:
        errs = validate(f) if isinstance(f, dict) else ["not an object"]
        (invalid if errs else valid).append(
            {"id": f.get("id") if isinstance(f, dict) else "?",
             "errors": errs} if errs else f)

    # Gate original findings before dedupe can discard severity/confidence/status.
    blocking, warn = gate(valid, a.gate) if a.gate else ([], [])
    kept, merged = dedupe(valid)
    canonical_ids = {m["id"]: m["merged_into"] for m in merged}
    blocking_ids = list(dict.fromkeys(canonical_ids.get(f["id"], f["id"])
                                     for f in blocking))
    warning_ids = list(dict.fromkeys(canonical_ids.get(f["id"], f["id"])
                                    for f in warn))
    skipped = [s for s in a.skipped_axes.split(",") if s.strip()]
    sev_count = {s: 0 for s in SEVS}
    axis_count = {x: 0 for x in sorted(AXES)}
    for f in kept:
        if f["status"] == "open":
            sev_count[f["severity"]] += 1
            axis_count[f["axis"]] += 1

    out = {"verdict": "VALID", "open": sum(1 for f in kept if f["status"] == "open"),
           "by_severity": sev_count, "by_axis": axis_count,
           "invalid": invalid, "merged": merged, "skipped_axes": skipped,
           "findings": kept}
    verdict_rc = 1 if invalid else 0
    if a.gate:
        out["gate"] = {"level": a.gate, "pass": not blocking and not invalid,
                       "blocking": blocking_ids,
                       "warnings": [i for i in warning_ids if i not in blocking_ids],
                       "invalid_findings": len(invalid),
                       "skipped_axes": skipped,
                       "note": "skipped/invalid checks are gaps, not passes"}
        verdict_rc = 0 if out["gate"]["pass"] else 1
    if invalid:
        out["verdict"] = "PARTIAL" if kept else "INVALID"
    text = json.dumps(out, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    sys.exit(verdict_rc)


if __name__ == "__main__":
    main()
