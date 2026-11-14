# Low-poly 3D (4.7 baseline)

Stylized minimal-geometry 3D. Not a default for "3D project" — a chosen style;
load only when the detected style matches.

## Look targets

- Faceted flat shading: `StandardMaterial3D` `flat_shading = true` (per-material
  inspector toggle `render_mode` equivalent), or per-face normals authored.
- Flat colors / small palettes: vertex colors or 1–2 shared atlas materials
  across many props; instance `MultiMeshInstance3D` for repeated props.
- Soft baked-feel lighting: `DirectionalLight3D` + `WorldEnvironment`
  (Glow off unless wanted; `sky` simple gradient); no SSAO/HDR-heavy stack on
  iGPU targets.

## Asset budget (typical starting points — measure, don't trust)

- Props: 100–1k tris; characters: 1–5k; one 512²–1k atlas per hero prop.
- Materials per scene: single digits; LOD via `VisibleOnScreen` range or
  `GeometryInstance3D` LOD path for dense sets.

## Pipeline

Import GLB (Blender or the lowpoly-reference-to-blender skill deliverables —
+Z up, +Y facing, 1 BU = 1 m repo convention). `ImportLibrary`/`.import`
settings: `generate_lods` off by default, compress on; verify names after
import. Collision: primitive shapes or simplified convex, never render mesh.

## Renderer note

Works on Forward+ and Mobile; on Compatibility keep to GL-friendly shaders
(`references/3d-development.md`, `references/shaders.md`).
