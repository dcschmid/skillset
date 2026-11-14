# Using the `design-authenticity` skill in your agents

Design authenticity and anti-AI-slop discipline for any UI surface
(websites, SaaS, dashboards, docs, PWAs, game menus/HUDs; audits of
existing React/Next/Astro projects). Modes: CREATE, REVIEW, REFACTOR,
GUARD. Product-context-first identity, a Design Identity Engine,
Anti-AI-Slop detection (default gradients, hero+card templates, glass/glow
blobs, decoration without purpose), a 100-pt visual gate (target ≥ 90),
screenshot review when a browser exists, WCAG AA as hard floor. Zero
external services. Framework skills own architecture; accessibility owns
a11y; this skill owns originality, coherence, product-fit.

## Install (this skill only)

```bash
tools/install-skills.sh design-authenticity
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh design-authenticity`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on design/identity/review
work:

```
Use the design-authenticity skill: REVIEW the landing page — score it on
the 100-pt gate, flag every generic pattern with file:line, propose
product-fit replacements.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the design-authenticity skill: CREATE the visual identity for a docs
product — typography, color, layout rationale — brand-preserving, no
template patterns.
```

## oh-my-pi (omp)

omp routes from the skill list; screenshots only when a browser exists,
otherwise the review is flagged, not scored:

```
Use the design-authenticity skill: GUARD — check my next component PR
against the identity rules before I merge.
```

## Working style (all hosts)

- Existing projects: zero-code audits, prioritized audit-and-fix,
  brand-preserving modernization, before/after regression review.
- Direct automation:
  `node skills/design-authenticity/scripts/validate_config.mjs <config>`
  (identity-config schema), `bash skills/design-authenticity/scripts/
  screenshot_audit.sh <url>` when a browser is available.

## Examples that work verbatim

```
Use the design-authenticity skill: REFACTOR the settings page toward our
identity without touching behavior — keep WCAG AA, show before/after.
```

## Verify the skill itself

```bash
python3 skills/design-authenticity/tests/test_skill.py
```

Exit 0 on PASS (static structure + routing validation).
