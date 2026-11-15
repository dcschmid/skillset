# human-writing

Write and revise English and German documentation, website copy, articles, UX text, and creative prose. Preserve facts, terminology, and the author’s voice.

Profile: Private and Working. Preparation: Provide the text or path, audience, language, and purpose. Include representative writing samples when voice matters.

Expected result: A revision or audit with concrete observations. Python tools detect patterns; the agent writes the replacement prose.

Requirements and limits: Lint findings do not identify authorship. Protect code, URLs, technical terms, and facts. Project rewrites start as dry runs and are applied within the approval already given.

## human-writing: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh human-writing
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the human-writing skill. Rewrite README.md in English for developers seeing the project for the first time. Preserve commands, links, and facts, and replace filler with concrete explanations.
```

**Codex:**

```text
Use the human-writing skill. Audit these three posts for repetition and empty phrasing. Report only, with a suggested improvement for each finding.
```

**oh-my-pi:**

```text
Use the human-writing skill. Rewrite the introduction using my supplied samples as a voice reference. Preserve my tone and do not invent product promises.
```

## human-writing: Self-test

Run from the repository root:

```bash
python3 skills/human-writing/tests/test_lint_text.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [hw_extract.py](scripts/hw_extract.py)
- [hw_http.py](scripts/hw_http.py)
- [hw_report.py](scripts/hw_report.py)
- [hw_rules.py](scripts/hw_rules.py)
- [hw_text.py](scripts/hw_text.py)
- [lint_text.py](scripts/lint_text.py)
- [project_audit.py](scripts/project_audit.py)
- [website_audit.py](scripts/website_audit.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/human-writing` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/lint_text.py /path/to/README.md --lang de
python3 scripts/project_audit.py audit /path/to/project
```
