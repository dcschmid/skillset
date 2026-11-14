# Tooling — modular, optional, probed

`scripts/tool_probe.py` checks presence+version+license on demand; missing
tools NEVER break the skill: each has an analysis-only fallback.

| Tool | Role | License | Fallback w/o it |
|---|---|---|---|
| Khronos glTF Validator | deep glTF spec check | Apache-2.0 | `gltf_validate.py` (stdlib, container+refs) |
| glTF Transform / gltfpack+meshoptimizer | edit/compress | MIT | report-only, no rewrite |
| KTX-Software (toktx/ktx) | KTX2/Basis | Apache-2.0 | recommend format, no encode |
| glslangValidator / SPIRV-Tools | GLSL/SPIR-V precheck | Apache-2.0 | dialect lint via skill review |
| Blender 5.3.0 bpy | export/bake/verify | GPL-2.0 | hand assets off pre-export |
| Pillow 12.x | pixel ops/metrics | MIT(C) | ImageMagick identify only |
| ImageMagick | format convert batch | Apache-like | Pillow |
| RenderDoc | GPU capture | MIT | estimate+label, never fake |

Integration gate per tool before use: version · maintenance · license ·
platform · deps · **engine-compat proven by import test, not by tool docs**.

This machine (probe with `tool_probe.py`, versions beat this list):
Blender 5.3.0, Godot 4.7.2, Pillow 12.3, ImageMagick, gltf-transform 4.5.1
(npm global), KTX-Software 4.4.2 `toktx/ktx/ktxinfo` (~/.local/opt,
symlinked ~/.local/bin), gltfpack (meshoptimizer 1.3), glslangValidator
16.6.0 — encode/inspect/precheck lanes LIVE. Not installed: Khronos glTF
Validator (spec-deep check still a pre-filter gap), RenderDoc (GUI capture).
Missing tool → named fallback, never a dead skill. Install policy: per-need,
version-pinned, user-approval; no bulk toolchains.
