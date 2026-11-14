"""Quality score: 100 points over 7 weighted categories.

Rules:
- Points are deducted ONLY from verifiable findings (validator output).
- Unchecked areas are returned as `unchecked` and score 0 credit —
  never automatic full marks.
- Security errors or invalid required metadata are blockers regardless
  of total.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# category: (points, checks-prefix map)
CATEGORIES = {
    "structure":        (15, ("meta.", "structure.", "size.")),
    "activation":       (20, ("content.activation",)),
    "content":          (20, ("content.",)),
    "security":         (15, ("security.", "secret.")),
    "tests":            (15, ()),     # from facts, not findings
    "maintainability":  (10, ()),     # from facts
    "efficiency":       (5,  ("structure.orphan-reference",)),
}
# findings severity → deduction (within its category)
SEV_DEDUCT = {"error": "full", "warn": 0.5, "info": 0.15}

GRADE_BANDS = [(90, "Excellent"), (80, "Good"), (70, "Needs Improvement"),
               (50, "Poor"), (0, "Critical")]


@dataclass
class Score:
    total: int
    grade: str
    categories: dict = field(default_factory=dict)
    unchecked: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {"score": self.total, "grade": self.grade,
             "categories": self.categories, "blockers": self.blockers,
             "unchecked": self.unchecked}
        return d


def _grade(total: int) -> str:
    for lo, name in GRADE_BANDS:
        if total >= lo:
            return name
    return "Critical"


def score_skill(skill_entry: dict, report) -> Score:
    """report: ValidationReport; skill_entry: catalog entry (facts)."""
    cats = {name: float(pts) for name, (pts, _) in CATEGORIES.items()}
    deduct: dict[str, float] = {name: 0.0 for name in CATEGORIES}
    blockers: list[str] = []
    for f in report.findings:
        for name, (_, prefixes) in CATEGORIES.items():
            if any(f.check.startswith(p) for p in prefixes):
                pts = CATEGORIES[name][0]
                mode = SEV_DEDUCT.get(f.severity, 0.15)
                deduct[name] -= pts if mode == "full" else pts * mode
                if f.severity == "error" and name in ("structure", "security"):
                    blockers.append(f"{f.check}: {f.message}")
                break
    unchecked: list[str] = []

    # Five points for discoverable test structure; execution and behavior
    # each reserve five points, awarded only by a future evidence-aware runner.
    deduct["tests"] -= 10 if skill_entry.get("has_tests") else 15
    if not skill_entry.get("has_tests"):
        unchecked.append("tests.structure: no tests/ directory")
    unchecked.extend([
        "tests.execution: NOT RUN by static audit (0/5)",
        "tests.behavior: NOT RUN by static audit (0/5)",
    ])
    # maintainability: body size vs references split (repo rule ~150 lines spine)
    mpts = CATEGORIES["maintainability"][0]
    body_lines = skill_entry.get("body_lines", 0)
    if body_lines > 500:
        deduct["maintainability"] -= mpts * 0.5
    refs = skill_entry.get("files", {}).get("references") or []
    if body_lines > 300 and not refs:
        deduct["maintainability"] -= mpts * 0.5
        unchecked.append(
            "maintainability: large body without references/ — split NOT VERIFIED")

    total = 0
    cat_out = {}
    for name, (pts, _) in CATEGORIES.items():
        got = max(0.0, min(float(pts), pts + deduct.get(name, 0.0)))
        cat_out[name] = round(got, 1)
        total += got
    total = int(round(total))
    if blockers:
        total = min(total, 69)
    return Score(total, _grade(total), cat_out, unchecked, blockers)
