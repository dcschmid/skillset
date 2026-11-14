# Using the `astro` skill in your agents

Project-type-agnostic Astro development (baseline Astro 7.4.x, version-gated
against npm at task time): SSG/on-demand/mixed rendering, route caching,
islands and hydration directives, Actions, sessions, middleware, Content
Layer, MDX, headless CMS intake, `astro:assets`, Fonts API, SEO, Core Web
Vitals, WCAG 2.2 AA, CSP/adapters/upgrades. Astro is never forced onto
stacks that fit it better.

## Install (this skill only)

```bash
tools/install-skills.sh astro
```

Symlinks into both host roots; remove with `tools/uninstall-skills.sh astro`.

## Claude Code

Discovered from `~/.claude/skills/`; activates inside any Astro project:

```
Use the astro skill: this marketing site ships 400 KB of JS on the
landing page — find the islands that should be static and cut hydration,
keep Actions working.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the astro skill: migrate our Content Collections config to the Content
Layer without breaking existing routes; show the diff and the verification
command.
```

## oh-my-pi (omp)

omp routes it from the skill list; explicit naming is stable:

```
Use the astro skill: add session-based auth + middleware redirect for the
dashboard pages, SSR only where needed, static elsewhere.
```

## Working style (all hosts)

- Detection first: the skill reads `astro.config.*`, `src/pages/`, lockfile
  and loads only matching references (17 references).
- Direct automation:
  `node skills/astro/scripts/audit_astro_project.mjs <project>` — project
  shape, versions, warnings as evidence.
- Claims are version-gated; unverified items are marked, never invented.

## Examples that work verbatim

```
Use the astro skill: wire a docs site with MDX, sitemap, RSS, and OG images
via astro:assets — static build, zero client JS outside the search island.
```

## Verify the skill itself

```bash
python3 skills/astro/tests/test_skill.py
```

Exit 0 on PASS (static structure + routing validation).
