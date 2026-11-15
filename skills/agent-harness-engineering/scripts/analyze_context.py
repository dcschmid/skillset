#!/usr/bin/env python3
"""analyze_context.py — context-budget analysis over instruction/prompt files.

Reads a context manifest JSON: {"layers": {"system": "path|text", ...}} or a
plain map of layer->file. Estimates tokens (transparent heuristic, marked as
estimate), flags layer overflow, cross-layer duplication, inline-vs-reference
violations, and secrets landing in instruction files.

Usage:
    python3 scripts/analyze_context.py manifest.json [--format json|markdown]
Exit: 0 clean, 1 findings, 2 input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness_lib import audit_context_layers, estimate_tokens  # noqa: E402

SECRET_PAT = __import__("re").compile(
    r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{16,}")
LAYER_BUDGETS = {"system": 1500, "project": 2000, "skills": 3000, "task": 4000,
                 "tool_results": 6000, "working": 2000, "persistent": 1000}


def load_layers(manifest: dict, base: Path):
    layers, missing = {}, []
    for name, ref in (manifest.get("layers") or manifest).items():
        if not isinstance(ref, str):
            continue
        p = (base / ref)
        if p.is_file():
            layers[name] = p.read_text(encoding="utf-8", errors="replace")
        else:
            layers[name] = ref if len(ref) < 4000 else ""
            if len(ref) >= 4000:
                missing.append(name)
    return layers, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", help="context manifest JSON")
    ap.add_argument("--budget", type=int, default=0, help="total token budget (0=report-only)")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args(argv)
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.manifest}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(manifest, dict):
        print("error: manifest must be an object", file=sys.stderr)
        return 2
    layers, unloaded = load_layers(manifest, Path(args.manifest).resolve().parent)
    if not layers:
        print("error: manifest references no readable layers — nothing analyzed (no fabricated verdict)",
              file=sys.stderr)
        return 2
    findings, sizes, budget = audit_context_layers(layers)
    for name, text in layers.items():
        cap = LAYER_BUDGETS.get(name, 4000)
        if sizes.get(name, 0) > cap:
            findings.append(f"layer '{name}' {sizes[name]} tok est > soft cap {cap} — compress or defer")
        for _ in SECRET_PAT.findall(text):
            findings.append(f"secret-looking literal in layer '{name}' — move to secret store")
    for name in unloaded:
        findings.append(f"layer '{name}' too large to inline and not a file path — unresolved reference")
    over = bool(args.budget and budget > args.budget)
    if over:
        findings.append(f"total {budget} tok est exceeds budget {args.budget}")
    report = {"manifest": str(args.manifest), "layer_tokens_estimate": sizes,
              "total_tokens_estimate": budget, "over_budget": over,
              "note": "token numbers are heuristic estimates unless the platform reports real usage",
              "findings": findings, "verdict": "PASS" if not findings else "FINDINGS"}
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"# Context analysis — {args.manifest}")
        print(f"~{budget} tokens (estimated). Verdict: **{report['verdict']}**\n")
        for k, v in sizes.items():
            print(f"- {k}: ~{v} tok")
        for f in findings:
            print(f"- {f}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
