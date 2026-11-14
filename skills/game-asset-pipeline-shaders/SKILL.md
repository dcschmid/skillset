---
name: game-asset-pipeline-shaders
description: >
  Technical game-asset pipeline for materials, textures, shaders, and
  import/export, engine-agnostic with Defold and Godot adapters (extensible to
  Unity, Unreal, Bevy, custom renderers, WebGL/WebGPU). Use for ANY asset
  pipeline task in ANY project or any asset-pipeline question: material and
  material-system audits (PBR metallic-roughness, unlit, flat, toon/cel,
  vertex-color, emissive, transparent, alpha-cutout, decal, terrain, water,
  glass, SSS, triplanar, stylized), texture pipeline and compression choices
  (PNG/JPEG/WebP/TGA/EXR/HDR/DDS/KTX2; Basis Universal ETC1S/UASTC, BC1-BC7,
  ASTC, ETC2), color-space correctness (sRGB vs linear data maps, normal-map
  conventions, alpha bleeding, seams), shader engineering and GLSL/Spatial/
  CanvasItem/fragment-cost audits, shader-variant explosion, glTF 2.0/GLB
  validation (KHR_draco, KHR_mesh_quantization, KHR_texture_basisu, EXT/KHR
  meshopt, EXT_mesh_gpu_instancing), Blender→engine export preflight (scale,
  transforms, UVs, normals, tangents, slots, skeletons, morphs), mesh/LOD and
  GPU/VRAM budgets, visual regression (pixel diff/SSIM), asset audit and safe
  auto-fix of existing projects, CI-ready headless asset gates. Art-style-aware
  rules (pixel-art/voxel/low-poly/hand-painted/toon/realistic/isometric/2D/
  2.5D/3D). Detects engine, engine version, art style, and installed tools from
  the project first; version-gated claims, unverified items marked, never
  invented; never mutates originals without dry-run plus backup.
---

# Game Asset Pipeline & Shaders (universal)

Engine baselines verified on this machine: **Defold 1.14.1 Stable**,
**Godot 4.7.2 stable (`ed1daf0b`)**, **Blender 5.3.0 (`02f0899d`, bundled
Python 3.13)**. Adapter concept extends to Unity/Unreal/Bevy/custom renderers;
claims about any engine are version-gated — read the docs or run the engine,
never assume. This skill owns the *technical pipeline* between asset creation
and engine runtime; it does not replace engine gameplay skills or Blender
modeling skills.

## Prime Directive

Before touching any asset: **read the actual project** — engine markers
(`game.project`, `project.godot`, `.uproject`, `Cargo.toml`), asset roots,
import settings, existing `asset-pipeline.yaml`, installed tool versions.
Engine-specific detail lives ONLY in adapters
(`references/engine-adapters.md`), never in shared pipeline logic. No claim of
engine compatibility ships unverified. No original asset is mutated without
dry-run + backup. A test that did not run is reported as not run.

## Ownership boundaries (do not duplicate other skills)

| Area | Owner |
|---|---|
| Modeling, geometry, rigging, asset design | `lowpoly-reference-to-blender` (Blender) |
| Engine gameplay, scenes, architecture, engine APIs | `defold-development`, `godot` |
| Cross-cutting gameplay/build/platform QA, CI harnesses | `ultimate-testing-qa` |
| Skill coordination, overlap detection | `skill-orchestrator` |
| **Materials, textures, shaders, glTF I/O, asset validation, asset GPU budgets** | **this skill** |

Hand off, never fork: asset creation → Blender skill; engine integration code
→ engine skill; this skill's scripts emit findings both can consume.

## Modes (every task)

Invoke by naming the skill and a mode; modes are skill behavior, not separate
slash commands shipped by the host.

| Mode | Does | Script entry |
|---|---|---|
| `audit` | whole-project asset inventory + findings | `scripts/asset_audit.py` |
| `validate` | single asset/group checks | `scripts/asset_validate.py` |
| `fix` | safe repairs, dry-run first | `scripts/pipeline_runner.py fix` |
| `optimize` | textures/meshes/materials budget passes | `scripts/pipeline_runner.py optimize` |
| `material` | material audit/create | `scripts/material_audit.py` |
| `textures` | texture analysis/compression plan | `scripts/texture_analyze.py` |
| `shader` | shader author/analyze/optimize | see `references/shaders.md` + engine docs |
| `export` | Blender→engine export preflight | `scripts/blender_preflight.py` (in Blender), `scripts/gltf_validate.py` |
| `benchmark` | size/VRAM/load estimates + measurements | `scripts/asset_report.py` |
| `compare` | original vs processed visual diff | `scripts/pipeline_runner.py compare` |

