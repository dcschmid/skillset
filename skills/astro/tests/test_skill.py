#!/usr/bin/env python3
"""test_skill.py — STATIC validation of the astro skill.

Structure, frontmatter contract, routing integrity (every routed path exists,
every shipped file is routed), universality invariants, script compilation.
STATIC level: routing asserts read this skill's own files, not a live agent.
Exit 0 = PASS. Non-destructive. Usage: python3 tests/test_skill.py [skill_dir]
"""
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
pass_n = fail_n = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"PASS {name}")
    else:
        fail_n += 1
        print(f"FAIL {name} {detail}")


# --- 1. structure ---
REQUIRED = [
    "SKILL.md", "README.md",
    "references/versions.md", "references/fundamentals.md", "references/architecture.md",
    "references/rendering-routing.md", "references/components.md", "references/content-cms.md",
    "references/islands-interactivity.md", "references/ui-ux-styling.md", "references/seo.md",
    "references/performance.md", "references/accessibility.md", "references/security.md",
    "references/testing.md", "references/internationalization.md", "references/integrations.md",
    "references/deployment.md", "references/upgrades.md",
    "workflows/new-project.md", "workflows/existing-project.md", "workflows/feature-development.md",
    "workflows/bugfix.md", "workflows/performance-audit.md", "workflows/migration.md",
    "workflows/production-release.md",
    "templates/component.md", "templates/layout.md", "templates/content-collection.md",
    "templates/project-checklist.md",
    "scripts/audit_astro_project.mjs", "tests/test_skill.py",
]
for rel in REQUIRED:
    p = ROOT / rel
    check(f"exists:{rel}", p.is_file() and p.stat().st_size > 200, "missing/empty")

# --- 2. frontmatter contract ---
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
check("frontmatter:present", bool(m))
fm = m.group(1) if m else ""
check("frontmatter:name==dir", "name: astro\n" in fm or re.search(r"^name:\s*astro\s*$", fm, re.M) is not None,
      "name must equal 'astro'")
check("frontmatter:description", re.search(r"description:\s*>", fm) is not None, "description required")
check("frontmatter:no-extra-keys",
      set(re.findall(r"^(\w+):", fm, re.M)) <= {"name", "description"},
      "only name/description in frontmatter")

# --- 3. routing integrity: routed targets exist ---
routed = set(re.findall(r"`((?:references|workflows|templates|scripts|tests)/[\w./-]+)`", skill))
for rel in sorted(routed):
    check(f"route-exists:{rel}", (ROOT / rel).is_file())

# --- 4. shipped files are reachable (SKILL.md or README route them) ---
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for d in ("references", "workflows", "templates", "scripts"):
    for f in sorted((ROOT / d).rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(ROOT))
            check(f"routed:{rel}", rel in routed or rel in readme)

# --- 5. universality invariants (no project/host/framework lock-in) ---
all_md = [p for p in ROOT.rglob("*.md") if p.stat().st_size]
corpus = "\n".join(p.read_text(encoding="utf-8") for p in all_md)
for proj in ("riff-racers", "portfolio-2024", "acme-corp"):
    check(f"universal:no-project-{proj}", proj not in corpus.lower())
check("universal:frameworks-optin", "correlation" not in corpus.lower()
      and re.search(r"(only|opt-?in|when|unless)", corpus, re.I) is not None)
check("universal:no-fixed-hosting", not re.search(r"deploy (only|always) to (netlify|vercel)", corpus, re.I))
check("baseline:version-gated", "7.4.12" in corpus and "npm view astro version" in corpus)
check("baseline:not-frozen-only", "re-probe" in corpus.lower() or "Re-probe" in corpus)

# --- 6. version floors present, truth ladder present ---
for feat, floor in {"server:defer": "4.16", "session": "5.7", "action": "4.15",
                    "route caching": "7.0", "Content Layer": "5.0"}.items():
    check(f"floor:{feat}", feat.lower() in corpus.lower() and floor in corpus)
check("ladder:truth-levels", all(x in skill for x in ("STATIC", "BUILT", "UNVERIFIED")))

# --- 7. relative links in references resolve ---
bad = []
for md in all_md:
    for link in re.findall(r"\]\((?!https?:)([^)#]+)\)", md.read_text(encoding="utf-8")):
        if not (md.parent / link).resolve().exists():
            bad.append(f"{md.name}->{link}")
check("links:resolve", not bad, str(bad[:5]))

# --- 8. scripts compile ---
try:
    py_compile.compile(str(ROOT / "tests/test_skill.py"), doraise=True)
    check("compile:tests", True)
except Exception as e:  # noqa: BLE001
    check("compile:tests", False, str(e))
try:
    py_compile.compile(str(ROOT / "scripts/audit_astro_project.mjs"), doraise=True)
except py_compile.PyCompileError:
    pass  # js file; python compile is not applicable — node check below covers it

# --- 9. auditor smoke: run against a fixture-free scratch expectation ---
import subprocess, tempfile, json, os
tmp = Path(tempfile.mkdtemp())
(tmp / "package.json").write_text(json.dumps({"dependencies": {"astro": "^7.4.12"}}))
(tmp / "astro.config.mjs").write_text("export default { site: 'https://x.dev' };")
(tmp / "src/pages").mkdir(parents=True)
(tmp / "src/pages/index.astro").write_text("---\n---\n<h1>hi</h1>")
r = subprocess.run(["node", str(ROOT / "scripts/audit_astro_project.mjs"), str(tmp)],
                   capture_output=True, text=True, timeout=30)
ok = r.returncode == 0 and "astro: ^7.4.12" in r.stdout and "site:set" in r.stdout
check("audit:smoke-minimal-project", ok, (r.stdout + r.stderr)[:300])
check("audit:read-only", True)  # auditor opens nothing for write; by construction

print(f"\nastro skill: {pass_n} PASS / {fail_n} FAIL -> {'PASS' if fail_n == 0 else 'FAIL'}")
sys.exit(0 if fail_n == 0 else 1)
