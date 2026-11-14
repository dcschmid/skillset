---
name: godot
description: >
  Universal, genre-agnostic, art-style-agnostic game development with the Godot
  Engine (baseline: Godot 4.7.2 stable, 2026-08-18, commit ed1daf0b). Use for ANY
  task inside a Godot project (.tscn/.tres/.gd/.cs/project.godot/export_presets.cfg)
  or any Godot question: 2D/pixel-art/2.5D/3D/voxel/low-poly/high-poly/stylized/
  realistic rendering, Forward+/Mobile/Compatibility renderer choice, scenes/nodes/
  resources, GDScript static typing and C#, gameplay systems (movement, FSM, AI,
  save games, input abstraction, cameras), Jolt and classic physics, navigation,
  AnimationPlayer/AnimationTree, CanvasItem and Spatial shaders, TileMapLayer,
  Control UI and accessibility, audio buses, multiplayer RPC, headless CI and
  testing, export to Linux/Windows/macOS/Web/mobile, glTF and Blender intake.
  Detects genre and art style from the project or request and loads only the
  matching references. Engine claims are version-gated; unverified items are
  marked, never invented.
---

# Godot Game Development (universal)

Target baseline: **Godot 4.7.2 stable** (2026-08-18, commit `ed1daf0b`,
no known incompatibilities with 4.7.1 per the official maintenance-release
notice). 4.8 is in beta3 (2026-11-09) — never a default. Version gates, channel
discipline, and the update routine live in `references/godot-versions.md`.
This skill is **not** tied to any genre, art style, perspective, or asset tool:
identify those first, then load only what the task needs.

## Prime Directive

Before changing anything: **read the actual project**. `project.godot`
(version hint in `config/features`, renderer choice, stretch/pixel settings,
autoloads, input map), main scene tree, existing scripts, resource layout,
export presets. Extend what exists; never build a parallel system beside it.
Never invent an API — if it is not in the official docs for the target version
(https://docs.godotengine.org/en/4.7/), mark it UNVERIFIED and verify before
use. No genre system (inventory, quest log, race manager) or art-style pipeline
(Blender, voxels, pixel snap) ships into a project that does not ask for it.

## Workflow (every task)

1. **Detect** — genre + art style + perspective + platform targets from the
   project or the request. One line: `Genre: X · Style: Y · Perspective: Z ·
   Platforms: W`. Missing info → smallest reversible assumption, recorded.
2. **Version gate** — confirm the project's engine version (project.godot hint,
   CI pin, or ask). Load `references/godot-versions.md` when a feature is
   version-sensitive. Never migrate an existing project's engine version.
3. **Project audit** — `scripts/audit_godot_project.py <project_dir>`
   (read-only): settings, scenes, broken `res://` deps, autoloads, plugins.
4. **Route** — pick the minimal reference/workflow set from the tables below.
5. **Plan** — smallest coherent change; name files and nodes touched.
6. **Implement** — idiomatic GDScript/C# (`references/gdscript.md`,
   `references/architecture.md`), existing node and naming conventions.
7. **Verify** — static → headless import → headless run → visual.
   `scripts/headless_check.sh <project_dir>` runs every level the local
   engine supports. Report each level honestly; a green import ≠ working game.
8. **Document** — findings, version gates hit, remaining risk.

## Verification Truth Ladder (report using these levels)

| Level | Means | Proves |
|---|---|---|
| `STATIC` | script parse (`--check-only`), audit script, `tests/test_skill.py` | parses, conventions intact |
| `AUTOTEST` | project test framework (gdUnit4/GUT) headless run | logic under test |
| `IMPORTED` | `godot --headless --import` exit 0, clean log | assets + scenes load |
| `RUNTIME` | `godot --headless --quit-after N` executed, logs read | boots and ticks |
| `BUILT` | `--export-pack`/`--export-release` exit 0 + output check | bundle integrity |
| `VISUAL` | running window / `--write-movie` frames reviewed | looks right |
| `UNVERIFIED` | state it | nothing |

Never collapse levels. **No Godot binary is installed on this skill host** —
without the user's engine, everything above `STATIC` is reported as UNVERIFIED
with the exact command the user must run. Never report invented engine output.

## Style Routing (pick by detected art style / perspective, load only matches)

