# Using the `human-writing` skill in your agents

Human prose in German and English: generate, rewrite, audit, and calibrate
blog posts, docs, READMEs, marketing copy, UX texts, creative writing,
dialogue, emails, reports. Anti-AI-slop rules and personal-voice
preservation. Detection and rules only — reports never assert authorship;
rewriting is authored by the agent and applied only after approval.
Python 3.10+, stdlib only, works offline (network only for public URL
audits).

## Install (this skill only)

```bash
tools/install-skills.sh human-writing
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh human-writing`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on write/humanize/de-slop/
audit-text asks:

```
Use the human-writing skill: audit the prose on https://example.com/blog —
slop patterns, rhythm, voice — report only, no edits.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the human-writing skill: rewrite the onboarding emails in this repo
to my voice (dry first, apply after I approve the diff).
```

## oh-my-pi (omp)

omp routes from the skill list; project rewrite defaults to dry-run:

```
Use the human-writing skill: de-slop docs/README.md EN + DE, keep
terminology, show the lint verdict before and after.
```

## Working style (all hosts)

- Mode selection first (generate/rewrite/audit/calibrate); approval gate
  before any file changes; authorship claims stay out of reports.
- Direct automation:
  `python3 skills/human-writing/scripts/lint_text.py <file>` (offline
  linter), `website_audit.py` (SSRF-guarded crawler, fixtures mode for
  offline tests), `project_audit.py` (safe rewrite, dry-run default;
  `hw_*.py` libs support them).

## Examples that work verbatim

```
Use the human-writing skill: calibrate these three versions of the changelog
entry against my previous posts — which one is most me? Evidence, not vibes.
```

## Verify the skill itself

```bash
python3 skills/human-writing/tests/test_lint_text.py
python3 skills/human-writing/tests/test_project_audit.py
python3 skills/human-writing/tests/test_website_audit.py
```

Exit 0 on PASS (offline, fixture-based).
