"""hw_report.py — findings -> scores -> human-readable and JSON reports.

Scores are transparent arithmetic over counted findings, never a
"human percentage". Machine findings and editorial judgement stay separate
in every output shape.
"""
from __future__ import annotations

import json
from collections import Counter

from hw_rules import RULES, Finding

# Dimension map: which finding categories feed which score axis.
_AXES = {
    "clarity": {"signposting", "overexplaining", "hedging"},
    "specificity": {"promotional-inflation", "empty-conclusion", "pseudo-profundity"},
    "naturalness": {"filler", "generic-transition", "synthetic-enthusiasm", "repetition"},
    "variety": {"rhythm", "rule-of-three", "formatting-overuse"},
    "structure": {"formulaic-structure", "artificial-contrast", "formatting-overuse"},
}
_SEV_WEIGHT = {"high": 3, "med": 2, "low": 1}


def scores(findings: list[Finding], prose_words: int) -> dict:
    """0-100 per axis + density. 100 = nothing found in this run, not 'perfect'."""
    dens = max(prose_words, 1)
    axes = {a: 0 for a in _AXES}
    for f in findings:
        cat = RULES[f.rule][0]
        w = _SEV_WEIGHT[RULES[f.rule][1]]
        for axis, cats in _AXES.items():
            if cat in cats:
                axes[axis] += w
    out = {a: max(0, 100 - round(100 * v / (3 * dens / 4))) for a, v in axes.items()}
    out["overall"] = round(sum(out.values()) / len(out)) if out else 100
    out["findings_per_100w"] = round(100 * len(findings) / dens, 1)
    out["note"] = "counted findings, not authorship; 100 = nothing flagged in this pass"
    return out


def by_category(findings: list[Finding]) -> dict:
    c: Counter = Counter()
    for f in findings:
        c[RULES[f.rule][0]] += 1
    return dict(sorted(c.items(), key=lambda kv: -kv[1]))


def to_json(findings: list[Finding], *, lang: str, scores_: dict, source: str = "-") -> dict:
    return {
        "tool": "human-writing-lint",
        "version": 1,
        "source": source,
        "lang": lang,
        "scores": scores_,
        "categories": by_category(findings),
        "findings": [f.as_dict() for f in findings],
        "machine_notes": "rule matches only; editorial review still required",
    }


def to_text(findings: list[Finding], *, lang: str, scores_: dict, source: str = "-") -> str:
    ln = [f"lint: {source}  lang: {lang}  findings: {len(findings)}"]
    for f in findings:
        cat, sev, _ = RULES[f.rule]
        ln.append(f"{f.line}:{f.col} [{sev:>4}] {f.rule:<20} {f.excerpt}")
        ln.append(f"       why: {f.why}")
        if f.fix:
            ln.append(f"       fix: {f.fix}")
    if scores_:
        ax = "  ".join(f"{k}={v}" for k, v in scores_.items() if k != "note")
        ln.append(f"scores: {ax}")
        ln.append("note:   " + scores_.get("note", ""))
    return "\n".join(ln)


def merge_findings(*groups: list[Finding]) -> list[Finding]:
    """Dedup across pages/files by (rule,line,col) keeping first."""
    out, seen = [], set()
    for g in groups:
        for f in g:
            if f.key() not in seen:
                seen.add(f.key())
                out.append(f)
    out.sort(key=lambda f: (f.line, f.col))
    return out


def dump_json(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
