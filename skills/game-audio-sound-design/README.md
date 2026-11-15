# game-audio-sound-design

Universal game audio & sound-design skill for the skillset: sound effects,
music, adaptive music, spatial audio, mixing, audits, safe repairs,
performance budgets, and release validation — for any genre, art style, or
engine (Defold + Godot adapters shipped; others adapter-ready). Generation
runs on **game-audio-forge**; analysis/audit/repair run on ffmpeg.

## Features

- **audio_doctor.py** — READY / PARTIALLY_READY / NOT_READY readiness report
  with per-check fix commands (never installs, never downloads)
- **audio_audit.py** — asset + engine audit (corrupt/silent/clipping/DC/
  loudness/loop-seam/missing-refs/unreferenced) in three modes:
  `analyze` (read-only), `fix` (safe ops → NEW files), `optimize` (plan)
- **audio_process.py / audio_batch.py** — verified ffmpeg ops per file or
  per set, idempotent, originals untouched, every change re-measured
- **audio_validate.py** — QA gate per profile (ui-sfx…cinematics) with
  PASS/WARNING/FAIL/**NOT_TESTED** — untested never reports as passed
- **audio_manifest.py** — provenance + per-asset license status
  (ACE-Step MIT approved; Stable Audio weights review_required <$1M/yr;
  dasheng restricted) with drift re-check before release
- **engine_defold.py / engine_godot.py** — verified-API emission (1.14.1 /
  4.7.2): `.sound`, AudioDirector GDScript, facts — nothing invented
- **gaf_adapter.py** — backend client for `gaf music|sfx|status`; resolves
  install via `--forge-root > $GAME_AUDIO_FORGE_ROOT > ~/dev/github/game-audio-forge`

## Prerequisites — Required Installation

**game-audio-forge is a mandatory external dependency and must be installed
and set up BEFORE this skill can generate audio.** The skill does NOT
install it automatically, and it never pretends the backend is available.
The two live in separate repositories: this skill is the control/QA layer,
game-audio-forge (https://github.com/dcschmid/game-audio-forge) is the
generation backend. Analysis, audit, and repair work with ffmpeg/ffprobe
alone — but say so honestly when generation is unavailable.

Setup order is binding:

```
1. clone game-audio-forge   2. bash scripts/setup.sh (its docs/SETUP.md)
3. models+binaries via its setup   4. gaf-test.sh 7/7
5. install this skill (installer)  6. audio_doctor.py READY
7. use the skill
```

## Game Audio Forge installation

```bash
mkdir -p ~/dev/github
git clone https://github.com/dcschmid/game-audio-forge ~/dev/github/game-audio-forge
cd ~/dev/github/game-audio-forge
bash scripts/setup.sh        # idempotent, no sudo; CUDA 12.8 user-space, gcc13
source scripts/gaf-env       # every new shell
```

Backend install/setup truth (host: Fedora, RTX 5070 8 GB):
`~/dev/github/game-audio-forge/docs/SETUP.md` (build), `docs/LICENSES.md`
(licensing), `docs/PROMPTING.md` (prompt behaviour). Generation = ACE-Step
1.5 music 48 kHz + Stable Audio 3 SFX 44.1 kHz on CUDA; sequential by
design (VRAM budget). Host needs NVIDIA driver, cmake, ninja, jq, jq,
ffmpeg (analysis-only work needs only ffmpeg/ffprobe + Python ≥3.12).

## Installation verification

```bash
cd ~/dev/github/skillset/skills/game-audio-sound-design
python3 scripts/audio_doctor.py --project .      # human report + exit code
python3 tests/test_skill.py                      # 40+ checks, no GPU needed
```

Doctor checks: forge dir/config/CLI · generator binaries+models ·
ffmpeg/ffprobe · Python host (3.14: audioop removed — metering is ffmpeg
by design) · writable output · engine detection. States stay separate:
*installed ≠ configured ≠ operational*; skill installed ≠ skill operational.

### Custom backend location

`--forge-root PATH` (per call) > `export GAME_AUDIO_FORGE_ROOT=…` >
`~/dev/github/game-audio-forge`. Doctor prints which source answered.

### Backend missing?

Doctor and tests still work; they name the repo, print
`git clone https://github.com/dcschmid/game-audio-forge ~/dev/github/game-audio-forge`,
the setup commands, and keep generation marked unavailable. Never an
auto-install, never a fake success.

## Skill installation

```bash
cd ~/dev/github/skillset
tools/install-skills.sh game-audio-sound-design    # symlink into Claude Code + Codex
tools/uninstall-skills.sh game-audio-sound-design  # manifest-tracked removal
```

## Configuration

Copy `templates/audio-config.json` (resolution, profiles, formats),
`templates/audio-budget.json` (voices/memory/rates — illustrative defaults,
per-project tuning mandatory), `templates/audio-manifest.json` (schema).
`--budget FILE` feeds audit/validate; loudness bands are guidance, never
universal laws.

## Usage

Name the skill by directory name in any agent host, or run the tools:

```bash
python3 scripts/audio_doctor.py --project /path/to/game
python3 scripts/audio_audit.py /path/to/game --json            # analyze
python3 scripts/audio_audit.py /path/to/game --mode fix --apply --out-dir out/
python3 scripts/audio_validate.py out/ --profile music --json
python3 scripts/audio_manifest.py create /path/to/game --out manifest.json
python3 scripts/audio_batch.py convert assets --to ogg --out-dir out/
python3 scripts/engine_defold.py /path/to/game --facts
python3 scripts/engine_godot.py /path/to/game --facts
```

Generation via the backend (the skill never re-implements it):

```bash
python3 scripts/gaf_adapter.py status
# or directly: ~/dev/github/game-audio-forge/scripts/gaf music "…" --duration 45
```

## Sound Design

Category map, 12-step loop, variation (round-robin + gain ±2 dB / atempo
±3 % — never for info-bearing pitch), processing table:
`references/sound-design.md`. Gate = validate + listening
(AUDIO_REVIEW_REQUIRED, separate state).

## Music Production

`gaf music` with 5-layer paragraph prompts (tags → tempo roulette);
`--bpm` does not move the DiT (measured) — trust measured BPM
(backend `gaf-quality.py`), normalize grids with `atempo`. Stems are NOT
independently generated files; layers get verified parity checks.
`references/music-production.md`.

## Adaptive Music

State machine + transitions (instant/crossfade/bar-locked) on engine-verified
playback facts; pause/scene-change/restart contract; fallback ladder.
`references/adaptive-music.md`.

## Spatial Audio

Computed panning/falloff fallbacks (Defold no listener API at 1.14.1; Godot
one listener per viewport type); split-screen ladder: shared listener →
priority culling → per-viewport buses. `references/spatial-audio.md`.

## Audio Audits

`audio_audit.py` findings carry {severity, category, file, problem, cause,
fix, status}; modes analyze|fix|optimize; reports JSON + human. Broken
assets, missing refs, unreferenced sets, loop clicks, loudness parity.

## Automatic Fixes

Safe ladder: safe-auto (resample/fade/trim/level → new files) → approved →
manual → impossible. After every fix: re-measure, before/after, rollback =
delete generated output. Originals are never modified — by construction.

## Performance Optimization

Budget template + audit enforcement (rate/channels/voices, unreferenced =
review-list). Runtime cost stays engine-side (documented split).
`references/performance.md`.

## Engine Integration

Defold 1.14.1 (`sound.play/stop/set_gain/set_pan/set_group_gain…` verified;
3D listener NOT emitted) · Godot 4.7.2 (players, buses, `AudioServer`
verified). Unity/Unreal: adapter-ready, honestly unimplemented until APIs +
test targets exist. `references/engine-integration.md`.

## Licensing

Per-asset `license_status` in manifests: ACE-Step MIT → approved; Stable
Audio 3 weights → review_required (commercial <$1M/yr tier); dasheng →
restricted (unlicensed runtime); imported → unknown until reviewed.
Commercial release blocks on unknown/restricted. `references/licensing.md`.

## Testing

```bash
python3 tests/test_skill.py    # static + live-no-GPU, deterministic verdict
```

GPU generation tests belong to backend `scripts/gaf-test.sh` (7/7, ~70 s).
Manual listening is a separate mandatory review state.

## Troubleshooting

| Symptom | Fix |
|---|---|
| doctor: game-audio-forge FAIL | clone+setup (commands above), or set `GAME_AUDIO_FORGE_ROOT` |
| `ace-lm/sa3-generate not found` | backend `bash scripts/setup.sh` |
| nvcc errors in shells | `source …/game-audio-forge/scripts/gaf-env` |
| hangs "GPU busy" | a generator runs; gaf queues by design (8 GB VRAM) |
| validate all-NOT_TESTED | ffmpeg missing → install ffmpeg-full |
| clipped reports on mastered files | flat_factor>10 = clipped; peak≈0 is normal |

## Limitations (open until proven — never claimed)

- Offline LUFS/true-peak streaming: NOT_TESTED (loudnorm single-pass);
  playback-time metering required
- Unity/Unreal adapters: not implemented (no verified APIs/test targets)
- Multi-listener native: neither shipped engine (fallbacks only)
- ACE-Step stems (lego/extract): base model needed — absent with SFT
- Voice/TTS: backend has none; import or external TTS behind the same gates
- Creative quality: always AUDIO_REVIEW_REQUIRED

## Examples

```bash
# audit a game project, fix safe findings, validate, manifest, license-gate
python3 scripts/audio_audit.py ~/games/mygame --mode fix --apply --out-dir fixes/
python3 scripts/audio_validate.py fixes/ --profile music --json
python3 scripts/audio_manifest.py create ~/games/mygame --out manifest.json
python3 scripts/audio_manifest.py check manifest.json
```
