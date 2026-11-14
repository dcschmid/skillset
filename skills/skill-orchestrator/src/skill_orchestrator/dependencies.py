"""Skill dependency graph: explicit deps, collaboration edges (cross
mentions), cycles, missing targets. Derived from real catalog data."""

from __future__ import annotations

from dataclasses import dataclass, field


# Layer inference from skill text roles (deterministic keyword classes).
LAYER_KEYWORDS = [
    ("coordinate", ("orchestrat", "catalog", "routing engine")),
    ("implementation", ("development", "build", "engine", "framework",
                        "create", "model")),
    ("asset-pipeline", ("asset", "modeling", "export", "glb", "blender")),
    ("audit", ("audit", "review", "security", "accessibility", "wcag",
               "seo", "quality", "authenticity")),
    ("verification", ("testing", "qa", "e2e", "regression")),
    ("content", ("writing", "prose", "i18n", "localization", "translate")),
]
LAYER_ORDER = ["coordinate", "implementation", "asset-pipeline", "audit",
               "verification", "content"]

EXPLICIT_DEP_RES = (
    r"depends?\s+on\s+([a-z0-9][a-z0-9-]*)\s+skill",
    r"requires?\s+([a-z0-9][a-z0-9-]*)\s+skill",
    r"requires?\s+([a-z0-9][a-z0-9-]*)(?:\s+skill)?\s+available",
)


def infer_layer(text: str) -> str:
    low = text.lower()
    best, score = "implementation", 0
    for layer, kws in LAYER_KEYWORDS:
        s = sum(1 for k in kws if k in low)
        if s > score:
            best, score = layer, s
    return best


@dataclass
class Graph:
    nodes: list[str] = field(default_factory=list)
    explicit: dict[str, list[str]] = field(default_factory=dict)   # a -> deps
    optional: dict[str, list[str]] = field(default_factory=dict)
    collaboration: list[tuple[str, str]] = field(default_factory=list)
    layers: dict[str, str] = field(default_factory=dict)
    cycles: list[list[str]] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)   # (src, target)

    def to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "explicit": self.explicit,
            "optional": self.optional,
            "collaboration": [list(e) for e in self.collaboration],
            "layers": self.layers,
            "cycles": self.cycles,
            "missing_targets": [{"from": s, "to": t} for s, t in self.missing],
        }

    def mermaid(self) -> str:
        lines = ["graph TD"]
        for src, deps in self.explicit.items():
            for dst in deps:
                lines.append(f"  {src} --> {dst}")
        for src, deps in self.optional.items():
            for dst in deps:
                lines.append(f"  {src} -.-> {dst}")
        for a, b in self.collaboration:
            lines.append(f"  {a} --- {b}")
        return "\n".join(lines)

    def topo_order(self, names: list[str]) -> list[str]:
        """Layer-ordered execution sequence for a selected set; ties keep
        catalog order. Cycles are reported separately."""
        rank = {l: i for i, l in enumerate(LAYER_ORDER)}
        return sorted(names, key=lambda n: (rank.get(self.layers.get(n, ""),
                                                     len(LAYER_ORDER)), n))


def build_graph(catalog: dict) -> Graph:
    import re
    skills = {s["id"]: s for s in catalog["skills"]}
    g = Graph(nodes=sorted(skills))
    for sid, s in skills.items():
        text = (s["description"] + "\n"
                + open_text(s.get("_body", "")))
        g.layers[sid] = infer_layer(text)
        deps: list[str] = []
        meta_deps = (s.get("frontmatter") or {}).get("metadata", {})
        if isinstance(meta_deps, dict):
            raw = str(meta_deps.get("dependencies", ""))
            deps += [d.strip() for d in raw.split(",") if d.strip()]
        for rx in EXPLICIT_DEP_RES:
            for m in re.finditer(rx, text, re.IGNORECASE):
                deps.append(m.group(1))
        for d in dict.fromkeys(deps):
            if d not in skills:
                g.missing.append((sid, d))
            elif d != sid:
                g.explicit.setdefault(sid, []).append(d)
        for m in s.get("mentions", []):
            if m in skills:
                g.collaboration.append((sid, m))
    g.cycles = _find_cycles(g.explicit)
    # collaboration dedupe (undirected)
    seen, collab = set(), []
    for a, b in g.collaboration:
        key = tuple(sorted((a, b)))
        if key not in seen:
            seen.add(key)
            collab.append((a, b))
    g.collaboration = collab
    return g


def open_text(v) -> str:
    return v if isinstance(v, str) else ""


def _find_cycles(adj: dict[str, list[str]]) -> list[list[str]]:
    """DFS cycle detection on explicit edges only."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj}
    for deps in adj.values():
        for d in deps:
            color.setdefault(d, WHITE)
    cycles: list[list[str]] = []
    stack: list[str] = []

    def dfs(n: str):
        color[n] = GRAY
        stack.append(n)
        for m in adj.get(n, []):
            if color.get(m, WHITE) == GRAY:
                i = stack.index(m)
                cyc = stack[i:] + [m]
                if cyc not in cycles:
                    cycles.append(list(cyc))
            elif color.get(m, WHITE) == WHITE:
                dfs(m)
        stack.pop()
        color[n] = BLACK

    for n in sorted(color):
        if color[n] == WHITE:
            dfs(n)
    return cycles
