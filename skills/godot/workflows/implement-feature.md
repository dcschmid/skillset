# Workflow: Implement a feature in an existing Godot project

Any genre/style project. Extends; never parallels.

## Steps

1. **Read the project first** — `scripts/audit_godot_project.py <dir>` +
   `project.godot` (renderer, stretch, autoloads, input map), main scene,
   nearest existing systems. Match their node/naming/signal conventions.
2. **Scope** — one-line spec + the system refs being touched
   (SKILL.md routing). Request-gated systems only: feature does not smuggle
   in inventory/physics/netcode the project lacks.
3. **Plan** — files + scenes touched; data as `Resource` if tunable;
   state as `enum`+`match` or existing FSM component; events via existing
   signal/bus pattern.
4. **Implement** — typed GDScript (`gdscript.md`), composition over
   inheritance, `@export` for designer knobs, no new autoload without 3+
   consumers.
5. **Style parity** — new visuals obey project style refs (pixel filtering,
   material palette, theme): a new asset in the wrong filter is a bug.
6. **Verify ladder** — `scripts/headless_check.sh <dir>`; gameplay paths get
   an AUTOTEST (existing harness) or scripted boot of the feature scene;
   visual change → VISUAL gate. Report levels honestly.
7. **Commit-shape** — `.tscn`/`.tres`/`.gd` + `.import` all staged; new
   autoload/settings diff called out in the summary.

## Rules

Existing conventions beat skill preferences. No drive-by refactors of
unrelated systems, no engine version bumps, no new dependencies without the
compatibility check. Every claim in the summary carries its verification level.
