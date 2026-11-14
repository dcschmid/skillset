# human-writing

Human writing + anti-AI-slop skill for generating, rewriting, auditing, and
calibrating German and English prose — articles, docs, marketing, UX copy,
creative writing, and whole websites. Ships three stdlib Python tools, fifteen
progressive-disclosure references, voice/website templates, and reproducible
offline test suites.

Detection and rules only: tools report, the agent rewrites (and only after
approval). Reports never assert authorship and never print a "human %".

## Quickstart

```bash
# lint prose offline (0 clean / 1 findings / 2 error; --fail-on high|med|all)
python3 scripts/lint_text.py README.md --lang de
cat draft.md | python3 scripts/lint_text.py - --format json --fail-on med

# audit one page, a sitemap, or a bounded crawl (public URLs; SSRF-guarded)
python3 scripts/website_audit.py https://example.com/about
python3 scripts/website_audit.py https://example.com --crawl --max-pages 50
python3 scripts/website_audit.py https://example.com/sitemap.xml --sitemap --format json

# local project: audit → plan → dry-run → write → validate (never auto-writes)
python3 scripts/project_audit.py audit .
python3 scripts/project_audit.py plan . --proposals proposals.json --out patch.json
python3 scripts/project_audit.py apply . --patch patch.json          # dry
python3 scripts/project_audit.py apply . --patch patch.json --write
python3 scripts/project_audit.py validate . --build "npm run build" --test "npm test"

# tests (offline, fixture transport; run from skill dir)
python3 tests/test_lint_text.py && python3 tests/test_website_audit.py && python3 tests/test_project_audit.py
```

## Modes (selected in SKILL.md)

A Generate · B Rewrite · C Audit · D Website Audit · E Website Rewrite ·
F Voice Calibration. Genre rules (`references/genre-guides.md`) separate docs
from marketing from stories; creative writing has its own law
(`references/creative-writing.md`). DE and EN rule sets are independent
(`references/style-de.md`, `style-en.md`) — no translated boilerplate.

## Loading model (don't read everything per edit)

Task → `SKILL.md` (always) → exactly the reference files the mode needs →
script for machine checks. Voice profiles and site voices live in `assets/`.

## Layout

```
SKILL.md            mode table, binding rules, tool calls, reading list
references/         patterns-core, style-de/en, genre-guides, creative-writing,
                    fidelity-rules, quality-gates, voice-calibration,
                    website-audit/-rewrite/-voice, seo-content,
                    accessibility-content, agent-integration, sources
scripts/            hw_text|hw_rules|hw_report|hw_http|hw_extract (libs),
                    lint_text|website_audit|project_audit (CLIs)
assets/             voice-profile + website-voice templates, audit-config
examples/           DE/EN before-after, technical, creative, audit/rewrite reports
tests/              three offline runners, fixtures/ (fixture site + content)
```

## Usage recipes (say these to your agent)

- "Schreibe einen natürlichen deutschen Blogartikel über X." (Mode A)
- "Humanize this text but keep my voice." → Mode B + fidelity rules
- "Überarbeite die README ohne technische Fakten zu ändern." → B, protected spans
- "Prüfe https://example.com auf KI-Floskeln." → D, `website_audit.py`
- "Analysiere alle Unterseiten." → D `--crawl`; findings then proposals
- "Ändere nichts bevor ich freigeben habe." → E keep dry-run default
- "Lerne meinen Stil aus diesen drei Texten." → F + voice-profile template
- "Nur Audit, keine Umschreibung." → C, C is read-only by contract

## What the tools do / don't do

`lint_text.py` and `website_audit.py` detect + report; the productive rewrite
is authored by the calling agent. URL-only audits see server-rendered HTML —
client-hydrated text can be missed and the report says so. Protected regions
(code, frontmatter, ARIA, hrefs, slugs, canonicals, structured data, ICU/
template vars) are never silently edited; unresolvable edits become manual
patches. Production CMS/deploy APIs are untouched without explicit approval.

## Integration

Installed by this repo's `tools/install-skills.sh` symlink convention into
`~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex); edits here
propagate live. Per-agent activation and honesty notes:
`references/agent-integration.md`. Collaboration contract with astro /
react-nextjs / accessibility / game-dev skills: same file.

## Honest limits

Style scoring counts rule findings — it is not quality, not authorship, not
"human percentage". Fixtures cover Astro/React/MD/markdown/JSON content shapes,
not every framework edge; unresolvable extraction is reported, not faked.
Repeated application converges (max 2 passes); a good sentence stays.
