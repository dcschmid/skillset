#!/usr/bin/env python3
"""
collect_metrics.py — evidence-based quality metrics for a project tree.

Computes per-file: lines, max nesting depth, branch-point counts (proxy for
cyclomatic complexity — labeled as a PROXY, not a certified metric), long
functions (indentation-scope heuristic), long parameter lists (signature
heuristic), TODO/FIXME debt markers, comment ratio. Aggregates top hotspots.

Zero dependencies, stdlib only, reads only. Language-agnostic: indentation +
brace heuristics with per-language keyword tables; unknown languages get a
conservative generic pass. Metrics without a real measurement base are "N/A".

Usage:
    python3 collect_metrics.py [PROJECT_DIR] [-o OUT.json] [--limit N]
              [--top N] [--max-lines N]

Exit codes: 0 ok | 1 bad args/dir | 2 I/O error.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP = {".git", "node_modules", "dist", "build", "target", "out", "vendor",
        "__pycache__", ".venv", "venv", ".next", ".nuxt", ".astro", "coverage",
        "obj", "bin", ".idea", "generated", "gen"}
INDENT_LANGS = {"python", "gdscript"}
CODE_EXTS = {
    "py": "python", "pyi": "python", "js": "javascript", "jsx": "javascript",
    "mjs": "javascript", "cjs": "javascript", "ts": "typescript",
    "tsx": "typescript", "vue": "html+js", "svelte": "html+js",
    "astro": "html+js", "go": "go", "rs": "rust", "java": "java",
    "kt": "java", "kts": "java", "cs": "java", "php": "java", "rb": "ruby",
    "swift": "java", "lua": "lua", "gd": "gdscript", "c": "c", "h": "c",
    "cpp": "c", "cc": "c", "cxx": "c", "hpp": "c", "sh": "shell",
    "bash": "shell", "sql": "sql",
}
BRANCH_WORDS = {
    "generic": ["if", "elif", "else", "for", "while", "case", "when", "match",
                "catch", "rescue", "except"],
    "python": ["if", "elif", "for", "while", "except", "and", "or"],
    "c-like": ["if", "for", "while", "switch", "case", "catch"],
}
LONG_FUNC_LINES = 50
LONG_PARAM_COUNT = 6
DEBT_MARK = re.compile(r"\b(TODO|FIXME|HACK|XXX|DEPRECATED)\b")


def iter_files(root: Path, limit: int):
    count = 0
    stack = [root]
    while stack:
        cur = stack.pop()
        try:
            entries = sorted(cur.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name in SKIP or e.name.startswith("."):
                    continue
                stack.append(e)
            elif count < limit:
                lang = CODE_EXTS.get(e.suffix.lower().lstrip("."))
                if lang:
                    yield e, lang
                    count += 1


def strip_noise(text: str, lang: str) -> str:
    """Blank out string contents and comments so keyword counts don't lie."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    if lang in ("python", "shell", "gdscript", "lua"):
        text = re.sub(r"--[^\n]*|#[^\n]*", " ", text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    return text


def file_metrics(path: Path, lang: str, max_lines: int, root: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"file": str(path.relative_to(root)), "status": "unreadable"}
    lines = raw.splitlines()
    n = len(lines)
    if n > max_lines:
        return {"file": str(path.relative_to(root)), "status": "skipped-large",
                "lines": n, "reason": f"exceeds --max-lines {max_lines}"}
    clean = strip_noise(raw, lang).splitlines()
    code = [l for l in clean if l.strip()]
    comments = sum(1 for l in lines
                   if l.strip().startswith(("#", "//", "/*", "*", "///", "--")))
    indent = lang in INDENT_LANGS
    depth = max_depth = 0
    for l in code:
        if indent:
            ws = len(l) - len(l.lstrip())
            max_depth = max(max_depth, min(ws // 4, 20))
        else:
            depth += l.count("{") - l.count("}")
            max_depth = max(max_depth, max(depth, 0))
    table = BRANCH_WORDS["python"] if lang == "python" else \
        BRANCH_WORDS["c-like"] if lang in ("c", "java", "rust", "go", "javascript",
                                           "typescript") else BRANCH_WORDS["generic"]
    branches = sum(len(re.findall(rf"\b{w}\b", l)) for l in code for w in table)
    many_params = 0
    for l in code:
        if (re.match(r"\s*(def |function |fn |func )", l)
                or re.match(r"\s*(public|private|protected|export|static|async)", l)) \
                and l.count(",") >= LONG_PARAM_COUNT - 1:
            many_params += 1
    long_funcs = 0
    if indent:
        cur_indent, run = 0, 0
        for l in code:
            d = (len(l) - len(l.lstrip())) // 4
            if d <= cur_indent:
                if run > LONG_FUNC_LINES:
                    long_funcs += 1
                run = 1
            else:
                run += 1
            cur_indent = max(cur_indent, d)
    else:
        run = 0
        for l in code:
            run += 1
            if "}" in l:
                if run > LONG_FUNC_LINES:
                    long_funcs += 1
                run = 0
    return {"file": str(path.relative_to(root)), "status": "measured",
            "language": lang, "lines": n, "code_lines": len(code),
            "comment_lines": comments, "max_nesting_depth": max_depth,
            "branch_points": branches, "complexity_proxy": branches + 1,
            "long_functions_over_50": long_funcs,
            "signatures_over_6_params": many_params,
            "debt_markers": len(DEBT_MARK.findall(raw))}


def main() -> int:
    ap = argparse.ArgumentParser(description="collect quality metrics (read-only)")
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--max-lines", type=int, default=3000)
    a = ap.parse_args()
    root = a.project.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1
    measured = skipped = 0
    totals = {"files": 0, "lines": 0, "code_lines": 0, "comment_lines": 0,
              "branch_points": 0, "debt_markers": 0}
    hotspots = []
    try:
        for path, lang in iter_files(root, a.limit):
            m = file_metrics(path, lang, a.max_lines, root)
            if m.get("status") != "measured":
                skipped += 1
                continue
            measured += 1
            for k in ("lines", "code_lines", "comment_lines", "branch_points",
                      "debt_markers"):
                totals[k] += m[k]
            totals["files"] += 1
            if m["complexity_proxy"] > 15 or m["max_nesting_depth"] > 4 \
                    or m["long_functions_over_50"]:
                hotspots.append(m)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    hotspots.sort(key=lambda m: -(m["complexity_proxy"] + m["max_nesting_depth"] * 3
                                  + m["long_functions_over_50"] * 10))
    report = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": str(root),
        "method": "static indentation/keyword heuristics; no language compiler",
        "metric_caveats": [
            "complexity_proxy = branch points + 1 (proxy; NOT certified CC)",
            "nesting depth: indentation for py/gd, braces otherwise",
            "long-function and long-param counts are signature heuristics",
            "coverage/test-pass rates: N/A (this script executes no project tools)",
        ],
        "totals": {**totals,
                   "avg_complexity_proxy": round(
                       totals["branch_points"] / max(totals["files"], 1) + 1, 2),
                   "coverage": "N/A", "typecheck_errors": "N/A",
                   "lint_findings": "N/A"},
        "files_measured": measured, "files_skipped": skipped,
        "hotspots": hotspots[:a.top],
    }
    out = json.dumps(report, indent=2, ensure_ascii=False)
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
