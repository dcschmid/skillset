# Architecture

```
game-audio-sound-design (control layer)
 ├─ SKILL.md            router: workflow spine + gates
 ├─ scripts/            executable tools (host Python 3.14 + ffmpeg)
 │   audio_common.py      shared: gaf resolve, ffprobe/astats facts,
 │                        unique_path (never-overwrite), verdicts
 │   audio_doctor.py      READY|PARTIALLY_READY|NOT_READY report
 │   gaf_adapter.py       backend client ONLY (music/sfx/status)
 │   audio_audit.py       asset+engine audit, fix/optimize modes
 │   audio_process.py     per-file ffmpeg ops (verified filters)
 │   audio_batch.py       sets: process/convert/report (idempotent)
 │   audio_validate.py    profile QA gate PASS|WARNING|FAIL|NOT_TESTED
 │   audio_manifest.py    provenance + license status records
 │   engine_defold.py     verified 1.14.1 API emit/facts
 │   engine_godot.py      verified 4.7.2 API emit/facts
 ├─ references/         domain depth (this router loads per step)
 ├─ templates/          audio-config / audio-manifest / audio-budget
 └─ tests/              static + live E2E (no GPU required)
        │
        ▼ shells out (never imports/copies)
game-audio-forge (backend, separate repo, ~/dev/github/game-audio-forge)
 gaf CLI · acestep.cpp (music) · sa3.cpp (sfx) · models in tools/ (gitignored)
```

## Rules

- **Layering**: skill = control/QA/integration; backend = generation.
  One platform per job; the skill never re-implements a generator and the
  backend never re-implements QA gates.
- **Resolution priority**: `--forge-root` > `$GAME_AUDIO_FORGE_ROOT` >
  `~/dev/github/game-audio-forge`. Any project may pin its own backend.
- **Adapters are scripts**, not a framework: engine adapters emit verified
  engine files/Lua/GDScript; generic projects need no adapter.
- **State**: nothing mutates a project in place. Outputs: unique suffixes
  (`-2`, `-3`), sidecars (`.meta.json`, `.proc-report.json`), manifests.
  Rollback = delete generated files; originals untouched by construction.
- **Independence**: works with zero knowledge of other skills; hands off
  cross-cutting a11y → accessibility skill, engine code → defold/godot
  skills, backend internals → game-audio-forge skill.
- **Testability**: every gate exits deterministic PASS/FAIL/WARNING;
  GPU work isolated behind gaf_adapter (mock-able: pure subprocess).
