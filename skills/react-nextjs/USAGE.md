# Using the `react-nextjs` skill in your agents

Project-type-agnostic React/Next.js development (baselines React 19.3.1,
Next.js 16.4.6, version-gated against the project lockfile): SPA/Vite,
App/Pages Router, Server vs Client Components, Suspense/streaming, Cache
Components and `use cache`, `proxy.ts` vs middleware, Server Functions,
Compiler memoization, hooks/TypeScript/state tooling, design systems,
WCAG 2.2 AA, CWV, SEO/metadata, testing stacks, deployment adapters,
upgrades. Next.js is never forced.

## Install (this skill only)

```bash
tools/install-skills.sh react-nextjs
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh react-nextjs`.

## Claude Code

Discovered from `~/.claude/skills/`; activates in any React/Next project:

```
Use the react-nextjs skill: this dashboard re-renders the whole table on
filter change. Profile, then fix with memoization boundaries — behavior
must not change, show the before/after flame evidence.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the react-nextjs skill: audit our App Router cache usage against
Cache Components, list violations with file:line, fix the P0s.
```

## oh-my-pi (omp)

omp routes from the skill list; name it to stay deterministic:

```
Use the react-nextjs skill: migrate this Pages Router blog to the App
Router with minimal diff, Server Components by default, tests green.
```

## Working style (all hosts)

- Mode gate → stack gate → version gate before any code; references load
  per task (22 references).
- Direct automation:
  `node skills/react-nextjs/scripts/audit_react_project.mjs <project>`,
  `bash skills/react-nextjs/scripts/check-versions.sh`.
- Unverified = marked, never invented; ship gate uses real test/build
  output.

## Examples that work verbatim

```
Use the react-nextjs skill: add i18n (next-intl) with hreflang and locale
routing to this SaaS marketing app; keep CWV green, report LCP before/after.
```

## Verify the skill itself

```bash
python3 skills/react-nextjs/tests/test_skill.py
```

Exit 0 on PASS (static structure + routing validation).
