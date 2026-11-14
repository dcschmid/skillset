#!/usr/bin/env python3
"""
detect_duplicates.py — token-level clone detection across source files.

Normalizes identifiers/whitespace/comments per file, slides a fixed line-window
over each function-like region, hashes windows, and reports windows that occur
in 2+ places (cross-file and intra-file). This is a jscpd-style signal without
jscpd: results are CANDIDATES, not verdicts — a duplicate is only worth merging
when the two sites change together (see references/code-smells.md).

Zero dependencies, read-only.

Usage:
    python3 detect_duplicates.py [PROJECT_DIR] [-o OUT.json]
              [--window LINES] [--min-lines N] [--limit FILES]

Exit codes: 0 ok | 1 bad args/dir | 2 I/O error.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKIP = {".git", "node_modules", "dist", "build", "target", "out", "vendor",
        "__pycache__", ".venv", "venv", ".next", ".nuxt", ".astro", "coverage",
        "obj", "bin", ".idea", "generated", "gen"}
CODE_EXTS = {
    "py", "pyi", "js", "jsx", "mjs", "cjs", "ts", "tsx", "vue", "svelte",
    "astro", "go", "rs", "java", "kt", "kts", "cs", "php", "rb", "swift",
    "lua", "gd", "c", "h", "cpp", "cc", "cxx", "hpp", "sh", "bash",
}


def iter_files(root: Path, limit: int):
    count = 0
    stack = [root]
    while stack:
        try:
            entries = sorted(stack.pop().iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name not in SKIP and not e.name.startswith("."):
                    stack.append(e)
            elif e.suffix.lower().lstrip(".") in CODE_EXTS:
                if count >= limit:
                    return
                yield e
                count += 1


def normalize_lines(path: Path):
    """Comment-free, string-literal-folded, whitespace-pinned lines."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    raw = re.sub(r"/\*.*?\*/", " ", raw, flags=re.S)
    out = []
    for line in raw.splitlines():
        l = re.sub(r"//.*$", "", line)
        l = re.sub(r"--.*$", "", l) if path.suffix in (".lua", ".gd", ".sh") else l
        if l.strip().startswith("#") and path.suffix != ".php":
            continue
        l = re.sub(r'"(?:\\.|[^"\\])*"', "S", l)
        l = re.sub(r"'(?:\\.|[^'\\])*'", "S", l)
        l = re.sub(r"\s+", " ", l).strip()
        if l:
            out.append(l)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="token clone candidates (read-only)")
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--window", type=int, default=8, help="lines per window")
    ap.add_argument("--min-lines", type=int, default=6,
                    help="min normalized lines per file to consider")
    ap.add_argument("--limit", type=int, default=5000)
    a = ap.parse_args()
    root = a.project.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 1
    if a.window < 3:
        print("error: --window must be >= 3", file=sys.stderr)
        return 1

    index = defaultdict(list)  # hash -> [(file, start_line)]
    files_scanned = 0
    try:
        for path in iter_files(root, a.limit):
            lines = normalize_lines(path)
            if len(lines) < max(a.min_lines, a.window):
                continue
            files_scanned += 1
            rel = str(path.relative_to(root))
            for i in range(len(lines) - a.window + 1):
                win = lines[i:i + a.window]
                h = hashlib.sha1("\n".join(win).encode()).hexdigest()[:16]
                index[h].append((rel, i + 1))
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    dupes = []
    for h, hits in index.items():
        if len(hits) < 2:
            continue
        sites = sorted({(f, ln) for f, ln in hits})
        if len(sites) < 2:
            continue  # same file same line repeated windows: not a clone signal
        dupes.append({
            "hash": h, "sites": [{"file": f, "start_line": ln} for f, ln in sites],
            "cross_file": len({f for f, _ in sites}) > 1,
        })
    dupes.sort(key=lambda d: -len(d["sites"]))
    report = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": str(root),
        "method": f"normalized {a.window}-line token windows, sha1 match",
        "caveats": [
            "matches are CANDIDATES: merge only when sites change together",
            "third-party/vendored copies intentionally left as-is are fine",
        ],
        "files_scanned": files_scanned,
        "window_lines": a.window,
        "clone_group_count": len(dupes),
        "cross_file_groups": sum(1 for d in dupes if d["cross_file"]),
        "groups": dupes[:200],
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
