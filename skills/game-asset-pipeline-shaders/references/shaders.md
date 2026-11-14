# Shaders — authoring, analysis, GPU tiers

Authoring dialect per engine is adapter data; here: engine-agnostic GLSL/
shader-graph hygiene plus validation truth.

## Validation ladder (no shortcuts)

1. `STATIC`: dialect parses (`glslangValidator` if installed — pre-filter only)
2. `HEADLESS`: engine import/compile (`godot --headless --import`; Defold
   engine build) — required for "compiles" claims
3. `RENDER`: on-target backend screenshot + compare — required for "works"

An external GLSL compile with green exit is level STATIC→, never RENDER.

## Cost audit checklist

- texture samples per pixel: count; each mask sampled separately is a
  channel-packing candidate (`textures.md`)
- branches: uniform branches fine, varying branches on mobile = divergence;
  prefer `mix`/`step`
- precision: `mediump` defaults on mobile; explicit lowp for masks/colors
- variant explosion: keywords × lightmodes × blend — enumerate and prune to
  what scenes use; report variant count before/after
- overdraw: transparent layers stacked; alpha-tested in transparent pass
- redundant work: per-pixel light loop where per-object/vertex suffices
- derivatives (`dFdx`) in conditionals → undefined on some GLES

## GPU tier targets (profiles, not constants)

| Tier | Budget/px | Notes |
|---|---|---|
| integrated | low | no compute dependence |
| mobile | lowest | mediump, ETC2/ASTC, few samples |
| old desktop | low-mid | no ASTC/BC7 if GL2/3 |
| modern desktop | high | BC7/compute fine |
| web | lowest + parse size | WebGL2 GLSL ES 3.0; WebGPU if engine ships it |

Tier budgets come from `asset-pipeline.yaml` `shader_profiles`, never invented
per game.

## Style-shader notes

toon/cel ramp bands · dissolve = masked fade w/ edge, sort order ·
outline = normal-extrude or post (choose one; report cost) · rim = dot(N,V)
term — all authored in the engine's dialect; Blender node trees are NOT
portable source (bake/replace per `blender-integration.md`).
