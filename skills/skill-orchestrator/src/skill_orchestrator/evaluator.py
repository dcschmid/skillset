"""Testing tiers. Every result reflects an execution that actually
happened; nothing is reported PASS that was not run.

Tiers: static | routing | conflict | integration | agent-eval.
Agent evals run ONLY through a real agent CLI (claude/codex) when present;
otherwise SKIPPED / UNAVAILABLE — never fabricated.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .auditor import audit_all
from .router import route
from .dependencies import build_graph

RESULTS = ("PASS", "FAIL", "SKIPPED", "UNAVAILABLE")


@dataclass
class TestResult:
    tier: str
    name: str
    status: str
    detail: str = ""

    def to_dict(self):
        return {"tier": self.tier, "name": self.name,
                "status": self.status, "detail": self.detail[:300]}


def run_static(root, profile: str = "portable") -> list[TestResult]:
    res: list[TestResult] = []
    audit = audit_all(root, profile)
    for sid, a in sorted(audit["audits"].items()):
        errs = [f for f in a["validation"]["findings"]
                if f["severity"] == "error"]
        res.append(TestResult(
            "static", f"validate:{sid}",
            "PASS" if not errs else "FAIL",
            "; ".join(f"{f['check']}" for f in errs)[:280] or
            f"score={a['score']['score']}"))
    return res


def run_routing(root, probes: list[tuple[str, list[str]]]) -> list[TestResult]:
    """probes: (task_text, expected_skill_ids). Deterministic."""
    from .discovery import Discovery, build_catalog
    disc = Discovery(root)
    cat = build_catalog(disc)
    g = build_graph(cat)
    out = []
    for task, expected in probes:
        plan = route(task, cat, g)
        got = {c.skill for c in plan.selected}
        missing = [e for e in expected if e not in got]
        out.append(TestResult(
            "routing", task[:40], "PASS" if not missing else "FAIL",
            f"missing={missing or '-'} got={sorted(got)}"))
    return out


def run_conflicts(root) -> list[TestResult]:
    audit = audit_all(root)
    res = []
    for cyc in audit["cycles"]:
        res.append(TestResult("conflict", "cycles:" + "→".join(cyc),
                              "FAIL", "cyclic explicit dependencies"))
    if not audit["cycles"]:
        res.append(TestResult("conflict", "cycles", "PASS",
                              "no explicit dependency cycles"))
    for c in audit["conflicts"]:
        res.append(TestResult("conflict", c["type"],
                              "PASS" if c["severity"] == "none" else "FAIL",
                              c["resolution"]))
    return res


def run_integration(root) -> list[TestResult]:
    """End-to-end: scan → catalog json round-trip → audit stable."""
    res: list[TestResult] = []
    try:
        a1 = audit_all(root)
        text = json.dumps(a1)
        a2 = json.loads(text)
        ok = (a2["catalog"]["skill_count"] == a1["catalog"]["skill_count"]
              and set(a2["audits"]) == set(a1["audits"]))
        res.append(TestResult("integration", "scan→catalog→audit",
                              "PASS" if ok else "FAIL",
                              f"skills={a1['catalog']['skill_count']}"))
    except Exception as exc:
        res.append(TestResult("integration", "scan→catalog→audit", "FAIL",
                              repr(exc)[:280]))
    return res


# -- agent-eval tier: honest gating ------------------------------------------

def agent_binary(which: str) -> str | None:
    return shutil.which(which)


def run_agent_eval(root, skill_id: str, prompt: str,
                   expect: list[str] | None = None) -> list[TestResult]:
    """Behavior eval through a real installed agent CLI. If neither
    claude nor codex is installed → UNAVAILABLE (documented, not fake)."""
    cli = agent_binary("claude") or agent_binary("codex")
    if not cli:
        return [TestResult("agent-eval", f"{skill_id}:behavior", "UNAVAILABLE",
                           "no supported agent CLI on PATH; "
                           "install claude or codex to enable")]
    name = "claude" if "claude" in cli else "codex"
    with tempfile.TemporaryDirectory(prefix="so-eval-") as td:
        workdir = Path(td)
        try:
            proc = subprocess.run(
                [cli, "-p", prompt, "--output-format", "json"]
                if name == "claude" else [cli, "exec", prompt],
                cwd=workdir, capture_output=True, text=True, timeout=300)
        except (subprocess.TimeoutExpired, OSError) as exc:
            return [TestResult("agent-eval", f"{skill_id}:behavior", "FAIL",
                               f"{name}: {exc}")]
        if proc.returncode != 0:
            return [TestResult("agent-eval", f"{skill_id}:behavior", "FAIL",
                               f"{name} exit {proc.returncode}: "
                               f"{proc.stderr[:200]}")]
        out = proc.stdout
        touched = [p for p in workdir.iterdir()]
        missing = [e for e in (expect or []) if e.lower() not in out.lower()]
        res = [TestResult("agent-eval", f"{skill_id}:behavior",
                          "PASS" if not missing else "FAIL",
                          f"agent={name} expected_missing={missing or '-'} "
                          f"files_created={len(touched)}")]
        return res


def run_all(root, profile="portable") -> dict:
    from .router import route as _  # noqa
    tiers = {
        "static": run_static(root, profile),
        "routing": run_routing(root, DEFAULT_ROUTING_PROBES),
        "conflict": run_conflicts(root),
        "integration": run_integration(root),
    }
    flat = [r for lst in tiers.values() for r in lst]
    summary = {s: sum(1 for r in flat if r.status == s)
               for s in RESULTS}
    return {"tiers": {k: [r.to_dict() for r in v] for k, v in tiers.items()},
            "summary": summary,
            "agent_evals": "gated: run `eval --skill <id>` when an agent "
                           "CLI is installed"}


DEFAULT_ROUTING_PROBES = [
    ("Erstelle eine barrierefreie Astro-Website",
     ["astro", "accessibility"]),
    ("Optimiere die Performance eines Godot-Spiels",
     ["godot"]),
    ("Audit the security of our Next.js dashboard",
     ["ultimate-security-hardening", "react-nextjs"]),
]
