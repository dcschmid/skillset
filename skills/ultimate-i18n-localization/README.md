# ultimate-i18n-localization

Check translation catalogs, placeholders, plurals, and locale routing in web and game projects. Use pseudolocalization to expose cramped layouts and untranslated text.

Profile: Private and Working. Preparation: Specify the project, reference language, target languages, and task: audit, additive fixes, translation drafts, or validation.

Expected result: A catalog-drift report, additive corrections, or translations clearly marked as drafts.

Requirements and limits: Never overwrite existing translations. New translations need human approval. CI blocks on confirmed BLOCKER/HIGH findings; heuristics remain advisory.

## ultimate-i18n-localization: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-i18n-localization
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-i18n-localization skill. Audit src/locales using German as the reference language. Report missing keys, placeholder mismatches, and plural issues without editing files.
```

**Codex:**

```text
Use the ultimate-i18n-localization skill. Add only missing catalog entries. Preserve existing translations and validate the catalogs again after changes.
```

**oh-my-pi:**

```text
Use the ultimate-i18n-localization skill. Plan English and Arabic support for the existing shop. Include locale routing, hreflang, and RTL. Mark new translations as drafts.
```

## ultimate-i18n-localization: Self-test

Run from the repository root:

```bash
node skills/ultimate-i18n-localization/tests/run.mjs
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [templates/](templates/): Templates for the target project.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [i18n](scripts/i18n)
- [i18n-audit](scripts/i18n-audit)
- [i18n-check](scripts/i18n-check)
- [i18n-extract](scripts/i18n-extract)
- [i18n-fix](scripts/i18n-fix)
- [i18n-pseudo](scripts/i18n-pseudo)
- [i18n-report](scripts/i18n-report)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/ultimate-i18n-localization` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/i18n audit --root /path/to/project
node scripts/i18n check --root /path/to/project
node scripts/i18n pseudo --text "Save {count} items" --expand 0.4
```
