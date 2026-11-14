#!/usr/bin/env python3
"""project_audit.py — local website project audit + safe rewrite application.

Part of the human-writing skill. Audit side runs the text rules on
Markdown/MDX/JSON/YAML content and Astro/React/Next/Vue/Svelte source text.
Apply side edits ONLY prose regions outside protected spans (code fences,
components, interpolation, frontmatter, URLs) and defaults to dry-run.

Usage:
    python3 project_audit.py audit  <dir> [--format text|json] [--out FILE]
    python3 project_audit.py plan   <dir> --out patch.json          # proposals
    python3 project_audit.py apply  <dir> --patch patch.json [--write]
    python3 project_audit.py validate <dir> [--build CMD] [--test CMD]

'apply' without --write prints the diff (dry run). Rewrites of prose are
authored by the calling agent and supplied via the patch file; this tool
validates and applies them structurally. It never rewrites prose itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hw_extract import extract_json_content, extract_markdown
from hw_report import scores, to_json
from hw_rules import RULES, scan
from hw_text import detect_lang

CONTENT_GLOBS = ["**/*.md", "**/*.mdx", "**/*.markdown"]
CODE_GLOBS = ["**/*.astro", "**/*.tsx", "**/*.jsx", "**/*.vue", "**/*.svelte"]
DATA_GLOBS = ["**/*.json", "!**/package-lock.json", "!**/*.min.json", "**/*.yml", "**/*.yaml"]
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".astro", ".output", "vendor"}

# Protected spans inside template/code files. Editable text = prose between them.
PROTECT = re.compile(
    r"```.*?```|~~~.*?~~~|`[^`\n]+`|<!--.*?-->|/\*.*?\*/"
    r"|\{\{[^{}]*\}\}|\{[^{}]*\}"                                   # mustache/JSX exprs
    r"|<[A-Za-z][^>]*>|</[A-Za-z][^>]*>"                             # tags
    r"|import\s+[^\n]+|export\s+[^\n]+"
    r"|\b(?:href|src|alt|class|id|to|slot|aria-\w+|data-\w+)=[\"'][^\"']*[\"']",
    re.S,
)


def files_in(root: Path, include_code: bool = True) -> list[Path]:
    out = []
    pats = CONTENT_GLOBS + DATA_GLOBS + (CODE_GLOBS if include_code else [])
    for pat in pats:
        if pat.startswith("!"):
            continue
        for f in root.glob(pat):
            if f.is_file() and not any(part in SKIP_DIRS for part in f.parts):
                out.append(f)
    return sorted(set(out))


# ---------------------------------------------------------------- protected regions
def editable_spans(text: str) -> list[tuple[int, int]]:
    """Prose ranges: outside protected spans, outside frontmatter block."""
    blocked = [m.span() for m in PROTECT.finditer(text)]
    fm = re.match(r"^---\n.*?\n---\n", text, re.S)
    if fm:
        blocked.insert(0, fm.span())
    blocked.sort()
    spans, pos = [], 0
    for s, e in blocked:
        if s > pos:
            spans.append((pos, s))
        pos = max(pos, e)
    if pos < len(text):
        spans.append((pos, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def prose_chunks(text: str) -> list[tuple[int, int, str]]:
    out = []
    for s, e in editable_spans(text):
        chunk = text[s:e]
        for para in re.split(r"(\n\s*\n)", chunk):
            if para.strip() and not re.fullmatch(r"\s*", para):
                start = s + chunk.index(para)
                out.append((start, start + len(para), para))
    return out


def audit_file(path: Path, root: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    rel = str(path.relative_to(root))
    if path.suffix in (".json", ".yml", ".yaml"):
        page = extract_json_content(text, rel)
        findings = scan(page.main_text, None)
        return {"file": rel, "kind": "data", "findings": [f.as_dict() for f in findings]}
    chunks = prose_chunks(text)
    joined = "\n\n".join(t for _, _, t in chunks)
    if len(joined.split()) < 20:
        return {"file": rel, "kind": "protected", "findings": [], "note": "no editable prose"}
    lang = detect_lang(joined)
    findings = scan(joined, lang if lang in ("de", "en") else "en")
    return {"file": rel, "kind": path.suffix.lstrip("."), "findings": [f.as_dict() for f in findings],
            "editable_spans": len(chunks)}


# ---------------------------------------------------------------- patch model
# A patch entry: {"file": rel, "span": [start,end], "original": str,
#                 "replacement": str, "reason": str, "approved": true}
def build_plan(root: Path, proposals: list[dict]) -> dict:
    """Validate agent-proposed replacements touch no protected spans."""
    plan, errors = [], []
    for prop in proposals:
        f = root / prop["file"]
        if not f.is_file():
            errors.append(f"missing file: {prop['file']}")
            continue
        text = f.read_text(encoding="utf-8")
        s, e = prop["span"]
        cur = text[s:e]
        if cur != prop["original"]:
            errors.append(f"span drift in {prop['file']}:{s}")
            continue
        prot_new = [m.group(0) for m in PROTECT.finditer(prop["replacement"])]
        prot_old = [m.group(0) for m in PROTECT.finditer(prop["original"])]
        if [p for p in prot_new if p not in prot_old]:
            errors.append(f"replacement adds protected markup in {prop['file']}:{s} — manual patch required")
            continue
        plan.append({**prop, "status": "ready"})
    return {"root": str(root), "plan": plan, "errors": errors, "apply": "dry-run unless --write"}


def apply_plan(root: Path, patch: dict, write: bool) -> str:
    """Apply ready entries; offsets applied back-to-front per file."""
    by_file: dict[str, list[dict]] = {}
    for entry in patch.get("plan", []):
        if entry.get("status") == "ready":
            by_file.setdefault(entry["file"], []).append(entry)
    diffs, applied = [], 0
    for rel, entries in by_file.items():
        f = root / rel
        text = f.read_text(encoding="utf-8")
        for entry in sorted(entries, key=lambda e: -e["span"][0]):
            s, e = entry["span"]
            if text[s:e] != entry["original"]:
                diffs.append(f"--- {rel}:{s}\nSKIP (drift)")
                continue
            text = text[:s] + entry["replacement"] + text[e:]
            applied += 1
        if write:
            f.write_text(text, encoding="utf-8")
        diffs.append(f"--- {rel}\n{applied} span(s) {'written' if write else 'would change (dry-run)'}")
    return "\n".join(diffs + [f"applied: {applied}", f"mode: {'write' if write else 'dry-run'}"])


# ---------------------------------------------------------------- validate
def validate(root: Path, build_cmd: str, test_cmd: str) -> dict:
    out = {}
    for name, cmd in (("build", build_cmd), ("tests", test_cmd)):
        if not cmd:
            out[name] = "skipped (no command configured)"
            continue
        try:
            r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=600)
            out[name] = {"code": r.returncode, "tail": (r.stdout + r.stderr)[-800:]}
        except subprocess.TimeoutExpired:
            out[name] = {"code": -1, "tail": "timeout 600s"}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["audit", "plan", "apply", "validate"])
    ap.add_argument("root", type=Path)
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--proposals", type=Path, help="JSON file of agent rewrite proposals for plan")
    ap.add_argument("--patch", type=Path, help="patch json from plan")
    ap.add_argument("--write", action="store_true", help="actually write files (apply)")
    ap.add_argument("--build", default="")
    ap.add_argument("--test", default="")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    rc = 0

    if args.mode == "audit":
        results = [r for f in files_in(root) if (r := audit_file(f, root))]
        total = sum(len(r["findings"]) for r in results)
        payload = {"tool": "human-writing-project-audit", "root": str(root),
                   "files": len(results), "findings": total, "results": results}
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json"
              else "\n".join(f"{r['file']}: {len(r['findings'])} ({r.get('kind')})" for r in results)
              + f"\nfiles: {len(results)} findings: {total}")
        rc = 1 if total else 0
    elif args.mode == "plan":
        proposals = json.loads(args.proposals.read_text()) if args.proposals and args.proposals.is_file() else []
        plan = build_plan(root, proposals if isinstance(proposals, list) else proposals.get("proposals", []))
        out = json.dumps(plan, ensure_ascii=False, indent=2)
        args.out.write_text(out, encoding="utf-8") if args.out else print(out)
        rc = 1 if plan["errors"] else 0
    elif args.mode == "apply":
        if not args.patch or not args.patch.is_file():
            print("error: --patch required", file=sys.stderr)
            return 2
        print(apply_plan(root, json.loads(args.patch.read_text()), args.write))
    else:
        print(json.dumps(validate(root, args.build, args.test), ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
