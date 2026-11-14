# design-authenticity — anti-AI-slop design discipline

Human-facing guide. The agent entry point is [`SKILL.md`](SKILL.md); usage
prompts for hosts live in [`USAGE.md`](USAGE.md).

Universal design authenticity for any UI surface (websites, SaaS,
dashboards, docs, PWAs, game menus/HUDs; audits of existing
React/Next/Astro projects). Modes CREATE · REVIEW · REFACTOR · GUARD.
Product-context-first identity, a Design Identity Engine, Anti-AI-Slop
detection (default gradients, hero+card templates, glass/glow blobs,
decoration without purpose), a 100-pt visual gate (target ≥ 90), screenshot
review when a browser exists, WCAG AA as hard floor. Zero external services.

## Layout

```
SKILL.md                     mode gate + engines (identity, anti-slop) + gates
references/                  12 docs: identity, slop catalog, rubric, per-mode depth
workflows/                   ordered procedures per mode
scripts/                     validate_config.mjs · screenshot_audit.sh (browser-gated)
examples/                    identity configs + review samples
tests/test_skill.py          static validation, exit 0 = PASS
USAGE.md                     host invocation guide (mirror of repo README section)
```

## Use (Claude Code / Codex / oh-my-pi)

Install: `tools/install-skills.sh design-authenticity` — symlinks into
`~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex); oh-my-pi
loads the same roots. Then invoke by name:

```text
Use the design-authenticity skill: REVIEW the landing page — score on the
100-pt gate, flag every generic pattern with file:line, propose product-fit
replacements.
Use the design-authenticity skill: CREATE the visual identity for a docs
product — typography, color, layout rationale — brand-preserving, no templates.
Use the design-authenticity skill: GUARD — check my next component PR against
the identity rules before I merge.
```

Existing projects get zero-code audits, prioritized audit-and-fix, and
brand-preserving modernization with before/after regression review.

## Tools

```bash
node scripts/validate_config.mjs <identity-config>   # schema + completeness
bash scripts/screenshot_audit.sh <url> <out-dir>     # browser-gated shots;
                                                     # no browser → BROWSER_UNAVAILABLE, exit 3
```

Scores only ship with visual comparison; otherwise `VISUAL_REVIEW_REQUIRED`.

## Validate

```bash
python3 tests/test_skill.py
```
