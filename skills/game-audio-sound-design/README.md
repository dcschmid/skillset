# game-audio-sound-design

Manage sound effects, music, mixing, and audio QA. Generate audio through game-audio-forge; use ffmpeg and ffprobe for analysis and repairs.

Profile: Private. Preparation: Provide the game project, audio category, mood, duration, and output format. Use a separate output directory for repairs.

Expected result: A readiness report, measured findings, repaired files, or generated assets with provenance and license status.

Requirements and limits: Generation requires a separately configured game-audio-forge backend. The doctor installs nothing. Defold and Godot adapters are included; Unity and Unreal adapters are not implemented. Creative quality remains AUDIO_REVIEW_REQUIRED; unmeasured checks remain NOT_TESTED. Recheck licensing before release.

## game-audio-sound-design: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh game-audio-sound-design
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the game-audio-sound-design skill. Check the audio environment, then audit assets/audio for silence, clipping, and loop seams. List missing tools and write repairs only to audio-fixes/.
```

**Codex:**

```text
Use the game-audio-sound-design skill. Generate a 45-second boss-fight loop through game-audio-forge with a mechanical, tense mood. Check measured tempo, loop seam, and provenance; leave listening review explicitly pending.
```

**oh-my-pi:**

```text
Use the game-audio-sound-design skill. Plan adaptive exploration, combat, and pause music for this Godot project. Verify scene changes and restart behavior against the installed engine version.
```

## game-audio-sound-design: Self-test

Run from the repository root:

```bash
python3 skills/game-audio-sound-design/tests/test_skill.py
```

Prerequisites: configure game-audio-forge before generating audio. Installing this skill alone does not make generation available.

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [templates/](templates/): Templates for the target project.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [audio_audit.py](scripts/audio_audit.py)
- [audio_batch.py](scripts/audio_batch.py)
- [audio_common.py](scripts/audio_common.py)
- [audio_doctor.py](scripts/audio_doctor.py)
- [audio_manifest.py](scripts/audio_manifest.py)
- [audio_process.py](scripts/audio_process.py)
- [audio_validate.py](scripts/audio_validate.py)
- [engine_defold.py](scripts/engine_defold.py)
- [engine_godot.py](scripts/engine_godot.py)
- [gaf_adapter.py](scripts/gaf_adapter.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/game-audio-sound-design` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/audio_doctor.py --project /path/to/game
python3 scripts/audio_audit.py /path/to/game --json
python3 scripts/gaf_adapter.py status
```

```bash
python3 scripts/audio_audit.py /path/to/game --mode fix --apply --out-dir audio-fixes/
python3 scripts/audio_validate.py audio-fixes/ --profile music --json
python3 scripts/audio_manifest.py create /path/to/game --out audio-manifest.json
python3 scripts/audio_manifest.py check audio-manifest.json
```

## Set up game-audio-forge

Generation requires the separate game-audio-forge repository. Follow its own
`docs/SETUP.md`; this skill does not install models or GPU tools. The documented
default location is `~/dev/github/game-audio-forge`.

Backend resolution uses `--forge-root`, then `GAME_AUDIO_FORGE_ROOT`, then the
default path. After setup, run the doctor and status commands above. Installed,
configured, and operational are different states; the doctor reports `READY`,
`PARTIALLY_READY`, or `NOT_READY`.

Analysis and repairs need ffmpeg/ffprobe and the appropriate Python runtime.
Generation also needs the backend binaries and models. GPU tests belong to the
backend test suite. The templates provide audio configuration, budgets, and a
manifest; tune budgets to the actual game.

The repair example above writes new files to `audio-fixes/` and preserves the
originals. Its validation profile is `music`; choose a profile that fits your
material. Measurements do not replace listening review. Native multiple-listener
support, Unity/Unreal adapters, and voice/TTS are not promised features of this
release. See `references/` for music, spatial audio, and licensing details.
