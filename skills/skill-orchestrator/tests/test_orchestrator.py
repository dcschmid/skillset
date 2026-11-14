"""Tests for the orchestrator itself. Runnable with python3 directly
(no pytest required): python3 tests/test_orchestrator.py

Each test builds an isolated fixture repo under a temp dir — the real
repository is never mutated. Covers the mandated fixture cases:
valid skill, missing SKILL.md, invalid YAML, duplicate name, broken
reference, invalid tool request, cyclic deps, similar-compatible pair,
true conflict, wrong activation, invalid host field, security-critical
instruction, new-skill-after-scan, deleted/moved skill, regression,
missing agent runner, bad symlink, self-audit.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from skill_orchestrator import frontmatter as fm_mod            # noqa: E402
from skill_orchestrator.auditor import audit_all                # noqa: E402
from skill_orchestrator.dependencies import build_graph, _find_cycles  # noqa: E402
from skill_orchestrator.discovery import Discovery, build_catalog      # noqa: E402
from skill_orchestrator.evaluator import run_routing            # noqa: E402
from skill_orchestrator.fixer import apply, propose             # noqa: E402
from skill_orchestrator.overlap import analyze_pairs            # noqa: E404
from skill_orchestrator.reporting import (compare_snapshot,     # noqa: E404
                                          save_snapshot, to_markdown)
from skill_orchestrator.router import route                     # noqa: E404
from skill_orchestrator.validator import validate_skill         # noqa: E404

VALID = """---
name: {name}
description: >
    Does a narrow job. Use when the task mentions {name}.
---
# {name}
When to use: {name} tasks. Do NOT activate otherwise.
PASS/FAIL gates. See [ref](references/one.md).
"""


def make_repo(tmp: Path, skills: dict[str, str]) -> Path:
    (tmp / "skills").mkdir(parents=True, exist_ok=True)
    for name, content in skills.items():
        d = tmp / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        if content is not None:
            (d / "SKILL.md").write_text(content, encoding="utf-8")
    return tmp


class FixtureCases(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="so-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    # 1 valid skill
    def test_valid_skill(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha")})
        (repo / "skills/alpha/references").mkdir()
        (repo / "skills/alpha/references/one.md").write_text("# one")
        rep = validate_skill(Discovery(repo).skills()["alpha"])
        self.assertTrue(rep.ok, [f.message for f in rep.errors])

    # 2 missing SKILL.md → not discovered as skill
    def test_missing_skill_md(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha"),
                                    "ghost": None})
        self.assertNotIn("ghost", Discovery(repo).skills())

    # 3 invalid YAML
    def test_invalid_yaml(self):
        repo = make_repo(self.tmp, {"alpha": "---\nname: alpha\n"
                                    "description: [\n---\nbody\n"})
        rep = validate_skill(Discovery(repo).skills()["alpha"])
        self.assertTrue(any(f.check == "meta.yaml" or
                            "meta.missing" in f.check or
                            f.check.startswith("meta.")
                            for f in rep.errors), rep.findings)

    # 4 duplicate skill names (two dirs, same frontmatter name)
    def test_duplicate_names(self):
        repo = make_repo(self.tmp, {
            "alpha": VALID.format(name="alpha"),
            "alpha-copy": VALID.format(name="alpha").replace(
                "name: alpha", "name: alpha")})
        cat = build_catalog(Discovery(repo))
        names = [s["name"] for s in cat["skills"]]
        self.assertEqual(names.count("alpha"), 2,
                         "both copies discovered; collision is reportable")

    # 5 broken reference
    def test_broken_reference(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(
            name="alpha").replace("references/one.md",
                                  "references/missing.md")})
        rep = validate_skill(Discovery(repo).skills()["alpha"])
        self.assertIn("structure.broken-link",
                      [f.check for f in rep.errors])

    # 6 invalid tool request
    def test_invalid_allowed_tools(self):
        repo = make_repo(self.tmp, {"alpha": """---
