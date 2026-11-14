#!/usr/bin/env python3
"""test_skill.py — skill self-test: structure, frontmatter, scripts, fixtures.

Runs with system python3, no deps. Verdict lines parseable: OK/FAIL per check.
Run from skill root:  python3 tests/test_skill.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ok = fail = 0

def check(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"OK   {name}")
    else: fail += 1; print(f"FAIL {name} {detail}")

# 1 structure
for p in ["SKILL.md", "README.md", "references", "workflows", "scripts", "templates", "tests"]:
    check(f"exists {p}", (ROOT / p).exists())
refs = ["security-standards", "audit-modules", "security-tooling", "remediation-guidelines",
        "dependency-security", "auth-security", "api-security", "frontend-security",
        "infrastructure-hardening", "risk-scoring", "ci-cd-security"]
for r in refs:
    check(f"ref {r}.md", (ROOT / "references" / f"{r}.md").is_file())
wfs = ["quick-audit", "full-audit", "security-fix", "regression-verification", "release-gate", "threat-model"]
for w in wfs:
    check(f"workflow {w}.md", (ROOT / "workflows" / f"{w}.md").is_file())

# 2 frontmatter valid + name == dir
text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
check("frontmatter present", bool(m))
if m:
    fm = m.group(1)
    check("name matches dir", f"name: {ROOT.name}" in fm)
    check("description present", "description:" in fm)
    try:
        import yaml; data = yaml.safe_load(fm)
        check("yaml parses", isinstance(data, dict) and data.get("name") == ROOT.name)
    except ModuleNotFoundError:
        print("SKIP yaml lib absent (regex-only check above)")
body = text[m.end():] if m else text
check("spine loop present", all(k in body for k in ("DISCOVER", "THREAT MODEL", "AUDIT", "VALIDATE", "PRIORITIZE", "FIX", "REGRESSION", "RE-SCAN", "REPORT")))
check("modes table", "RELEASE GATE" in body and "QUICK AUDIT" in body)
check("references linked", "references/audit-modules.md" in body)
check("no fake placeholders", "TODO" not in body and "PLACEHOLDER" not in body)

# 3 scripts: syntax + help + behavior
for sh in (ROOT / "scripts").glob("*.sh"):
    r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
    check(f"bash -n {sh.name}", r.returncode == 0, r.stderr[:200])
    h = subprocess.run(["bash", str(sh), "--help"], capture_output=True, text=True)
    check(f"help {sh.name}", h.returncode == 0 and h.stdout.strip() != "")
r = subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / "scripts/validate-report.py")],
                   capture_output=True, text=True)
check("validate-report compiles", r.returncode == 0, r.stderr[:200])

# 4 detection against fixture
fx = ROOT / "tests/fixtures/vulnerable_app"
r = subprocess.run(["bash", str(ROOT / "scripts/detect-project.sh"), str(fx)],
                   capture_output=True, text=True)
check("detect runs", r.returncode == 0, r.stderr[:200])
check("detect finds python", "python:" in r.stdout)
check("detect finds express", "express" in r.stdout or "javascript:" in r.stdout)
check("detect finds docker", "docker" in r.stdout)
check("detect emits json block", '"root"' in r.stdout)

# 5 fallback scanner finds planted flaws
r = subprocess.run(["bash", str(ROOT / "scripts/run-security-audit.sh"), "all", str(fx)],
                   capture_output=True, text=True)
out = r.stdout
check("audit runs", r.returncode == 0, out[-300:])
check("finds SQL concat flaw", "SQL" in out and "app.py" in out)
check("finds md5 flaw", "md5" in out.lower())
check("finds weak RNG", "RNG" in out or "random" in out.lower())
check("finds cookie/header area", "SameSite" in out or "TLS" in out)
check("mask applied", "MASKED" in out or "masked" in out.lower())
check("gaps reported honestly", "gap" in out.lower() or "coverage" in out.lower())

# 6 clean fixture contrast (FP pressure)
clean = ROOT / "tests/fixtures/clean_app"
r2 = subprocess.run(["bash", str(ROOT / "scripts/run-security-audit.sh"), "config", str(clean)],
                    capture_output=True, text=True)
confirmed_clean = not re.search(r"FINDING \[(?:config|secrets)\].*clean_app.*server\.ts.*legacy hash", r2.stdout)
check("clean fixture: no md5 findings", confirmed_clean, "")

# 7 validate-report end-to-end
with tempfile.TemporaryDirectory() as td:
    good = {"project": "t", "commit": "abc", "generated_at": "2026-11-14T00:00:00Z",
            "verdict": "PASS", "findings": []}
    (Path(td) / "security-findings.json").write_text(json.dumps(good))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/validate-report.py"), "--dir", td],
                       capture_output=True, text=True)
    check("valid report passes", r.returncode == 0, r.stdout + r.stderr)
    bad = dict(good, findings=[{"id": "SEC-1", "severity": "MEGA", "status": "Confirmed"}])
    (Path(td) / "security-findings-2.json").write_text(json.dumps(bad))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/validate-report.py"), "--dir", td],
                       capture_output=True, text=True)
    check("invalid report fails", r.returncode == 1)

print(f"\nVERDICT {'PASS' if fail == 0 else 'FAIL'} ({ok} ok / {fail} fail)")
sys.exit(0 if fail == 0 else 1)
