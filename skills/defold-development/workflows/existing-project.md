# Workflow: Feature/Change in an Existing Defold Project

Default workflow. The project's existing truth beats every preference here.

## Steps

1. **Audit first** — `scripts/audit_defold_project.py <dir>` (read-only):
   `game.project` sections, engine version hints, collections, scripts,
   module tree, render pipeline, asset roots, physics config.
2. **Find the owner** — which module/collection currently owns the state you
   touch? If two owners exist, that is the bug to fix first.
3. **Match conventions** — naming, message ids, module style, comment
   density of existing code (read 2-3 sibling files before writing one).
4. **Version-check the feature** — version-gated? Check
   `references/version-compatibility.md` gates and the project's actual
   engine version before using 1.14.x-era features (vector fonts, KTX2,
   GLES2 opt-out...).
5. **Plan smallest change** — files touched, messages added, data added.
   Existing module extended > new module > new system.
6. **Implement** — `references/lua-engineering.md` + existing style.
7. **Verify at every reachable level** — STATIC (compile/lint) → AUTOTEST
   (project harness) → BUILT (`scripts/bob_build.sh` then
   `scripts/check_build.sh`) → RUNTIME (log) → VISUAL (screenshot/recording).
   Report levels separately; state what was NOT run.
8. **Leave docs current** — README/CHANGELOG line, new message ids
   centralized.

## Stop conditions

- Engine version unclear → ask before version-gated features.
- Project uses a convention this skill contradicts → project wins.
- Mid-task scope grows (needs voxel worlds, online play) → reassess
  feasibility (`references/voxel-development.md`,
  `references/multiplayer.md`) and report before implementing.
