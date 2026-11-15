# astro

Develop new and existing Astro sites, including content, routing, islands, server features, and deployment. Start by inspecting the project and installed version.

Profile: Private. Preparation: Provide the project, affected route, and task. Include measurements and target devices for performance work.

Expected result: An implementation that fits the existing Astro project, build results, and clearly identified runtime checks still pending.

Requirements and limits: Reference versions are starting points. Verify APIs against the project. Add integrations, UI frameworks, and hosting dependencies only when the task calls for them.

## astro: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh astro
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the astro skill. The home page ships too much JavaScript. Inspect islands and remove unnecessary hydration while preserving interactive behavior. Compare delivered JavaScript before and after.
```

**Codex:**

```text
Use the astro skill. Add an article page backed by the existing content collection. Reuse layouts and verify invalid slugs and the build.
```

**oh-my-pi:**

```text
Use the astro skill. Migrate content configuration for the installed Astro version. Preserve existing URLs and content.
```

## astro: Self-test

Run from the repository root:

```bash
python3 skills/astro/tests/test_skill.py
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

- [audit_astro_project.mjs](scripts/audit_astro_project.mjs)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/astro` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/audit_astro_project.mjs /path/to/astro-project
```

## Reference and example index

- [references/accessibility.md](references/accessibility.md)
- [references/architecture.md](references/architecture.md)
- [references/components.md](references/components.md)
- [references/content-cms.md](references/content-cms.md)
- [references/deployment.md](references/deployment.md)
- [references/fundamentals.md](references/fundamentals.md)
- [references/integrations.md](references/integrations.md)
- [references/internationalization.md](references/internationalization.md)
- [references/islands-interactivity.md](references/islands-interactivity.md)
- [references/performance.md](references/performance.md)
- [references/rendering-routing.md](references/rendering-routing.md)
- [references/security.md](references/security.md)
- [references/seo.md](references/seo.md)
- [references/testing.md](references/testing.md)
- [references/ui-ux-styling.md](references/ui-ux-styling.md)
- [references/upgrades.md](references/upgrades.md)
- [references/versions.md](references/versions.md)
- [workflows/bugfix.md](workflows/bugfix.md)
- [workflows/existing-project.md](workflows/existing-project.md)
- [workflows/feature-development.md](workflows/feature-development.md)
- [workflows/migration.md](workflows/migration.md)
- [workflows/new-project.md](workflows/new-project.md)
- [workflows/performance-audit.md](workflows/performance-audit.md)
- [workflows/production-release.md](workflows/production-release.md)
- [templates/component.md](templates/component.md)
- [templates/content-collection.md](templates/content-collection.md)
- [templates/layout.md](templates/layout.md)
- [templates/project-checklist.md](templates/project-checklist.md)
