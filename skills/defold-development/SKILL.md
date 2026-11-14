---
name: defold-development
description: >
  Universal, genre-agnostic, art-style-agnostic game development with the
  Defold engine (baseline: Defold 1.14.1 Stable, 2026-11-10, sha
  ee283d4). Use for ANY task inside a Defold project or any Defold question:
  2D/pixel-art/voxel/2.5D/3D rendering, sprites, tilemaps, cameras, Lua
  scripts and lifecycle, game objects/collections/factories/proxies,
  gameplay systems (movement, AI, save games, input, cameras), physics,
  shaders/materials/PBR, glTF/GLB and Draco/Meshopt/KTX2 import, local
  multiplayer/split-screen, replay/rewind, GUI/fonts/vector fonts, audio,
  performance/profiling, bob.jar builds for Linux/Windows/HTML5/mobile,
  DAP debugging and automated tests. Detects genre and art style from the
  project/request and loads only the matching references. Engine claims are
  version-gated; unverified items are marked, never invented.
---

# Defold Game Development (universal)

Target baseline: **Defold 1.14.1 Stable** (`ee283d4dad9fa451dd6399d83602e1dc25133681`,
2026-11-10). Version gates, channel discipline, and the update routine for
future releases live in `references/version-compatibility.md`. This skill is
**not** tied to any genre or art style: identify both first, then load only
what the task needs.

## Prime Directive

Before changing anything: **read the actual project**. `game.project`,
bootstrap collection, existing modules, naming, messaging, render pipeline.
Extend what exists; never build a parallel system beside it. Never invent an
API — if it is not in the official docs for this version
(https://defold.com/ref/), mark it UNVERIFIED and verify before use.
No genre-specific or project-specific system ships into a project that does
not ask for it.

## Workflow (every task)

1. **Detect** — genre + art style + platform targets from the project or the
   request. One line: `Genre: X · Style: Y · Platforms: Z`.
2. **Version gate** — confirm the project's Defold version. Load
   `references/version-compatibility.md` when a feature is version-sensitive.
3. **Project audit** — `scripts/audit_defold_project.py <project_dir>`
   (read-only) or inspect: `game.project`, `main.collection`, module tree,
   render pipeline, asset roots.
4. **Route** — pick the minimal reference/workflow set from the tables below.
5. **Plan** — smallest coherent change; name files and systems touched.
6. **Implement** — idiomatic Lua, existing conventions
   (`references/lua-engineering.md`, `references/architecture.md`).
7. **Verify** — static → autotest → build → runtime → visual. Report each
   level honestly; a green build ≠ working gameplay.
8. **Document** — findings, limits, remaining risk.

## Verification Truth Ladder (report using these levels)

| Level | Means | Proves |
|---|---|---|
| `STATIC` | lua compile/lint, structure audit, `validate_skill.py` | parses, conventions |
| `AUTOTEST` | project test harness / `tests/test_skill.py` run | logic under test |
| `BUILT` | `bob.jar` build exit 0 + output check (`check_build.sh`) | bundle integrity |
| `RUNTIME` | engine executed, logs inspected | loads and runs |
| `VISUAL` | screenshot/recording compared | looks right |
| `UNVERIFIED` | state it | nothing |

Never collapse levels. Never report invented results.

## Style Routing (pick by detected art style, load only matches)

| Style / task | Load |
|---|---|
| Pixel art, sprites, flipbooks, tilemaps, integer scaling, shimmering | `references/2d-pixel-art.md` |
| General 2D rendering, texture filtering, atlas, screen-size adaptation | `references/2d-rendering.md` |
| Voxel look or voxel worlds, chunking, greedy meshing, streaming | `references/voxel-development.md` |
| Low-poly 3D, flat shading, vertex colors, iGPU budgets | `references/3d-lowpoly.md` |
| High-poly 3D, PBR, normal maps, KTX2, rigging budgets | `references/3d-highpoly.md` |
| 2.5D, isometric, billboards, 2D-in-3D layering | `references/hybrid-2-5d.md` |
| Shaders, materials, PBR support, GLES2/WebGL1 opt-in, render scripts | `references/shaders-materials.md` |
| Asset pipelines (pixel sheets, glTF/GLB, voxel exports, procedural) | `references/asset-pipelines.md` |

## System Routing (load only what the project actually needs)

| Task touches | Load |
|---|---|
| project layout, collections, factories, proxies, scene/save flow | `references/architecture.md` |
| Lua style, lifecycle, modules, error handling, determinism | `references/lua-engineering.md` |
| reusable gameplay system shapes (movement, FSM, AI, inventory…) | `references/gameplay-systems.md` |
| physics engines, collision groups, raycasts, NPC navigation | `references/physics-ai.md` |
| local multiplayer, gamepads, split-screen, replay/rewind, online analysis | `references/multiplayer.md` |
| procedural generation, seeded RNG, chunk streaming | `references/procedural-generation.md` |
| GUI, fonts (vector/SDF/bitmap), localization, accessibility | `references/ui-ux.md` |
| sound, music, positional audio, music-driven mechanics | `references/audio.md` |
| draw calls, memory, profiling protocol, platform budgets | `references/performance.md` |
| profiler, DAP debugging, unit/integration tests, log analysis | `references/debugging-testing.md` |
| bob.jar, platform builds, Steam/itch.io, CI/CD | `references/build-deployment.md` |
| version, channels, update routine | `references/version-compatibility.md` |
| official doc index and citation discipline | `references/official-sources.md` |

## Workflows

| Situation | Run |
|---|---|
| new project from scratch | `workflows/new-project.md` |
| feature/change in an existing project | `workflows/existing-project.md` |
| add one gameplay feature | `workflows/implement-feature.md` |
| bug hunt / broken feature | `workflows/debug-feature.md` |
| 2D asset intake (sheets, atlases, tile sources) | `workflows/import-2d-assets.md` |
| 3D asset intake (glTF/GLB, materials, LODs) | `workflows/import-3d-assets.md` |
| performance pass | `workflows/optimize-performance.md` |
| release/build/publish prep | `workflows/prepare-release.md` |

## Project Profiles (opt-in overlays, never defaults)

Load `project-profiles/<name>.md` **only** when the invocation names that
project. `riff-racers.md` is one optional profile (racing, karts, rewind,
split-screen); `*.example.md` files are templates. Racing/voxel/inventory
systems NEVER leak from profiles into unrelated projects.

## Binding Rules

- No stale or unverified APIs; alpha/beta features never presented as stable.
- GLES2/WebGL1 shaders are **opt-in** since 1.14.1 (`exclude_gles_sm100`).
- Import-time support (Draco/Meshopt) ≠ runtime capability. Say which is which.
- Fixed steps for gameplay physics; frame-rate independent motion; rewind
  needs real state capture, not backwards transforms.
- Performance claims only from measurements (`templates/performance-report.md`).
- Builds are "successful" only after a real exit-0 build + output check.
- `scripts/` are non-destructive; outputs collide → dated suffix.
- Existing project conventions beat this skill's preferences.

## Tools

- `scripts/validate_skill.py` — structure validator (this skill's own gate)
- `scripts/audit_defold_project.py` — read-only Defold project auditor
- `scripts/check_version.py` — version/channel gate vs official releases
- `scripts/gltf_preflight.py` — GLB/glTF import preflight (stdlib only)
- `scripts/bob_build.sh` — bob.jar wrapper, dry-run default
- `scripts/check_build.sh` — build-output verifier (never claims success blindly)
- `templates/performance-report.md`, `templates/import-checklist.md`

## Test

```bash
python3 skills/defold-development/tests/test_skill.py   # structure + routing + tools
```
