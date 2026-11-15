#!/usr/bin/env python3
"""test_skill.py — playwright validation (repo convention: python3 runner,
parseable VERDICT). Headless by design: checks structure, decoupling, and the
wrapper contract without launching a browser (that needs a CLI and is the
user's runtime, asserted only when one exists)."""
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
check("frontmatter name==dir", "name: playwright" in fm)
check("frontmatter description", "description:" in fm)
check("USAGE.md mirrors skill", (skill / "USAGE.md").is_file()
      and "playwright" in (skill / "USAGE.md").read_text(encoding="utf-8"))
check("stack-decoupled (no mm-* / CODEX_HOME)",
      "mm-playwright" not in text and "CODEX_HOME" not in text
      and "CODEX_HOME" not in (skill / "references/cli.md").read_text())
check("session separation", "session" in text.lower())
check("runtime honesty", "Never report an unrun browser check as passed" in text
      or "never report" in text.lower() or "Never report" in text)
check("references linked", "references/cli.md" in text and "references/workflows.md" in text)
wrapper = skill / "scripts/playwright_cli.sh"
check("wrapper resolves $PLAYWRIGHT_CLI", "PLAYWRIGHT_CLI" in wrapper.read_text())
check("upstream provenance kept", (skill / "upstream.json").is_file())
check("no empty files", all(f.stat().st_size > 100 for f in skill.rglob("*.md")
      if "__pycache__" not in str(f)))

print("VERDICT:", "PASS" if not failures else f"FAIL {failures}")
raise SystemExit(0 if not failures else 1)
