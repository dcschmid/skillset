"""Audit: run discovery → validation → scoring per skill; overlap and
graph pass over the whole collection. Read-only by construction —
auditing never mutates skills."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .dependencies import build_graph
from .discovery import Discovery, build_catalog
from .overlap import analyze_pairs, find_conflicts
from .scoring import score_skill
from .validator import validate_skill


@dataclass
class SkillAudit:
    skill_id: str
    profile: str
    score: object
    validation: object
    def to_dict(self):
        return {"skill": self.skill_id, "profile": self.profile,
                "score": self.score.to_dict(),
                "validation": self.validation.to_dict()}


def audit_all(root, profile: str = "portable",
              only: set[str] | None = None) -> dict:
    disc = Discovery(root)
    catalog = build_catalog(disc)
    graph = build_graph(catalog)
    audits = {}
    for entry in catalog["skills"]:
        if only and entry["id"] not in only:
            continue
        ds = disc.skills()[entry["id"]]
        rep = validate_skill(ds, profile)
        audits[entry["id"]] = SkillAudit(
            entry["id"], profile, score_skill(entry, rep), rep)
        entry["quality"] = audits[entry["id"]].score.to_dict()
    overlaps = analyze_pairs(catalog, graph)
    conflicts = find_conflicts(catalog)
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "profile": profile,
        "catalog": catalog,
        "graph": graph.to_dict(),
        "audits": {k: v.to_dict() for k, v in audits.items()},
        "overlaps": [o.to_dict() for o in overlaps],
        "conflicts": conflicts,
        "cycles": graph.cycles,
    }


def audit_changed(root, profile: str = "portable") -> dict:
    """`--changed`: git status against HEAD for changed skill dirs."""
    import subprocess
    disc = Discovery(root)
    out = subprocess.run(["git", "status", "--porcelain", "--", "skills/"],
                         cwd=root, capture_output=True, text=True)
    changed: set[str] = set()
    for line in out.stdout.splitlines():
        path = line[3:].strip().split(" ")[-1]
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "skills":
            changed.add(parts[1])
    # direct dependents included
    base = audit_all(root, profile)
    graph = build_graph(base["catalog"])
    deps = {d for src, lst in graph.explicit.items()
            for d in lst if src in changed}
    changed |= deps
    return audit_all(root, profile, only=changed or None)