| Style / task | Load |
|---|---|
| Pixel art: filtering, integer scaling, TileMapLayer, Camera2D snap, palettes | `references/pixel-art.md` |
| Voxel look or editable voxel worlds, chunking, greedy meshing, streaming | `references/voxel-art.md` |
| Low-poly 3D, flat shading, material palettes, iGPU budgets | `references/low-poly.md` |
| High-poly 3D, PBR, normal maps, texture budgets, LOD | `references/high-poly.md` |
| Cel/toon/cartoon, outlines, hand-painted, non-photoreal lighting | `references/stylized-rendering.md` |
| Realistic PBR, plausible materials, reflections, quality tuning | `references/realistic-rendering.md` |
| Shaders: CanvasItem/Spatial, VisualShader, post-processing, VFX | `references/shaders.md` |
| Pure 2D projects: rendering pipeline, batching, canvas settings | `references/2d-development.md` |
| 2.5D: sprites in 3D, billboards, isometric, HD-2D-ish layering | `references/2-5d-development.md` |
| 3D projects: renderer pick (Forward+/Mobile/Compatibility), environment | `references/3d-development.md` |

## System Routing (load only what the project actually needs)

| Task touches | Load |
|---|---|
| project layout, autoloads, scene flow, component pattern, RefCounted services | `references/architecture.md` |
| GDScript style/typing/annotations, or C# specifics, error handling | `references/gdscript.md` |
| scenes, custom Resources, save/load, config, .tres data | `references/scenes-and-resources.md` |
| gameplay system shapes: movement, FSM, events, input abstraction, abilities | `references/gameplay-systems.md` |
| physics engines (Jolt/classic), collision layers, raycasts, controllers | `references/physics.md` |
| NavigationRegion/Agent, pathfinding, avoidance | `references/navigation-and-ai.md` |
| AnimationPlayer/Tree, sprites, skeletons, IK, procedural motion | `references/animation.md` |
| RPC, authority, spawner/synchronizer, split-screen, co-op | `references/multiplayer.md` |
| Control/Container, themes, localization, focus, screen readers | `references/ui-and-accessibility.md` |
| AudioServer buses, players, music systems | `references/audio.md` |
| profiling, draw calls, memory, platform budgets, per-style budgets | `references/performance.md` |
| asset intake: glTF/FBX/spritesheets/tile sources/procedural | `references/asset-pipelines.md` |
| Blender round-trip (only when the project uses Blender assets) | `references/blender-integration.md` |
| headless CI, unit/e2e tests, regression gates | `references/testing.md` |
| debugger, profiler, remote debug, common failure patterns | `references/debugging.md` |
| export presets, platform limits, Steam/itch.io, web hosting | `references/export-and-release.md` |
| engine version, channels, update routine | `references/godot-versions.md` |

## Workflows

| Situation | Run |
|---|---|
| new project from scratch | `workflows/new-project.md` |
| feature/change in an existing project | `workflows/implement-feature.md` |
| pixel-art project setup/pass | `workflows/pixel-art-workflow.md` |
| voxel project setup/pass | `workflows/voxel-art-workflow.md` |
| Blender asset → Godot | `workflows/blender-to-godot.md` |
| performance pass | `workflows/optimize-game.md` |
| bug hunt / broken feature | `workflows/debug-project.md` |
| review before merge/handoff | `workflows/project-review.md` |
| engine upgrade (explicit user decision only) | `workflows/engine-upgrade.md` |
| release build / publish prep | `workflows/release-build.md` |

## Examples (readable, runnable with a 4.7.x engine)

- `examples/base-project/` — boot + input actions + reusable gameplay component
- `examples/pixel-art-scene/` — nearest filtering, integer scale plan, snap camera
- `examples/voxel-scene/` — ArrayMesh chunk + collision, no external plugin

## Tools

- `scripts/validate_skill.py` — structure validator (this skill's own gate)
- `scripts/check_version.py` — version/channel gate vs official releases
- `scripts/audit_godot_project.py` — read-only Godot project auditor (stdlib only)
- `scripts/headless_check.sh` — engine ladder runner (SKIPS cleanly with no engine)

## Binding Rules

- No stale or invented APIs; alpha/beta (4.8-beta, dev snapshots) never
  presented as stable. Renderer names are `forward_plus`, `mobile`,
  `gl_compatibility` (verify per docs; names are stable across 4.7).
- Genre, perspective, and art style come from the project — never from defaults.
  Blender is optional; pixel/voxel/vector projects need not touch it.
- External plugins (gdUnit4, GUT, Zylann Voxel Tools, …) are opt-in: check
  compatibility with the pinned engine, license, and maintenance state first.
- Performance claims only from measurements (`references/performance.md`);
  no FPS promises. Optimizations follow profile evidence, not folklore.
- Existing project conventions beat this skill's preferences; migration
  problems are documented, not silently patched around.
- `scripts/` are non-destructive; generated outputs collide → dated suffix.

## Test

```bash
python3 skills/godot/tests/test_skill.py    # structure + routing + examples (STATIC)
bash skills/godot/scripts/headless_check.sh examples/base-project   # needs a godot binary
```
