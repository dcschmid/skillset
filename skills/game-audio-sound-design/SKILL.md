---
name: game-audio-sound-design
description: >
  Universal, genre-, art-style- and engine-agnostic game audio production:
  sound effects, music, adaptive/interactive music, spatial audio, mixing,
  audio audits, safe repairs, performance budgets, and release validation
  for any game project (Defold and Godot adapters shipped; Unity/Unreal
  adapter-ready). REQUIRES the game-audio-forge backend (gaf CLI,
  ~/dev/github/game-audio-forge) for generation — analysis, audit, and
  repair run on ffmpeg alone. Use for: game audio/music/sound requests in any
  project, audio asset audits ("find broken sounds", "audio QA"), SFX/music
  generation via gaf, mixing/mastering checks, audio performance budgets,
  engine audio integration, audio accessibility (separate volume sliders,
  mono, captions), audio licensing review (ACE-Step MIT, Stable Audio
  Community <$1M). Doctor: audio_doctor.py → READY/PARTIALLY_READY/NOT_READY.
---

# Game Audio & Sound Design (universal)

Backend truth (verified 2026-11-14): game-audio-forge at
`~/dev/github/game-audio-forge` (config `config/gaf.json`, music = ACE-Step
1.5 SFT DiT 48 kHz stereo, SFX = sa3.cpp Stable Audio 3 44.1 kHz stereo,
legacy dasheng 16 kHz mono internal-only). Host: ffmpeg/ffprobe on PATH,
Python 3.14 (no audioop — all metering is ffmpeg-based). Engine baselines:
Defold 1.14.1, Godot 4.7.2. Nothing here re-implements generation.

## Prime Directive

**game-audio-forge first, and never fake readiness.** Resolve it
(`--forge-root` > `$GAME_AUDIO_FORGE_ROOT` > `~/dev/github/game-audio-forge`).
Missing → tell the user to clone+setup it (link in README); diagnosis works
without it, generation is honestly reported unavailable. Project files are
never overwritten: outputs are new files (unique suffixes), originals are
sacred, every change gets a re-measure. Untested ≠ passed: `NOT_TESTED`
stays `NOT_TESTED`; creative quality → `AUDIO_REVIEW_REQUIRED` always.

## Workflow (every task)

1. **Doctor** — `python3 scripts/audio_doctor.py --project PROJECT` →
   READY | PARTIALLY_READY | NOT_READY + fixes. Generation only when READY
   for the needed part; analysis/audit/fix work with ffmpeg alone.
2. **Detect** — engine (defold/game.project, godot/project.godot, generic),
   genre/art-style (never assumed), profile (ui-sfx | gameplay-sfx |
   ambience | music | voice | cinematics). One line: `Engine · Genre ·
   Profile · Forge root`.
3. **Plan** — analyze → generate/process → QA → integrate → validate. Read
   the matching `references/*.md` only for the step that needs it (router
   table below). Reuse existing project audio + architecture; never build a
   parallel system beside it.
4. **Execute** — generation ONLY via the backend (`scripts/gaf_adapter.py`
   or `gaf` directly — layered prompts per references/sound-design.md;
   measured facts in references/game-audio-forge.md). Processing = ffmpeg
   ops (`scripts/audio_process.py`). Engine integration = verified APIs of
   the installed version only (`scripts/engine_defold.py`,
   `scripts/engine_godot.py`) — never invent an API.
5. **Gate** — `audio_audit.py` (asset+engine findings), `audio_validate.py`
   (profile QA: PASS|WARNING|FAIL|NOT_TESTED — untested never PASS),
   measurements before/after every change. Manual listening is a separate,
   mandatory review state — numbers never claim creative quality.
6. **Deliver** — manifest (`audio_manifest.py`) with license status per
   asset (`approved|review_required|restricted|unknown` — ACE-Step MIT ok
   commercial; Stable Audio weights: commercial only <$1M/yr revenue →
   `review_required` for commercial releases unless confirmed; dasheng
   runtime: never commercial). Report findings + open risks honestly.

## Router (load only what the step needs)

| Task | Read | Run |
|---|---|---|
| setup unknown / "is audio ready?" | references/installation.md | `audio_doctor.py` |
| SFX/music generation, prompts | references/sound-design.md, music-production.md, game-audio-forge.md | `gaf_adapter.py` |
| adaptive/interactive music | references/adaptive-music.md | audit+plan |
| spatial/positional/split-screen | references/spatial-audio.md | engine adapter |
| mix/master, loudness targets | references/mixing-mastering.md | `audio_audit.py` |
| audit/fix existing audio (any project) | references/quality-standards.md | `audio_audit.py`, `audio_process.py`, `audio_batch.py` |
| performance, budgets, platforms | references/performance.md | budget + audit |
| engine integration | references/engine-integration.md | `engine_defold.py` / `engine_godot.py` |
| accessibility | references/accessibility.md (+ existing a11y skill for cross-cutting rules) | validate profile |
| voice/dialog | references/voice-dialog.md | process+validate |
| licensing, release check | references/licensing.md | manifest license fields |
| release gate | templates: audio-config/manifest/budget | `audio_validate.py` |

## Boundaries (hard)

- Generation belongs to game-audio-forge ONLY — no second platform, no
  model weights in this repo, no touching backend files unasked.
- `--bpm` does not move ACE-Step tempo (measured): for sync work trust
  measured BPM, adjust with `atempo` — see references/music-production.md.
- Fixes: safe ops only (trim/fade/resample/level) → new files; audible-risk
  or creative changes need explicit user approval; after each fix:
  re-measure, before/after, rollback via original.
- Multi-listener/split-screen: not native in either shipped engine —
  documented fallbacks, never claim native support.
- Offline LUFS unavailable (loudnorm single-pass): report NOT_TESTED +
  playback-time measurement route (references/mixing-mastering.md).
- Cross-skill: accessibility policies → accessibility skill; engine-wide
  code → defold/godot skills; generation internals → game-audio-forge skill.
  This skill owns audio production + QA, never a second a11y system.
