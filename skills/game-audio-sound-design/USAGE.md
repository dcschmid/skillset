# Using the `game-audio-sound-design` skill in your agents

Game audio production and QA on top of the **game-audio-forge** backend
(mandatory prerequisite, separate repo): SFX/music generation via `gaf`,
adaptive/interactive music, spatial audio, mixing gates, asset+engine
audits with safe repairs, performance budgets, license-gated release
checks, Defold 1.14.1 + Godot 4.7.2 adapters. Generation never happens
here; measurements never replace listening (`AUDIO_REVIEW_REQUIRED`).

**Before first use:** game-audio-forge must be installed and configured —
see the skill README "Prerequisites – Required Installation". The skill
reports `NOT_READY` honestly; it never installs the backend or fakes it.

## Install (this skill only)

```bash
tools/install-skills.sh game-audio-sound-design    # repo root
```

Symlinks into `~/.claude/skills` + `~/.agents/skills`, tracked in
`.installed-manifest`; remove with `tools/uninstall-skills.sh
game-audio-sound-design`.

## Claude Code

Discovers via `~/.claude/skills/`. Frontmatter triggers on audio/music/SFX/
mix/audit requests. Force activation:

```
Use the game-audio-sound-design skill to doctor-check this project, then
audit its audio (analyze mode, findings by severity, nothing written).
```

## Codex

Reference explicitly; carry the mode in the request:

```
Use game-audio-sound-design: fix mode on assets/audio, safe ops into a new
directory, re-measure before/after, list every NOT_TESTED.
```

## oh-my-pi

Routes from the skill list; run `scripts/audio_doctor.py --project DIR` as
the first step of any audio task (READY gate). Backend: `gaf_adapter.py` or
the backend's own `gaf` CLI directly.

## Verify

```bash
python3 skills/game-audio-sound-design/tests/test_skill.py   # no GPU needed
```

Backend generation gate (GPU): `~/dev/github/game-audio-forge/scripts/gaf-test.sh`.
