# Realistic 3D (4.7 baseline)

Photoreal-leaning projects. Load only when the style gate says realistic.

## Renderer first

Forward+ (desktop GPUs) or Mobile (mid-range/web-leaning); Compatibility
renderer caps you at GL-era feature set — realistic pipelines usually rule it
out. `references/3d-development.md` for the choice procedure.

## Material & light stack

- Full PBR: albedo/normal/roughness/metallic (+height, AO in ORM);
  verify texture-mode flags per 4.7 "Standard Material" docs.
- Environment: `WorldEnvironment` with a real HDRI/voxel-cone or SDFGI
  (Forward+, dynamic scenes); reflection probes for interiors; screen-space
  reflections cost — profile before enabling on targets.
- Shadows: directional shadow budget + ranged shadows for heroes;
  lightmap GI for static interiors + realtime lights for actors.
- Post: gentle glow, DOF, SSC, contrast — each is a fullscreen pass; keep 2–3.

## Performance reality (measure, never promise)

Realistic = highest GPU cost of the styles. Budget on the LOWEST target GPU
first: texture VRAM total, lights per tile, post passes. If iGPU-bound, drop
to Mobile renderer + baked GI before touching art.

## Gates

RUNTIME profiler on target hardware; VISUAL pass at target resolution;
memory report under platform cap (`references/performance.md` protocol).
