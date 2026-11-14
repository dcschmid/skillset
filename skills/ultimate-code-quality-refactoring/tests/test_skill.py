#!/usr/bin/env python3
"""test_skill.py — ultimate-code-quality-refactoring self-test.

System python3, stdlib only, no network, no writes outside temp dirs.
Covers spec scenarios: A duplicates, B complexity, C safe fix, D regression
detection, E pre-existing failures, F user changes protected, G no tests,
H unknown language, I monorepo, J audit read-only.

Run from skill root:  python3 tests/test_skill.py
Verdict lines: OK/FAIL per check; final VERDICT: PASS|FAIL. Exit 0/1.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
PY = sys.executable
ok = fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"OK   {name}")
    else:
        fail += 1
        print(f"FAIL {name} {detail}")


def run(script, *args, expect=0):
    r = subprocess.run([PY, str(SCRIPTS / script), *[str(a) for a in args]],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != expect:
        return None, r.stderr.strip()[:300], r.returncode
    return r.stdout, r.stderr, r.returncode


# ---------- 1 structure ----------
for p in ["SKILL.md", "README.md", "references", "scripts", "assets", "tests"]:
    check(f"exists {p}", (ROOT / p).exists())
refs = ["audit-methodology", "architecture-review", "code-smells",
        "refactoring-patterns", "behavior-preservation", "testing-strategy",
        "performance-analysis", "technical-debt", "quality-metrics",
        "language-adapters", "tool-integration", "safety-and-rollback",
        "reporting"]
for r in refs:
    check(f"ref {r}.md", (ROOT / "references" / f"{r}.md").is_file())
scripts = ["detect_project", "run_audit", "collect_metrics", "detect_duplicates",
           "verify_changes", "compare_baseline", "generate_report"]
for s in scripts:
    check(f"script {s}.py", (SCRIPTS / f"{s}.py").is_file())
for t in ["audit-report", "refactoring-plan", "technical-debt-backlog",
          "before-after-report"]:
    check(f"asset {t}.md", (ROOT / "assets" / f"{t}.md").is_file())

# ---------- 2 frontmatter ----------
text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
check("frontmatter present", bool(m))
if m:
    fm = m.group(1)
    check("name matches dir", f"name: {ROOT.name}" in fm)
    check("description present", "description:" in fm)
    low = fm.lower()
    check("desc: trigger hint", "audit" in low and "refactor" in low)
    check("desc: validated-changes hint", "verif" in low or "valid" in low)

# referenced files exist (relative paths in SKILL.md body)
body = text[m.end():] if m else text
for rel in sorted(set(re.findall(r"references/([a-z-]+\.md)", body))):
    check(f"SKILL ref exists {rel}", (ROOT / "references" / rel).is_file())
for rel in sorted(set(re.findall(r"assets/([a-z-]+\.md)", body))):
    check(f"SKILL asset exists {rel}", (ROOT / "assets" / rel).is_file())

# ---------- 3 scripts compile ----------
for s in scripts:
    r = subprocess.run([PY, "-m", "py_compile", str(SCRIPTS / f"{s}.py")],
                       capture_output=True, text=True)
    check(f"py_compile {s}.py", r.returncode == 0, r.stderr[:200])

tmp = Path(tempfile.mkdtemp(prefix="ucqr-test-"))
try:
    # ---------- A duplicates ----------
    out, _, rc = run("detect_duplicates.py", FIXTURES / "duplicate_project",
                     "--window", "5")
    d = json.loads(out) if out else {}
    check("A duplicate groups found", d.get("clone_group_count", 0) >= 1,
          str(d.get("clone_group_count")))

    # ---------- B complexity ----------
    out, _, rc = run("collect_metrics.py", FIXTURES / "complex_project")
    m2 = json.loads(out) if out else {}
    hot = [h for h in m2.get("hotspots", []) if "engine.py" in h["file"]]
    check("B hotspot reported", bool(hot) and hot[0]["max_nesting_depth"] >= 4,
          str(hot[:1]))
    check("B complexity proxy numeric",
          isinstance(m2.get("totals", {}).get("avg_complexity_proxy"), (int, float)))

    # ---------- detection / I monorepo / G declared cmds ----------
    out, _, rc = run("detect_project.py", FIXTURES / "mono_project")
    det = json.loads(out) if out else {}
    check("I monorepo detected", det.get("monorepo", {}).get("detected") is True,
          str(det.get("monorepo")))
    check("I languages present", "python" in det.get("languages", {}))
    check("declared cmds are a list (honest, not executed)",
          isinstance(det.get("test_commands_declared"), list))

    # ---------- H unknown language (lua) ----------
    out, _, rc = run("collect_metrics.py", FIXTURES / "unknown_project")
    uh = json.loads(out) if out else {}
    check("H lua measured generically", uh.get("files_measured", 0) >= 1,
          str(uh)[:120])

    # ---------- J audit read-only ----------
    src = tmp / "proj"
    shutil.copytree(FIXTURES / "duplicate_project", src)
    before = {p: p.read_bytes() for p in src.rglob("*") if p.is_file()}
    out, err, rc = run("run_audit.py", src, "-o", tmp / "bundle")
    after = {p: p.read_bytes() for p in src.rglob("*") if p.is_file()}
    check("J audit mutates no project file", before == after)
    check("J bundle written", any((tmp / "bundle").glob("quality-audit*.json")))
    check("J quick mode works",
          run("run_audit.py", src, "-o", tmp / "bundle", "--quick")[2] == 0)

    # ---------- report ----------
    bundle = sorted((tmp / "bundle").glob("quality-audit*.json"))[0]
    out, _, rc = run("generate_report.py", bundle)
    check("report renders exec-summary", bool(out) and "Executive Summary" in out)
    check("report labels proxies (no fabricated certainty)",
          bool(out) and "prox" in out.lower())

    # ---------- baseline / verify: C, D, E, F ----------
    subprocess.run(["git", "-C", str(src), "init", "-q"], capture_output=True)
    subprocess.run(["git", "-C", str(src), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(src), "-c", "user.email=t@t", "-c",
                    "user.name=t", "commit", "-qm", "base"], capture_output=True)
    (src / "user_dirty.py").write_text("user = 1\n")  # F: user's uncommitted work

    # E: failing command recorded as baseline; re-run must NOT blame the change
    run("verify_changes.py", src, "--save-baseline", "--baseline", tmp / "base.json",
        "--cmd", "python3 -c 'raise SystemExit(1)'")
    base = json.loads((tmp / "base.json").read_text()) if (tmp / "base.json").exists() else {}
    check("E baseline records failing cmd",
          base.get("commands", [{}])[0].get("exit") == 1, str(base)[:150])
    (src / "app.py").write_text((src / "app.py").read_text() + "\n# touched\n")
    out, _, rc = run("verify_changes.py", src, "--baseline", tmp / "base.json",
                     "--cmd", "python3 -c 'raise SystemExit(1)'")
    rep = json.loads(out) if out and out.startswith("{") else {}
    check("E baseline failure not blamed on change",
          rep.get("new_failures_vs_baseline") == [] and rep.get("verdict") != "FAIL",
          str(rep.get("verdict")))

    # D: NEW failure (green baseline cmd now red) => FAIL verdict
    run("verify_changes.py", src, "--save-baseline", "--baseline", tmp / "base2.json",
        "--cmd", "true")
    out, _, rc = run("verify_changes.py", src, "--baseline", tmp / "base2.json",
                     "--cmd", "python3 -c 'raise SystemExit(1)'", expect=1)
    rep = json.loads(out) if out and out.startswith("{") else {}
    check("D new regression detected as FAIL",
          rep.get("verdict") == "FAIL" and len(rep.get("new_failures_vs_baseline", [])) == 1,
          str(rep.get("verdict")))

    # C: green checks + change => PASS
    out, _, rc = run("verify_changes.py", src, "--baseline", tmp / "base2.json",
                     "--cmd", "true")
    rep = json.loads(out) if out and out.startswith("{") else {}
    check("C safe change verifies PASS", rep.get("verdict") == "PASS")

    # F: user's uncommitted file intact and visible in the change surface
    check("F user dirty file untouched",
          (src / "user_dirty.py").read_text() == "user = 1\n")
    check("F user change visible",
          any("user_dirty" in p for p in rep.get("changed_paths", [])))

    # G: non-git project without runners => UNVERIFIED (exit 2), never PASS
    plain = tmp / "notests"
    plain.mkdir()
    (plain / "main.rs").write_text("fn main() {}\n")
    out, _, rc = run("verify_changes.py", plain, "--cmd", "true", expect=2)
    check("G unverifiable project stays UNVERIFIED",
          rc == 2 and "UNVERIFIED" in (out or ""))

    # ---------- delta compare ----------
    run("collect_metrics.py", src, "-o", tmp / "mb.json")
    run("collect_metrics.py", src, "-o", tmp / "ma.json")
    out, _, rc = run("compare_baseline.py", tmp / "mb.json", tmp / "ma.json")
    check("delta table renders", bool(out) and "Before / After" in out)
    out, _, rc = run("compare_baseline.py", tmp / "mb.json", tmp / "ma.json",
                     "--format", "json")
    dj = json.loads(out) if out else {}
    check("delta json measured-only", dj.get("note", "").startswith("measured"))

    # ---------- exit codes ----------
    check("bad dir exit 1",
          run("detect_project.py", "/definitely/missing", expect=1)[2] == 1)
    check("bad window exit 1",
          run("detect_duplicates.py", str(ROOT), "--window", "1", expect=1)[2] == 1)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\nchecks: {ok} ok, {fail} fail")
print("VERDICT:", "PASS" if fail == 0 else "FAIL")
sys.exit(0 if fail == 0 else 1)
