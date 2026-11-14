---
name: human-writing
description: >
    Human writing and anti-AI-slop skill for generating, rewriting, auditing
    and calibrating prose in German and English: blog posts, docs, READMEs,
    marketing copy, UX texts, creative writing, dialogue, emails, reports.
    Use when asked to write/humanize/de-slop/audit text, audit or rewrite
    website content (single URL, sitemap, crawl, local Astro/React/Markdown
    project), or preserve a personal voice. Ships offline Python linter
    (scripts/lint_text.py), website auditor with SSRF-guarded crawler
    (scripts/website_audit.py), and safe project rewrite tool with dry-run
    default (scripts/project_audit.py). Detection and rules only: reports
    never assert authorship; rewriting is authored by the agent, applied
    only after approval.
license: MIT
metadata:
    author: danielschmid
    version: "1.0.0"
compatibility: Python 3.10+, stdlib only. Network only for public URL audits;
    all text analysis works offline. Fixtures mode for offline crawl tests.
---

# Human Writing & Anti-AI-Slop

Improve actual writing quality. Never disguise text for detectors, never
assert or deny who wrote something, never rewrite what already works.

## When this skill activates

Activate for any prose task: write/rewrite/audit human-facing text (DE or EN)
— articles, docs, READMEs, changelogs, emails, marketing, UX strings, stories,
dialogue — or website content audit/rewrite via the scripts below. Do NOT
activate for pure code edits, config, or commit messages with no prose intent.

## Mode selection (first decision, always)

| Task | Mode | Details |
|---|---|---|
| Write new text | A Generate | section below + `references/style-{de,en}.md` per language |
| Improve existing text | B Rewrite | `references/fidelity-rules.md` first |
| Report problems, no edit | C Audit | `references/patterns-core.md` + linter |
| Audit a live site | D Website Audit | `scripts/website_audit.py`, `references/website-audit.md` |
| Rewrite site content | E Website Rewrite | D then `references/website-rewrite.md` |
| Learn a user's voice | F Voice Calibration | `references/voice-calibration.md` |

Before any write: internally settle genre, audience, language, intent. Load
only the references the task needs (progressive disclosure; do not read all
of `references/` per small edit). Never rewrite unasked; never open with a
question that a default would answer.

## Binding rules (all modes)

1. Meaning first: a rewrite may not change, invent, or drop facts. Missing
   facts get reported as missing — never fabricated.
2. Density decides severity: one flagged phrase is noise; clusters are worth
   fixing. Isolated hits are reported as informational, not errors.
3. What stays untouched: quotes, code, numbers, links, protected technical
   spans, deliberate literary/rhetorical devices, domain terminology.
4. No authorship verdicts, no "X% human" scores. Scores count findings only.
5. Linter output serves the text; text never serves the linter. If a rule
   fires on a good sentence, the sentence wins.
6. Priority: facts > intent > user instructions > voice profile > genre rules
   > style rules > linter.
7. Rewrite loops terminate: max 2 passes; then keep the better version, don't
   grind linter numbers.
8. DE and EN have separate rule sets; DE is not translated EN rules. Default
   de-DE; honor configured AT/CH variants, US/EN variants.
9. Site work: dry-run first, apply only approved edits, protected regions
   (code, frontmatter, ARIA, URLs, slugs, canonicals) never edited silently.

## Generate discipline (Mode A)

Draft with the reader and subject fixed: specific claims over important-
sounding ones, varied sentence lengths, direct verbs, genre-appropriate
register. No staged openers, no booster adjectives without evidence, no
conclusion that only echoes. Good text is finished in pass one — the rewrite
modes are for existing text, not a license to churn fresh drafts.

## Tools (run; don't reimplement)

```bash
python3 scripts/lint_text.py FILE... --lang de|en|auto   # offline linter; JSON/text; CI exit codes
python3 scripts/website_audit.py URL [--crawl|--sitemap --max-pages N]   # public site audit
python3 scripts/project_audit.py audit|plan|apply|validate DIR           # local project; dry-run default
```

`website_audit.py --fixtures DIR` runs offline against local fixtures (used
by tests). Rewrites in project mode arrive as agent-authored proposals in a
patch JSON; `apply` validates protected spans and applies — dry-run unless
`--write`. See `references/agent-integration.md` for Claude Code / Codex
activation, limitations and honest capability notes (Python never rewrites
prose productively).

## Reading list (load per task, not per session)

- `references/patterns-core.md` — 15 pattern categories + what stays allowed
- `references/style-de.md` / `style-en.md` — per-language rule sets
- `references/genre-guides.md` — docs, business, editorial, marketing, UX, creative
- `references/creative-writing.md` — dialogue, POV, pacing (separate law)
- `references/fidelity-rules.md` — what a rewrite may not touch
- `references/quality-gates.md` — the 11 gates, pass criteria
- `references/voice-calibration.md` + `assets/voice-profile.template.md`
- `references/website-audit.md` / `website-rewrite.md` / `website-voice.md`
- `references/seo-content.md` · `references/accessibility-content.md`
- `references/agent-integration.md` — per-agent activation + integration table
- `references/sources.md` — OSS lineage, licenses, attribution
