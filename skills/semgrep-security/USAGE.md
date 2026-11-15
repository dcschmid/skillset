# Using the `semgrep-security` skill in your agents

Semgrep as the deterministic security validation lane after security-relevant
changes. Findings are evidence to investigate, never automatic truth;
repository Semgrep configuration outranks package defaults.

## Install (this skill only)

```bash
tools/install-skills.sh semgrep-security
```

Symlinks into the shared roots (`~/.claude/skills`, `~/.agents/skills`;
`tools/profile-map.tsv` routes unlisted skills as `both`); remove with
`tools/uninstall-skills.sh semgrep-security`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on security validation around
auth, endpoints, file handling or dependency changes:

```
Use the semgrep-security skill: run the security lane on this diff and
triage findings — valid, in-scope fixes first, false positives documented.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the semgrep-security skill: gate this API change with the repo's
semgrep config before we call it done.
```

## oh-my-pi (omp)

Routes from the skill list; naming keeps activation deterministic:

```
Use the semgrep-security skill: is the auth refactor clean? Deterministic
lane only, no vibes.
```

## Verify

```bash
python3 skills/semgrep-security/tests/test_skill.py
```
