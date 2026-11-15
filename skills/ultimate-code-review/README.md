# ultimate-code-review

Review standards, requirements, bugs, security, testing, and performance. Findings include severity, confidence, and verifiable locations.

Profile: Private and Working. Preparation: Specify a branch, commit range, PR, or local changes. Include requirements and define the review scope.

Expected result: Prioritized findings, code evidence, and a coverage record showing reviewed and skipped areas.

Requirements and limits: Reviews are read-only by default. Fixes require an explicit request. Missing requirements and checks that were not run remain coverage gaps.

## ultimate-code-review: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-code-review
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-code-review skill. Review my uncommitted changes for bugs, security issues, and missing tests. Include new files and do not edit anything.
```

**Codex:**

```text
Use the ultimate-code-review skill. Review this branch against main using docs/spec.md as the requirements. Report evidence-backed findings with file and line references.
```

**oh-my-pi:**

```text
Use the ultimate-code-review skill. Review the last commit for API compatibility and performance. Separate confirmed issues from open questions.
```

## ultimate-code-review: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-code-review/tests/test_skill.py
```

Corrections belong to the explicitly requested fix mode (`--fix`); a normal review does not edit files. The documented remote-action rule is “No commit/push ever without approval”. Authorization already granted for that action remains valid.

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [collect_context.py](scripts/collect_context.py)
- [generate_report.py](scripts/generate_report.py)
- [git_review.py](scripts/git_review.py)
- [prepare_review.py](scripts/prepare_review.py)
- [validate_findings.py](scripts/validate_findings.py)

## Separate preparation from review

`scripts/prepare_review.py` prepares context and change scope; it does not review
code itself. An empty findings file produced during preparation is not a passed
review. Follow [SKILL.md](SKILL.md) for the full workflow. The scripts validate
and render the resulting findings. Use a new workspace for each run.
