#!/usr/bin/env python3
"""lint_text.py — local, offline text linter for the human-writing skill.

Usage:
    python3 lint_text.py README.md [more.md ...] [--lang de|en|auto]
                         [--format text|json] [--max-findings N]
                         [--quiet] [--fail-on high|med|all] [-]   # - = STDIN

Exit codes (CI): 0 no findings at/above threshold, 1 findings at/above
threshold, 2 usage/input error. Detection only — this tool never rewrites
text; rewriting is the calling agent's job under the skill's rules.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hw_report import dump_json, scores, to_json, to_text  # noqa: E402
from hw_rules import RULES, scan  # noqa: E402
from hw_text import detect_lang, words  # noqa: E402

SEV_ORDER = {"high": 3, "med": 2, "low": 1}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="files to lint; '-' reads STDIN")
    ap.add_argument("--lang", choices=["de", "en", "auto"], default="auto")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--max-findings", type=int, default=400)
    ap.add_argument("--fail-on", choices=["high", "med", "all"], default="all",
                    help="severity threshold for exit code 1")
    ap.add_argument("--quiet", action="store_true", help="exit codes only")
    args = ap.parse_args(argv)

    if not args.paths:
        args.paths = ["-"]
    threshold = {"high": 3, "med": 2, "all": 1}[args.fail_on]
    failed = False
    all_findings = []
    for path in args.paths:
        try:
            text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        if not text.strip():
            print(f"skip: {path} empty", file=sys.stderr)
            continue
        lang = args.lang if args.lang != "auto" else (detect_lang(text) if detect_lang(text) in ("de", "en") else "en")
        findings = scan(text, lang, max_findings=args.max_findings)
        all_findings.extend(findings)
        failed = failed or any(SEV_ORDER[RULES[f.rule][1]] >= threshold for f in findings)
        if args.quiet:
            continue
        sc = scores(findings, len(words(text)))
        if args.format == "json":
            print(dump_json(to_json(findings, lang=lang, scores_=sc, source=path)))
        else:
            print(to_text(findings, lang=lang, scores_=sc, source=path))
        print()
    if args.quiet:
        return 1 if failed else 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
