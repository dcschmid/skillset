#!/usr/bin/env python3
"""prepare_review.py — one-call review-bundle builder (read-only).

Runs git_review.py + collect_context.py against a target repo, assembles
the review workspace, and prints the work plan the orchestrator follows.
It does NOT review code itself — findings come from the axis agents; this
prepares evidence and enforces the assembly contract afterwards.

  build:  python3 scripts/prepare_review.py -w DIR [repo] -- [--base main ...]
  finish: python3 scripts/prepare_review.py --finish DIR [--gate LEVEL]

Workspace DIR gets scope.json, context.json, findings.json (agents fill);
--finish validates findings.json and renders the report into DIR.
Exit 0 ok / gate pass; 1 gate fail or error; bad scope refs propagate.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(script, *args):
    return subprocess.run([PY, str(HERE / script), *[str(a) for a in args]],
                          capture_output=True, text=True, timeout=600)


def build(ws, repo, mode_args):
    ws.mkdir(parents=True, exist_ok=True)
    rc = run("git_review.py", repo, *mode_args, "-o", ws / "scope.json")
    if rc.returncode != 0:
        print(rc.stdout or rc.stderr)
        return rc.returncode
    scope = json.loads((ws / "scope.json").read_text(encoding="utf-8"))
    ctx_r = run("collect_context.py", repo, "-o", ws / "context.json")
    (ws / "findings.json").write_text('{"findings": []}\n', encoding="utf-8")
    ctx = json.loads((ws / "context.json").read_text(encoding="utf-8")) \
        if (ws / "context.json").exists() else {}
    if ctx_r.returncode != 0:
        plan_note = ("collect_context failed: "
                     + (ctx_r.stderr or ctx_r.stdout).strip()[-200:])
    else:
        plan_note = None
    plan = {
        "workspace": str(ws), "scope_status": scope.get("status"),
        "mode": scope.get("mode"), "files": len(scope.get("files", [])),
        "spec_status": ctx.get("spec_status", "?"),
        "context_note": plan_note,
        "skipped_axes_file": str(ws / "skipped-axes.txt"),
        "next": [
            "1. spawn axis agents (max depth 1; agents never re-invoke this "
            "skill or spawn reviewers) — each writes finding objects per "
            "schemas/finding.schema.json into findings-<axis>.json",
            "2. merge findings-*.json into findings.json ({\"findings\":[...]})",
            "3. python3 scripts/validate_findings.py "
            + str(ws / "findings.json") + " -o " + str(ws / "validated.json")
            + " --gate LEVEL --skipped-axes \"$(cat "
            + str(ws / "skipped-axes.txt") + ")\"",
            "4. python3 scripts/generate_report.py "
            + str(ws / "validated.json") + " --scope " + str(ws / "scope.json")
            + " --context " + str(ws / "context.json")
            + " --format both -o DIR",
            "5. report only what ran; skipped axes stay gaps, never passes"],
    }
    if scope.get("status") == "NEEDS_BASE_REF":
        plan["next"] = ["pick baseline from scope.candidates or ask the user; "
                        "rerun build with --base REF — no arbitrary base"] \
            + plan["next"]
    if scope.get("status") == "NO_CHANGES":
        plan["next"] = ["emit NO_CHANGES report with empty findings; do not "
                        "invent findings"]
    print(json.dumps(plan, indent=1))
    return 0


def finish(ws, gate):
    ws = Path(ws)
    src = ws / "findings.json"
    if not src.is_file():
        print(json.dumps({"error": f"{src} missing — agents must write "
                                   "findings before --finish"}))
        return 1
    args = [src, "-o", ws / "validated.json"]
    if gate:
        args += ["--gate", gate]
    skipped = ws / "skipped-axes.txt"
    if skipped.is_file():
        args += ["--skipped-axes", skipped.read_text(encoding="utf-8").strip()]
    rv = run("validate_findings.py", *args)
    if rv.returncode == 2:
        print(rv.stdout or rv.stderr)
        return 2
    rp = run("generate_report.py", ws / "validated.json",
             "--scope", ws / "scope.json", "--context", ws / "context.json",
             "--format", "both", "-o", ws)
    print((rp.stdout or "") + (rv.stdout or ""))
    return 0 if rv.returncode == 0 else 1


def main():
    ap = argparse.ArgumentParser(prog="prepare_review.py")
    ap.add_argument("-w", "--workspace", default="/tmp/review-ws")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--finish", metavar="DIR")
    ap.add_argument("--gate", choices=["critical", "high", "security", "all"])
    argv = sys.argv[1:]
    sep = argv.index("--") if "--" in argv else len(argv)
    head, mode = argv[:sep], argv[sep + 1:]  # scope args live after bare --
    a = ap.parse_args(head)
    if a.finish:
        sys.exit(finish(a.finish, a.gate))
    sys.exit(build(Path(a.workspace), Path(a.repo), [m for m in mode]))


if __name__ == "__main__":
    main()
