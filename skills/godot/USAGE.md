# Using the `godot` skill in your agents

Universal Godot 4.7.2 game development for any agent host: genre- and
art-style-agnostic gameplay work (movement, FSM/AI, save games, input
abstraction, cameras), Jolt/classic physics, shaders, TileMapLayer, Control
accessibility, multiplayer RPC, headless CI, export pipelines, glTF/Blender
intake. Engine claims are version-gated against the real binary; unverified
items are marked, never invented.

## Install (this skill only)

```bash
tools/install-skills.sh godot            # from the repo root
```

The installer symlinks `skills/godot/` into both host roots and records the
link in `.installed-manifest`. Remove it again with
`tools/uninstall-skills.sh godot`.

## Claude Code

Claude Code discovers skills in `~/.claude/skills/`. The link created above
is enough: the skill's frontmatter `description` is matched against your
request, and the skill activates on any Godot task. To force activation:

```
Use the godot skill to add coyote-time jumping to the player controller in
this project (Godot 4.7, GDScript, static typing).
```

## Codex

Codex reads skills from `~/.agents/skills/`. The same symlink serves it;
reference the skill by name (Codex surfaces it through its skills list and
`AGENTS.md`):

```
Use the godot skill: audit this project's project.godot and export presets
for headless CI, then propose the minimal headless_check-compatible setup.
```

## oh-my-pi (omp)

omp loads the same skill roots and picks the matching skill from its skill
list automatically; naming it explicitly is still the reliable form:

```
Use the godot skill to implement a jolt-physics character body with
input-buffered double jump, static-typed GDScript, plus a headless test.
```

## Working style (all hosts)

- The skill routes by task: `references/` files are loaded only for the
  domain at hand (27 references — never all at once).
- Automation you can call directly:
  `python3 skills/godot/scripts/audit_godot_project.py <project>`,
  `bash skills/godot/scripts/headless_check.sh <project>`,
  `python3 skills/godot/scripts/check_version.py`.
- Deliverables are non-destructive; existing project files are edited in
  place only where the task demands it.

## Examples that work verbatim

```
Use the godot skill to convert this pixel-art platformer from CharacterBody2D
to a Jolt RigidBody2D setup without changing game feel.
```

```
Use the godot skill to review my AnimationTree: signals fire twice on scene
reload — find the root cause and fix it with a regression test.
```

## Verify the skill itself

```bash
python3 skills/godot/tests/test_skill.py
bash skills/godot/scripts/headless_check.sh skills/godot/examples/base-project
```

Both exit 0 on PASS; the first is static validation (structure, routing,
compile), the second needs the local Godot binary.
