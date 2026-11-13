# skillset

Central repository of reusable AI-agent skills for Claude Code and Codex.
Skills are plain directories with `SKILL.md` (YAML frontmatter + workflow),
installed into both agents via symlinks — one source, many consumers.

## Layout

```
skills/<name>/SKILL.md      entry point + progressive-disclosure root
skills/<name>/references/   deep docs, loaded on demand
skills/<name>/scripts/      working automation (Blender Python, system Python)
skills/<name>/assets/       templates reused per run
skills/<name>/tests/        runnable validation
profiles/<project>.md       optional project overlays (never auto-applied)
tools/                      installer / uninstaller / installer tests
docs/                       architecture + authoring guides
```

## Skills

| Skill | Purpose |
|---|---|
| [lowpoly-reference-to-blender](skills/lowpoly-reference-to-blender/SKILL.md) | Reference image → stylized low-poly Blender asset → validated GLB (Defold-ready) |

## Install (Claude Code + Codex)

```bash
tools/install-skills.sh      # symlinks skills/ into ~/.claude/skills and ~/.agents/skills
tools/uninstall-skills.sh    # removes ONLY links this repo created
```

Idempotent; foreign skills in the target dirs are never modified.

## Use

```
Use lowpoly-reference-to-blender to build a high-quality game-ready low-poly
character for Riff Racers from this concept art.
```

Optional parameters (asset_type, polygon_budget, quality_profile, views, …)
are documented in each SKILL.md; defaults are sane, the agent only stops for
missing references or contradictory specs.

## Validate

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
bash tools/test_installer.sh   # set TEST_HOME to a scratch dir first
```

## Adding skills

`docs/adding-new-skills.md`. Each skill stays independent: its own directory,
testable on its own, versionable on its own.

## Environment truth (last probe: 2026-11-13)

Blender **5.3.0** (`02f0899d`, bundled Python 3.13) at
`~/.local/opt/blender-5.3.0-linux-x64/blender`; BlenderMCP addon 1.8 live
(protocol 15); system `python3` 3.14 without `bpy`.
