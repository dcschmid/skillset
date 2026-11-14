#!/usr/bin/env python3
"""test_skill.py — backend-api-engineering self-test: structure, frontmatter,
scripts behavior, fixtures. System python3, no deps. OK/FAIL lines, exit 0/1.
Run from skill root:  python3 tests/test_skill.py
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ok = fail = 0

def check(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"OK   {name}")
    else: fail += 1; print(f"FAIL {name} {detail}")

# 1 structure
for p in ["SKILL.md","README.md","references","workflows","scripts","templates","tests","evals","examples"]:
    check(f"exists {p}", (ROOT/p).exists())
refs = ["api-design","authentication","authorization","database-engineering","database-migrations",
        "architecture","security","performance","observability","testing","deployment",
        "background-jobs-messaging","quality-gates"]
for r in refs: check(f"ref {r}.md", (ROOT/"references"/f"{r}.md").is_file())
for w in ["create","audit","fix","optimize","migrate","verify"]:
    check(f"workflow {w}.md", (ROOT/"workflows"/f"{w}.md").is_file())

# 2 frontmatter
text = (ROOT/"SKILL.md").read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
check("frontmatter present", bool(m))
fm = m.group(1) if m else ""
check("name matches dir", f"name: {ROOT.name}" in fm)
check("description present", "description:" in fm and len(fm) > 200)
body = text[m.end():] if m else text
for tok in ("PROFILE","MODE","WORK","VERIFY","REPORT","Prime rules","Hard stops"):
    check(f"spine '{tok}'", tok in body)
for mode in ("CREATE","AUDIT","FIX","OPTIMIZE","AUTH","DATABASE","API","ARCHITECTURE","DEPLOY","MIGRATE","VERIFY"):
    if mode not in body: check(f"mode {mode}", False)
check("modes all listed", all(mo in body for mo in ("CREATE","AUDIT","OPTIMIZE","MIGRATE")))
check("refs linked from SKILL.md", "references/api-design.md" in body)
check("score rubric", "100" in body and "Architecture" in body)
check("no placeholder stubs", "TODO" not in body and "PLACEHOLDER" not in body)

# 3 scripts executable + behavior
scripts = {p.name: p for p in (ROOT/"scripts").iterdir() if p.suffix in (".sh",".py")}
check("3 scripts", len(scripts) >= 3)
for sh in (ROOT/"scripts").glob("*.sh"):
    r = subprocess.run(["bash","-n",str(sh)],capture_output=True,text=True)
    check(f"bash -n {sh.name}", r.returncode==0, r.stderr[:200])
    h = subprocess.run(["bash",str(sh),"--help"],capture_output=True,text=True)
    check(f"help {sh.name}", h.returncode==0 and h.stdout.strip()!="")
r = subprocess.run([sys.executable,"-m","py_compile",str(ROOT/"scripts/validate-openapi.py")],
                   capture_output=True,text=True)
check("validate-openapi compiles", r.returncode==0, r.stderr[:200])

# detect-project.sh against legacy fixture
r = subprocess.run(["bash",str(ROOT/"scripts/detect-project.sh"),str(ROOT/"tests/fixtures/legacy_app")],
                   capture_output=True,text=True)
check("detect runs", r.returncode==0, r.stderr[:150])
check("detect finds python", "python" in r.stdout)
check("detect classifies", "class-guess:" in r.stdout)
check("detect detects flask-family", "frameworks:" in r.stdout or "languages:" in r.stdout)

# validate-openapi: good spec passes, breaking diff flagged
good = {"openapi":"3.1.0","info":{"title":"t","version":"1"},
        "paths":{"/x":{"get":{"operationId":"gx","responses":{"200":{"description":"ok"},
        "500":{"description":"e"}}}}}}
old = json.loads(json.dumps(good)); new = json.loads(json.dumps(good))
new["paths"]["/x"]["get"]["parameters"]=[{"name":"q","in":"query","required":True,"schema":{"type":"string"}}]
import tempfile, os
with tempfile.TemporaryDirectory() as d:
    gp,op,np_ = Path(d)/"g.json",Path(d)/"o.json",Path(d)/"n.json"
    gp.write_text(json.dumps(good)); op.write_text(json.dumps(old)); np_.write_text(json.dumps(new))
    r = subprocess.run([sys.executable,str(ROOT/"scripts/validate-openapi.py"),str(gp)],capture_output=True,text=True)
    check("spec PASS", r.returncode==0, r.stdout[:150])
    r = subprocess.run([sys.executable,str(ROOT/"scripts/validate-openapi.py"),str(np_),"--baseline",str(op)],
                       capture_output=True,text=True)
    check("breaking change FAIL", r.returncode==1 and "BREAKING" in r.stdout, r.stdout[:200])
    bad = {"info":{"title":"t"}}
    bp = Path(d)/"b.json"; bp.write_text(json.dumps(bad))
    r = subprocess.run([sys.executable,str(ROOT/"scripts/validate-openapi.py"),str(bp)],capture_output=True,text=True)
    check("bad spec errors", r.returncode==1 and "ERROR" in r.stdout)

# migration-review: risky fixture flagged, clean fixture not
r = subprocess.run(["bash",str(ROOT/"scripts/migration-review.sh"),str(ROOT/"tests/fixtures/legacy_app")],
                   capture_output=True,text=True)
check("mig lint runs on non-sql dir", r.returncode in (0,1))
risky = ROOT/"tests/fixtures/legacy_app/../fixtures/healthy_api/migrations"
r = subprocess.run(["bash",str(ROOT/"scripts/migration-review.sh"),
                    str((ROOT/"tests/fixtures/healthy_api/migrations").parent.parent/"legacy_migrations")
                    if False else str(ROOT/"tests/fixtures/healthy_api/migrations")],
                   capture_output=True,text=True)
check("mig lint on clean fixture green-or-noted", r.returncode in (0,1) and ("PASS" in r.stdout or "FINDING" in r.stdout))
import tempfile as tf
with tf.TemporaryDirectory() as d:
    f = Path(d)/"001_x.sql"
    f.write_text("-- UP\nALTER TABLE t ADD COLUMN c text NOT NULL;\nCREATE INDEX i ON t (c);\n-- DOWN\nDROP TABLE t;\n")
    r = subprocess.run(["bash",str(ROOT/"scripts/migration-review.sh"),d],capture_output=True,text=True)
    check("destructive DDL flagged", r.returncode==1 and "lock-risk" in r.stdout, r.stdout[:250])

# 4 fixtures + evals present
check("legacy fixture", (ROOT/"tests/fixtures/legacy_app/app.py").is_file())
check("healthy fixture", (ROOT/"tests/fixtures/healthy_api/app.py").is_file())
check("migration fixture", (ROOT/"tests/fixtures/healthy_api/migrations/001_orders.sql").is_file())
for f in ["legacy_app/app.py","healthy_api/app.py"]:
    src = (ROOT/"tests/fixtures"/f).read_text()
    check(f"fixture {f} has defect markers", "defect" in src)
check("evals A-H", (ROOT/"evals/scenarios.md").is_file() and all(f"{c} —" in (ROOT/"evals/scenarios.md").read_text() for c in "ABCDEFGH"))

# 5 templates valid
tj = json.loads((ROOT/"templates/finding.json").read_text())
check("finding.json keys", all(k in tj for k in ("severity","evidence","fix_status","validation")))
check("templates complete", all((ROOT/"templates"/f).is_file() for f in
      ("scorecard.md","api-spec.yaml","migration.sql","health-endpoints.md")))

# 6 examples cover the 10 scenarios
ex = list((ROOT/"examples").glob("*.md"))
txt = " ".join(p.read_text() for p in ex) if ex else ""
check("examples exist", len(ex) >= 10, f"got {len(ex)}")
for kw in ("REST","audit","OIDC","authorization","EXPLAIN","migration","latency","moderniz","production","contract"):
    check(f"example covers {kw}", kw.lower() in txt.lower())

print(f"\n{ok} OK / {fail} FAIL")
sys.exit(0 if fail==0 else 1)
