#!/usr/bin/env python3
"""validate_skill.py — structure validator for the godot skill (read-only).

Checks: required files present + non-empty, SKILL.md frontmatter contract,
every reference/workflow/example routed from SKILL.md resolves, scripts
compile, no empty placeholders. Non-destructive. Exit 0 = PASS.
Usage: python3 scripts/validate_skill.py [skill_dir]
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "SKILL.md", "README.md",
    "references/godot-versions.md", "references/architecture.md",
    "references/gdscript.md", "references/scenes-and-resources.md",
    "references/gameplay-systems.md", "references/pixel-art.md",
    "references/voxel-art.md", "references/low-poly.md",
    "references/high-poly.md", "references/stylized-rendering.md",
    "references/realistic-rendering.md", "references/shaders.md",
    "references/2d-development.md", "references/2-5d-development.md",
    "references/3d-development.md", "references/animation.md",
    "references/physics.md", "references/navigation-and-ai.md",
    "references/multiplayer.md", "references/ui-and-accessibility.md",
    "references/audio.md", "references/asset-pipelines.md",
    "references/blender-integration.md", "references/performance.md",
    "references/testing.md", "references/debugging.md",
    "references/export-and-release.md",
    "workflows/new-project.md", "workflows/implement-feature.md",
    "workflows/pixel-art-workflow.md", "workflows/voxel-art-workflow.md",
    "workflows/blender-to-godot.md", "workflows/optimize-game.md",
    "workflows/debug-project.md", "workflows/project-review.md",
    "workflows/engine-upgrade.md", "workflows/release-build.md",
    "scripts/validate_skill.py", "scripts/check_version.py",
    "scripts/audit_godot_project.py", "scripts/headless_check.sh",
    "examples/base-project/project.godot", "examples/base-project/main.tscn",
    "examples/base-project/main.gd",
    "examples/pixel-art-scene/project.godot", "examples/pixel-art-scene/main.tscn",
    "examples/pixel-art-scene/main.gd", "examples/pixel-art-scene/player.gd",
    "examples/voxel-scene/project.godot", "examples/voxel-scene/main.tscn",
    "examples/voxel-scene/main.gd", "examples/voxel-scene/chunk.gd",
    "tests/test_skill.py",
]


def fail(msg: str) -> int:
    print(f"FAIL {msg}")
    return 1


def main() -> int:
    if not ROOT.is_dir():
        return fail(f"skill dir missing: {ROOT}")
    errors = []
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"missing: {rel}")
        elif p.stat().st_size == 0:
            errors.append(f"empty: {rel}")

    skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").is_file() else ""
    fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
    if not fm:
        errors.append("SKILL.md frontmatter missing/unparsable")
    elif "name: godot" not in fm.group(1):
        errors.append("frontmatter name != godot")

    routed = set(re.findall(r"(?:references|workflows|examples)/[\w./-]+", skill_md))
    dead = [t for t in sorted(routed)
            if not (ROOT / t).exists() and not (ROOT / (t + ".md")).is_file()
            and not (ROOT / t).is_dir()]
    dead = [t for t in dead if not t.endswith(("base-project", "pixel-art-scene", "voxel-scene"))]
    if dead:
        errors.append(f"routed targets missing: {dead}")

    for py in sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py")):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as e:
            errors.append(f"py syntax {py.name}: {e}")

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        return 1
    print(f"PASS godot skill structure ({len(REQUIRED_FILES)} required files, "
          f"{len(routed)} routed targets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
