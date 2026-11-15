# semgrep-security

Use Semgrep as a reproducible security check after relevant code changes. Investigate whether findings apply to the actual project.

Profile: Private and Working. Preparation: Specify the changed area and existing Semgrep configuration. State whether confirmed findings should also be fixed.

Expected result: Scan results, assessed findings, and a follow-up scan after authorized corrections.

Requirements and limits: Repository rules take precedence over defaults. Semgrep must be available; a missing scanner is not a passed scan. A finding is a lead to investigate.

## semgrep-security: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh semgrep-security
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the semgrep-security skill. Check the upload-handler changes using the repository Semgrep configuration. Confirm relevant findings in code and fix them within the requested scope.
```

**Codex:**

```text
Use the semgrep-security skill. Rerun the relevant Semgrep check after the authentication fix. Report the configuration, scanned scope, and remaining findings.
```

**oh-my-pi:**

```text
Use the semgrep-security skill. Assess this Semgrep finding using the data flow. Explain whether it applies and briefly document a false positive if appropriate.
```

## semgrep-security: Self-test

Run from the repository root:

```bash
python3 skills/semgrep-security/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [tests/](tests/): Self-tests and fixtures.

## Choose the scan configuration

This skill does not bundle or install Semgrep. Find the repository configuration
and existing CI invocation first, then use the same rules and exclusions locally.
If no configuration exists, choose rules to match the requested scope rather
than presenting an invented default as project policy.
