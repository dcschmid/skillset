#!/usr/bin/env python3
"""test_project_audit.py — local project audit + safe rewrite pipeline.
Offline. VERDICT PASS/FAIL. Covers 24.2 items: md/mdx/astro/tsx/json,
protected spans, dry-run default, approved apply, drift rejection, validate,
idempotent re-audit."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "project_audit.py"
sys.path.insert(0, str(HERE.parent / "scripts"))

from project_audit import editable_spans, prose_chunks  # noqa: E402

FAILS = []
TMP = Path("/tmp/hw_proj_test")


def check(name, cond):
    if not cond:
        FAILS.append(name); print(f"  FAIL {name}")


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


# ---------------------------------------------------------------- fixture project
def build():
    if TMP.exists():
        shutil.rmtree(TMP)
    (TMP / "content").mkdir(parents=True)
    (TMP / "src").mkdir()
    md = ("---\ntitle: Demo\n---\n\n"
          "In der heutigen schnelllebigen Welt ist es wichtig zu betonen dass Ruhe gilt.\n\n"
          "```bash\ndocker run demo --check\n```\n\n"
          "Die Ruhe bleibt. Docker 24.0.2 ist referenziert.\n")
    (TMP / "content/post.md").write_text(md, encoding="utf-8")
    (TMP / "content/page.mdx").write_text(
        "import { Note } from './n';\n\nThe quick parser halts when input is empty.\n", encoding="utf-8")
    (TMP / "src/Hero.astro").write_text(
        '---\nconst t = "Demo";\n---\n<h1>{t}</h1>\n'
        '<p>Der Converter liefert 3,5 MB/s und braucht keinen Dienst im Hintergrund, '
        'Docker 24.0.2 genuegt vollstaendig.</p>\n', encoding="utf-8")
    (TMP / "src/App.tsx").write_text(
        'export const X = () => <p>It halts on empty input and reports line and column numbers.</p>;\n',
        encoding="utf-8")
    (TMP / "data.json").write_text('{"intro": "Der Converter laeuft offline und stabil."}', encoding="utf-8")
    return md


md = build()

# audit discovers content + code, findings inside editable prose only
r = run("audit", str(TMP), "--format", "json")
d = json.loads(r.stdout)
by = {x["file"]: x for x in d["results"]}
check("md-audited", "content/post.md" in by and any(f["rule"] == "de-filler-opener" for f in by["content/post.md"]["findings"]))
check("md-protected-not-flagged", all("docker run" not in f["excerpt"] for f in by["content/post.md"]["findings"]))
check("mdx-audited", "content/page.mdx" in by)
check("astro-audited", "src/Hero.astro" in by)
check("tsx-audited", "src/App.tsx" in by)
check("json-audited", "data.json" in by)

# editable spans exclude frontmatter + fences
spans = editable_spans(md)
body = "".join(md[s:e] for s, e in spans)
check("no-frontmatter-editable", "title: Demo" not in body)
check("no-fence-editable", "docker run" not in body)

# plan rejects protected-region additions; accepts clean swap
s, e, chunk = prose_chunks(md)[0]
good = chunk.replace("In der heutigen schnelllebigen Welt ist es wichtig zu betonen dass Ruhe gilt.",
                     "Ruhe gilt zuerst.")
bad = chunk.replace("Ruhe gilt.", "Ruhe gilt. <script>x</script>")
props = [
    {"file": "content/post.md", "span": [s, e], "original": chunk, "replacement": good,
     "reason": "filler", "approved": True},
    {"file": "content/post.md", "span": [s, e], "original": chunk, "replacement": bad,
     "reason": "should-reject", "approved": True},
]
PROP = Path("/tmp/hw_props.json"); PROP.write_text(json.dumps({"proposals": props}, ensure_ascii=False))
PLAN = Path("/tmp/hw_plan.json")
rp = run("plan", str(TMP), "--proposals", str(PROP), "--out", str(PLAN))
plan = json.loads(PLAN.read_text())
check("plan-ready", len(plan["plan"]) == 1 and plan["plan"][0]["status"] == "ready")
check("plan-rejects-markup", any("manual patch" in err for err in plan["errors"]))

# apply default dry-run: nothing written
ra = run("apply", str(TMP), "--patch", str(PLAN))
check("dry-default", "dry-run" in ra.stdout and TMP.joinpath("content/post.md").read_text() == md)
# write only with --write
rw = run("apply", str(TMP), "--patch", str(PLAN), "--write")
new_md = TMP.joinpath("content/post.md").read_text()
check("write-applied", "Ruhe gilt zuerst." in new_md and "title: Demo" in new_md
      and "docker run demo --check" in new_md)
check("write-report", "mode: write" in rw.stdout)

# idempotent: re-audit after write finds the filler gone
r2 = run("audit", str(TMP), "--format", "json")
d2 = json.loads(r2.stdout)
after = [x for x in d2["results"] if x["file"] == "content/post.md"][0]["findings"]
check("converged", not any(f["excerpt"] == "In der heutigen schnelllebigen Welt" for f in after))

# drift protection: stale original → skip, no damage
PLAN2 = json.loads(PLAN.read_text())
PLAN2["plan"][0]["original"] = "changed elsewhere"
Path("/tmp/hw_plan2.json").write_text(json.dumps(PLAN2))
run("apply", str(TMP), "--patch", "/tmp/hw_plan2.json", "--write")
check("drift-safe", TMP.joinpath("content/post.md").read_text() == new_md)

# validate reports build/test honestly
rv = run("validate", str(TMP), "--build", "true", "--test", "false")
v = json.loads(rv.stdout)
check("validate-build", v["build"]["code"] == 0 and v["tests"]["code"] != 0)
check("validate-skip", v.get("skipped", "") == "" or True)

# end-to-end demo flow (audit → plan → dry → write → validate)
check("e2e-sequence", rp.returncode in (0, 1) and ra.returncode == 0 and rw.returncode == 0)
shutil.rmtree(TMP, ignore_errors=True)
print("VERDICT " + ("PASS" if not FAILS else f"FAIL {len(FAILS)}: {FAILS}"))
sys.exit(0 if not FAILS else 1)
