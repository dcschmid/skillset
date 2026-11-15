#!/usr/bin/env python3
"""collect_context.py — discover review context: standards sources, spec
candidates, project stack, available tools, test commands.

Read-only. stdlib-only, Python 3.8+. Output JSON to stdout or -o FILE.

  collect_context.py [repo-dir] [--spec PATH] [-o out.json] [--max-walk N]

Discovery (never invents; absence is a fact):
  standards  AGENTS.md CLAUDE.md CONTRIBUTING.md CODING_STANDARDS.md
             .editorconfig docs/ specs/ repo-rules (top-level + nested, capped)
  spec       --spec PATH, then docs/ specs/ .scratch/ *.md matching
             branch/feature words; empty list -> SPEC_NOT_AVAILABLE
  stack      manifests -> languages/frameworks (name-only detection)
  tools      probed on PATH: git gh glab eslint tsc ruff pytest semgrep
             gitleaks cargo go node python3 gltf ... (presence only)
  tests      declared test/check commands from manifests when parseable
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STANDARD_FILES = ["AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md",
                  "CODING_STANDARDS.md", "README.md", ".editorconfig"]
SPEC_DIRS = ["docs", "specs", "spec", ".scratch"]
TOOL_PROBES = ["git", "gh", "glab", "node", "python3", "npx", "cargo", "go",
               "eslint", "tsc", "ruff", "pytest", "semgrep", "gitleaks",
               "osv-scanner", "trivy", "glab"]
MANIFESTS = {
    "package.json": "node", "pyproject.toml": "python",
    "setup.py": "python", "requirements.txt": "python", "Cargo.toml": "rust",
    "go.mod": "go", "pom.xml": "java", "build.gradle": "java",
    "pubspec.yaml": "dart", "Project.godot": "godot",
    "game.project": "defold", "astro.config.mjs": "astro",
    "next.config.js": "next", "Dockerfile": "docker",
}


def probe_tools():
    found = {}
    for t in TOOL_PROBES:
        p = shutil.which(t)
        if p:
            found[t] = p
    return found


def read_manifest(root):
    langs, cmds = set(), []
    for name, lang in MANIFESTS.items():
        f = root / name
        if not f.is_file():
            continue
        if lang:
            langs.add(lang)
        try:
            text = f.read_text(encoding="utf-8", errors="replace")[:60000]
        except OSError:
            continue
        if name == "package.json":
            try:
                data = json.loads(text)
                for k, v in (data.get("scripts") or {}).items():
                    if any(w in k for w in ("test", "lint", "check", "build")) \
                            or any(w in str(v) for w in ("test", "lint")):
                        cmds.append({"tool": "npm", "script": k, "cmd": v})
            except json.JSONDecodeError:
                pass
        elif name == "pyproject.toml":
            if "pytest" in text or "[tool.pytest" in text:
                cmds.append({"tool": "python", "script": "pytest",
                             "cmd": "pytest"})
        elif name == "Project.godot":
            cmds.append({"tool": "godot", "script": "headless",
                         "cmd": "godot --headless --import"})
    return sorted(langs), cmds


def find_standards(root, max_walk):
    hits, count = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in
                       ("node_modules", ".git", "dist", "build",
                        "__pycache__", ".venv")]
        rel = Path(dirpath).relative_to(root)
        for name in STANDARD_FILES:
            if name in filenames:
                hits.append(str(rel / name))
        for name in filenames:
            count += 1
            if count > max_walk:
                return sorted(hits), True
    return sorted(hits), False


def find_specs(root, branch, max_walk):
    words = [w for w in (branch or "").replace("/", "-").split("-")
             if len(w) > 2]
    hits = []
    scanned = 0
    for d in SPEC_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            scanned += 1
            if scanned > max_walk:
                return sorted(hits), True
            rel = str(md.relative_to(root))
            hits.append(rel)
    return sorted(hits, key=lambda p: (0 if any(
        w in p.lower() for w in words) else 1, p)), False


def branch_name(root):
    r = subprocess.run(["git", "-C", str(root), "rev-parse",
                        "--abbrev-ref", "HEAD"],
                       capture_output=True, text=True, timeout=30)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser(prog="collect_context.py")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--spec")
    ap.add_argument("--max-walk", type=int, default=2000)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    root = Path(a.repo).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        sys.exit(1)

    branch = branch_name(root)
    langs, cmds = read_manifest(root)
    standards, std_trunc = find_standards(root, a.max_walk)
    specs, spec_trunc = find_specs(root, branch, a.max_walk)
    if a.spec:
        p = Path(a.spec)
        specs = [str(p if p.is_absolute() else root / p)]

    ctx = {
        "tool": "collect_context.py",
        "generated_at": datetime.now(timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": str(root), "branch": branch,
        "languages": langs,
        "check_commands": cmds,
        "standards_sources": standards, "standards_truncated": std_trunc,
        "spec_candidates": specs, "spec_truncated": spec_trunc,
        "spec_status": "AVAILABLE" if (a.spec or specs) else "SPEC_NOT_AVAILABLE",
        "tools_available": probe_tools(),
        "notes": ["presence-based detection only; content conformance is the "
                  "review's job", "missing tools/standards/specs are coverage "
                  "gaps, never passes"],
    }
    text = json.dumps(ctx, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
        print(f"context -> {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
