# astro — universal Astro web-development skill

Agent skill (open `SKILL.md` format: Claude Code, Codex, any SKILL.md runner)
for building ANY Astro web project — portfolio, blog, docs, marketing,
product, game-site, i18n, SSR portal — with coding agents. Baseline:
**Astro 7.4.12 stable** (npm `latest`, probe 2026-11-14; 7.0 shipped
2026-06-22), version-gated and re-probed per task, never a frozen number.

## What this is / is not

- IS: router (`SKILL.md`) + 16 references + 7 workflows + 4 templates +
  working read-only tooling; rendering/island/security/version decisions with
  explicit criteria; measurement-backed perf/a11y/SEO claims.
- IS NOT: a portfolio/blog/one-framework skill. React/Vue/etc., CMSes, hosts,
  and integrations are opt-in with reasons; Astro itself is not forced onto
  stacks that fit another framework better.

## Layout

| Path | Content | Loaded |
|---|---|---|
| `SKILL.md` | triggers, workflow spine, routing tables, truth ladder | on trigger |
| `references/` | 16 deep docs (versions, architecture, rendering, content, islands, styling, seo, perf, a11y, security, testing, i18n, integrations, deployment, upgrades, fundamentals) | per routing table |
| `workflows/` | 7 playbooks (new → existing → feature → bugfix → audit → migration → release) | per task type |
| `templates/` | component, layout, collection, ship checklist | per delivery |
| `scripts/` | `audit_astro_project.mjs` (read-only auditor, node ≥ 18.17) | at audit step |
| `tests/` | structure + routing validator (python3, stdlib) | CI / before commit |

## Use

Install via repo installer (`tools/install-skills.sh` → symlinks into
`~/.claude/skills` + `~/.agents/skills`). Any Astro task in an agent session
triggers it; references load on demand.

```bash
python3 tests/test_skill.py                       # skill self-check (STATIC)
node scripts/audit_astro_project.mjs <project_dir>  # read-only project census
```
