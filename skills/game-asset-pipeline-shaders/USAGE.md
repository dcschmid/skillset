# Using the `game-asset-pipeline-shaders` skill in your agents

Technical asset pipeline for any engine: material/texture/shader audits,
safe repairs, glTF/GLB validation, budget reports, CI gates. Defold 1.14.1 +
Godot 4.7.2 adapters probed on this machine; adapter contract for
Unity/Unreal/Bevy/custom. Dry-run-first repairs, `.orig` backups,
art-style-aware rules (pixel-art keeps lossless + nearest).

## Install (this skill only)

```bash
tools/install-skills.sh game-asset-pipeline-shaders
```

Symlinks into both host roots plus the Private profile roots
(`~/.omp/profiles/private/agent/skills`, `~/.codex/skills`;
`tools/profile-map.tsv`), records in `.installed-manifest`. Remove:
`tools/uninstall-skills.sh game-asset-pipeline-shaders`.

## Claude Code

Discovers from `~/.claude/skills/`; activates on asset-pipeline tasks
(textures, materials, shaders, glTF, export, VRAM budgets). Explicit:

```
Use the game-asset-pipeline-shaders skill: audit the asset pipeline of
this project (audit mode), report findings by severity, no writes.
```

Modes travel in the request: `audit | fix | optimize | shader | material |
textures | export | validate | benchmark | compare` — skill behavior, not
separate slash-commands.

## Codex

Same content via `~/.agents/skills/`:

```
Use the game-asset-pipeline-shaders skill: run fix mode dry-run on
assets/, show the plan and risk notes before touching anything.
```

## oh-my-pi (omp)

Loaded from both roots; name it to keep activation deterministic:

```
game-asset-pipeline-shaders — textures mode on assets/textures/, profile
mobile, pixel-art project: what compresses, what must stay lossless?
```

## Scripts directly (CI/headless)

```bash
python3 scripts/asset_audit.py PROJ --json out.json      # audit gate
python3 scripts/gltf_validate.py model.glb               # per-asset
python3 scripts/pipeline_runner.py compare --before a.png --after b.png
python3 scripts/tool_probe.py                            # lane capability
```

Verify: `python3 tests/test_skill.py` (exit 0 = PASS).
