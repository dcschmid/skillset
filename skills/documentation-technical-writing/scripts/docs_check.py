#!/usr/bin/env python3
"""docs_check — structural + link validation for Markdown docs in a project.

Checks run offline and deterministic:
  heading hierarchy, duplicate/empty headings, unbalanced code fences,
  internal file links, anchor links, image references, secret-looking
  literals in examples. External tools (markdownlint/vale/lychee/redocly)
  are probed; absent tools report NOT RUN, never fake PASS.

Usage: docs_check.py [--json] [--out FILE] [ROOT]     exit: 0 ok, 1 review, 2 fail
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_lib as L  # noqa: E402


def anchor_index(texts: dict[Path, str]) -> dict[str, set[str]]:
    idx: dict[str, set[str]] = {}
    for path, text in texts.items():
        body = L.split_frontmatter(text)[1]
        idx[str(path)] = {L.slugify(t) for _, _, t in L.headings(body)}
    return idx


def check_file(path: Path, text: str, anchors: dict[str, set[str]], root: Path) -> list[dict]:
    findings: list[dict] = []
    body = L.split_frontmatter(text)[1]
    rel = str(path.relative_to(root))

    # fences balanced
    fence_count = sum(1 for line in text.splitlines() if L.FENCE_RE.match(line.strip()))
    if fence_count % 2:
        findings.append({"priority": "P1", "path": rel,
                         "message": "unbalanced code fence (odd count of ```/~~~)"})

    # headings
    hs = L.headings(body)
    prev_level = 0
    seen_slugs: dict[str, int] = {}
    for lineno, level, title in hs:
        if not title:
            findings.append({"priority": "P3", "path": rel,
                             "line": lineno, "message": "empty heading"})
        if prev_level and level > prev_level + 1:
            findings.append({"priority": "P3", "path": rel, "line": lineno,
                             "message": f"heading jumps h{prev_level}->h{level}: '{title[:40]}'"})
        prev_level = level
        slug = L.slugify(title)
        if slug:
            if slug in seen_slugs:
                findings.append({"priority": "P3", "path": rel, "line": lineno,
                                 "message": f"duplicate anchor '{slug}'"})
            seen_slugs[slug] = lineno

    # links + anchors + images
    for lineno, link_text, target, kind in L.md_links(body):
        if kind == "file":
            frag = ""
            file_part = target
            if "#" in target:
                file_part, frag = target.split("#", 1)
            if file_part:
                target_path = (path.parent / file_part).resolve()
                if not target_path.exists():
                    findings.append({"priority": "P1", "path": rel, "line": lineno,
                                     "message": f"broken file link -> {target}"})
            else:
                target_path = path
            if frag:
                pool = anchors.get(str(target_path), set())
                if L.slugify(frag) not in pool and frag.lower() not in pool:
                    findings.append({"priority": "P2", "path": rel, "line": lineno,
                                     "message": f"anchor #{frag} not found in {file_part or 'this file'}"})
        elif kind == "anchor":
            frag = target[1:]
            pool = anchors.get(str(path), set())
            if L.slugify(frag) not in pool and frag.lower() not in pool:
                findings.append({"priority": "P2", "path": rel, "line": lineno,
                                 "message": f"anchor {target} not found in file"})
        if kind in ("file", "anchor") and not link_text.strip():
            findings.append({"priority": "P3", "path": rel, "line": lineno,
                             "message": "empty link text (screen-reader issue)"})

    # secrets (report label only, never the value)
    for lineno, label in L.secrets_in(text):
        findings.append({"priority": "P0", "path": rel, "line": lineno,
                         "message": f"secret-looking literal in docs (redact/placeholder): {label}…"})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".", type=Path)
    ap.add_argument("--json", action="store_true", help="full JSON to stdout")
    ap.add_argument("--out", type=Path, help="write report file (non-destructive)")
    ap.add_argument("--max-files", type=int, default=500)
    args = ap.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        L.die(f"not a directory: {root}")

    files = L.walk_docs(root, args.max_files)
    if not files:
        print("no markdown files found; nothing checked (NOT RUN, not PASS)")
        return 0

    texts: dict[Path, str] = {}
    for f in files:
        t = L.read_text(f)
        if t is not None:
            texts[f] = t

    anchors = anchor_index(texts)
    findings: list[dict] = []
    for f, text in texts.items():
        findings.extend(check_file(f, text, anchors, root))

    ext_checks = []
    for tool in ("markdownlint-cli2", "vale", "lychee"):
        present = L.have(tool)
        ext_checks.append({
            "id": f"ext:{tool}",
            "verdict": "NOT RUN" if not present else "REVIEW_REQUIRED",
            "detail": "tool not installed on this machine — install or wire in CI "
                      "to run it; no result claimed" if not present
            else "tool present; run it directly (this CLI does not shell out)"})

    verdict = ("FAIL" if any(f["priority"] in ("P0", "P1") for f in findings)
               else "WARN" if findings else "PASS")
    checks = [{"id": "markdown-structure-links", "verdict": verdict,
               "detail": f"{len(texts)} files, {len(findings)} findings "
                         "(P0/P1 fail, P2+ warn)",
               "findings": findings}] + ext_checks

    report = {"title": f"docs_check {root.name}", "checks": checks}
    L.emit(report, args.out, args.json)
    return {"PASS": 0, "WARN": 0, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
