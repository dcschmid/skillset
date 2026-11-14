"""Shared helpers for documentation-technical-writing CLIs.

Python 3.10+, stdlib only. Used by docs_audit.py, docs_check.py, docs_sync.py.
All file access is non-destructive: reports never overwrite existing files,
collisions get a dated suffix.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Probe-first: a tool that is not installed yields NOT RUN, never a fake pass.
EXTERNAL_TOOLS = {
    "markdownlint-cli2": "markdownlint-cli2",
    "vale": "vale",
    "lychee": "lychee",
    "redocly": "redocly",
    "mmdc": "mmdc",  # mermaid-cli
}

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv",
             "__pycache__", ".next", "out", "target", ".cache", "vendor"}

MD_NAME_RE = re.compile(r"\.(md|mdx)$", re.IGNORECASE)
FENCE_RE = re.compile(r"^(```|~~~)")
ATX_RE = re.compile(r"^(#{1,6})\s+(.*)$")
SETTEXT_RE = re.compile(r"^(=+|-+)\s*$")
LINK_RE = re.compile(r"!?\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
ANCHOR_RE = re.compile(r"(?:^|\s)-\s+\[[ xX]\]\s")
SECRET_RES = [
    (re.compile(r"(?P<pre>\b(?:api[_-]?key|apikey|secret|token|password|passwd|"
                r"access[_-]?key|private[_-]?key)\b\s*[:=]\s*[\"']?)(?P<val>[A-Za-z0-9+/=_\-\.]{12,})",
                re.IGNORECASE), "key=value"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"), "token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}"), "access-key"),
    (re.compile(r"\b(?:sk|pk)-[A-Za-z0-9]{20,}"), "api-token"),
]
PLACEHOLDER_VAL_RE = re.compile(
    r"^(?:<[^>]+>|\{\{[^}]+\}\}|\$\{[^}]+\}|(?:YOUR|your)[_\-\s]?\w*|"
    r"(?:example|sample|placeholder|redacted|xxx+|changeme|change-me)[_\-\w]*|"
    r"\*{3,})[\w\-]*$")

VERDICTS = ("PASS", "WARN", "FAIL", "REVIEW_REQUIRED", "NOT RUN")


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def have(tool: str) -> bool:
    """Tool presence probe; callers emit NOT RUN when False."""
    from shutil import which
    return which(EXTERNAL_TOOLS.get(tool, tool)) is not None


def walk_docs(root: Path, max_files: int = 2000) -> list[Path]:
    """Markdown files under root, deterministic order, vendored dirs skipped."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if MD_NAME_RE.search(name):
                out.append(Path(dirpath) / name)
                if len(out) >= max_files:
                    return out
    return out


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("\n")
        if parts and parts[0].strip() == "---":
            for i in range(1, len(parts)):
                if parts[i].strip() in ("---", "..."):
                    return "\n".join(parts[1:i]), "\n".join(parts[i + 1:])
    return "", text


def strip_code(text: str) -> list[tuple[int, str]]:
    """(lineno, line) pairs outside fenced code blocks; fences stay visible."""
    lines: list[tuple[int, str]] = []
    fence = None
    for i, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line.strip())
        if m:
            tick = m.group(1)
            if fence is None:
                fence = tick
            elif tick == fence:
                fence = None
            lines.append((i, line))
            continue
        if fence is None:
            lines.append((i, line))
    return lines


def headings(text: str) -> list[tuple[int, int, str]]:
    """(lineno, level, title) ATX headings outside code fences."""
    out = []
    fence = None
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        m = FENCE_RE.match(s)
        if m:
            tick = m.group(1)
            fence = tick if fence is None else (None if tick == fence else fence)
            continue
        if fence is not None:
            continue
        m = ATX_RE.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def slugify(title: str) -> str:
    """GitHub-flavoured anchor: lowercase, spaces->dashes, punctuation stripped."""
    t = re.sub(r"`|\*|_|~", "", title).strip().lower()
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"[^\w\-]", "", t, flags=re.UNICODE)
    return t


def md_links(text: str) -> list[tuple[int, str, str, str]]:
    """(lineno, link_text, target, kind) with kind in file|url|anchor|other."""
    out = []
    for lineno, line in strip_code(text):
        for m in LINK_RE.finditer(line):
            target = m.group("target")
            if target.startswith(("http://", "https://")):
                kind = "url"
            elif target.startswith("#"):
                kind = "anchor"
            elif re.match(r"^[A-Za-z]:|^[/~]", target) or "/" in target or MD_NAME_RE.search(target.split("#")[0]):
                kind = "file"
            else:
                kind = "file" if target else "other"
            out.append((lineno, m.group("text"), target, kind))
    return out


def secrets_in(text: str) -> list[tuple[int, str]]:
    """(lineno, label) for secret-looking literals; values never returned whole."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for rx, kind in SECRET_RES:
            for m in rx.finditer(line):
                candidate = (m.groupdict().get("val") or m.group(0)).strip(" \"',;")
                candidate = candidate.split("=")[-1] if "val" not in m.groupdict() else candidate
                if PLACEHOLDER_VAL_RE.match(candidate) or "<" in candidate:
                    continue
                hits.append((i, kind))  # kind only; the value is never echoed
    return hits


def nondestructive_path(path: Path) -> Path:
    """Never clobber: on collision insert a dated suffix before the suffix."""
    if not path.exists():
        return path
    stamp = date.today().isoformat()
    stem, suffix = path.stem, path.suffix
    cand = path.with_name(f"{stem}-{stamp}{suffix}")
    n = 2
    while cand.exists():
        cand = path.with_name(f"{stem}-{stamp}-{n}{suffix}")
        n += 1
    return cand


def emit(report: dict, out_path: Path | None, as_json: bool) -> None:
    """Machine-readable stdout plus optional report file (non-destructive)."""
    verdicts = [c.get("verdict") for c in report.get("checks", [])]
    counts = {v: verdicts.count(v) for v in VERDICTS}
    report["summary"] = {
        "verdict": ("FAIL" if counts.get("FAIL") else
                    "REVIEW_REQUIRED" if counts.get("REVIEW_REQUIRED") else
                    "WARN" if counts.get("WARN") else
                    "PASS" if counts.get("PASS") else "NOT RUN"),
        "counts": counts,
    }
    if out_path is not None:
        out_path = nondestructive_path(out_path)
        text = (json.dumps(report, indent=2, ensure_ascii=False) if as_json
                else render_md(report))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"report: {out_path}")
    print(json.dumps(report if as_json else {"verdict": report["summary"]["verdict"],
                                             "counts": report["summary"]["counts"]},
                     indent=2, ensure_ascii=False))


def render_md(report: dict) -> str:
    lines = [f"# {report.get('title', 'Documentation report')}", "",
             f"Verdict: **{report.get('summary', {}).get('verdict', 'NOT RUN')}**", ""]
    for c in report.get("checks", []):
        lines.append(f"## {c['id']} — {c.get('verdict', 'NOT RUN')}")
        if c.get("detail"):
            lines.append("")
            lines.append(c["detail"])
        for item in c.get("findings", []):
            lines.append(f"- [{item.get('priority', '?')}] {item.get('path', '')}"
                         f"{':' + str(item.get('line')) if item.get('line') else ''}: "
                         f"{item.get('message', '')}")
        lines.append("")
    return "\n".join(lines)


def verdict_exit(report: dict) -> int:
    v = report["summary"]["verdict"]
    return {"PASS": 0, "WARN": 0, "NOT RUN": 0,
            "REVIEW_REQUIRED": 1, "FAIL": 2}[v]
