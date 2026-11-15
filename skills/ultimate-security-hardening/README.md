# ultimate-security-hardening

Inspect attack surfaces, confirm suspected vulnerabilities in code, and verify fixes with regression tests and another scan. Cover application code, dependencies, and infrastructure as needed.

Profile: Private and Working. Preparation: Specify the project and relevant features. State whether you want findings only or local fixes as well.

Expected result: Prioritized findings with code evidence, tool coverage, fix status, and verification results.

Requirements and limits: Missing scanners and untested areas remain coverage gaps. A report does not guarantee complete security. Keep secrets out of output; high-risk actions require appropriate authorization.

## ultimate-security-hardening: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-security-hardening
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-security-hardening skill. Audit the API service for authentication and authorization defects. Confirm findings with code evidence and report without editing files.
```

**Codex:**

```text
Use the ultimate-security-hardening skill. Fix the confirmed IDOR in order access. Add a regression test for another user and rerun the relevant security check.
```

**oh-my-pi:**

```text
Use the ultimate-security-hardening skill. Check dependencies, containers, and configuration before release. List available scanners, missing coverage, and remaining blockers.
```

## ultimate-security-hardening: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-security-hardening/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [workflows/](workflows/): Task-specific procedures.
- [templates/](templates/): Templates for the target project.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [check-tools.sh](scripts/check-tools.sh)
- [detect-project.sh](scripts/detect-project.sh)
- [run-security-audit.sh](scripts/run-security-audit.sh)
- [validate-report.py](scripts/validate-report.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/ultimate-security-hardening` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
bash scripts/detect-project.sh /path/to/project
bash scripts/check-tools.sh /path/to/project
```
