# game-asset-pipeline-shaders

Technical game-asset pipeline skill: materials, textures, shaders, glTF/GLB
import-export, asset validation, and asset-side GPU budgeting — engine-agnostic
with Defold + Godot adapters (adapter contract extends to Unity/Unreal/Bevy/
custom renderers, WebGL/WebGPU). Baselines probed on this machine: Blender
5.3.0, Godot 4.7.2 (`ed1daf0b`), Defold 1.14.1; versions always come from the
project, never from assumption.

Owns the pipeline between asset creation and engine runtime: audits, safe
repairs, optimization plans, budget reports. Modeling/rigging stays with
`lowpoly-reference-to-blender`, engine APIs with `defold-development`/`godot`,
cross-cutting QA with `ultimate-testing-qa`.

## Layout

```
SKILL.md                     router: modes, workflow, hard rules, truth ladder
references/                  depth loaded on demand (9 topic files + adapters)
scripts/                     8 stdlib-first Python tools + Blender in-engine gate
assets/templates/            asset-pipeline.yaml project-config template
examples/                    defold-pixelart.yaml, godot-pbr.yaml
tests/                       test_skill.py (exit 0 = PASS) + fixtures
```

## Modes

`audit · validate · fix · optimize · material · textures · shader · export ·
benchmark · compare` — declared modes are skill behavior invoked by naming
the skill; they are not host slash-commands. `fix` is dry-run unless
`--apply`; originals get `.orig` backups, protected globs are never touched.

## Scripts (all read-only unless noted)

| Script | Lane | Needs |
|---|---|---|
| `asset_audit.py` | whole-project inventory + findings | python3 |
| `gltf_validate.py` | glTF/GLB structure + refs | python3 |
| `texture_analyze.py` | kinds/color-space/disk-vs-VRAM | python3 (Pillow richer) |
| `material_audit.py` | material integrity, style-aware | python3 |
| `pipeline_runner.py` | mode dispatcher incl. `compare` | python3 (Pillow for compare) |
| `asset_report.py` | aggregate JSON+MD, CI gate | python3 |
| `tool_probe.py` | tool presence/version/license | python3 |
| `blender_preflight.py` | export gate | runs inside Blender |

## Verify

```bash
python3 skills/game-asset-pipeline-shaders/tests/test_skill.py
```

## Honesty contract

`STATIC → HEADLESS → RENDER → MEASURED`; a lane whose engine/tool was absent
reports `NOT_RUN` with the reason. VRAM math labeled `estimated`; profiler
numbers labeled by their tool. Estimates never presented as measurements,
unrun tests never green.

## Known limits

glTF lane ships container+reference checks plus the installed encode/inspect
tools (toktx/KTX-Software, gltfpack, gltf-transform, glslangValidator — probe
with `tool_probe.py`); spec-deep validation still wants the Khronos glTF
Validator (not installed, named fallback). Engine truth (HEADLESS/RENDER)
requires the engine invoked per project; the skill scripts cap at STATIC and
say so. `asset-pipeline.yaml` parses via PyYAML, else the bundled mini-parser
(subset: scalars/lists/nested maps, no anchors/multi-doc).
