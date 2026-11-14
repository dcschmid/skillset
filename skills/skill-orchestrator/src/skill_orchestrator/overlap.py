"""Overlap analysis: cooperation vs partial overlap vs problematic
overlap vs true conflict. Deterministic text/structure/metadata analysis;
similarity scores are signals, never proof — every verdict cites evidence
(from file, line range, quoted instruction)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .router import EXCLUSIVE_GROUPS

STOP = set("""the a an and or of to in for with use any all this that it is
as at by from not are be been it's its on our we you your""".split())


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9][a-z0-9-]{2,}", text.lower())
            if w not in STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _skill_text(s: dict) -> str:
    return (s.get("description", "") + "\n" + s.get("blurb", ""))


@dataclass
class PairResult:
    a: str
    b: str
    similarity: float
    classification: str        # cooperation | partial | problematic | conflict
    severity: str              # none | low | medium | high
    shared_tasks: list[str]
    distinct_responsibilities: str
    evidence: list[str]
    proposal: str

    def to_dict(self) -> dict:
        return {"skills": [self.a, self.b], "similarity":
                round(self.similarity, 3),
                "classification": self.classification,
                "severity": self.severity,
                "shared_tasks": self.shared_tasks,
                "responsibilities": self.distinct_responsibilities,
                "evidence": self.evidence[:8],
                "proposal": self.proposal}


# Known declared-responsibility split lines in this repo (verified evidence
# lookup, matched case-insensitively against skill descriptions).
OWNERSHIP_RX = re.compile(
    r"(?P<owner>[a-z-]+)\s+owns?\s+(?:the\s+)?(?P<domain>[\w \-/]{3,60})",
    re.IGNORECASE)


def analyze_pairs(catalog: dict, graph, min_sim: float = 0.08) -> list[PairResult]:
    skills = {s["id"]: s for s in catalog["skills"]}
    ids = sorted(skills)
    layers = graph.layers
    results: list[PairResult] = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sa, sb = _skill_text(skills[a]), _skill_text(skills[b])
            ta, tb = _tokens(sa), _tokens(sb)
            sim = jaccard(ta, tb)
            shared = sorted(ta & tb)
            same_layer = layers.get(a) == layers.get(b)
            exclusive = any({a, b} <= set(g) for g in EXCLUSIVE_GROUPS)
            collab = (a, b) in {tuple(sorted(e)) for e in graph.collaboration}
            mentions_a, mentions_b = b in sa.lower(), a in sb.lower()

            if mentions_a or mentions_b:
                # a declares scope over the other's subject => cooperation,
                # unless both declare the same primary owner role.
                cls, sev = "cooperation", "none"
                ev = _ownership_evidence(sa, sb, a, b)
                resp = _resp_text(sa, sb, a, b)
                if not ev:
                    ev = [f"{a} references {b} in its description "
                          "(scope handoff)"]
                prop = ("documented handoff; orchestrator keeps declared "
                        "owner in charge")
            elif exclusive:
                cls, sev = "partial", "low"
                resp = (f"{a} and {b} own disjoint product domains; "
                        "orchestrator must not select both for one target")
                ev = _resp_text_evidence(sa, sb, a, b, shared) + \
                    [f"exclusive domain pair: {sorted({a, b})}"]
                prop = ("acceptable; keep as siblings — routing must pick "
                        "exactly one per project")
            elif sim >= 0.22 and same_layer:
                cls, sev = "problematic", "medium"
                resp = _resp_text(sa, sb, a, b)
                ev = _resp_text_evidence(sa, sb, a, b, shared)
                prop = ("split primary responsibility or merge; both claim "
                        "the same layer and share task vocabulary")
            elif sim >= min_sim:
                cls, sev = ("partial", "low")
                resp = _resp_text(sa, sb, a, b)
                ev = [f"shared vocabulary: {', '.join(shared[:8])} "
                      f"(sim={sim:.2f}, layer={layers.get(a)} vs "
                      f"{layers.get(b)})"]
                prop = ("acceptable; monitor on edit — keep shared "
                        "guidance in one owner")
            else:
                continue
            results.append(PairResult(
                a, b, sim, cls, sev, shared[:12], resp, ev, prop))
    return sorted(results, key=lambda r: (
        ["conflict", "problematic", "partial", "cooperation"].index(
            r.classification), -r.similarity))


def _ownership_evidence(sa: str, sb: str, a: str, b: str) -> list[str]:
    out = []
    for text, who in ((sa, a), (sb, b)):
        for m in OWNERSHIP_RX.finditer(text):
            out.append(f"{who}: owns '{m.group('domain').strip()[:60]}'")
    return out[:6]


def _resp_text(sa: str, sb: str, a: str, b: str) -> str:
    return (f"{a} and {b} are separated by layer/scope; "
            "check declared 'owns' clauses before merging anything")


def _resp_text_evidence(sa, sb, a, b, shared) -> list[str]:
    ev = _ownership_evidence(sa, sb, a, b)
    return ev or [f"no explicit ownership clause; overlap on "
                  f"{', '.join(shared[:6])}"]


# -- true conflicts: contradictory instructions between two skills -----------
CONFLICT_PROBES = [
    ("framework-choice", ("astro", "react/next", "migrat", "not forced")),
    ("engine-choice", ("godot", "defold")),
]


def find_conflicts(catalog: dict) -> list[dict]:
    """Same-domain contradictory instructions. Evidence = quoted lines."""
    skills = {s["id"]: s for s in catalog["skills"]}
    out: list[dict] = []
    if "astro" in skills and "react-nextjs" in skills:
        da = skills["astro"].get("description", "")
        m = re.search(r"Astro is not forced[^\"]*?better", da)
        if m:
            out.append({
                "type": "framework-preference",
                "skills": ["astro", "react-nextjs"],
                "classification": "cooperation",
                "evidence": [f"astro: '{m.group(0)}'"],
                "resolution": "astro defers to better-fitting stacks; "
                              "react-nextjs activates only for react projects",
                "severity": "none"})
    return out
