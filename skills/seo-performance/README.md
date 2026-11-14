# seo-performance

Universal SEO & web-performance skill for Claude Code / Codex: audits any
website (framework or CMS, new or existing), fixes safe issues at the root
cause, proves results with before/after snapshots, and gates regressions in
CI. The auditor itself is zero-dependency Node (>=18.17) — runs offline,
without API keys, and never invents numbers.

Baseline verified 2026-11-14 · lighthouse 13.6.0 · @lhci/cli 0.16.1 ·
unlighthouse 0.19.1 · playwright 1.65.1 · node 22 tested (>=18.17 required).

## Quickstart
```bash
node scripts/seo.mjs audit .                     # audit current project
node scripts/seo.mjs audit https://example.com   # external, read-only
node scripts/seo.mjs audit . --source-dist dist  # audit built output
node scripts/seo.mjs fix . --apply               # safe fixes (git-reviewable)
node scripts/seo.mjs performance .               # budgets + CWV discipline
node scripts/seo.mjs schema <target>             # JSON-LD tiers
node scripts/seo.mjs ci . --init                 # LHCI + GH Action scaffold
node scripts/seo.mjs tools                       # detected tool versions
node tests/run.mjs                               # 24 tests, deterministic
```

## How agents use it
- **Claude Code**: skill lives in `~/.claude/skills/seo-performance`
  (symlink). Invoke `/seo-performance audit` or ask "audit my SEO" — the
  description triggers on SEO/perf intents and never on incidental UI edits.
- **Codex**: skill in `~/.agents/skills/seo-performance` (symlink). Ask
  "run the seo-performance skill: audit this project" — subcommands are
  arguments to the same workflow, no extra slash-commands needed.
- Both: read `SKILL.md` (router) → `references/*.md` (depth on demand) →
  execute `scripts/seo.mjs` (the tool). Progressive disclosure keeps
  context cheap.

## Install / update
`bash setup.sh` — idempotent symlinks into `~/.claude/skills` and
`~/.agents/skills`, never overwriting foreign dirs. Global = symlink;
per-project = symlink into `<project>/.claude/skills/`. After central edits
all consumers update at once (one source: this directory).

## Layout
```
SKILL.md            router: workflows, gates, commands
references/         12 docs: google rules, technical, CWV, perf, schema,
                    content, ai-search, astro, nextjs, react, methodology,
                    remediation
scripts/seo.mjs     CLI: audit|fix|performance|technical|content|schema|
                    monitor|ci|compare|serve|tools
scripts/lib/        html, crawler, detectors, schema, perf, project, report,
                    config, fix  (stdlib only)
config/             default | strict | performance-budgets (project-tunable)
templates/          audit-report, remediation-plan, lighthouse-ci, GH action
tests/              fixtures + 24 unit/integration tests (run.mjs)
examples/           minimal SEO component snippets per framework
```

## What works today vs optional
Working offline: crawl, robots/sitemap, canonical/collision, hreflang
group+reciprocity, metadata/headings, schema 3-tier + content cross-check,
budgets, snapshots, compare(noise/regression), safe fixes (static
meta/lang/alt, robots.txt), CI gate, serve, monitor scaffold.
Optional/enhancing (graceful UNAVAILABLE without them): Lighthouse/Unlighthouse/
LHCI/Playwright (probe via `tools`; used when installed), PSI/CrUX/GSC
(network + user access), rich-result award + Google-index status (never
claimable offline — always reported as UNAVAILABLE).
Integration seam: `human-writing`/`accessibility`/`astro`/`react-nextjs`
skills if installed; otherwise self-contained.

## Verify any change
`node tests/run.mjs` (expect `VERDICT PASS pass=24 fail=0`).
