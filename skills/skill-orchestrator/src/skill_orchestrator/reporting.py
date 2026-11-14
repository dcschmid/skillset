"""Reports: Markdown + JSON, prioritized task list, regression
comparation against stored snapshots. Snapshots are stored under the
configurable output dir (default <repo>/.artifacts/skill-orchestrator/)."""

from __future__ import annotations

import json
import time
from pathlib import Path

OUTPUT_DIRNAME = ".artifacts/skill-orchestrator"

PRIORITY_BY_SEVERITY = {"error": "P0", "warn": "P2", "info": "P3"}


def output_dir(root: Path, override: str | None = None) -> Path:
    d = Path(override) if override else Path(root) / OUTPUT_DIRNAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def snapshot_path(root: Path, override=None) -> Path:
    return output_dir(root, override) / "last-audit.json"


def save_snapshot(root: dict, root_path, override=None) -> Path:
    p = snapshot_path(Path(root_path), override)
    slim = {k: root[k] for k in
            ("generated_at", "profile", "cycles", "conflicts")}
    slim["scores"] = {k: v["score"]["score"] for k, v in
                      root["audits"].items()}
    slim["errors"] = {
        sid: [f["check"] for f in v["validation"]["findings"]
              if f["severity"] == "error"]
        for sid, v in root["audits"].items()}
    slim["skill_count"] = root["catalog"]["skill_count"]
    p.write_text(json.dumps(slim, indent=1), encoding="utf-8")
    return p


def compare_snapshot(current: dict, root_path, override=None) -> list[str]:
    p = snapshot_path(Path(root_path), override)
    if not p.exists():
        return []
    try:
        prev = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["previous snapshot unreadable — no regression baseline"]
    notes: list[str] = []
    if prev.get("skill_count") != current["catalog"]["skill_count"]:
        notes.append(f"skill count {prev.get('skill_count')} → "
                     f"{current['catalog']['skill_count']}")
    for sid, sc in current_scores(current).items():
        old = prev.get("scores", {}).get(sid)
        if old is None:
            notes.append(f"{sid}: NEW skill (no baseline)")
        elif sc < old:
            notes.append(f"{sid}: score regression {old} → {sc}")
    for sid, errs in current_errors(current).items():
        gone = set(prev.get("errors", {}).get(sid, [])) - set(errs)
        if gone - {""} and errs:
            for e in errs:
                notes.append(f"{sid}: NEW error {e}")
    return notes


def current_scores(audit: dict) -> dict:
    return {k: v["score"]["score"] for k, v in audit["audits"].items()}


def current_errors(audit: dict) -> dict:
    return {sid: [f["check"] for f in v["validation"]["findings"]
                  if f["severity"] == "error"]
            for sid, v in audit["audits"].items()}


def to_markdown(audit: dict) -> str:
    cat = audit["catalog"]
    L = [f"# Skill Audit — {cat['repository']}",
         "",
         f"Profile: `{audit['profile']}` · {audit['generated_at']}",
         "",
         "## Inventory", "",
         "| Skill | Score | Grade | Errors | Blockers | Tests |",
         "|---|--:|---|--:|--:|---|"]
    for sid in sorted(audit["audits"]):
        a = audit["audits"][sid]["score"]
        entry = next(s for s in cat["skills"] if s["id"] == sid)
        L.append(f"| {sid} | {a['score']} | {a['grade']} | "
                 f"{len(current_errors(audit).get(sid, []))} | "
                 f"{len(a['blockers'])} | "
                 f"{'yes' if entry['has_tests'] else 'MISSING'} |")
    valid = sum(1 for a in audit["audits"].values()
                if a["score"]["score"] >= 70)
    L += ["", f"**{cat['skill_count']} skills · {valid} ≥70 · "
          f"{sum(len(a['score']['blockers']) for a in audit['audits'].values())} "
          "blockers · cycles: {0}**".format(len(audit["cycles"])), ""]
    L.append("## Overlaps (classified, evidence-linked)")
    L.append("")
    for o in audit["overlaps"][:25]:
        L.append(f"- **{o['classification']}** {o['skills'][0]} ↔ "
                 f"{o['skills'][1]} (sim {o['similarity']}, "
                 f"sev {o['severity']}): {o['proposal']}")
        for ev in o["evidence"][:2]:
            L.append(f"    - {ev}")
    if audit["cycles"]:
        L += ["", "## Cycles"] + [f"- {' → '.join(c)}"
                                  for c in audit["cycles"]]
    regress = audit.get("regressions") or []
    if regress:
        L += ["", "## Regressions vs last snapshot"] + \
             [f"- {r}" for r in regress]
    L += ["", "## Prioritized tasks"]
    tasks = _tasks(audit)
    for prio in ("P0", "P1", "P2", "P3"):
        for t in tasks:
            if t[0] == prio:
                L.append(f"- **{prio}** {t[1]}")
    L.append("")
    L.append("_Unchecked categories are scored 0 credit, not full marks; "
             "see per-skill `unchecked` in JSON. Numeric score never "
             "replaces a test result._")
    return "\n".join(L)


def _tasks(audit: dict):
    out = []
    for sid in sorted(audit["audits"]):
        a = audit["audits"][sid]
        for f in a["validation"]["findings"]:
            if f["severity"] == "error":
                out.append(("P0" if f["check"].startswith("meta.") else
                            "P1", f"{sid}: {f['check']} — {f['message']}"))
        for u in a["score"]["unchecked"]:
            out.append(("P2", f"{sid}: {u}"))
        if not next(s for s in audit["catalog"]["skills"]
                    if s["id"] == sid)["has_tests"]:
            out.append(("P2", f"{sid}: add tests/"))
    for o in audit["overlaps"]:
        if o["classification"] in ("problematic", "conflict"):
            out.append(("P1", f"overlap {o['skills'][0]}↔{o['skills'][1]}: "
                        f"{o['proposal']}"))
    for cyc in audit["cycles"]:
        out.append(("P0", f"break dependency cycle {'→'.join(cyc)}"))
    return out
