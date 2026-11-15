# ci-triage

Read actual job logs and CI configuration, distinguish code regressions from infrastructure, dependency, and permission problems, and reproduce the relevant failure locally when possible.

Profile: Private and Working. Preparation: Provide the PR, branch, job link, or logs. State whether you want a local fix.

Expected result: An evidence-backed cause, a local fix when requested, and results from relevant checks.

Requirements and limits: Remote access requires an authenticated forge tool. A local fix request does not automatically authorize pushing, rerunning jobs, or changing secrets and protection rules.

## ci-triage: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ci-triage
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ci-triage skill. Analyze the failing GitHub Actions job linked in this PR. Find the first relevant cause, fix it locally, and run the appropriate check.
```

**Codex:**

```text
Use the ci-triage skill. The build fails only in CI. Compare the workflow, lockfile, and local runtime. Separate an environment issue from a code regression.
```

**oh-my-pi:**

```text
Use the ci-triage skill. Analyze these GitLab CI logs without remote access. Explain the cause supported by the logs and identify what remains unverified.
```

## ci-triage: Self-test

Run from the repository root:

```bash
python3 skills/ci-triage/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [tests/](tests/): Self-tests and fixtures.

## Work without remote access

Supply the relevant log excerpt and workflow in the request. The agent can use
them to investigate the cause and run local checks. Remote job status and results
remain unverified without access. This skill supplies no forge client or credentials.
