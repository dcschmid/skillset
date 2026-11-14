# Using the `seo-performance` skill in your agents

Technical SEO and web performance for any framework (Astro, Next.js
app/pages, React/Vite/CSR, static, CMS via URL): crawling, indexability,
canonicals, sitemaps, robots, hreflang; Core Web Vitals
(LCP/INP/CLS/TTFB/TBT) with lab-vs-field discipline; delivered-HTML vs
JS-rendered DOM checks; schema.org/JSON-LD validation; AI-search readiness;
approval-gated auto-fixes; CI gates; regression monitoring. Works offline,
no API keys, never invents scores.

## Install (this skill only)

```bash
tools/install-skills.sh seo-performance
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh seo-performance`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on SEO/speed asks:

```
Use the seo-performance skill: audit https://example.com — indexation,
canonicals, schema, LCP/INP — then propose the fix list with approval
gates before any change.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the seo-performance skill: why is LCP bad on the product page? Lab +
field comparison, delivered-HTML check, minimal fixes only.
```

## oh-my-pi (omp)

omp routes from the skill list; the auditor is zero-dependency Node:

```
Use the seo-performance skill: wire the CI gate + monitor for release
candiates, fail on confirmed regressions against the stored baseline.
```

## Working style (all hosts)

- Entry picks one workflow and loads ONE reference; audit levels
  auto-escalate, never silently.
- Direct automation:
  `node skills/seo-performance/scripts/seo.mjs audit <url>` — plus
  `fix|performance|technical|content|schema|monitor|ci|compare|serve`;
  optional Lighthouse/Unlighthouse/LHCI/Playwright when present.

## Examples that work verbatim

```
Use the seo-performance skill: hreflang + canonical audit for the de/en
locale pair per Google rules, then validate the JSON-LD blocks.
```

## Verify the skill itself

```bash
node skills/seo-performance/tests/run.mjs
```

Exit 0 on PASS (zero-dep runner, unit + integration fixtures).
