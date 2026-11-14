# Using the `accessibility` skill in your agents

Accessibility engineering and auditing across every web surface (HTML/CSS/
JS/TS, React, Next.js, Astro, Vue/Svelte, SPAs/SSR/SSG, webshops,
dashboards, forms, design systems). WCAG 2.2 A/AA binding, AAA as a
separate quality tier. Owns the a11y layer across framework skills.
Automated PASS ≠ conformance: reports always separate the automated gate
from manual and screenreader evidence.

## Install (this skill only)

```bash
tools/install-skills.sh accessibility
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh accessibility`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on any a11y/WCAG task:

```
Use the accessibility skill: audit /checkout for WCAG 2.2 AA — automated
axe gate plus keyboard/focus evidence, and list what needs manual review.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the accessibility skill: build the modal component keyboard-first
(focus trap, ESC, restore focus) and prove it with the SR harness or
mark the environment gap honestly.
```

## oh-my-pi (omp)

omp routes it from the skill list; the SR harness gates its own environment
(Orca/Guidepup availability) rather than faking passes:

```
Use the accessibility skill: remediate the findings in reports/a11y.json,
prioritized, with a re-audit after each fix.
```

## Working style (all hosts)

- Mode gate first: Build (every UI change), Audit (WCAG-EM 2.0 slice), or
  Remediate; framework skills keep their own specifics.
- Direct automation:
  `node skills/accessibility/scripts/check-standards.mjs <url>` (axe +
  Playwright audit; JSON/HTML/JUnit/SARIF output, CI exit codes),
  `bash skills/accessibility/scripts/setup-check.sh` (environment gating).

## Examples that work verbatim

```
Use the accessibility skill: is this form WCAG 2.2 AA — labels, error
messages, focus order, contrast? Show the automated gate and the manual
checklist separately.
```

## Verify the skill itself

```bash
python3 skills/accessibility/tests/test_skill.py
```

Exit 0 on PASS (static structure + routing validation).
