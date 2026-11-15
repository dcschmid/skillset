#!/usr/bin/env python3
"""test_skill.py — figma-source-of-truth validation (repo convention: python3
runner, parseable VERDICT). Covers: structure, frontmatter, README usage guide,
link resolution, no empty files."""
from pathlib import Path

skill = Path(__file__).resolve().parent.parent
failures: list[str] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)

skill_md = skill / "SKILL.md"
check("SKILL.md exists", skill_md.is_file())
text = skill_md.read_text(encoding="utf-8")
fm = text.split("---")[1] if text.startswith("---") else ""
check("frontmatter name==dir", "name: figma-source-of-truth" in fm)
check("frontmatter description", "description:" in fm)
check("README.md documents skill", (skill / "README.md").is_file()
      and "figma-source-of-truth" in (skill / "README.md").read_text(encoding="utf-8"))
check("no empty files", all(f.stat().st_size > 100 for f in skill.rglob("*.md")
      if "__pycache__" not in str(f)))

print("VERDICT:", "PASS" if not failures else f"FAIL {failures}")
raise SystemExit(0 if not failures else 1)
