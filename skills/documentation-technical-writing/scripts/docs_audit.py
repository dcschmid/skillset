#!/usr/bin/env python3
"""docs_audit — documentation coverage audit for a project.

Compares the docs that exist against what the PROJECT ITSELF proves it needs
(manifests, routes, env samples, CI, lockfiles). Evidence tiers, never guesses:
  VERIFIED      observed in code/config/tests
  DOCUMENTED    stated in project files (manifests, CI, existing docs)
  PLAUSIBLE     inferred, not confirmed  -> emitted as REVIEW_REQUIRED
  UNKNOWN       no basis                -> emitted as open question

Usage: docs_audit.py [--json] [--out FILE] [--scope all|readme|api|config|setup|ci] [ROOT]
exit: 0 pass/warn, 2 fail (P0/P1 gaps found)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_lib as L  # noqa: E402

SHEETS = {
    "package.json": "npm/yarn/pnpm project",
    "pyproject.toml": "Python project",
    "Cargo.toml": "Rust project",
    "go.mod": "Go project",
    "composer.json": "PHP project",
    "pom.xml": "JVM/Maven project",
}
DOC_CANDIDATES = ["README.md", "readme.md", "README.rst", "docs/index.md"]
CI_DIRS = (".github/workflows", ".gitlab-ci.yml", "Jenkinsfile",
           "azure-pipelines.yml", ".circleci")


def stack_of(root: Path) -> list[tuple[str, str]]:
    return [(name, desc) for name, desc in SHEETS.items() if (root / name).exists()]


def scripts_of(root: Path) -> dict:
    pkg = root / "package.json"
    if pkg.exists():
        try:
            return json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
        except (ValueError, OSError):
            return {}
    return {}


def env_keys(root: Path) -> list[str]:
    keys: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in L.SKIP_DIRS]
        for name in filenames:
            if name.startswith(".env") and ("example" in name or "sample" in name):
                text = L.read_text(Path(dirpath) / name) or ""
                keys.update(m.group(1) for m in re.finditer(r"^([A-Z][A-Z0-9_]{2,})=", text, re.M))
    return sorted(keys)


def ci_present(root: Path) -> list[str]:
    return [c for c in CI_DIRS if (root / c).exists()]


def readme_text(root: Path) -> tuple[Path | None, str]:
    for cand in ("README.md", "readme.md", "README.rst", "docs/index.md"):
        p = root / cand
        if p.exists():
            return p, L.read_text(p) or ""
    return None, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scope", default="all",
                    choices=["all", "readme", "api", "config", "setup", "ci"])
    args = ap.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        L.die(f"not a directory: {root}")

    stacks = stack_of(root)
    scripts = scripts_of(root)
    env = env_keys(root)
    ci = ci_present(root)
    rpath, rtext = readme_text(root)
    docs = L.walk_docs(root, 1000)
    findings: list[dict] = []

    def add(pid, prio, msg, tier, path=None, fix=None):
        if args.scope != "all" and not pid.startswith(args.scope):
            return
        findings.append({"id": pid, "priority": prio, "tier": tier,
                         "path": str(path or ""), "message": msg,
                         "fix": fix or "verify against source before writing"})

    # A. Completeness — README presence and the questions it must answer
    if rpath is None:
        add("readme:missing", "P2", "no README found at repo root", "VERIFIED", "README.md",
            "create README.md from assets/README.template.md, fill ONLY from manifests/scripts")
    else:
        low = rtext.lower()
        required = {"install": ["install", "setup", "npm ci", "pip install", "cargo", "make"],
                    "run": ["start", "dev", "serve", "run", "build"],
                    "test": ["test", "pytest", "vitest", "jest", "cargo test"],
                    "config": ["env", "config", "port", "database"],
                    "requirements": ["requirement", "node", "python", "rust", "version"]}
        for topic, needles in required.items():
            if stacks and not any(n in low for n in needles):
                add(f"readme:{topic}", "P2",
                    f"README.md does not answer '{topic}' though the project has commands/config for it",
                    "VERIFIED", rpath)
        # commands cited in README must exist in manifests (stale-command detector)
        if scripts:
            for m in re.finditer(r"(?:npm|yarn|pnpm)\s+(?:run\s+)?([\w:\-]+)", rtext):
                name = m.group(1)
                if name not in scripts and name not in ("install", "ci"):
                    add("readme:stale-command", "P1",
                        f"README runs '{name}' but package.json has no such script",
                        "VERIFIED", rpath,
                        f"document only existing scripts, e.g. {sorted(scripts)[:6]}")
    if stacks and not docs:
        add("setup:missing", "P2", "no developer setup docs anywhere in repo", "VERIFIED",
            "docs/developer-guide.md",
            "assets/DEVELOPER_GUIDE.template.md; fill from scripts/CI only")
    if env:
        blob = "\n".join(L.read_text(d) or "" for d in docs[:200])
        missing = [k for k in env if k not in blob]
        if missing:
            add("config:undocumented-keys", "P2",
                f"env keys exist in samples but in no doc: {missing[:8]}", "VERIFIED",
                ".env.example", f"document {missing} with defaults from the sample file")
    if stacks and not ci:
        add("ci:none", "P3", "no CI config found — docs-check gate cannot exist", "VERIFIED",
            ".github/workflows")

    # API surface signals without API docs
    api_docs = [d for d in docs if re.search(r"(openapi|swagger|api\.md|graphql|\.proto)", str(d), re.I)]
    api_signal = any((root / p).exists() for p in ("openapi.yaml", "openapi.json",
                                                   "schema.graphql", "graphql.schema.json")) \
        or bool(next(root.rglob("*.proto"), None))
    if (stacks or api_signal) and api_signal and not api_docs:
        add("api:undocumented", "P2", "API surface signals present, no API docs found",
            "VERIFIED", "docs/api.md", "assets/API.template.md; schemas from framework metadata only")

    # E. Security — secrets in docs (label reported, value never echoed)
    for d in docs[:300]:
        for lineno, label in L.secrets_in(L.read_text(d) or ""):
            add("security:secret-in-docs", "P0",
                f"secret-looking literal in {d.relative_to(root)} line {lineno} "
                f"(value not copied): {label}…", "VERIFIED", d,
                "replace with placeholder like YOUR_API_KEY; keep the value out of docs")

    open_questions = []
    if not stacks:
        open_questions.append("UNKNOWN stack: no manifest at root — audit is README-level only")

    verdict = ("FAIL" if any(f["priority"] in ("P0", "P1") for f in findings)
               else "WARN" if findings or open_questions else "PASS")
    checks = [{"id": "docs-audit", "verdict": verdict,
               "detail": f"stack={[s for s, _ in stacks] or 'UNKNOWN'} scripts={len(scripts)} "
                         f"env_keys={len(env)} ci={len(ci)} docs={len(docs)}",
               "findings": findings, "open_questions": open_questions}]
    L.emit({"title": f"docs_audit {root.name}", "checks": checks},
           args.out, args.json or bool(args.out))
    return {"PASS": 0, "WARN": 0, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
