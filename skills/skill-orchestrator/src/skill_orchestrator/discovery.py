"""Repository-aware skill discovery.

Finds skills by their actual files (a skill is a directory containing
SKILL.md), resolves symlinks, avoids cycles and generated directories,
and records facts — never inventions — about each skill.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from . import frontmatter as fm

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             ".artifacts", "out", ".cache", ".pytest_cache", ".mypy_cache"}

CATALOG_VERSION = 1

# Directory-name → catalog id normalization is identity; skills are keyed by
# directory name per repository convention (name == directory).


def find_repo_root(start: Path | None = None) -> Path:
    """Locate the skillset repository root from an explicit env override,
    the current directory, or this file's ancestors."""
    env = os.environ.get("SKILL_ORCHESTRATOR_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "skills").is_dir():
            return p
        raise FileNotFoundError(f"SKILL_ORCHESTRATOR_ROOT={env} has no skills/ dir")
    candidates = []
    if start:
        candidates.append(Path(start).resolve())
    candidates.append(Path.cwd().resolve())
    here = Path(__file__).resolve()
    candidates.extend([here.parent.parent.parent, here.parent.parent,
                       here.parent])
    for base in candidates:
        for probe in _self_and_parents(base, 6):
            if (probe / "skills").is_dir() and any(
                    (probe / "skills").glob("*/SKILL.md")):
                return probe
    raise FileNotFoundError(
        "no skillset repository root found (need a directory with "
        "skills/*/SKILL.md); set SKILL_ORCHESTRATOR_ROOT")


def _self_and_parents(p: Path, limit: int) -> Iterator[Path]:
    cur = p
    for _ in range(limit + 1):
        yield cur
        if cur.parent == cur:
            return
        cur = cur.parent


@dataclass
class DiscoveredSkill:
    dir_name: str
    path: Path                      # resolved, absolute
    skill_md: Path
    frontmatter: dict = field(default_factory=dict)
    body: str = ""
    yaml_error: str | None = None
    is_symlink: bool = False
    link_target: str | None = None
    broken: bool = False

    @property
    def name(self) -> str:
        return str(self.frontmatter.get("name") or self.dir_name)

    def rel(self, root: Path) -> str:
        try:
            return str(self.path.relative_to(root))
        except ValueError:
            return str(self.path)


class Discovery:
    """Walks the repository once and caches per-directory results."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self._skills: dict[str, DiscoveredSkill] | None = None
        self._seen_real: set[Path] = set()

    # -- walking ----------------------------------------------------------
    def _iter_dirs(self) -> Iterator[tuple[Path, bool]]:
        """Yield (dir_path, is_symlink) depth-first, cycle-safe."""
        def walk(d: Path) -> Iterator[tuple[Path, bool]]:
            try:
                entries = sorted(d.iterdir(), key=lambda p: p.name)
            except OSError:
                return
            for entry in entries:
                if entry.name in SKIP_DIRS:
                    continue
                if entry.is_symlink():
                    if entry.is_dir():
                        if not self._link_ok(entry):
                            continue
                        yield entry, True
                        continue  # do not descend through links (cycle guard)
                elif entry.is_dir():
                    real = self._realpath(entry)
                    if real in self._seen_real:
                        continue
                    self._seen_real.add(real)
                    yield entry, False
                    yield from walk(entry)
        root_real = self._realpath(self.root)
        self._seen_real.add(root_real)
        yield from walk(self.root)

    @staticmethod
    def _link_ok(link: Path) -> bool:
        try:
            target = link.resolve()
            return target.exists()
        except OSError:
            return False

    @staticmethod
    def _realpath(p: Path) -> Path:
        try:
            return p.resolve()
        except OSError:
            return p

    # -- results ----------------------------------------------------------
    def skills(self) -> dict[str, DiscoveredSkill]:
        if self._skills is not None:
            return self._skills
        found: dict[str, DiscoveredSkill] = {}
        for d, is_link in self._iter_dirs():
            md = d / "SKILL.md"
            if not md.is_file():
                continue
            skill = self._read_skill(d, md, is_link)
            key = d.name
            if key in found:
                found[key].broken = found.get(key, skill).broken
            found[key] = skill
        self._skills = found
        return found

    def _read_skill(self, d: Path, md: Path, is_link: bool) -> DiscoveredSkill:
        skill = DiscoveredSkill(
            dir_name=d.name,
            path=self._realpath(d),
            skill_md=md,
            is_symlink=is_link,
            link_target=str(d.resolve()) if is_link else None,
        )
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            skill.yaml_error = f"unreadable SKILL.md: {exc}"
            skill.broken = True
            return skill
        parsed = fm.parse(text)
        skill.frontmatter = parsed.data
        skill.body = parsed.body
        skill.yaml_error = parsed.yaml_error
        return skill

    def skill_dirs(self) -> list[Path]:
        """All directories containing a SKILL.md, sorted."""
        return sorted((s.path for s in self.skills().values()), key=str)

    def find_skill_dir(self, name: str) -> Path | None:
        s = self.skills().get(name)
        return s.path if s else None


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def _last_modified(path: Path, root: Path) -> str | None:
    """Last commit date via git (ISO date); None when git unavailable."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            cwd=root, capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        from datetime import datetime
        return datetime.fromtimestamp(
            max((p.stat().st_mtime for p in path.rglob("*") if p.is_file()),
                default=path.stat().st_mtime)
        ).isoformat(timespec="seconds")
    except OSError:
        return None


def _file_inventory(skill_dir: Path) -> dict:
    inv: dict[str, list[str]] = {"scripts": [], "references": [],
                                 "tests": [], "assets": [], "workflows": [],
                                 "templates": [], "other": []}
    for p in sorted(skill_dir.rglob("*")):
        if p.is_dir() or any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = str(p.relative_to(skill_dir))
        if rel == "SKILL.md":
            continue
        top = p.parts[0] if len(p.parts) > 1 else None
        bucket = {"scripts": "scripts", "references": "references",
                  "tests": "tests", "assets": "assets",
                  "workflows": "workflows", "templates": "templates"}.get(top or "")
        (inv[bucket] if bucket else inv["other"]).append(rel)
    return {k: v for k, v in inv.items() if v}


def build_catalog(disc: Discovery) -> dict:
    """Machine-readable inventory. Facts only; quality fields are filled
    by the auditor, never guessed here."""
    skills = []
    all_skills = disc.skills()
    names = set(all_skills)
    for dir_name in sorted(names):
        s = all_skills[dir_name]
        body = s.body or ""
        # deterministic cross-skill mentions (dependencies/collaboration edges)
        mentioned = sorted(
            {n for n in names if n != dir_name and n in body + " " +
             json.dumps(s.frontmatter, ensure_ascii=False)})
        entry = {
            "id": dir_name,
            "name": s.name,
            "name_matches_dir": s.name == dir_name,
            "description": str(s.frontmatter.get("description") or ""),
            "dir": s.rel(disc.root),
            "skill_md": s.rel(disc.root) + "/SKILL.md",
            "frontmatter_keys": sorted(str(k) for k in s.frontmatter),
            "extra_frontmatter_keys": sorted(
                str(k) for k in s.frontmatter
                if k not in ("name", "description", "license",
                             "compatibility", "metadata", "allowed-tools")),
            "frontmatter_error": s.yaml_error,
            "symlink": s.is_symlink,
            "body_lines": len(body.splitlines()),
            "body_bytes": len(body.encode("utf-8")),
            "mentions": mentioned,
            "files": _file_inventory(s.path),
            "has_tests": bool((s.path / "tests").is_dir()
                              or list(s.path.glob("test_*.py"))),
            "has_scripts": (s.path / "scripts").is_dir(),
            "last_modified": _last_modified(s.path, disc.root),
            "quality": None,  # filled by audit
        }
        skills.append(entry)
    return {
        "catalog_version": CATALOG_VERSION,
        "repository": str(disc.root),
        "skill_count": len(skills),
        "skills": skills,
    }
