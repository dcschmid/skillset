#!/usr/bin/env python3
"""test_skill.py — semgrep-security validation (repo convention: python3
runner, parseable VERDICT). Covers: structure, frontmatter, USAGE mirror,
evidence discipline, no empty files."""
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
check("frontmatter name==dir", "name: semgrep-security" in fm)
check("frontmatter description", "description:" in fm)
check("USAGE.md mirrors skill", (skill / "USAGE.md").is_file()
      and "semgrep-security" in (skill / "USAGE.md").read_text(encoding="utf-8"))
check("findings-as-evidence discipline", "evidence" in text.lower()
      and "false positives" in text.lower())
check("repo-config precedence", "Repository" in text or "repository" in text)
check("no empty files", all(f.stat().st_size > 100 for f in skill.rglob("*.md")
      if "__pycache__" not in str(f)))

print("VERDICT:", "PASS" if not failures else f"FAIL {failures}")
raise SystemExit(0 if not failures else 1)
