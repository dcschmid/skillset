# skillset — repository rules

## What this repo is

Authoritative source for reusable agent skills. Skills are installed by
symlink, never copied, into `~/.claude/skills` (Claude Code) and
`~/.agents/skills` (Codex). Edits here propagate live.

## Skill contract

- Every skill: `skills/<name>/SKILL.md` with YAML frontmatter — `name` and
  `description` required; `name` matches the directory name.
- Progressive disclosure: SKILL.md = trigger + binding workflow;
  `references/` = deep guidance; `scripts/` = code that runs; `assets/` =
  templates; `tests/` = validation. No empty placeholders.
- Skills are independent: one skill must work without reading another.
- Project specifics live in `profiles/<project>.md` and load only when the
  skill invocation names that project.

## Format truth (verified on this machine)

- Blender 5.3.0, hash 02f0899d — bundled Python 3.13; system python has no
  bpy. Scripts split: `detect_blender.py` runs on system Python, everything
  importing `bpy` runs inside Blender (MCP exec or `blender -b --python`).
- `Mesh.is_manifold`, `Mesh.use_auto_smooth`,
  `mathutils.geometry.area_tri_loop` are REMOVED in 5.3.
- `BLENDER_WORKBENCH` renders but hides from the engine enum list — assign
  by string inside try/except.
- glTF: `io_scene_gltf2` with `export_format/export_yup/use_selection/
  export_apply` verified present.
- Convention for all assets: **+Z up, +Y facing, +X right; 1 BU = 1 m.**
- Godot 4.7.2-stable (`ed1daf0b`) at `~/.local/opt/godot-4.7.2/godot` (`godot`
  on PATH); `--headless --import` / `--quit-after` verified on this machine.

## Editing rules

- Don't add second Blender installs, don't touch system Blender settings.
- Scripts are non-destructive: never overwrite existing deliverables, dated
  suffix on collision.
- Reference art is the design authority in every asset workflow — simplify
  allowed, substitute forbidden; reconstructed views flagged as such.
- Quality scores cite observations; without visual comparison emit
  `VISUAL_REVIEW_REQUIRED` instead of a number.
- Installer/uninstaller manage only symlinks they created (manifest:
  `.installed-manifest`, `name<TAB>target` lines). Both accept skill names to
  install/remove individually; uninstall with no args removes all managed
  links.
- Detailed per-skill usage lives in `README.md` (the `### \`<skill>\``
  sections: scope, Claude Code / Codex / oh-my-pi invocation, examples, verify
  command) — that is canonical. `skills/<name>/USAGE.md` mirrors it into the
  symlinked folder. Keep both in sync when scripts or entry points change.

## Verify before commit

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
python3 -m py_compile skills/*/scripts/*.py skills/*/tests/*.py
node skills/design-system-ui/tests/run.mjs
TEST_HOME=$(mktemp -d) bash tools/test_installer.sh
python3 skills/godot/tests/test_skill.py
bash skills/godot/scripts/headless_check.sh skills/godot/examples/base-project
```
