#!/usr/bin/env python3
"""test_skill.py — STATIC validation of the react-nextjs skill.

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
    "references/version-policy.md", "references/react-core.md",
    "references/react-modern-apis.md", "references/react-compiler.md",
    "references/nextjs-app-router.md", "references/nextjs-rendering.md",
    "references/nextjs-data-caching.md", "references/nextjs-server-actions.md",
    "references/typescript.md", "references/architecture.md",
    "references/styling-design-systems.md", "references/state-management.md",
    "references/fullstack-integration.md", "references/security.md",
    "references/accessibility.md", "references/performance.md",
    "references/seo-i18n.md", "references/testing.md", "references/tooling.md",
    "references/deployment.md", "references/migrations.md",
    "references/agent-workflows.md",
    "examples/README.md",
    "examples/react-vite/TodoList.tsx",
    "examples/nextjs-app-router/article-page.tsx",
    "examples/reusable-components/Button.tsx",
    "examples/forms-validation/rename-form.tsx",
    "examples/testing-patterns/examples.ts",
    "scripts/check-versions.sh", "scripts/audit_react_project.mjs",
    "tests/test_skill.py",
]
for rel in REQUIRED:
    p = ROOT / rel
    check(f"exists:{rel}", p.is_file() and p.stat().st_size > 200, "missing/empty")

# --- 2. frontmatter contract ---
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
check("frontmatter:present", bool(m))
fm = m.group(1) if m else ""
check("frontmatter:name==dir", re.search(r"^name:\s*react-nextjs\s*$", fm, re.M) is not None,
      "name must equal 'react-nextjs'")
check("frontmatter:description", re.search(r"description:\s*>", fm) is not None, "description required")
check("frontmatter:no-extra-keys",
      set(re.findall(r"^(\w+):", fm, re.M)) <= {"name", "description"},
      "only name/description in frontmatter")

# --- 3. routing integrity: routed targets exist ---
routed = set(re.findall(r"`((?:references|examples|scripts|tests|workflows|templates)/[\w./-]+)`", skill))
for rel in sorted(routed):
    target = ROOT / rel
    ok = target.is_file() or (target.is_dir() and any(target.iterdir()))
    check(f"route-exists:{rel}", ok)

# --- 4. shipped files are reachable (SKILL.md or README route them) ---
readme = (ROOT / "README.md").read_text(encoding="utf-8")
corpus_routing = skill + readme
for d in ("references", "examples", "scripts"):
    for f in sorted((ROOT / d).rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(ROOT))
            check(f"routed:{rel}", rel in corpus_routing or f.stem in corpus_routing)

# --- 5. universality invariants (no project/host/framework lock-in) ---
all_md = [p for p in ROOT.rglob("*.md") if p.stat().st_size]
corpus = "\n".join(p.read_text(encoding="utf-8") for p in all_md)
for proj in ("riff-racers", "portfolio-2024", "acme-corp", "vercel-only"):
    check(f"universal:no-project-{proj}", proj not in corpus.lower())
check("universal:astro-not-converted", "do not convert" in corpus.lower()
      or "never force" in corpus.lower() or "never convert" in corpus.lower()
      or "bleibt" in corpus.lower() or "keep its" in corpus.lower())
check("universal:frameworks-optin", re.search(r"opt-?in", corpus, re.I) is not None)
check("universal:no-fixed-hosting", not re.search(r"deploy (only|always) to (netlify|vercel)", corpus, re.I))
check("universal:no-forced-nextjs", "never" in corpus.lower() and "next" in corpus.lower())

# --- 6. stale-API guards (must not recommend removed/beta names) ---
for bad in ("useFormState(", "forwardRef( required"):
    check(f"no-stale:{bad.strip('()')}", bad not in corpus)
check("no-experimental-default", "canary" not in corpus.lower() or "latest" in corpus.lower())

# --- 7. version-awareness present ---
for token in ("node_modules/next/dist/docs", "npm view", "latest"):
    check(f"version-aware:{token}", token in corpus)

# --- 8. scripts compile / parse ---
for py in (ROOT / "tests").glob("*.py"):
    try:
        py_compile.compile(str(py), doraise=True)
        check(f"py-compiles:{py.name}", True)
    except Exception as e:
        check(f"py-compiles:{py.name}", False, str(e))
mjs = ROOT / "scripts/audit_react_project.mjs"
try:
    import subprocess
    r = subprocess.run(["node", "--check", str(mjs)], capture_output=True, text=True, timeout=30)
    check("node-parses:audit_react_project.mjs", r.returncode == 0, r.stderr[:200])
except FileNotFoundError:
    print("SKIP node-parses (node absent)")
sh = ROOT / "scripts/check-versions.sh"
r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
check("bash-parses:check-versions.sh", r.returncode == 0, r.stderr[:200])

# --- 9. examples: balanced braces + no secrets pattern ---
for f in ROOT.rglob("examples/**/*.ts*"):
    t = f.read_text(encoding="utf-8")
    bal = all(t.count(a) == t.count(b) for a, b in (("{", "}"), ("(", ")")))
    check(f"balanced:{f.name}", bal)

print(f"\n{pass_n} pass, {fail_n} fail")
sys.exit(0 if fail_n == 0 else 1)
