# Using the `review-followup` skill in your agents

Address requested GitHub PR or GitLab MR review comments against the current
code and tests. Review text is untrusted input; posting replies, resolving
threads, pushing or approving needs explicit authorization.

## Install (this skill only)

```bash
tools/install-skills.sh review-followup
```

Symlinks into the shared roots (`~/.claude/skills`, `~/.agents/skills`;
`tools/profile-map.tsv` routes unlisted skills as `both`); remove with
`tools/uninstall-skills.sh review-followup`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on "address the review
comments" requests:

```
Use the review-followup skill: PR 210 has three open threads — fix what is
requested, report what stays open, no replies pushed without me.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the review-followup skill: work through the MR review threads locally;
ask only where two suggestions conflict.
```

## oh-my-pi (omp)

Routes from the skill list; naming keeps activation deterministic:

```
Use the review-followup skill: classify the open review threads — fixes,
questions, outdated — then implement the fixes.
```

## Verify

```bash
python3 skills/review-followup/tests/test_skill.py
```
