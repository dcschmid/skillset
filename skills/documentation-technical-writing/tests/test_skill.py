#!/usr/bin/env python3
"""test_skill.py — validation of the documentation-technical-writing skill.

Static: frontmatter contract, routing integrity (every referenced file exists),
action-table integrity, template sanity. Dynamic: runs scripts/ against
in-repo fixtures (healthy + stale project) and asserts verdicts/exit codes.
Exit 0 = PASS. Non-destructive (fixtures built under a temp dir).

Usage: python3 tests/test_skill.py [skill_dir]
"""
import json
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
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


# ---------- 1. frontmatter contract ----------
skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
check("frontmatter.parses", bool(fm))
check("frontmatter.name_matches_dir", bool(fm) and "name: documentation-technical-writing" in fm.group(1))
check("frontmatter.description_present",
      bool(fm) and re.search(r"description:", fm.group(1)) and len(fm.group(1)) > 200)

# ---------- 2. routing integrity ----------
routed = set(re.findall(r"(?:references|assets|scripts|tests)/[\w./-]+\.(?:md|py|template\.md)", skill_md))
dead = [t for t in sorted(routed) if not (ROOT / t).is_file() or (ROOT / t).stat().st_size == 0]
check("routing.targets_exist", not dead, str(dead))

# ---------- 3. actions promised in repo spec all present ----------
for action in ("/docs-audit", "/docs-create", "/docs-fix", "/docs-sync", "/docs-readme",
               "/docs-api", "/docs-architecture", "/docs-guide", "/docs-adr",
               "/docs-check", "/docs-site"):
    check(f"actions.{action.strip('/')}", action in skill_md)

# ---------- 4. evidence tiers + honest verdicts stated ----------
body = skill_md[skill_md.find("---", 3) + 3:]
for tier in ("VERIFIED", "DOCUMENTED", "PLAUSIBLE", "UNKNOWN"):
    check(f"tiers.{tier}", tier in body)
check("verdicts.not_run", "NOT RUN" in body)

# ---------- 5. scripts compile ----------
for script in sorted((ROOT / "scripts").glob("*.py")):
    try:
        py_compile.compile(str(script), doraise=True)
        check(f"scripts.compile.{script.name}", True)
    except py_compile.PyCompileError as e:
        check(f"scripts.compile.{script.name}", False, str(e))

# ---------- 6. fixtures: dynamic behavior ----------
tmp = Path(tempfile.mkdtemp(prefix="dtw-test-"))


def run(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *argv],
                          capture_output=True, text=True)


# healthy fixture: README answers everything, commands match package.json
good = tmp / "good"
(good / "docs").mkdir(parents=True)
(good / "package.json").write_text(json.dumps(
    {"scripts": {"dev": "vite", "build": "vite build", "test": "vitest run"}}))
(good / "README.md").write_text(
    "# Good\n\n## Install\n\nnpm install\n\n## Run\n\nnpm run dev\n\n"
    "## Test\n\nnpm run test\n\n## Requirements\n\nNode 22\n\nsee [guide](docs/guide.md)\n")
(good / "docs" / "guide.md").write_text("# Guide\n\n## Setup\n\nsteps\n")

r = run("docs_check.py", str(good))
check("check.good.exit0", r.returncode == 0, r.stdout[-200:] + r.stderr[-200:])

r = run("docs_audit.py", str(good))
check("audit.good.no_p0p1", r.returncode == 0, r.stdout[-300:])

# stale fixture: broken link, dead command, stale anchor, secret, heading jump
stale = tmp / "stale"
(stale / "docs").mkdir(parents=True)
(stale / "package.json").write_text(json.dumps({"scripts": {"dev": "vite"}}))
(stale / "README.md").write_text(
    "# Stale\n\n#### Skipped level\n\nnpm run deploy\n\n[missing](docs/nope.md)\n\n"
    "[see setup](docs/guide.md#gone)\n\n"
    "API key: sk-abcdefghijklmnopqrstuvwxyz1234\n")
(stale / "docs" / "guide.md").write_text("# Guide\n\n## Setup\n\nsteps\n")

r = run("docs_check.py", "--json", str(stale))
rep = json.loads(r.stdout)
findings = rep["checks"][0]["findings"]
msgs = " | ".join(f["message"] for f in findings)
check("check.stale.detects_broken_link", "docs/nope.md" in msgs)
check("check.stale.detects_anchor", "#gone" in msgs)
check("check.stale.detects_heading_jump", "heading jumps" in msgs)
check("check.stale.detects_secret", any(f["priority"] == "P0" for f in findings))
check("check.stale.secret_value_not_echoed", "sk-abcdefghijklmnopqrstuvwxyz1234" not in msgs)
check("check.stale.exit2_on_fail", r.returncode == 2, str(r.returncode))

r = run("docs_audit.py", "--json", str(stale))
arep = json.loads(r.stdout)
amsgs = " | ".join(f["message"] for f in arep["checks"][0]["findings"])
check("audit.stale.detects_stale_command", "deploy" in amsgs, amsgs[:200])
check("audit.stale.secret_p0", any(f["priority"] == "P0" for f in arep["checks"][0]["findings"]))

# sync: fixture is not a git repo -> plan empty, exit 0, never edits
r = run("docs_sync.py", str(good))
check("sync.nongit.graceful", r.returncode == 0 and "git" in (r.stdout + r.stderr).lower())
check("sync.nongit.no_writes", (good / "docs" / "guide.md").read_text() == "# Guide\n\n## Setup\n\nsteps\n")

# absence honesty: tools missing on this machine => NOT RUN rows, not PASS
missing_tools = [t for t in ("markdownlint-cli2", "vale", "lychee") if shutil.which(t) is None]
ext = [c for c in rep["checks"] if c["id"].startswith("ext:")]
check("check.absence.not_run",
      all(c["verdict"] == "NOT RUN" for c in ext if c["id"].split(":")[1] in missing_tools)
      and len(ext) == 3)

# non-destructive: reports never overwrite an existing file
out = good / "report.json"
out.write_text("original")
run("docs_check.py", "--out", str(out), str(good))
check("emit.nondestructive", out.read_text() == "original", "existing report was overwritten")

# ---------- 7. templates: placeholders, no slop ----------
for tpl in sorted((ROOT / "assets").glob("*.template.md")):
    t = tpl.read_text(encoding="utf-8")
    check(f"templates.nonempty.{tpl.name}", len(t) > 80)
    check(f"templates.placeholders.{tpl.name}", "<" in t and ">" in t)
    low = t.lower()
    slop = [w for w in ("delve", "seamless", "robust solution", "in today") if w in low]
    check(f"templates.no_slop.{tpl.name}", not slop, str(slop))

print(f"\n{'PASS' if fail_n == 0 else 'FAIL'} {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
