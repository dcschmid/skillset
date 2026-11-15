# Installation & readiness

Order is law: **backend → config → models → backend test → skill → doctor →
use**. The skill never installs the backend and never fakes readiness.

## 1. game-audio-forge (required dependency)

Repo: https://github.com/dcschmid/game-audio-forge · default path
`~/dev/github/game-audio-forge`.

```bash
git clone https://github.com/dcschmid/game-audio-forge ~/dev/github/game-audio-forge
cd ~/dev/github/game-audio-forge
bash scripts/setup.sh          # idempotent; CUDA 12.8 user-space, gcc13, builds
source scripts/gaf-env         # every new shell
scripts/gaf-test.sh            # 7-case quality gate ≈70 s (needs GPU)
```

Models (music ACE-Step 1.5 Q8 ≈4.1 GB, sfx SA3 Q8 ≈2.6 GB) download via
setup / `models.sh` inside the backend — see its docs/SETUP.md. Host needs:
NVIDIA driver, cmake, ninja, git, jq, ffmpeg (analysis works without GPU;
generation does not).

## 2. Custom backend location

```bash
export GAME_AUDIO_FORGE_ROOT=/path/to/forge    # or --forge-root per call
```
Priority: CLI arg > env > default. Doctor prints which one answered.

## 3. Skill install (via skillset installer)

```bash
cd ~/dev/github/skillset && tools/install-skills.sh game-audio-sound-design
```
Symlinks into ~/.claude/skills + ~/.agents/skills; manifest-tracked removal
via `tools/uninstall-skills.sh game-audio-sound-design`.

## 4. Verify (no GPU needed for READY-analysis)

```bash
python3 skills/game-audio-sound-design/scripts/audio_doctor.py --project .
```
READY = forge + CLI + ffmpeg/ffprobe + writable output. PARTIALLY_READY =
analysis works, some generation path blocked (missing models/GPU → run
backend setup; never skip reporting it). NOT_READY = ffmpeg/output broken.

## States (report them separately, never collapse)

| State | Proof |
|---|---|
| backend installed | scripts/gaf exists |
| backend configured | config/gaf.json parses |
| backend operational | `gaf status`: binaries+models OK |
| skill installed | symlink in host root |
| skill operational | doctor READY + validate runs on a fixture |

## Missing backend → what to say

Name the repo, link it, give the clone+setup commands, state that generation
is unavailable until then, and continue with analysis-only work if useful.
Never auto-clone, never claim success.
