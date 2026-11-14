"""skill-orchestrator CLI.

Exit codes: 0 = success, 1 = validation findings (audit errors/blockers
or failed tests), 2 = technical error (repo not found, bad args).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .discovery import Discovery, build_catalog, find_repo_root
from .dependencies import build_graph
from .router import route
from .auditor import audit_all, audit_changed
from .overlap import analyze_pairs, find_conflicts
from . import evaluator, fixer, reporting


GLOBAL_FLAGS = {"--root": 1, "--profile": 1, "--json": 0, "--verbose": 0,
                "--output": 1}
SUBCOMMANDS = {"scan", "audit", "overlap", "route", "plan", "test", "eval",
               "fix", "report", "doctor"}


def _hoist_globals(argv: list[str]) -> list[str]:
    """Allow `cmd --json` as well as `--json cmd`: move recognized global
    flags from after the subcommand to before it. Stops at option values
    and the first `--`."""
    if "--" in argv:
        head, _, tail = argv.partition("--")
        return _hoist_globals(head) + ["--"] + tail
    sub_i = next((i for i, a in enumerate(argv) if a in SUBCOMMANDS), None)
    if sub_i is None:
        return argv
    head, rest = argv[:sub_i], argv[sub_i + 1:]
    moved, keep, i = [], [], 0
    while i < len(rest):
        tok = rest[i]
        name, _, inline = tok.partition("=")
        if name in GLOBAL_FLAGS:
            if GLOBAL_FLAGS[name] == 0 or inline:
                moved.append(tok)
                i += 1
            elif i + 1 < len(rest):
                moved += [tok, rest[i + 1]]
                i += 2
            else:
                moved.append(tok)
                i += 1
            continue
        keep.append(tok)
        i += 1
    # hoisted globals land BEFORE the subcommand token (the parent parser
    # consumes them); positionals like `route TASK` stay after it
    return head + moved + [argv[sub_i]] + keep


def main(argv: list[str] | None = None) -> int:
    argv = _hoist_globals(list(sys.argv[1:] if argv is None else argv))
    ap = argparse.ArgumentParser(
        prog="skill-orchestrator",
        description="Discovery, validation, routing and quality system "
                    "for a skillset repository.")
    ap.add_argument("--root", help="repository root (default: autodetect)")
    ap.add_argument("--profile", choices=["portable", "claude", "codex"],
                    default="portable")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--output", help="report/canvas output dir")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("scan", help="discover skills, print/write catalog")
    p = sub.add_parser("audit", help="validate + score skills")
    p.add_argument("--all", action="store_true")
    p.add_argument("--skill", action="append")
    p.add_argument("--changed", action="store_true")
    p.add_argument("--save", action="store_true",
                   help="store snapshot for regression comparison")
    p.add_argument("--report", action="store_true",
                   help="write markdown report to output dir")
    p = sub.add_parser("overlap", help="overlap/conflict analysis")
    p.add_argument("--skill", action="append",
                   help="limit to pairs involving these skills")
    p = sub.add_parser("route", help="routing plan for a task (read-only)")
    p.add_argument("task")
    p.add_argument("--skill", action="append", help="explicit selection")
    sub_ = sub.add_parser("plan", help="same as route; orchestration plan")
    sub_.add_argument("task")
    sub_.add_argument("--skill", action="append")
    p = sub.add_parser("test", help="static/routing/conflict/integration tiers")
    p.add_argument("--all", action="store_true")
    p = sub.add_parser("eval", help="behavior eval via a real agent CLI "
                                    "(honest gating)")
    p.add_argument("--skill", required=True)
    p.add_argument("--prompt", default=None)
    p.add_argument("--expect", action="append", default=[])
    p = sub.add_parser("fix", help="repair proposals; dry-run unless --apply")
    p.add_argument("--skill", action="append")
    p.add_argument("--dry-run", action="store_true",
                   help="default behavior anyway")
    p.add_argument("--apply", action="store_true")
    sub.add_parser("report", help="markdown report of latest audit")
    sub.add_parser("doctor", help="environment + repository health")
    args = ap.parse_args(argv)

    try:
        root = Path(args.root).resolve() if args.root else find_repo_root()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        return _dispatch(args, root)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # technical
        if args.verbose:
            raise
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


def _dispatch(args, root) -> int:
    out = Path(args.output) if args.output else None
    if args.cmd == "scan":
        return _scan(args, root, out)
    if args.cmd == "audit":
        return _audit(args, root, out)
    if args.cmd == "overlap":
        return _overlap(args, root, out)
    if args.cmd in ("route", "plan"):
        return _route(args, root)
    if args.cmd == "test":
        return _test(args, root)
    if args.cmd == "eval":
        return _eval(args, root)
    if args.cmd == "fix":
        return _fix(args, root, apply=not args.dry_run)
    if args.cmd == "report":
        return _report(args, root, out)
    if args.cmd == "doctor":
        return _doctor(args, root)
    return 2


def _emit(payload, as_json: bool, human) -> None:
    if as_json:
        print(json.dumps(payload, indent=1, ensure_ascii=False))
    else:
        human(payload)


def _scan(args, root, out) -> int:
    disc = Discovery(root)
    cat = build_catalog(disc)
    if out:
        p = reporting.output_dir(root, str(out)) / "skill-catalog.json"
        p.write_text(json.dumps(cat, indent=1), encoding="utf-8")
        print(f"catalog → {p}")
    if args.as_json:
        print(json.dumps(cat, indent=1, ensure_ascii=False))
    else:
        print(f"skills discovered: {cat['skill_count']} in {root}")
        for s in cat["skills"]:
            flags = []
            if s["frontmatter_error"]:
                flags.append("yaml-error")
            if not s["name_matches_dir"]:
                flags.append("name!=dir")
            if s["symlink"]:
                flags.append("symlink")
            print(f"  {s['id']:<36} {s['body_lines']:>4} lines  "
                  f"{' '.join(flags)}")
    return 0


def _audit(args, root, out) -> int:
    only = set(args.skill or [])
    if args.changed:
        audit = audit_changed(root, args.profile)
    else:
        audit = audit_all(root, args.profile, only=only or None)
    audit["regressions"] = reporting.compare_snapshot(audit, root,
                                                      out and str(out))
    if args.save:
        p = reporting.save_snapshot(audit, root, out and str(out))
        print(f"snapshot → {p}")
    if args.report:
        d = reporting.output_dir(root, out and str(out))
        rp = d / "audit-report.md"
        rp.write_text(reporting.to_markdown(audit), encoding="utf-8")
        print(f"report → {rp}")
    bad = _audit_bad(audit)
    if args.as_json:
        print(json.dumps(audit, indent=1, ensure_ascii=False))
    else:
        _print_audit(audit)
    return 1 if bad else 0


def _audit_bad(audit) -> bool:
    return any(a["score"]["score"] < 70 or a["score"]["blockers"]
               for a in audit["audits"].values())


def _print_audit(audit):
    for sid in sorted(audit["audits"]):
        s = audit["audits"][sid]["score"]
        mark = {"Excellent": "✓", "Good": "✓", "Needs Improvement": "~",
                "Poor": "✗", "Critical": "✗"}.get(s["grade"], "?")
        print(f"{mark} {sid:<36} {s['score']:>3}/100  {s['grade']}")
        for b in s["blockers"]:
            print(f"    BLOCKER {b}")
        for u in s["unchecked"]:
            print(f"    unchecked: {u}")
    if audit["cycles"]:
        print(f"cycles: {audit['cycles']}")
    for r in audit.get("regressions") or []:
        print(f"regression: {r}")


def _overlap(args, root, out) -> int:
    disc = Discovery(root)
    cat = build_catalog(disc)
    g = build_graph(cat)
    pairs = analyze_pairs(cat, g)
    if args.skill:
        keep = set(args.skill)
        pairs = [p for p in pairs if keep & set(p.a if isinstance(p.a, str)
                                                else "")
                 or keep & set([p.a, p.b])]
    payload = {"pairs": [p.to_dict() for p in pairs],
               "conflicts": find_conflicts(cat)}
    _emit(payload, args.as_json, _print_overlap)
    return 1 if any(p.classification == "conflict" for p in pairs) else 0


def _print_overlap(payload):
    for p in payload["pairs"]:
        print(f"[{p['classification']:<13}] sev={p['severity']:<6} "
              f"{p['skills'][0]} ↔ {p['skills'][1]} (sim {p['similarity']})")
        for ev in p["evidence"][:3]:
            print(f"    evidence: {ev}")
        print(f"    proposal: {p['proposal']}")
    for c in payload["conflicts"]:
        print(f"[conflict-probe] {c['type']}: {c['classification']}")
        for ev in c["evidence"]:
            print(f"    evidence: {ev}")


def _route(args, root) -> int:
    disc = Discovery(root)
    cat = build_catalog(disc)
    g = build_graph(cat)
    plan = route(args.task, cat, g, explicit=args.skill)
    if args.as_json:
        print(json.dumps(plan.to_dict(), indent=1, ensure_ascii=False))
        return 0
    print(f"task: {plan.task}")
    print(f"tech: {plan.tech}  domains: {plan.domains}")
    for c in plan.selected:
        print(f"  {c.role:<11} {c.skill:<36} ({c.score:>3}) {c.reason}")
    for sid, why in plan.considered_rejected:
        print(f"  rejected    {sid:<36} {why}")
    print(f"order: {' → '.join(plan.order)}")
    for g_ in plan.quality_gates:
        print(f"gate: {g_}")
    return 0


def _test(args, root) -> int:
    tiers = evaluator.run_all(root, args.profile)
    if args.as_json:
        print(json.dumps(tiers, indent=1, ensure_ascii=False))
    else:
        for tier, results in tiers["tiers"].items():
            print(f"── {tier}")
            for r in results:
                print(f"  {r['status']:<11} {r['name']:<40} {r['detail']}")
        print("agent-evals: gated — `eval --skill <id>` needs a local "
              "agent CLI; SKIPPED/UNAVAILABLE reported honestly")
    print(json.dumps({"summary": tiers["summary"]}))
    return 1 if tiers["summary"].get("FAIL") else 0


def _eval(args, root) -> int:
    prompt = args.prompt or (
        f"Using the skill '{args.skill}' if available, state what it is "
        "for in one sentence, then STOP.")
    res = evaluator.run_agent_eval(root, args.skill, prompt, args.expect)
    if args.as_json:
        print(json.dumps([r.to_dict() for r in res], indent=1))
    for r in res:
        print(f"{r.status:<11} {r.name}: {r.detail}")
    return 1 if any(r.status == "FAIL" for r in res) else 0


def _fix(args, root, apply: bool) -> int:
    fixes = fixer.propose(root, args.skill)
    if not fixes:
        print("no safe fixes proposed")
        return 0
    for f in fixes:
        print(f"── fix[{f.kind}] {f.skill}/{f.file} "
              f"({'APPLIED' if apply else 'proposal'})")
        print(f.diff())
    if apply:
        results = fixer.apply(root, fixes)
        for r in results:
            print(json.dumps(r))
        return 0 if all(r.get("applied") for r in results) else 1
    print(f"{len(fixes)} proposal(s); rerun with --apply after review")
    return 0


def _report(args, root, out) -> int:
    audit = audit_all(root, args.profile)
    audit["regressions"] = reporting.compare_snapshot(audit, root,
                                                      out and str(out))
    md = reporting.to_markdown(audit)
    d = reporting.output_dir(root, out and str(out))
    (d / "audit-report.md").write_text(md, encoding="utf-8")
    (d / "last-audit.json").write_text(json.dumps(
        {k: audit[k] for k in ("generated_at", "profile", "catalog",
                               "audits", "cycles", "conflicts")},
        indent=1), encoding="utf-8")
    print(md if not args.as_json else json.dumps(audit, indent=1)[:2000])
    print(f"→ {d / 'audit-report.md'}")
    return 0


def _doctor(args, root) -> int:
    import shutil
    try:
        import yaml  # noqa: F401
        have_yaml = True
    except Exception:
        have_yaml = False
    disc = Discovery(root)
    disc.skills()
    info = {
        "root": str(root),
        "python": sys.version.split()[0],
        "pyyaml": have_yaml,
        "agents": {a: bool(shutil.which(a)) for a in ("claude", "codex")},
        "git": bool(shutil.which("git")),
        "skills_discovered": len(disc.skills()),
        "profiles": ["portable", "claude", "codex"],
    }
    if args.as_json:
        print(json.dumps(info, indent=1))
    else:
        for k, v in info.items():
            print(f"{k}: {v}")
        print("note: missing PyYAML → built-in subset parser; missing "
              "agent CLIs → agent-eval tier UNAVAILABLE (not faked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
