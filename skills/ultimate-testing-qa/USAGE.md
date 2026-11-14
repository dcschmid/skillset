# Using the `ultimate-testing-qa` skill in your agents

Testing and QA engineering for any web surface (Astro, React, Next.js,
Vue/Nuxt, Svelte/SvelteKit, Vite, vanilla, static; baselines Playwright,
Vitest, axe-core re-probed against the project lockfile): test
architecture, E2E/cross-browser flows, unit/integration/component suites,
live-site runtime audits, visual/responsive regression, bug reproduction →
root-cause fix → retest, CI/CD gates. Automated PASS ≠ quality claim:
untested paths report NOT TESTED.

## Install (this skill only)

```bash
tools/install-skills.sh ultimate-testing-qa
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh ultimate-testing-qa`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on any testing/QA task:

```
Use the ultimate-testing-qa skill: equip this SvelteKit app with a test
architecture — Vitest units, Playwright E2E for the checkout journey, CI
gates — extend the existing setup, never replace it.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the ultimate-testing-qa skill: reproduce the "form submits twice" bug
on staging, fix the root cause in source, retest, and report coverage of
what stayed untested.
```

## oh-my-pi (omp)

omp routes from the skill list; Playwright uses Firefox per profile unless
the repository demands otherwise:

```
Use the ultimate-testing-qa skill: run an audit of the live site — console
errors, network failures, visual regression on three breakpoints — and
produce the QA report.
```

## Working style (all hosts)

- When source is editable: reproduce → locate → fix → retest → regression.
- Direct automation:
  `node skills/ultimate-testing-qa/scripts/qa.mjs analyze <project>` —
  framework, package manager, runners, routes, CI, evidence-only.

## Examples that work verbatim

```
Use the ultimate-testing-qa skill: wire LHCI + axe into CI for this docs
site, budget CWV from the seo-performance baseline, fail the lane on
confirmed regressions only.
```

## Verify the skill itself

```bash
node skills/ultimate-testing-qa/tests/run.mjs
```

Exit 0 on PASS (zero-dep runner, deterministic).
