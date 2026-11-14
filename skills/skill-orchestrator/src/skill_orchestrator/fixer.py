"""Auto-fix: proposals and diffs, dry-run by default.

Applied ONLY with explicit --apply. Never deletes skills, never merges
large content, never touches global config, never installs, never
commits. Every applied fix is a minimal textual edit, reversible via
git (repo is the backup — see AGENTS.md)."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .discovery import Discovery
from .validator import validate_skill


@dataclass
class Fix:
    skill: str
    file: str
    kind: str
    rationale: str
    old: str
    new: str
    safe: bool = True

    def diff(self) -> str:
        return "".join(difflib.unified_diff(
            self.old.splitlines(keepends=True),
            self.new.splitlines(keepends=True),
            fromfile=f"a/{self.file}", tofile=f"b/{self.file}"))


def propose(root, skill_ids: list[str] | None = None) -> list[Fix]:
    disc = Discovery(root)
    fixes: list[Fix] = []
    for dir_name, skill in sorted(disc.skills().items()):
        if skill_ids and dir_name not in skill_ids:
            continue
        if skill.yaml_error or skill.is_symlink:
            continue
        rep = validate_skill(skill)
        text = skill.skill_md.read_text(encoding="utf-8")
        fixes += _name_fixes(dir_name, skill, text, rep)
        fixes += _link_fixes(skill, text, rep)
    return [f for f in fixes if f.old != f.new]


def _name_fixes(dir_name, skill, text, rep) -> list[Fix]:
    out = []
    if any(f.check == "meta.name.dirmatch" for f in rep.findings):
        m = re.search(r"^(name:[ \t]*)(.+?)[ \t]*$", text, re.MULTILINE)
        if m and m.group(2).strip("\"'") != dir_name:
            out.append(Fix(dir_name, "SKILL.md", "name-dir-match",
                           f"name must equal directory (repo rule)",
                           m.group(0), f"{m.group(1)}{dir_name}"))
    return out


def _link_fixes(skill, text, rep) -> list[Fix]:
    out: list[Fix] = []
    base = skill.path
    from .validator import _LINK_RE
    for m in _LINK_RE.finditer(text):
        target = m.group(1).strip()
        if (base / target).exists():
            continue
        cand = _nearest(base, target)
        if cand:
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start:line_end if line_end != -1 else None]
            out.append(Fix(skill.dir_name, "SKILL.md", "link-target",
                           f"'{target}' missing; nearest real file '{cand}'",
                           line, line.replace(f"({target})", f"({cand})")))
    return out


def _nearest(base: Path, target: str) -> str | None:
    want = Path(target)
    stem = want.stem
    best = None
    for p in base.rglob(f"{stem}*"):
        if p.is_file():
            rel = str(p.relative_to(base))
            if best is None or len(rel) < len(best):
                best = rel
    return best


def apply(root, fixes: list[Fix]) -> list[dict]:
    results = []
    for f in fixes:
        if not f.safe:
            results.append({"skill": f.skill, "applied": False,
                            "why": "unsafe proposal"})
            continue
        path = _resolve_skill_file(root, f)
        try:
            text = path.read_text(encoding="utf-8")
            if f.old not in text:
                results.append({"skill": f.skill, "applied": False,
                                "why": "stale anchor"})
                continue
            path.write_text(text.replace(f.old, f.new, 1), encoding="utf-8")
            results.append({"skill": f.skill, "applied": True,
                            "kind": f.kind, "revert": f"git checkout -- {path}"})
        except OSError as exc:
            results.append({"skill": f.skill, "applied": False,
                            "why": str(exc)})
    return results


def _resolve_skill_file(root, f: Fix) -> Path:
    disc = Discovery(Path(root))
    d = disc.find_skill_dir(f.skill)
    if d is None:
        raise FileNotFoundError(f.skill)
    return d / f.file