## Workflow (every task)

1. **Detect** — engine + version + art style + platform targets + installed
   tools. One line: `Engine: X vN · Style: Y · Targets: Z · Tools: ok/missing`.
   Read the project's `asset-pipeline.yaml` if present; else start from
   `assets/templates/asset-pipeline.yaml` and conservative defaults.
2. **Route** — load ONLY the matching references from the table below.
3. **Inventory** — run the mode's script read-only; scripts report
   `Critical/High/Medium/Low/Informational` findings with file, cause, fix,
   impact, validation status. Never report an unrun test as passed.
4. **Plan** — smallest coherent change set; separate measured from estimated.
5. **Apply** — dry-run → show risk → on approval, mutate copies only, keep
   `.orig` backups; pixel-art/voxel assets are NEVER lossy-resampled.
6. **Verify** — re-run the narrowest check that exercises the change; engine
   validation happens in the real engine (`godot --headless`, `bob.jar`),
   an external GLSL compile alone is NOT an engine test.
7. **Report** — before/after: file size, VRAM (estimated vs measured),
   vertices/triangles, draw calls if measurable, quality risk, findings left.

## Reference routing

| Task touches | Load |
|---|---|
| material types, audits, repairs | `references/materials.md` |
| texture types, formats, compression, color space | `references/textures.md` |
| shader authoring/analysis, GPU tiers | `references/shaders.md` |
| glTF/GLB, extensions, round-trip | `references/gltf-pipeline.md` |
| budgets, VRAM, draw calls, profiles | `references/optimization.md` |
| Blender export/preflight/baking | `references/blender-integration.md` |
| Defold specifics | `references/defold.md` (engine docs beat this file) |
| Godot specifics | `references/godot.md` (engine docs beat this file) |
| Unity/Unreal/Bevy/custom adapters | `references/engine-adapters.md` |
| quality gates, CI integration | `references/quality-gates.md` |
| tool probes, optional deps | `references/tooling.md` |
| failures, unknowns | `references/troubleshooting.md` |

## Hard rules (binding)

1. **Versions beat assumptions.** Installed engine/Blender versions win over
   docs and defaults; unverifiable → mark `UNVERIFIED`, verify, or gate.
2. **Estimates labeled `estimated`, never silently.** Measured values cite the
   command and environment that produced them.
3. **No style drift.** Optimizations preserve the art style; pixel-art keeps
   nearest filtering, no lossy resample, no mipmaps unless the project asks;
   style changes need an explicit reason and approval.
4. **Dry-run first.** `fix`/`optimize` always start read-only; applying keeps
   originals (`.orig` or VCS), reports risk per change, and re-validates.
5. **Engine truth is engine-side.** Import/render validation runs in the
   target engine; external validators are a pre-filter, not proof.
6. **Extensions are opt-in per engine+version.** Draco/meshopt are mesh-only;
   KTX2/Basis is texture-only; never mix the claims.
7. **Optional tools are optional.** Probed on this machine: toktx/ktxinfo
   4.4.2, gltfpack, gltf-transform, glslangValidator present → encode/inspect
   lanes live; missing elsewhere degrades to analysis-only with a named
   fallback, never a dead skill (`tool_probe.py` decides per run).
8. **Findings, not vibes.** Every report line: file · category · severity ·
   cause · fix · impact · validation status.
9. **Config, not constants.** Budgets and thresholds come from
   `asset-pipeline.yaml` (defaults + project overrides); no fixed per-game
   numbers in scripts.
10. **Unrun = unreported.** Visual tests without a render environment report
    `NOT_RUN` with the missing dependency, never a fake pass.

## Verification truth ladder (report using these levels)

| Level | Means | Proves |
|---|---|---|
| `STATIC` | script exit 0, glTF JSON parse, config parse | structure |
| `HEADLESS` | `godot --headless`, `blender -b`, `bob.jar` | engine ingests |
| `RENDER` | real render target + pixel diff/SSIM | looks right |
| `MEASURED` | profiler/CI log numbers | budget truth |

Static+headless without RENDER → report it; never upgrade a level silently.
