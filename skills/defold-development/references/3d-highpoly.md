# Detailed / High-Poly 3D + PBR — Defold 1.14.1 baseline

Load when the project wants realistic or high-fidelity 3D: detailed meshes,
PBR materials, normal maps, rigged characters. State support levels honestly
— Defold ships a **solid but bounded** metallic/roughness PBR, not a
full modern engine renderer.

## PBR support level (honest ledger)

https://defold.com/manuals/physically-based-rendering/ (checked 2026-11-13):

| Area | Status |
|---|---|
| Metallic/roughness, base color, vertex color | Built-in (`gltf.*` materials, `gltf.fp`) |
| Normal maps | Built-in **when tangent data is available** in the mesh |
| Occlusion, emissive (+ emissive strength) | Built-in |
| sRGB decode/encode round-trip | Built-in (base color/emissive sRGB; MR/normal/occlusion linear) |
| Unlit, masked alpha, double-sided normals | Built-in (blending + culling state is yours in the render script) |
| Specular/glossiness, clearcoat, transmission, sheen, iridescence, IOR, volume | **Parameters are imported; built-in shaders do NOT render them** — custom shading required |
| Environment/IBL lighting, realtime shadows, cascades | **Not built-in** — ambient is an approximation; custom shading / custom render pipeline required |

Sampler names for custom materials: `PbrMaterial_baseColorTexture`,
`..._metallicRoughnessTexture`, `..._normalTexture`, `..._occlusionTexture`,
`..._emissiveTexture` (PBR manual). Custom shaders: copy the built-in
`.material` + `gltf.fp`, keep sampler names and Local vertex space, and
replace `gltf_sampling.glsl` / `gltf_lighting.glsl` outputs to plug in your
own BRDF/IBL. Omit-unused-members rule applies to the `PbrMaterial` block.

## Lighting & shadow reality

- Light types: ambient, directional, point, spot; **`light.max_count`
  default 64** total Light components (ambient included); directional/point/
  spot consume `lights[]` slots while active; over-limit = component-buffer
  error (/manuals/light/, 2026-11-13). No documented per-draw lit-light
  cap beyond this — measure shader cost of looping many `lights[]` entries.
- **No shadow system is documented.** No cascades, no baked lightmaps, no
  SSAO built-in. Extensions: depth-prepass + shadow map in a custom render
  script (/manuals/render/), or fake it (blob shadows, projected decals) —
  both are project code, not engine features.
- Double-sided: disable face culling in the pass or back faces never reach
  the shader (PBR manual, built-in shader behavior).

## Tangents, normals, UVs

- Normal maps need tangents in the imported mesh; export tangents from the
  DCC tool or provide them in glTF — otherwise built-in normal mapping is
  inactive (PBR manual: "when tangent data is available"). Verify what the
  1.14.1 importer does with missing tangents before relying on auto-gen
  (UNVERIFIED).
- Custom-shader vertex attributes listed for Model in /manuals/shader/:
  `position`, `texcoord0`, `normal`; add `tangent`/`color` only after
  checking /ref for the pinned version (UNVERIFIED in the manual excerpt).
- UVs: unwrap in the DCC tool; lightmap/texture overlap discipline is a
  DCC-side concern. Defold preserves imported transforms; no re-centering
  (/manuals/importing-models/).

## Rigging/animation budgets

- Baked skeletal animation only (matrices per bone per key; linear
  interpolation; prebake fancy curves) — /manuals/importing-models/ and
  /manuals/model-animation/ (2026-11-13).
- GPU skinning via Local-space materials uses an `RGBA32F` bone-matrix
  cache texture; GLES2/WebGL1 needs the float-texture extension, else fall
  back to world-space CPU skinning (no instancing) — /manuals/model/.
  Cache dimensions: `/manuals/project-settings/#model`.
- Starting budgets (measure, not engine constants): bones ≤ 60 mobile /
  ≤ 100 desktop per skinned mesh; skinned meshes on screen ≤ 10 low-end
  mobile; anim set files split per character to bound memory.

## Mesh pipeline & compression

- Draco (`KHR_draco_mesh_compression`), Meshopt (`EXT_meshopt_compression`,
  `KHR_meshopt_compression`) — **decode at import/build only**; the runtime
  uses normal geometry; smaller source ≠ smaller bundle
  (/manuals/importing-models/, 2026-11-13). Use them for repo/transfer
  size, not runtime memory.
- Decimate/remesh in the DCC tool; the runtime has no LOD system documented
  for 1.14.1 — swap glTF scenes per distance yourself (manual detail
  levels, one Model per LOD, or one scene with named meshes).

## Texture formats & memory

- `.ktx2` in `.gltf`/`.glb` (external or embedded): **import-time** since
  1.14.1. Texture profiles decide output: `keep_ktx2_format: true` keeps
  ETC1S→ETC1S, UASTC→UASTC, BC7→BC7 (bypasses platform Formats when
  compression enabled); default decodes+re-encodes via profile
  Format/Compressor; no match/compression off → uncompressed output
  (/manuals/texture-profiles/#ktx2-source-textures, 2026-11-13). Double
  loss on re-compressing already-lossy sources — check targets.
- Build-time compressors: Basis Universal and ASTC; compression is
  **build-time**, textures load uncompressed-to-API format at runtime;
  compressing many textures = very long builds (/manuals/texture-profiles/).

## Budgets per platform class — starting points to measure

Not engine constants. Validate on the weakest device with /manuals/profiling
and /manuals/optimization-memory / -speed.

| | HTML5/WebGL1 | Mobile low | Mobile flag | Desktop |
|---|---|---|---|---|
| Tris drawn | ≤ 150k | 200–400k | 0.5–1M | 2–5M |
| Draw calls | ≤ 100 | 150–300 | 300–600 | 1000+ verify |
| Tex VRAM | 64–128 MB | 128–256 MB | 256–512 MB | 1–2 GB |
| Skinned meshes | 2–4 | 4–8 | 8–16 | 32+ |
| Active lights (shaded) | 2–4 | 4–8 | 8–16 | 16+ (cap 64 comps) |

GLES2/WebGL1 ceiling reminders (1.14.1): shaders excluded by default
(`[shader] exclude_gles_sm100`, opt back with `exclude_gles_sm100 = 0`);
float-texture-dependent features (vector fonts RGBA16F/R32UI, RGBA32F skin
cache) depend on adapter extensions. Desktop/GL3 can compile things mobile
rejects — test mobile targets early (/manuals/shader/).

## Failure modes

- "PBR asset looks flat" → check tangents present, linear vs sRGB flags on
  maps, and that the render script draws the `model` tag predicate.
- Clearcoat/glass "broken" → parameters import but `gltf.fp` doesn't render
  them; custom shading or accept the ceiling.
- Huge builds → texture compression pass; profile per-platform or disable
  compression for iteration builds.
