# react-nextjs

Work on React SPAs and Next.js App or Pages Router projects, including components, data flow, caching, forms, and server boundaries.

Profile: Working. Preparation: Provide the project, router, affected component, and observed behavior. Read installed versions from manifests and lockfiles.

Expected result: A change within the existing stack, checked with relevant component, integration, or build commands.

Requirements and limits: This skill belongs to the Working profile. Private frontend work remains Astro-first under repository policy. Adapt examples to the actual React and Next.js versions.

## react-nextjs: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh react-nextjs
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude working
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the react-nextjs skill. The whole table rerenders when a filter changes. Measure the cause and improve the affected data flow without changing behavior.
```

**Codex:**

```text
Use the react-nextjs skill. Audit cache usage in this Next.js App Router project. Identify concrete locations and fix confirmed defects with appropriate tests.
```

**oh-my-pi:**

```text
Use the react-nextjs skill. Fix the form that hides server errors. Preserve existing validation and test success, invalid input, and server failure.
```

## react-nextjs: Self-test

Run from the repository root:

```bash
python3 skills/react-nextjs/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [audit_react_project.mjs](scripts/audit_react_project.mjs)
- [check-versions.sh](scripts/check-versions.sh)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/react-nextjs` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
node scripts/audit_react_project.mjs /path/to/react-project
```

## Reference and example index

- [references/accessibility.md](references/accessibility.md)
- [references/agent-workflows.md](references/agent-workflows.md)
- [references/architecture.md](references/architecture.md)
- [references/deployment.md](references/deployment.md)
- [references/fullstack-integration.md](references/fullstack-integration.md)
- [references/migrations.md](references/migrations.md)
- [references/nextjs-app-router.md](references/nextjs-app-router.md)
- [references/nextjs-data-caching.md](references/nextjs-data-caching.md)
- [references/nextjs-rendering.md](references/nextjs-rendering.md)
- [references/nextjs-server-actions.md](references/nextjs-server-actions.md)
- [references/performance.md](references/performance.md)
- [references/react-compiler.md](references/react-compiler.md)
- [references/react-core.md](references/react-core.md)
- [references/react-modern-apis.md](references/react-modern-apis.md)
- [references/security.md](references/security.md)
- [references/seo-i18n.md](references/seo-i18n.md)
- [references/state-management.md](references/state-management.md)
- [references/styling-design-systems.md](references/styling-design-systems.md)
- [references/testing.md](references/testing.md)
- [references/tooling.md](references/tooling.md)
- [references/typescript.md](references/typescript.md)
- [references/version-policy.md](references/version-policy.md)
- [examples/README.md](examples/README.md)
- [examples/forms-validation/rename-form.tsx](examples/forms-validation/rename-form.tsx)
- [examples/nextjs-app-router/article-page.tsx](examples/nextjs-app-router/article-page.tsx)
- [examples/react-vite/TodoList.tsx](examples/react-vite/TodoList.tsx)
- [examples/reusable-components/Button.tsx](examples/reusable-components/Button.tsx)
- [examples/testing-patterns/examples.ts](examples/testing-patterns/examples.ts)
