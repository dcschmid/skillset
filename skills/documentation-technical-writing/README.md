# documentation-technical-writing

Create and maintain READMEs, API documentation, architecture notes, and guides. Check claims and commands against source files, manifests, and actual verification.

Profile: Private and Working. Preparation: Specify documents, audience, language, and scope. Explain the expected outcome of important steps.

Expected result: Updated documentation with practical examples, valid references, and an account of the checks performed.

Requirements and limits: Code is the source of truth for technical claims. Commands that were not executed remain NOT RUN. A documentation request does not automatically authorize application code changes.

## documentation-technical-writing: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh documentation-technical-writing
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the documentation-technical-writing skill. Rewrite README.md in English for new developers. Check installation, start, and test instructions against the project and add a complete getting-started example.
```

**Codex:**

```text
Use the documentation-technical-writing skill. Check docs/ against the API implementation. Identify outdated endpoints, incorrect parameters, and commands that no longer match the project.
```

**oh-my-pi:**

```text
Use the documentation-technical-writing skill. Update the guides affected by this change. Preserve valid examples and identify commands you could not execute.
```

## documentation-technical-writing: Self-test

Run from the repository root:

```bash
python3 skills/documentation-technical-writing/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [docs_audit.py](scripts/docs_audit.py)
- [docs_check.py](scripts/docs_check.py)
- [docs_lib.py](scripts/docs_lib.py)
- [docs_sync.py](scripts/docs_sync.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/documentation-technical-writing` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/docs_audit.py /path/to/project
python3 scripts/docs_check.py /path/to/project
```
