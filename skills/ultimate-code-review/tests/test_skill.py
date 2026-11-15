#!/usr/bin/env python3
"""test_skill.py — ultimate-code-review self-test (deterministic layer).

System python3, stdlib only, no network, writes only to temp dirs. The
axis-judgment layer is the host model and is exercised end-to-end by the
agent, not faked here; this suite pins the contract the agents rely on.

Scenarios: 1 standards-source discovery, 2 spec-missing status,
3 no-changes status, 4 regression-scope resolution, 5 security-axis gate
math, 6 read-only guarantee (no project writes), 7 invalid git ref ->
error+exit 1, 8 empty diff NO_CHANGES, 9 schema validation + gate
exit codes, 10 dedupe/link across axes, 11 report md/json shape,
12 missing tools = documented gap list, 13 staged/unstaged/untracked split
without double count, 14 full-mode inventory cap, 15 fix-mode contract
(docs-only assertion of rules).

Run from skill root:  python3 tests/test_skill.py
Verdict lines: OK/FAIL per check; final VERDICT: PASS|FAIL. Exit 0/1.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
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
        return None, (r.stderr or r.stdout).strip()[:300], r.returncode
    return r.stdout, r.stderr, r.returncode


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=60)


def fixture(tmp):
    repo = tmp / "proj"
    repo.mkdir(parents=True)
    env = dict(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
    for cmd in (["init", "-q", "-b", "main"],
                ["-c", "commit.gpgsign=false", "commit", "-qm", "one"]):
        pass
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"],
                   capture_output=True, env=env)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"],
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"],
                   capture_output=True)
    (repo / "app.py").write_text("a = 1\n")
    (repo / "docs").mkdir()
    (repo / "docs" / "spec.md").write_text("# spec\nR1 a\nR2 b\nR3 c\n")
    (repo / "AGENTS.md").write_text("# rules\nno print()\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false",
                    "commit", "-qm", "one"], capture_output=True)
    return repo, env


def commit_all(repo, msg):
    subprocess.run(["git", "-C", str(repo), "add", "-A"], capture_output=True)
    return subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false",
                           "commit", "-qm", msg], capture_output=True)


def F(**kw):  # finding factory
    base = dict(id="CR-001", axis="bugs", severity="high",
                confidence="confirmed", file="app.py", title="test defect",
                description="test description", impact="i", recommendation="r",
                status="open")
    base.update(kw)
    return base


try:
    tmp = Path(tempfile.mkdtemp())
    repo, env = fixture(tmp)

    # ---------- 1 structure & frontmatter ----------
    for p in ["SKILL.md", "README.md", "USAGE.md", "SKILL.md"]:
        check(f"exists {p}", (ROOT / p).is_file())
    for p in ["agents/standards-reviewer.md", "agents/spec-reviewer.md",
              "agents/bug-reviewer.md", "agents/security-reviewer.md",
              "agents/testing-reviewer.md", "agents/performance-reviewer.md",
              "references/review-methodology.md", "references/severity-model.md",
              "references/report-schema.md", "references/skill-integrations.md",
              "schemas/finding.schema.json", "schemas/report.schema.json",
              "assets/example-review.md", "assets/review-config.example.yml"]:
        check(f"file {p}", (ROOT / p).is_file())
    fm = (ROOT / "SKILL.md").read_text()
    check("frontmatter name", "name: ultimate-code-review" in fm)
    for s in ["git_review.py", "collect_context.py", "validate_findings.py",
              "generate_report.py", "prepare_review.py"]:
        check(f"script {s}", (SCRIPTS / s).is_file())

    # ---------- 1 standards discovery: rule source cited ----------
    out, _, _ = run("collect_context.py", repo, "-o", tmp / "ctx.json",
                    expect=0) if False else (None, None, 0)
    o, _, rc = run("collect_context.py", str(repo), "-o", tmp / "ctx.json")
    ctx = json.loads((tmp / "ctx.json").read_text()) if rc == 0 else {}
    check("1 standards source found (AGENTS.md)",
          any(p.endswith("AGENTS.md") for p in ctx.get("standards_sources", [])))

    # ---------- 2 spec discovery + SPEC_NOT_AVAILABLE ----------
    check("2 spec candidate found",
          any(p.endswith("spec.md") for p in ctx.get("spec_candidates", [])))
    bare = tmp / "bare"
    bare.mkdir()
    (bare / "x.py").write_text("x = 1\n")
    subprocess.run(["git", "-C", str(bare), "init", "-q"], capture_output=True)
    run("collect_context.py", str(bare), "-o", tmp / "ctx0.json")
    c0 = json.loads((tmp / "ctx0.json").read_text())
    check("2 no-spec -> SPEC_NOT_AVAILABLE (nothing invented)",
          c0.get("spec_status") == "SPEC_NOT_AVAILABLE"
          and c0.get("spec_candidates") == [])

    # ---------- 4 regression scope: diff vs base resolves ----------
    (repo / "app.py").write_text("a = 2\n")
    (repo / "new.py").write_text("n = 1\n")
    commit_all(repo, "two")
    o, _, rc = run("git_review.py", str(repo), "--base", "HEAD~1",
                   "-o", tmp / "sc.json")
    sc = json.loads((tmp / "sc.json").read_text()) if rc == 0 else {}
    paths = {f["path"] for f in sc.get("files", [])}
    check("4 base scope resolves changed files",
          sc.get("status") == "RESOLVED" and paths == {"app.py", "new.py"},
          str(sc.get("status")) + str(paths))
    check("4 merge-base recorded", bool(sc.get("merge_base_sha")))

    # ---------- 13 staged / unstaged / untracked split ----------
    (repo / "app.py").write_text("a = 3\n")           # unstaged
    (repo / "new.py").write_text("n = 2\n")
    subprocess.run(["git", "-C", str(repo), "add", "new.py"], capture_output=True)
    (repo / "free.py").write_text("f = 1\n")          # untracked
    o, _, rc = run("git_review.py", str(repo), "--uncommitted",
                   "-o", tmp / "sc2.json")
    sc2 = json.loads((tmp / "sc2.json").read_text()) if rc == 0 else {}
    check("13 staged/unstaged/untracked separated, no double count",
          sc2.get("staged_files") == ["new.py"]
          and sc2.get("unstaged_files") == ["app.py"]
          and sc2.get("untracked_files") == ["free.py"]
          and len({f["path"] for f in sc2.get("files", [])}) == 3)

    # ---------- 7 invalid ref: error + exit 1, no fake report ----------
    o, err, rc = run("git_review.py", str(repo), "--base", "nosuch/branch",
                     expect=1)
    check("7 invalid ref exits 1 with message", rc == 1 and "invalid ref" in
          json.dumps(o if o else err))

    # ---------- 8 empty diff NO_CHANGES ----------
    o, _, rc = run("git_review.py", str(repo), "--base", "HEAD",
                   "-o", tmp / "sc3.json")
    sc3 = json.loads((tmp / "sc3.json").read_text()) if rc == 0 else {}
    check("8 empty scope -> NO_CHANGES", sc3.get("status") == "NO_CHANGES")

    # ---------- 9/10 schema, dedupe, gate math ----------
    findings = {"findings": [
        F(id="CR-001"), F(id="CR-002", axis="spec", title="test defect",
                          line_start=1, line_end=1),
        F(id="CR-003", axis="security", file="db.py", severity="critical",
          confidence="suspected", title="security defect", line_start=2, line_end=3),
        {"id": "CR-004", "axis": "bugs", "severity": "low",
         "confidence": "confirmed", "file": "app.py", "title": "m",
         "description": "d", "impact": "i", "recommendation": "r",
         "status": "open", "line_start": 9, "line_end": 2}]}  # inverted -> invalid
    (tmp / "f.json").write_text(json.dumps(findings))
    o, err, rc = run("validate_findings.py", tmp / "f.json", "--gate", "high",
                     "--skipped-axes", "spec", "-o", tmp / "v.json")
    v = json.loads((tmp / "v.json").read_text()) if (tmp / "v.json").exists() else {}
    check("9 gate fails on confirmed high (exit 1)", rc == 1)
    check("9 invalid finding surfaces, not silent",
          [i["id"] for i in v.get("invalid", [])] == ["CR-004"])
    check("10 cross-axis dup linked not counted twice",
          any(m["id"] == "CR-002" and m["merged_into"] == "CR-001"
              for m in v.get("merged", [])))
    kept = {f["id"]: f for f in v.get("findings", [])}
    check("10 primary axis preserved after link",
          kept.get("CR-001", {}).get("axis") == "bugs"
          and "spec" in kept.get("CR-001", {}).get("also_flagged_by", []))
    check("9 suspected critical does not block 'high' gate",
          "CR-003" in v.get("gate", {}).get("warnings", [])
          and "CR-003" not in v.get("gate", {}).get("blocking", []))
    check("gate skips stay visible",
          v.get("gate", {}).get("skipped_axes") == ["spec"])
    # clean gate: only low open -> pass exit 0
    clean = {"findings": [F(id="CR-010", severity="low",
                            confidence="suspected", title="low confidence defect")]}
    (tmp / "f2.json").write_text(json.dumps(clean))
    o, _, rc = run("validate_findings.py", tmp / "f2.json", "--gate", "high",
                   "-o", tmp / "v2.json", expect=0)
    check("gate passes with no blocking (exit 0)", rc == 0 and
          json.loads((tmp / "v2.json").read_text())["gate"]["pass"] is True)

    # ---------- 5 security axis gate ----------
    sec = {"findings": [F(id="CR-020", axis="security", severity="low",
                          title="security defect")]}
    (tmp / "f3.json").write_text(json.dumps(sec))
    run("validate_findings.py", tmp / "f3.json", "--gate", "security",
        "-o", tmp / "v3.json")
    check("5 security gate blocks confirmed security finding",
          json.loads((tmp / "v3.json").read_text())["gate"]["pass"] is False)

    # Regression: schema parity and invalid input must fail without a gate.
    invalid_cases = [
        {"file": 123}, {"title": []}, {"line_start": True},
        {"id": "bad"}, {"title": "x"}, {"description": "d"},
        {"unknown": "value"}, {"refs": [1]},
        {"also_flagged_by": ["unknown"]}, {"axis": []},
        {"line_start": "1", "line_end": 2},
        {"line_start": 3, "line_end": 2},
        {"file": "../outside.py"}, {"file": "/outside.py"},
    ]
    for patch in invalid_cases:
        (tmp / "invalid.json").write_text(json.dumps([F(**patch)]))
        o, err, rc = run("validate_findings.py", tmp / "invalid.json", expect=1)
        result = json.loads(o) if o else {}
        check(f"invalid schema {patch!r} exits 1 without gate",
              rc == 1 and result.get("verdict") == "INVALID"
              and len(result.get("invalid", [])) == 1, err)
    # Schema-valid optional fields must continue to work.
    (tmp / "valid.json").write_text(json.dumps([F(
        line_start=1, line_end=2, evidence="quoted code", verification="run test",
        refs=["AGENTS.md"], also_flagged_by=["security"])]))
    o, err, rc = run("validate_findings.py", tmp / "valid.json")
    check("all optional schema fields accepted", rc == 0 and
          json.loads(o)["verdict"] == "VALID", err)

    # Dedupe cannot erase a later security axis or stronger blocking signal.
    for level, first, second in [
        ("security", F(), F(id="CR-002", axis="security")),
        ("high", F(severity="low", confidence="suspected"),
         F(id="CR-002", severity="critical")),
        ("high", F(status="fixed"), F(id="CR-002")),
    ]:
        for ordered in ([first, second], [second, first]):
            (tmp / "duplicates.json").write_text(json.dumps(ordered))
            o, err, rc = run("validate_findings.py", tmp / "duplicates.json",
                             "--gate", level, expect=1)
            result = json.loads(o) if o else {}
            check(f"{level} gate survives dedupe order {ordered[0]['id']}",
                  rc == 1 and result.get("gate", {}).get("pass") is False
                  and result["gate"]["blocking"] == [ordered[0]["id"]], err)

    # ---------- 11 report md/json shape ----------
    run("collect_context.py", str(repo), "-o", tmp / "ctx.json")
    o, err, rc = run("generate_report.py", tmp / "v.json",
                     "--scope", tmp / "sc.json", "--context", tmp / "ctx.json",
                     "--format", "both", "-o", tmp / "rep")
    md = (tmp / "rep" / "code-review.md").read_text()
    bj = json.loads((tmp / "rep" / "code-review.json").read_text())
    check("11 md keeps standards/spec separate sections",
          "## Standards Review" in md and "## Specification Review" in md
          and "## Bugs & Regression Risks" in md)
    check("11 json bundle schema keys", {"report", "scope", "context"} <=
          set(bj) and bj["report"]["verdict"] == "PARTIAL")
    check("11 skipped axis prints gap not pass",
          "SKIPPED — documented gap, not a pass" in md)
    check("11 no cross-axis total score key",
          "total_score" not in json.dumps(bj))

    # ---------- 12 missing tools = honest gaps ----------
    tools = ctx.get("tools_available", {})
    check("12 tool probe presence-only dict", isinstance(tools, dict))

    # ---------- 14 full-mode inventory cap ----------
    o, _, rc = run("git_review.py", str(repo), "--full", "--max-files", "2",
                   "-o", tmp / "sc4.json")
    sc4 = json.loads((tmp / "sc4.json").read_text()) if rc == 0 else {}
    check("14 full inventory capped + flagged truncated",
          sc4.get("file_count", 0) <= 2 and "truncated" in sc4)

    # ---------- 3/6 read-only: scripts never write in project ----------
    before = {p: p.stat().st_mtime_ns for p in repo.rglob("*")
              if p.is_file() and ".git" not in p.parts}
    run("prepare_review.py", "-w", str(tmp / "ws"), str(repo), "--",
        "--base", "HEAD~1")
    run("git_review.py", str(repo), "--full", "-o", tmp / "sc5.json")
    after = {p: p.stat().st_mtime_ns for p in repo.rglob("*")
             if p.is_file() and ".git" not in p.parts}
    check("6 read-only: project files untouched by scripts", before == after)
    check("workspace artifacts land outside project",
          (tmp / "ws" / "scope.json").is_file())

    # ---------- 15 fix contract lives in docs ----------
    sk = (ROOT / "SKILL.md").read_text()
    rd = (ROOT / "README.md").read_text()
    check("15 fix-mode contract documented read-only-first",
          "Read-only default" in sk and "--fix" in rd
          and "No commit/push ever without approval" in rd)
    check("9 no-recursion contract documented", "Depth 1" in sk)

finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\nchecks: {ok} ok, {fail} fail")
print("VERDICT:", "PASS" if fail == 0 else "FAIL")
sys.exit(0 if fail == 0 else 1)
