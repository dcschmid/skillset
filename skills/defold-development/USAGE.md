# Using the `defold-development` skill in your agents

Universal Defold 1.14.1 game development for any agent host: rendering
(2D/pixel/voxel/2.5D/3D), Lua scripts and lifecycle, game
objects/collections/factories/proxies, physics, shaders/materials/PBR,
glTF/GLB with Draco/Meshopt/KTX2, local multiplayer, replay, GUI/fonts,
audio, profiling, `bob.jar` builds, DAP debugging. Version-gated engine
claims; unverified items are marked, never invented.

## Install (this skill only)

```bash
tools/install-skills.sh defold-development
```

Symlinks `skills/defold-development/` into both host roots and records the
link in `.installed-manifest`. Remove with
`tools/uninstall-skills.sh defold-development`.

## Claude Code

Claude Code discovers it from `~/.claude/skills/` and activates on any
Defold task from the frontmatter description. Explicit invocation:

```
Use the defold-development skill to add split-screen local co-op to this
top-down shooter (Defold 1.14.1, Lua), with camera proxies and a focus plan.
```

## Codex

Codex reads the same content from `~/.agents/skills/`:

```
Use the defold-development skill: run a preflight on my glTF pipeline and
tell me which Draco/Meshopt flags are safe for the HTML5 target.
```

## oh-my-pi (omp)

omp matches the skill from its skill list; naming it keeps behavior stable:

```
Use the defold-development skill to wire DAP debugging and a headless
bob.jar build lane into CI for this project.
```

## Working style (all hosts)

- Routing loads one reference set per task (21 references, never all).
- Direct automation:
  `python3 skills/defold-development/scripts/audit_defold_project.py <project>`,
  `bash skills/defold-development/scripts/bob_build.sh <project>`,
  `python3 skills/defold-development/scripts/gltf_preflight.py <file.glb>`.
- Engine facts are version-gated; the skill reports NOT TESTED rather than
  guessing.

## Examples that work verbatim

```
Use the defold-development skill: implement save games with versioned
schema migration for this roguelike, non-destructive on old saves.
```

## Verify the skill itself

```bash
python3 skills/defold-development/tests/test_skill.py
```

Exit 0 on PASS; static validation of structure, routing, and script
compilation.
