"""Routing engine: task text → auditable skill plan.

Deterministic first: tech detection, domain scoring, mutual-exclusion
rules (engine A vs engine B), explicit selection, negative examples.
No external model required; a model may refine the plan but the plan
must stand without one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .dependencies import Graph

# Domain detection: task tokens → skill ids. Identity-style (explicit),
# tech (project files/frameworks), role (task verbs).
TECH_SKILL_MAP = {
    "astro": "astro",
    "react": "react-nextjs", "next.js": "react-nextjs", "nextjs": "react-nextjs",
    "godot": "godot",
    "defold": "defold-development", "lua": "defold-development",
    "blender": "lowpoly-reference-to-blender", "glb": "lowpoly-reference-to-blender",
    "low-poly": "lowpoly-reference-to-blender", "lowpoly": "lowpoly-reference-to-blender",
    "voxel": None,  # engine decides; both game skills own voxel
}

DOMAIN_SKILLS = {
    "accessibility": ["accessibility"],
    "security": ["ultimate-security-hardening"],
    "testing": ["ultimate-testing-qa"],
    "seo": ["seo-performance"], "performance-web": ["seo-performance"],
    "i18n": ["ultimate-i18n-localization"], "localization": ["ultimate-i18n-localization"],
    "code-quality": ["ultimate-code-quality-refactoring"],
    "refactoring": ["ultimate-code-quality-refactoring"],
    "design": ["design-authenticity"], "ui": ["design-authenticity"],
    "writing": ["human-writing"], "prose": ["human-writing"],
}
DOMAIN_TOKENS = {
    "accessibility": ("accessib", "wcag", "barrier", "screenreader",
                      "screen reader", "keyboard nav", "a11y"),
    "security": ("security", "sicherhei", "owasp", "vulnerabilit", "xss",
                 "injection", "auth", "csp"),
    "testing": ("test", "qa", "e2e", "playwright", "vitest", "regression",
                 "quality gate", "abnahme"),
    "seo": ("seo", "lighthouse", "core web vitals", "lcp", "inp", "cls",
            "schema.org", "sitemap"),
    "performance-web": ("performance", "perf", "speed", "langsam", "slow",
                        "optimi"),
    "i18n": ("i18n", "locale", "localization", "übersetz", "translation",
             "mehrsprach"),
    "code-quality": ("refactor", "code smell", "tech debt", "technical debt",
                     "code qualität", "code-quality", "cleanup"),
    "design": ("design", "ui", "brand", "identity", "look", "optik",
               "landing page", "dashboard"),
    "writing": ("text", "prose", "blog", "copy", "documentation", "readme",
                "schreib", "writing"),
    "asset3d": ("3d asset", "modell", "model ", "character", "mesh",
                "concept art", "reference image", "low-poly"),
}
GAME_DOMAIN = ("game", "spiel", "level", "gameplay", "player", "npc",
               "tilemap", "genre", "platformer", "rpg", "shooter")
WEB_DOMAIN = ("website", "webseite", "site", "web app", "webapp", "spa",
              "landing", "frontend", "website")

# Mutual exclusion: only one game engine skill / web framework stack at a time
# unless the task explicitly names both.
EXCLUSIVE_GROUPS = [
    {"godot", "defold-development"},
    {"astro", "react-nextjs"},
]

BASE_SCORE = 10


@dataclass
class RouteChoice:
    skill: str
    score: int
    reason: str
    role: str            # primary | support | gate


@dataclass
class RoutingPlan:
    task: str
    tech: list[str]
    domains: list[str]
    selected: list[RouteChoice] = field(default_factory=list)
    considered_rejected: list[tuple[str, str]] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "tech_detected": self.tech,
            "domains_detected": self.domains,
            "selected": [{"skill": c.skill, "score": c.score,
                          "role": c.role, "reason": c.reason}
                         for c in self.selected],
            "considered_rejected": [{"skill": s, "why": w}
                                    for s, w in self.considered_rejected],
            "execution_order": self.order,
            "quality_gates": self.quality_gates,
            "expected_results": self.expected_results,
        }


def detect(task: str) -> tuple[list[str], list[str]]:
    low = task.lower()
    tech = sorted({t for t in TECH_SKILL_MAP if t in low and TECH_SKILL_MAP[t]})
    domains = sorted({d for d, toks in DOMAIN_TOKENS.items()
                      if any(t in low for t in toks)})
    if any(t in low for t in GAME_DOMAIN):
        domains.append("game")
    if any(t in low for t in WEB_DOMAIN):
        domains.append("web")
    return tech, sorted(set(domains))


def route(task: str, catalog: dict, graph: Graph,
          explicit: list[str] | None = None) -> RoutingPlan:
    tech, domains = detect(task)
    low = task.lower()
    skills = {s["id"]: s for s in catalog["skills"]}
    scores: dict[str, int] = {}
    reasons: dict[str, list[str]] = {}
    rejected: list[tuple[str, str]] = []

    def add(sid: str, pts: int, why: str):
        if sid not in skills:
            return
        scores[sid] = scores.get(sid, 0) + pts
        reasons.setdefault(sid, []).append(why)

    for t in tech:
        sid = TECH_SKILL_MAP.get(t)
        if sid:
            add(sid, BASE_SCORE + 20, f"tech '{t}' named in task")
    web_context = ("web" in domains or "web" in "".join(tech)
                   or {"astro", "react", "next.js", "nextjs"} & set(tech)
                   or "seo" in domains)
    for d in domains:
        for sid in DOMAIN_SKILLS.get(d, []):
            if d in ("seo", "performance-web") and not web_context:
                continue  # web perf/seo skills must not hijack game tasks
            add(sid, BASE_SCORE + 5, f"domain '{d}' detected")
        if d == "game":
            for sid in ("godot", "defold-development"):
                add(sid, BASE_SCORE, f"game domain (engine undecided)")
        if d == "web":
            for sid in ("astro", "react-nextjs"):
                add(sid, BASE_SCORE, "web domain (framework undecided)")
        if d == "asset3d":
            add("lowpoly-reference-to-blender", BASE_SCORE + 5,
                "3D asset task")

    for sid, s in skills.items():
        if sid.lower() in low and sid not in scores:
            add(sid, BASE_SCORE + 15, "skill id named in task")

    for x in explicit or []:
        add(x, 100, "explicitly selected")

    # engine exclusion: named tech suppresses rival stack skills
    named = {TECH_SKILL_MAP.get(t) for t in tech if TECH_SKILL_MAP.get(t)}
    named_techs = {t for t in tech}
    if "godot" in named_techs and "defold-development" in scores:
        rejected.append(("defold-development",
                         "godot named; engine skills are exclusive"))
        scores.pop("defold-development", None)
    if "defold" in named_techs and "godot" in scores:
        rejected.append(("godot", "defold named; engine skills are exclusive"))
        scores.pop("godot", None)
    if ("react" in named_techs or "next.js" in named_techs) \
            and "astro" in scores and "astro" not in named_techs:
        rejected.append(("astro",
                         "react/next project; no migration without request"))
        scores.pop("astro", None)
    if "astro" in named_techs and "react-nextjs" in scores \
            and "react" not in named_techs:
        rejected.append(("react-nextjs",
                         "astro project; react only as island lib if needed"))
    for group in EXCLUSIVE_GROUPS:
        present = [s for s in group if s in scores]
        if len(present) > 1 and len(named) >= 1:
            loser = min(present, key=lambda s: scores.get(s, 0))
            rejected.append((loser,
                             f"exclusivity with {named & set(group)}"))
            scores.pop(loser, None)

    # caps: never select more than needed; support skills only alongside core
    ordered = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    threshold = max(5, BASE_SCORE)
    selected = [RouteChoice(sid, sc, "primary" if sc >= BASE_SCORE + 15 else
                            "support" if sc >= threshold else "gate",
                            "; ".join(reasons.get(sid, [])))
                for sid, sc in ordered if sc >= threshold]
    if len(selected) > 8:
        for c in selected[8:]:
            rejected.append((c.skill, "cap: routing precision over coverage"))
        selected = selected[:8]

    # graph dependencies of selected
    need = {c.skill for c in selected}
    for c in list(selected):
        for dep in graph.explicit.get(c.skill, []):
            if dep in skills and dep not in need:
                selected.append(RouteChoice(dep, scores.get(dep, 0),
                                            "dependency",
                                            f"required by {c.skill}"))
                need.add(dep)

    plan = RoutingPlan(task=task, tech=tech, domains=domains,
                       selected=selected,
                       considered_rejected=list(
                           dict((s, w) for s, w in rejected).items()))
    role_rank = {"primary": 0, "support": 1, "gate": 2, "dependency": 1}
    order_names = [c.skill for c in sorted(
        selected, key=lambda c: (role_rank.get(c.role, 3), -c.score))]
    plan.order = graph.topo_order(order_names)
    gates = []
    if "ultimate-testing-qa" in need or any("testing" in d for d in domains):
        gates.append("functional test gate (testing skill or project runner)")
    if "accessibility" in need:
        gates.append("a11y gate: automated PASS is not conformance; manual+SR evidence")
    if "ultimate-security-hardening" in need:
        gates.append("security gate: findings confirmed before fix, re-scan after")
    if "seo-performance" in need:
        gates.append("perf gate: lab vs field separated, before/after measured")
    plan.quality_gates = gates
    plan.expected_results = [
        f"{c.skill}: {c.role} contribution ({'implements' if c.role == 'primary' else 'supports' if c.role == 'support' else 'gates'} the task)"
        for c in selected]
    return plan
