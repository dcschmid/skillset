# Shaders & materials (4.7 baseline)

## Shader languages & surfaces

- `gdShader` text files (`.gdshader`) + `.gdshaderinc` shared chunks — the
  default for authored, reviewable shaders.
- VisualShader — node graph, artist-tunable; same backends; prefer for
  variants someone non-coding retunes.
- Surfaces: `CanvasItem` (2D/UI), `Spatial`-style 3D via `ShaderMaterial`,
  particles (`ParticlesProcessMaterial` shader), sky, sound — verify exact
  per-type pages in 4.7 docs (class `Shader` docs index).

## Style-driven shader work

| Need | Technique |
|---|---|
| Toon ramp | quantized N·L banding (`shade_parameter_1d` or custom shader) |
| Outlines | hull pass or depth/normal post edge (stylized-rendering.md) |
| Pixelation in 3D | viewport → nearest downscaled texture, snap sampling |
| Palette swap | `PackedColorArray` uniform + indexed albedo |
| Water/grass motion | vertex offset in vertex shader w/ `TIME` |

## Cost discipline

Each material feature toggle = new shader variant (compile + memory); each
post-process = fullscreen pass; each custom shader on many objects = pipeline
switches. Prefer: few shared materials, uniforms over variants, `WorldEdge`
glow off on mobile targets.

## Web/mobile gates

Compatibility renderer GLSL differs from Vulkan SPIR-V path: verify feature
pages before assuming (e.g. instancing/SSMO support). `--rendering-method`
CLI lets CI run both paths.

## Verification

IMPORTED: shader compile errors surface at import/run. RUNTIME: shader
errors printed; VISUAL: reference comparison. Shader caching: first-run
compile spikes → warm up at load screens.
