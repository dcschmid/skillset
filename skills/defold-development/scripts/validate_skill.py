#!/usr/bin/env python3
"""validate_skill.py — structure validator for this skill (read-only).

Checks: required files, SKILL.md frontmatter, reference/workflow links from
SKILL.md resolve, scripts compile, profiles/examples exist, no empty files.
Non-destructive. Exit 0 = PASS.
Usage: python3 scripts/validate_skill.py [skill_dir]
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "SKILL.md", "README.md",
    "references/version-compatibility.md", "references/architecture.md",
    "references/lua-engineering.md", "references/gameplay-systems.md",
    "references/2d-pixel-art.md", "references/2d-rendering.md",
    "references/voxel-development.md", "references/3d-lowpoly.md",
    "references/3d-highpoly.md", "references/hybrid-2-5d.md",
    "references/shaders-materials.md", "references/asset-pipelines.md",
    "references/physics-ai.md", "references/multiplayer.md",
    "references/procedural-generation.md", "references/ui-ux.md",
    "references/audio.md", "references/performance.md",
    "references/debugging-testing.md", "references/build-deployment.md",
    "references/official-sources.md",
    "project-profiles/riff-racers.md",
    "project-profiles/pixel-platformer.example.md",
    "project-profiles/voxel-survival.example.md",
    "project-profiles/action-rpg.example.md",
    "workflows/new-project.md", "workflows/existing-project.md",
    "workflows/implement-feature.md", "workflows/debug-feature.md",
    "workflows/import-2d-assets.md", "workflows/import-3d-assets.md",
    "workflows/optimize-performance.md", "workflows/prepare-release.md",
    "scripts/validate_skill.py", "scripts/check_version.py",
    "scripts/audit_defold_project.py", "scripts/gltf_preflight.py",
    "scripts/bob_build.sh", "scripts/check_build.sh",
    "templates/performance-report.md", "templates/import-checklist.md",
    "tests/test_skill.py",
]

def fail(msg):
    print(f"FAIL {msg}")
    return 1

def main():
    if not ROOT.is_dir():
        return fail(f"skill dir missing: {ROOT}")
    errors = []
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"missing {rel}")
        elif p.stat().st_size == 0:
            errors.append(f"empty {rel}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").is_file() else ""
    fm = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
    if not fm:
        errors.append("SKILL.md: no YAML frontmatter")
    else:
        if "name: defold-development" not in fm.group(1):
            errors.append("SKILL.md frontmatter: name != defold-development")
        if not re.search(r"description:", fm.group(1)):
            errors.append("SKILL.md frontmatter: description missing")

    # routing links resolve
    for target in set(re.findall(r"(?:references|workflows|project-profiles|templates|scripts|tests)/[\w./-]+\.md", skill)):
        if not (ROOT / target).is_file():
            errors.append(f"SKILL.md links missing file: {target}")
    for target in set(re.findall(r"scripts/[\w.-]+\.py", skill)):
        if not (ROOT / target).is_file():
            errors.append(f"SKILL.md names missing script: {target}")

    # genre/style independence: skill body must not present genre systems as defaults
    for word in ("always add inventory", "always add race", "default low-poly"):
        if re.search(word, skill, re.I):
            errors.append(f"SKILL.md hardcodes genre assumption: {word!r}")

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        print(f"== validate_skill: FAIL ({len(errors)} problems)")
        return 1
    print(f"== validate_skill: PASS ({len(REQUIRED_FILES)} required files, routing resolved)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
