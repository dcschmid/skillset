# Using the `playwright` skill in your agents

Terminal browser automation for UI exploration, snapshots and interaction
debugging. One session per project/purpose; fresh snapshots before element
references; never an installed-test replacement, and never an unrun check
reported as passed.

## Install (this skill only)

```bash
tools/install-skills.sh playwright
```

Symlinks into the shared roots (`~/.claude/skills`, `~/.agents/skills`;
`tools/profile-map.tsv` routes unlisted skills as `both`); remove with
`tools/uninstall-skills.sh playwright`. Needs a Playwright CLI
(`playwright-cli`, `$PLAYWRIGHT_CLI`, or a repo launcher) — the skill never
installs one.

## Claude Code

Discovered from `~/.claude/skills/`; activates on UI inspection and
reproduction requests:

```
Use the playwright skill: open the staging checkout page, snapshot it, and
reproduce the double-submit on slow networks — screenshots into
output/playwright/.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the playwright skill: walk the signup flow at localhost:4321 and report
console errors; Firefox default unless the repo pins another browser.
```

## oh-my-pi (omp)

Routes from the skill list; naming keeps activation deterministic:

```
Use the playwright skill: reproduce this layout bug at 375px and attach the
trace.
```

## Verify

```bash
python3 skills/playwright/tests/test_skill.py
```
