#!/usr/bin/env python3
"""
detect_project.py — read-only project fingerprint for quality audits.

Reports languages, frameworks, manifests, package managers, test/build
commands, CI, monorepo packages, git state, conventions, docs, and ignored
paths as JSON on stdout (or -o FILE). Detection only: writes nothing into the
project, installs nothing, runs nothing that mutates state (git is called
read-only).

Usage:
    python3 detect_project.py [PROJECT_DIR] [-o OUT.json] [--limit N]

Exit codes: 0 ok | 1 bad args/dir | 2 I/O or git error
Every unprovable field is the string "unknown" or an empty list — never a guess.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCAN_SKIP = {
    ".git", "node_modules", "dist", "build", "target", "out", "vendor",
    "__pycache__", ".venv", "venv", ".next", ".nuxt", ".svelte-kit", ".astro",
    "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".parcel-cache",
    "obj", "bin", "Debug", "Release", ".idea", ".vscode-cache",
}
EXT_LANG = {
    "py": "python", "pyi": "python", "js": "javascript", "jsx": "javascript",
    "mjs": "javascript", "cjs": "javascript", "ts": "typescript",
    "tsx": "typescript", "vue": "vue", "svelte": "svelte", "astro": "astro",
    "html": "html", "htm": "html", "css": "css", "scss": "scss",
    "sass": "scss", "less": "css", "go": "go", "rs": "rust",
    "java": "java", "kt": "kotlin", "kts": "kotlin", "cs": "csharp",
    "php": "php", "rb": "ruby", "swift": "swift", "lua": "lua",
    "gd": "gdscript", "c": "c", "h": "c", "cpp": "cpp", "cc": "cpp",
    "cxx": "cpp", "hpp": "cpp", "m": "objc", "sh": "shell",
    "bash": "shell", "zsh": "shell", "ex": "elixir", "exs": "elixir",
    "dart": "dart", "sql": "sql", "tf": "terraform",
}
CONFIG_EXTS = {"json", "yaml", "yml", "toml", "xml", "ini", "cfg"}
MANIFESTS = [
    "package.json", "pnpm-workspace.yaml", "pnpm-lock.yaml",
    "package-lock.json", "yarn.lock", "bun.lockb", "requirements.txt",
    "pyproject.toml", "uv.lock", "poetry.lock", "Pipfile", "setup.py",
    "setup.cfg", "Cargo.toml", "Cargo.lock", "go.mod", "go.work", "go.sum",
    "composer.json", "composer.lock", "Gemfile", "pom.xml", "build.gradle",
    "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
    "*.csproj", "pubspec.yaml", "game.project", "project.godot",
    "CMakeLists.txt", "Makefile", "Dockerfile", "deno.json",
]
DOCS_HINTS = ["README", "CHANGELOG", "CONTRIBUTING", "docs", "adr", "ACTIONS"]


def read_text(path: Path, limit: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def parse_gitignore(root: Path) -> set:
    """Directory names excluded via .gitignore (simple non-glob dir entries)."""
    skip = set()
    for line in read_text(root / ".gitignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entry = line.rstrip("/").lstrip("/")
        if entry and not any(ch in entry for ch in "*?[]!"):
            skip.add(entry.split("/")[-1])
    return skip


def walk(root: Path, limit: int, skip: set):
    files, dirs, truncated = [], [], False
    stack = [root]
    while stack:
        cur = stack.pop()
        try:
            entries = sorted(cur.iterdir())
        except OSError:
            continue
        for entry in entries:
            name = entry.name
            if entry.is_dir():
                if name in SCAN_SKIP or name in skip or name.startswith("."):
                    dirs.append(name)
                    continue
                dirs.append(name)
                stack.append(entry)
            else:
                if len(files) >= limit:
                    truncated = True
                    break
                if entry.suffix.lower().lstrip(".") in CONFIG_EXTS | set(EXT_LANG):
                    files.append(entry)
                elif name in ("Makefile", "Dockerfile") or name.endswith(
                        (".tf", ".gemspec")):
                    files.append(entry)
    return files, dirs, truncated


def detect(root: Path, limit: int) -> dict:
    skip = parse_gitignore(root)
    files, _dirs, truncated = walk(root, limit, skip)
    rel = lambda p: str(p.relative_to(root)) if p.is_relative_to(root) else str(p)

    langs = {}
    for f in files:
        lang = EXT_LANG.get(f.suffix.lower().lstrip("."))
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    langs = dict(sorted(langs.items(), key=lambda kv: -kv[1]))

    names = {rel(f) for f in files}
    base = {f.name for f in files}
    manifests_present = sorted(
        m for m in MANIFESTS if m != "*.csproj" and m in base)
    if any(f.suffix == ".csproj" for f in files):
        manifests_present.append("*.csproj")

    pj_text = ""
    for f in files:
        if f.name == "package.json" and f.parent == root:
            pj_text = read_text(f)
            break
    any_pkg_text = "".join(read_text(f) for f in files
                           if f.name == "package.json" and "node_modules" not in rel(f))[:600_000]

    frameworks = []
    fw_grep = {"react": r'"react"\s*:', "next": r'"next"\s*:',
               "astro": r'"astro"\s*:', "vue": r'"vue"\s*:',
               "svelte": r'"svelte"\s*:', "express": r'"express"\s*:',
               "fastify": r'"fastify"\s*:'}
    for name, pat in fw_grep.items():
        if re.search(pat, any_pkg_text):
            frameworks.append(name)
    py_all = "".join(read_text(f) for f in files if f.suffix in (".py", ".toml", ".txt", ".cfg"))
    for name, pat in {"django": r"\bdjango\b", "fastapi": r"\bfastapi\b",
                      "flask": r"\bflask\b", "pytest": r"\bpytest\b",
                      "sphinx": r"\bsphinx\b"}.items():
        if re.search(pat, py_all[:1_500_000]):
            frameworks.append(name)
    if "game.project" in base or any(EXT_LANG.get(f.suffix.lstrip(".")) == "lua"
                                     for f in files):
        if "game.project" in base:
            frameworks.append("defold")
    if "project.godot" in base:
        frameworks.append("godot")
    if any(f.name in ("Cargo.toml",) for f in files) and re.search(
            r"tokio|axum|\brocket\b", "".join(
                read_text(f) for f in files if f.name == "Cargo.toml")):
        frameworks.append("rust-async")

    # package managers by lockfile/manifest evidence
    pkg_mgrs = []
    if "pnpm-lock.yaml" in base: pkg_mgrs.append("pnpm")
    if "yarn.lock" in base: pkg_mgrs.append("yarn")
    if "package-lock.json" in base: pkg_mgrs.append("npm")
    if "bun.lockb" in base: pkg_mgrs.append("bun")
    if "uv.lock" in base: pkg_mgrs.append("uv")
    if "poetry.lock" in base: pkg_mgrs.append("poetry")
    if "uv" not in pkg_mgrs and "requirements.txt" in base: pkg_mgrs.append("pip")
    if any(f.name.startswith(("Cargo",)) for f in files): pkg_mgrs.append("cargo")
    if "go.mod" in base: pkg_mgrs.append("go-mod")
    if "composer.json" in base: pkg_mgrs.append("composer")

    # test & check commands (declared, NOT verified to pass)
    test_cmds, check_cmds = [], []
    try:
        pj = json.loads(pj_text) if pj_text else {}
    except json.JSONDecodeError:
        pj = {}
    for key, cmd in (pj.get("scripts") or {}).items():
        bucket = test_cmds if re.search(r"test|vitest|jest|playwright", key + str(cmd)) \
            else check_cmds if re.search(r"lint|check|typecheck|format|build",
                                         key + str(cmd)) else None
        if bucket is not None:
            bucket.append({"script": key, "cmd": str(cmd)})
    if (root / "pyproject.toml").is_file() or any(
            f.name.startswith("test_") and f.suffix == ".py" for f in files):
        test_cmds.append({"script": "pytest", "cmd": "python3 -m pytest -q"})
    if "go.mod" in base:
        test_cmds.append({"script": "go-test", "cmd": "go test ./..."})
    if any(f.name == "Cargo.toml" for f in files):
        test_cmds.append({"script": "cargo-test", "cmd": "cargo test"})
        check_cmds.append({"script": "cargo-clippy", "cmd": "cargo clippy"})

    ci = []
    if (root / ".github" / "workflows").is_dir(): ci.append("github-actions")
    if (root / ".gitlab-ci.yml").is_file(): ci.append("gitlab-ci")
    if (root / "Jenkinsfile").is_file(): ci.append("jenkins")
    if (root / ".woodpecker.yml").is_file() or (root / ".woodpecker").is_dir():
        ci.append("woodpecker")

    conventions = []
    for name, label in ((".editorconfig", "editorconfig"),
                        ("biome.json", "biome"), ("tsconfig.json", "typescript"),
                        (".eslintrc", "eslint"), (".prettierrc", "prettier"),
                        ("ruff.toml", "ruff"), (".rubocop.yml", "rubocop"),
                        (".clang-format", "clang-format")):
        if any(str(f.name).startswith(name) for f in files) or (root / name).exists():
            conventions.append(label)
    if re.search(r"\[tool\.ruff\]|\[tool\.mypy\]", py_all[:1_500_000]):
        if "ruff" not in conventions: conventions.append("ruff")
        conventions.append("mypy")

    docs = sorted({n for n in DOCS_HINTS
                   if any(str(f).lower().startswith(n.lower()) or
                          Path(f).parts and Path(f).parts[0].lower() == n.lower()
                          for f in names | set(_dirs))})

    monorepo = {"detected": False, "packages": [], "kind": "unknown"}
    ws = []
    try:
        ws = (json.loads(pj_text).get("workspaces") or []) if pj_text else []
    except Exception:
        pass
    if isinstance(ws, dict): ws = ws.get("packages", [])
    if ws:
        monorepo.update(detected=True, kind="npm-workspaces")
    elif (root / "pnpm-workspace.yaml").is_file():
        monorepo.update(detected=True, kind="pnpm-workspace")
    elif (root / "go.work").is_file():
        monorepo.update(detected=True, kind="go-work")
    elif any(f.name == "Cargo.toml" and "[workspace]" in read_text(f)
             for f in files if f.parent == root):
        monorepo.update(detected=True, kind="cargo-workspace")
    elif (root / "settings.gradle").is_file() or (root / "settings.gradle.kts").is_file():
        monorepo.update(detected=True, kind="gradle-multi")
    if monorepo["detected"]:
        for sub in sorted(p for p in root.iterdir() if p.is_dir() and p.name not in SCAN_SKIP):
            if any((sub / m).is_file() for m in ("package.json", "pyproject.toml",
                                                 "Cargo.toml", "go.mod", "pom.xml",
                                                 "build.gradle", "setup.py")):
                monorepo["packages"].append(sub.name)

    git = {"state": "unknown"}
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            st = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                                capture_output=True, text=True, timeout=20)
            git = {"state": "git", "branch": r.stdout.strip(),
                   "dirty_files": len([l for l in st.stdout.splitlines() if l.strip()])
                   if st.returncode == 0 else "unknown"}
    except (OSError, subprocess.TimeoutExpired):
        pass

    source_roots = sorted(d for d in ("src", "app", "lib", "packages", "cmd",
                                      "internal") if (root / d).is_dir()) or ["."]
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": str(root),
        "languages": langs,
        "primary_language": next(iter(langs), "unknown"),
        "frameworks": sorted(set(frameworks)),
        "manifests": manifests_present,
        "package_managers": sorted(set(pkg_mgrs)),
        "test_commands_declared": test_cmds,
        "check_commands_declared": check_cmds,
        "conventions": sorted(set(conventions)),
        "ci": ci,
        "docs_and_rules": docs,
        "monorepo": monorepo,
        "source_roots": source_roots,
        "git": git,
        "stats": {"files_scanned": len(files), "languages_seen": len(langs),
                  "truncated": truncated, "file_limit": limit},
        "notes": [
            "test/check commands are DECLARED by manifests, not executed here",
            "framework detection is manifest-grep evidence, version-independent",
            "no field is inferred without file evidence; 'unknown' = not provable",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--limit", type=int, default=20000)
    a = ap.parse_args()
    root = a.project.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1
    try:
        data = detect(root, a.limit)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    out = json.dumps(data, indent=2, ensure_ascii=False)
    if a.out:
        try:
            a.out.parent.mkdir(parents=True, exist_ok=True)
            a.out.write_text(out + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write {a.out}: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {a.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