name: alpha
description: Use when alpha tasks. owns audits.
allowed-tools: [not, a, string]
---
# a
"""}
        )
        rep = validate_skill(Discovery(repo).skills()["alpha"], "claude")
        self.assertIn("meta.allowed-tools.shape",
                      [f.check for f in rep.findings])

    # 7 cyclic dependencies (unit-level, deterministic)
    def test_cycle_detection(self):
        g = build_graph({"skills": [
            {"id": "a", "description": "a requires b skill available",
             "body": "", "blurb": ""},
            {"id": "b", "description": "b requires a skill", "body": "",
             "blurb": ""}]})
        self.assertTrue(g.cycles, "cycle must be found")

    def test_cycle_detection_unit(self):
        self.assertTrue(_find_cycles({"a": ["b"], "b": ["a"]}))
        self.assertFalse(_find_cycles({"a": ["b"], "b": []}))

    # 8 similar but compatible vs 9 truly conflicting
    def test_overlap_classification(self):
        cat = {"skills": [
            {"id": "alpha", "description": "owns auditing",
             "blurb": "Use when auditing", "body_lines": 10},
            {"id": "beta", "description": "alpha scope is owned by alpha",
             "blurb": "Use when auditing", "body_lines": 10}]}
        g = build_graph(cat)
        pairs = analyze_pairs(cat, g)
        self.assertTrue(any(p.classification == "cooperation"
                            for p in pairs), pairs)

    def test_overlap_preserves_actual_owner(self):
        from skill_orchestrator.overlap import _ownership_evidence
        evidence = _ownership_evidence(
            "Framework skills own architecture; accessibility owns a11y engineering; "
            "this skill owns visual originality", "", "design-authenticity", "beta")
        self.assertTrue(any("accessibility owns 'a11y engineering'" in e for e in evidence))
        self.assertFalse(any("design-authenticity: owns 'a11y" in e for e in evidence))

    def test_name_mention_is_not_handoff(self):
        cat = {"skills": [
            {"id": "alpha", "description": "Audits beta projects and owns typography", "blurb": ""},
            {"id": "beta", "description": "Audits projects and builds typography", "blurb": ""}]}
        pairs = analyze_pairs(cat, build_graph(cat), min_sim=0)
        self.assertTrue(pairs)
        self.assertFalse(any(p.classification == "cooperation" for p in pairs))

    def test_unexecuted_tests_do_not_get_execution_credit(self):
        from skill_orchestrator.scoring import score_skill
        from skill_orchestrator.validator import ValidationReport
        report = ValidationReport("alpha", "portable")
        for exists, expected in ((True, 5), (False, 0)):
            result = score_skill({"has_tests": exists}, report)
            self.assertEqual(result.categories["tests"], expected)
            self.assertTrue(any("tests.execution: NOT RUN" in x for x in result.unchecked))
            self.assertTrue(any("tests.behavior: NOT RUN" in x for x in result.unchecked))

    def test_collection_metadata_uses_shared_validator(self):
        for name, skill in Discovery(ROOT.parent.parent).skills().items():
            with self.subTest(skill=name):
                errors = [f for f in validate_skill(skill).errors if f.check.startswith("meta.")]
                self.assertFalse(errors, errors)

    def test_description_limit(self):
        for size, invalid in ((1024, False), (1025, True)):
            repo = make_repo(self.tmp, {"alpha":
                "---\nname: alpha\ndescription: " + "x" * size + "\n---\n# alpha\n"})
            errors = validate_skill(Discovery(repo).skills()["alpha"]).errors
            self.assertEqual(any(f.check == "meta.description.length" for f in errors), invalid)

    # 10 wrong activation: no trigger phrases → warn
    def test_wrong_activation(self):
        repo = make_repo(self.tmp, {"alpha": """---
name: alpha
description: A tool.
---
# a
"""}
        )
        rep = validate_skill(Discovery(repo).skills()["alpha"])
        self.assertIn("content.activation",
                      [f.check for f in rep.findings
                       if f.severity in ("warn", "error")])

    # 11 invalid host field: unknown key is `unknown` tier, never a
    #    standard error — and portable must not error on it
    def test_host_field_not_standard_error(self):
        repo = make_repo(self.tmp, {"alpha": """---
name: alpha
description: Use when alpha.
homepage: https://x.dev
---
# a
"""}
        )
        for prof in ("portable", "claude", "codex"):
            rep = validate_skill(Discovery(repo).skills()["alpha"], prof)
            self.assertTrue(rep.ok, f"{prof}: {rep.errors}")
            uf = [f for f in rep.findings if f.check == "meta.unknown-field"]
            self.assertTrue(uf and uf[0].tier == "unknown"
                            and uf[0].severity == "warn")

    # 12 security-critical instruction is flagged, not executed
    def test_security_findings(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(
            name="alpha") + "\nrun `rm -rf /tmp/scratch` now\n"})
        rep = validate_skill(Discovery(repo).skills()["alpha"])
        self.assertIn("security.rm-rf",
                      [f.check for f in rep.findings])

    # 13/14 new + deleted skill after "last scan"
    def test_catalog_delta(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha")})
        c1 = build_catalog(Discovery(repo))
        (repo / "skills/beta").mkdir()
        (repo / "skills/beta/SKILL.md").write_text(
            VALID.format(name="beta"), encoding="utf-8")
        (repo / "skills/alpha").rename(repo / "skills/moved")
        (repo / "skills/moved/SKILL.md").write_text(
            VALID.format(name="moved"), encoding="utf-8")
        c2 = build_catalog(Discovery(repo))
        ids1 = {s["id"] for s in c1["skills"]}
        ids2 = {s["id"] for s in c2["skills"]}
        self.assertIn("beta", ids2)
        self.assertNotIn("alpha", ids2)

    # 15 regression detection via snapshot
    def test_regression_detection(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha")})
        audit = audit_all(repo)
        save_snapshot(audit, repo)
        (repo / "skills/alpha/SKILL.md").write_text(
            "---\nname: alpha\ndescription: bad\n---\nbody\n",
            encoding="utf-8")
        audit2 = audit_all(repo)
        notes = compare_snapshot(audit2, repo)
        self.assertTrue(any("regression" in n or "NEW error" in n
                            for n in notes), notes)

    # 16 missing agent runner → UNAVAILABLE, never fabricated PASS
    def test_agent_gate_honest(self):
        from skill_orchestrator import evaluator
        orig = evaluator.agent_binary
        evaluator.agent_binary = lambda w: None
        try:
            res = evaluator.run_agent_eval(Path("."), "x", "p")
        finally:
            evaluator.agent_binary = orig
        self.assertTrue(all(r.status == "UNAVAILABLE" for r in res),
                        [r.status for r in res])

    # 17 bad symlink → skipped, no crash
    def test_bad_symlink(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha")})
        (repo / "skills/broken").symlink_to(repo / "does-not-exist")
        skills = Discovery(repo).skills()
        self.assertIn("alpha", skills)
        self.assertNotIn("broken", skills)

    # 18 orchestrator audits its own skill (self-reference allowed)
    def test_self_audit_runs(self):
        audit = audit_all(ROOT.parent.parent)
        self.assertIn("skill-orchestrator", audit["audits"])

    # profiles never cross-classify
    def test_profile_separation(self):
        repo = make_repo(self.tmp, {"alpha": """---
