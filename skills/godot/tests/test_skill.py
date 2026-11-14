#!/usr/bin/env python3
"""test_skill.py — STATIC validation of the godot skill.

Structure, frontmatter contract, routing integrity, universality invariants,
script compilation, and router-content scenarios (which references a task
selects). STATIC level: routing asserts check the SKILL.md tables' content,
not a live LLM call — reported as such. Exit 0 = PASS. Non-destructive.
Usage: python3 tests/test_skill.py [skill_dir]
"""
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
pass_n = fail_n = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"PASS {name}")
    else:
        fail_n += 1
        print(f"FAIL {name} {detail}")


# 1. frontmatter contract (Claude Code / Codex discovery)
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
check("frontmatter.parses", bool(fm))
check("frontmatter.name", bool(fm) and "name: godot" in fm.group(1))
desc = re.search(r"description: >\n(.*?)\n---", skill_md, re.S)
check("frontmatter.description_triggers",
      bool(desc) and "Godot" in desc.group(1) and "4.7.2" in desc.group(1)
      and len(desc.group(1)) > 200)

# 2. every routed reference/workflow/example exists and is non-empty
routed_refs = set(re.findall(r"(?:references|workflows)/[\w./-]+\.md", skill_md))
dead = [t for t in sorted(routed_refs)
        if not (ROOT / t).is_file() or (ROOT / t).stat().st_size == 0]
check("routing.targets_exist", not dead, str(dead))

# 3. universality invariants: no genre/style/engine-tool forced as default
body = skill_md[skill_md.find("---", 3) + 3:]
check("universal.no_racing_default", "racing" not in body.lower()
      or body.lower().count("racing") <= 3)
check("universal.blender_optional", "Blender is optional" in body or "Blender is NOT" in body
      or "OPTIONAL lane" in (ROOT / "references/blender-integration.md").read_text())
for style in ("pixel-art", "voxel-art", "low-poly", "high-poly",
              "stylized-rendering", "realistic-rendering"):
    check(f"style.route.{style}", f"references/{style}.md" in routed_refs)

# 4. version honesty: baseline + channel rule present, no beta-as-stable
check("version.baseline_pinned", "4.7.2" in body and "ed1daf0b" in body)
check("version.beta_gated", "beta" in body.lower())

# 5. truth ladder: UNVERIFIED reporting mandated
check("ladder.unverified", "UNVERIFIED" in body)

# 6. scripts + examples compile / exist
for py in sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py")):
    try:
        py_compile.compile(str(py), doraise=True)
        check(f"py.compiles {py.name}", True)
    except Exception as e:
        check(f"py.compiles {py.name}", False, str(e))
for ex in ("base-project", "pixel-art-scene", "voxel-scene"):
    d = ROOT / "examples" / ex
    ok = all((d / f).is_file() and (d / f).stat().st_size > 0
             for f in ("project.godot", "main.tscn", "main.gd"))
    check(f"example.{ex}", ok)
    if (d / "main.gd").is_file():
        src = (d / "main.gd").read_text()
        check(f"example.{ex}.gdscript_shape",
              src.startswith("extends ") and "func _ready" in src)

# 7. router scenarios: task -> expected reference selection (content check)
style_section = body[body.find("## Style Routing"):body.find("## System Routing")]
system_section = body[body.find("## System Routing"):body.find("## Workflows")]
scenarios = [
    ("pixel platformer", "pixel-art.md", style_section, "pixel-art"),
    ("voxel world", "voxel-art.md", style_section, "voxel"),
    ("realistic rpg", "realistic-rendering.md", style_section, "realistic"),
    ("multiplayer co-op", "multiplayer.md", system_section, "multiplayer"),
    ("save system", "scenes-and-resources.md", system_section, "save"),
]
for name, target, section, kw in scenarios:
    line = next((ln for ln in section.splitlines() if kw in ln.lower()), "")
    check(f"route.{name}", target in line, f"'{target}' not on '{kw}' line")

print(f"\n{pass_n} PASS / {fail_n} FAIL — STATIC level (routing = content "
      "asserts; live-agent behavior and engine runtime = separate levels)")
sys.exit(0 if fail_n == 0 else 1)
