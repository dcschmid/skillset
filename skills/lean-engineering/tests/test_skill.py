#!/usr/bin/env python3
"""test_skill.py — lean-engineering self-test.

System python3, stdlib only, no network, no writes outside temp dirs.
Asserts the skill's static contracts: structure, frontmatter, mode/command
coverage, cross-references, ladder+floor completeness, scenario coverage
(S1-S10 from references/scenarios.md). Scenario EXECUTION is agent-driven
(LLM behavior is verified by inspection per the skill's own honesty rule);
this test proves the shipped instructions cannot silently lose a rule.

Run from repo root:  python3 skills/lean-engineering/tests/test_skill.py
Lines: OK/FAIL per check; final VERDICT: PASS|FAIL. Exit 0/1.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ok = fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"OK   {name}")
    else:
        fail += 1
        print(f"FAIL {name} {detail}")


# ---------- 1 structure ----------
for p in ["SKILL.md", "README.md", "USAGE.md", "references", "tests"]:
    check(f"exists {p}", (ROOT / p).exists())
refs = ["engineering-ladder", "modes", "audit-and-review", "simplify",
        "debt", "scenarios"]
for r in refs:
    check(f"ref {r}.md", (ROOT / "references" / f"{r}.md").is_file())
skill = (ROOT / "SKILL.md").read_text()
readme = (ROOT / "README.md").read_text()
usage = (ROOT / "USAGE.md").read_text()
bodies = {r: (ROOT / "references" / f"{r}.md").read_text() for r in refs}

# no runtime cruft: the skill must ship no scripts/assets (its own rule)
check("no scripts dir", not (ROOT / "scripts").exists())
check("no assets dir", not (ROOT / "assets").exists())

# ---------- 2 frontmatter ----------
fm = re.match(r"---\n(.*?)\n---\n", skill, re.S)
check("frontmatter block", bool(fm))
if fm:
    check("name matches dir", "name: lean-engineering" in fm.group(1))
    check("description present", "description:" in fm.group(1))
    check("argument-hint present", "argument-hint:" in fm.group(1))
    for mode in ["lite", "full", "ultra", "off", "review", "audit",
                 "simplify", "debt", "status", "help"]:
        check(f"hint has {mode}", mode in fm.group(1))
    check("license MIT", "license: MIT" in fm.group(1))

# ---------- 3 SKILL.md core contracts ----------
need_core = ["simplest COMPLETE", "not the shortest", "ladder",
             "whole session", "/lean off", "references/",
             "shortcut: <the limit>, <when to upgrade>"]
for t in need_core:
    check(f"core: {t!r}", t.lower() in skill.lower())
for t in ["lite", "full (default)", "ultra", "off"]:
    check(f"mode table: {t}", t in skill)
for cmd in ["/lean review", "/lean audit", "/lean simplify", "/lean debt",
            "/lean status", "/lean help"]:
    check(f"cmd: {cmd}", cmd in skill)

# ---------- 4 ladder + floor completeness ----------
ladder = bodies["engineering-ladder"]
for rung in ["1. **Necessity", "2. **Existing implementation",
             "3. **Extension over replacement", "4. **Platform/stdlib",
             "5. **Installed dependencies", "6. **Few readable edits",
             "7. **New abstraction"]:
    check(f"ladder {rung[:24]}", rung in ladder)
for floor in ["validation", "authn/authz", "accessibility",
              "concurrency", "performance", "platform compatibility",
              "tests", "explicitly asked"]:
    check(f"floor: {floor}", floor in ladder.lower())
check("line-count-not-metric", "line count" in ladder.lower())
check("nontrivial-logic-check", "assert-based" in ladder)
check("game-stack-clause", "frame budget" in ladder.lower())

# ---------- 5 modes ----------
modes = bodies["modes"]
for m in ["lite", "full", "ultra", "off"]:
    check(f"mode def {m}", m in modes)
check("ultra keeps requested", "NEVER cut" in modes or "never cut" in modes)
for plat in ["Claude Code", "Codex", "oh-my-pi"]:
    check(f"platform {plat}", plat in modes)
check("session stickiness", "sticky" in modes.lower())
check("stateless fallback", "per turn" in modes.lower())

# ---------- 6 audit/review contracts ----------
ar = bodies["audit-and-review"]
for f in ["file:line", "where", "actual problem", "why needless",
          "proposed simplification", "risk", "expected benefit",
          "tests needed"]:
    check(f"finding field {f!r}", f.lower() in ar.lower())
for h in ["duplicate", "dependenc", "abstraction", "config option",
          "workaround", "data flow", "round-trip", "control flow",
          "error handling", "layer"]:
    check(f"audit hunt {h!r}", h.lower() in ar.lower())
check("KEEP rows", "KEEP" in ar)
check("audit read-only", "read-only" in ar.lower())

# ---------- 7 simplify contracts ----------
sm = bodies["simplify"]
for step in ["Understand", "checks", "reversible", "Verify", "revert"]:
    check(f"simplify step {step}", step.lower() in sm.lower())
for keep in ["public API", "validation", "error handling", "baseline"]:
    check(f"simplify keep {keep}", keep.lower() in sm.lower())
check("simplify git-diff", "git diff" in sm)
check("simplify approval", "approval" in sm.lower())

# ---------- 8 debt ledger ----------
debt = bodies["debt"]
for t in ["shortcut:", "LEAN-DEBT.md", "KEEP", "RIPENED", "STALE",
          "reuse beats creation"]:
    check(f"debt: {t}", t in debt)

# ---------- 9 scenarios S1-S10 ----------
sc = bodies["scenarios"]
for n, key in [(1, "dependency"), (2, "helper"), (3, "callers"), (4, "uplicate"),
               (5, "test suite"), (6, "validation"), (7, "abstraction"),
               (8, "complex architecture"), (9, "perf"), (10, "conflict")]:
    check(f"S{n} {key}", f"S{n}" in sc and key.lower() in sc.lower())
check("no-fake-benchmarks", "not a fake benchmark" in sc.lower()
      or "nothing here is a fake benchmark" in sc.lower())

# ---------- 10 README/USAGE ----------
for t in ["Install", "modes", "Commands", "Examples", "collaboration",
          "limits", "Troubleshooting"]:
    check(f"README {t}", t.lower() in readme.lower())
for t in ["Claude Code", "Codex", "oh-my-pi", "install-skills.sh"]:
    check(f"USAGE {t}", t in usage)
check("readme verify cmd", "tests/test_skill.py" in readme)
check("usage mirrors readme", "tests/test_skill.py" in usage)

print(f"\n{ok} checks, {fail} failed")
print("VERDICT:", "PASS" if fail == 0 else "FAIL")
sys.exit(0 if fail == 0 else 1)