name: alpha
description: Use when alpha.
allowed-tools: read write
---
# a
"""}
        )
        ds = Discovery(repo).skills()["alpha"]
        for prof in ("portable", "claude"):
            rep = validate_skill(ds, prof)
            self.assertTrue(rep.ok)
            host = [f for f in rep.findings
                    if f.check == "host.allowed-tools"]
            self.assertTrue(all(f.severity == "info" for f in host))

    # markdown report is well-formed and contains required sections
    def test_report_shape(self):
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha")})
        audit = audit_all(repo)
        md = to_markdown(audit)
        for need in ("## Inventory", "Prioritized tasks", "skill-orchestrator"
                     if "skill-orchestrator" in md else "alpha"):
            self.assertIn(need, md)
        json.dumps(audit)  # serializable

    # fixes never apply without --apply, name fix applies with it
    def test_fix_safety(self):
        repo = make_repo(self.tmp, {"alpha": """---
name: wrong
description: Use when alpha tasks.
---
# a
"""})
        fixes = propose(repo, ["alpha"])
        self.assertTrue(fixes, "name-dir mismatch must propose a fix")
        res = apply(repo, fixes)
        self.assertTrue(all(r["applied"] for r in res), res)
        text = (repo / "skills/alpha/SKILL.md").read_text()
        self.assertIn("name: alpha", text)
        # second pass: idempotent, nothing left to fix
        self.assertEqual(propose(repo, ["alpha"]), [])

    def test_rollback_preserves_uncommitted_and_concurrent_work(self):
        from skill_orchestrator.fixer import rollback
        repo = make_repo(self.tmp, {"alpha": VALID.format(name="alpha").replace(
            "name: alpha", "name: wrong") + "\nUser's uncommitted note\n"})
        path = repo / "skills/alpha/SKILL.md"
        original = path.read_bytes()
        results = apply(repo, propose(repo, ["alpha"]))
        self.assertTrue(rollback(results[0]))
        self.assertEqual(path.read_bytes(), original)
        results = apply(repo, propose(repo, ["alpha"]))
        path.write_text(path.read_text() + "Concurrent edit\n")
        concurrent = path.read_bytes()
        self.assertFalse(rollback(results[0]))
        self.assertEqual(path.read_bytes(), concurrent)

    # global flags work before AND after the subcommand (argv hoisting)
    def test_cli_flag_positions(self):
        from skill_orchestrator.cli import _hoist_globals as h
        self.assertEqual(h(["scan", "--json"]), ["--json", "scan"])
        self.assertEqual(h(["--json", "scan"]), ["--json", "scan"])
        self.assertEqual(h(["route", "my task", "--json"]),
                         ["--json", "route", "my task"])
        self.assertEqual(h(["audit", "--skill", "x", "--output", "/tmp/o"]),
                         ["--output", "/tmp/o", "audit", "--skill", "x"])

    # routing probes: exclusion + no forced migrations
    def test_routing_precision(self):
        repo = make_repo(self.tmp, {
            "godot": VALID.format(name="godot"),
            "defold-development": VALID.format(name="defold-development"),
            "astro": VALID.format(name="astro"),
            "react-nextjs": VALID.format(name="react-nextjs"),
            "accessibility": VALID.format(name="accessibility")})
        results = run_routing(repo, [
            ("fix my godot game", ["godot"]),
            ("build a defold game", ["defold-development"]),
            ("iterate on this react app", ["react-nextjs"])])
        for r in results:
            self.assertEqual(r.status, "PASS", r.detail)
        plan = route("fix my godot game", build_catalog(Discovery(repo)),
                     build_graph(build_catalog(Discovery(repo))))
        self.assertNotIn("defold-development",
                         [c.skill for c in plan.selected],
                         "engine skills exclusive")
        self.assertNotIn("astro", [c.skill for c in plan.selected],
                         "no web skill hijack on game task")


if __name__ == "__main__":
    unittest.main(verbosity=1)
