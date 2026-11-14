# Stylized / Low-Poly 3D — Defold 1.14.1 baseline

Load when the project uses 3D models with a stylized, low-poly, or
flat-shaded look. For PBR-heavy assets see `3d-highpoly.md`; for the
authoring-tool side see `asset-pipelines.md`.

## The one true import path

glTF 2.0 only: `.gltf` (JSON + `.bin` + images) or `.glb` (single binary).
FBX/OBJ must be converted to glTF by your DCC tool — Defold does not import
them. https://defold.com/manuals/importing-models/ (checked 2026-11-13)

- Defold **preserves imported transforms** and does not re-center models.
  Old-model reimport drift is fixed in the DCC tool, then re-exported.
- Model component (`/manuals/model/`): `Scene` = the glTF file; `Mesh` =
  optional single named mesh (drops node transforms — you place it yourself);
  `Skeleton` = glTF with bones; `Animations` = Animation Set resource.
- Morph targets import with the scene and can be read/overridden via
  `model.get_blend_weights()` / `model.set_blend_weights()`
  (/ref/model — checked against 1.14.1).

## Flat shading and vertex colors

- Flat/faceted look = **authored normals in the DCC tool** (Blender: shade
  flat + auto-smooth before export). Defold has no "flat shading" toggle;
  the shader consumes the imported `normal` attribute.
- Built-in glTF shaders use **base color + vertex color** (PBR manual,
  built-in shader behavior — https://defold.com/manuals/physically-based-rendering/).
  Custom-shader attribute list for Model shows `position`, `texcoord0`,
  `normal` in /manuals/shader/; confirm `color` in /ref for the pinned
  version before depending on it in a custom `.vp` (UNVERIFIED).
- Vertex-color-only low-poly needs **no textures** — cheapest 3D path
  that still lights correctly with the built-in `model`/`gltf` materials.

## Lighting you can actually promise

Facts from https://defold.com/manuals/light/ (checked 2026-11-13):

- Four light resources: ambient, directional, point, spot.
- `light.max_count` project setting caps total Light components; **default
  64**. Exceeding it = full-component-buffer error. Ambient lights count
  toward `max_count` but do not consume `lights[]` shader slots; directional/
  point/spot consume slots while active.
- Lights are **data, not automatic shading**: shaders read the light buffer
  and decide usage. Built-in `gltf.*` materials do direct dir/point/spot +
  simple ambient; **no built-in shadows, no environment lighting**
  (/manuals/physically-based-rendering/, built-in shader behavior). Do not
  promise cascades, baked lightmaps, or realtime GI — not documented;
  extension/custom-pipeline work.
- Stylized-friendly: a toon ramp in a custom `.fp` looping `lights[]` is
  standard practice (pattern shown in /manuals/light/ example).

## Materials for low-poly (from /manuals/model/, checked 2026-11-13)

| Model type | General shading | glTF PBR |
|---|---|---|
| Static | `model.material` | `gltf.material` |
| Static instanced | `model_instanced.material` | `gltf_instanced.material` |
| Skinned | `model_skinned.material` | `gltf_skinned.material` |
| Skinned instanced | `model_skinned_instanced.material` | `gltf_skinned_instanced.material` |

- Built-ins use **Local vertex space**; required for instancing and GPU
  skinning. GPU skinning bone cache is an `RGBA32F` texture — on GLES2/
  WebGL1 it needs the adapter float-texture extension; fallback = custom
  **world-space material (CPU skinning, no instancing)**
  (/manuals/model/#material).
- Textures per draw: **max 16** (`texture0`–`texture15`), usable count can
  be lower on small sampler-limit adapters (/manuals/model/, 2026-11-13).

## Animation (characters/props)

https://defold.com/manuals/model-animation/ (checked 2026-11-13):

- **Baked skeletal only**: matrices per bone per keyframe — exporters must
  bake; non-linear curves must be pre-baked to linear.
- One animation playing per model component at a time; skeletal + morph can
  combine only via `model.set_blend_weights()` overrides, not two
  `play_anim` calls.
- `model.play_anim("#model", "wiggle", go.PLAYBACK_LOOP_PINGPONG)`;
  `cursor` property tweenable with `go.animate`; bones are internal GOs,
  reachable with `model.get_go("#model", "Bone_002")`.

## Geometry + batching discipline

- Low-poly is a style and a budget: kit-kit pieces (walls, props, foliage)
  authored on a shared grid, snap-placed, instanced where static and
  same-material.
- Instanced materials require Local vertex space (above). Same material +
  same texture = the batching lever; material count and texture swaps are
  the cost to watch, not raw vertex count, on iGPU targets
  (/manuals/optimization-speed/).
- Merge static kit pieces per material when the style allows; split only
  when culling or instancing needs differ.

## iGPU starting budgets — measure, don't trust

Starting points to validate with profiling on the weakest target device
(/manuals/profiling/, /manuals/optimization-speed/); **not engine
constants**:

| Class | Tris on screen | Draw calls | Tex mem | Notes |
|---|---|---|---|---|
| HTML5/WebGL1 | 100–250k | 50–150 | 64–128 MB | RGBA32F skin risk |
| Mobile low-end | 150–400k | 80–200 | 96–192 MB | ETC/ASTC via profiles |
| Desktop iGPU | 500k–1M | 200–400 | 256 MB | verify after |

## Blender export checklist (→ /manuals/importing-models/)

- `File ▸ Export ▸ glTF 2.0 (.glb/.gltf)`; *Selected Objects* on; `.glb`
  for single kit props, `.gltf+bin+textures` when editing textures in-project.
- Shade flat/auto-smooth before export; UV-unwrap textured meshes.
- Animation: enable export **and bake** (matrices per keyframe).
- Up-axis: glTF is Y-up; Blender's exporter default (+Y up, `export_yup`)
  matches. Defold preserves imported transforms — engine-space handedness
  is not stated on the import page; **verify at /manuals/gltf/ /
  /manuals/building-blocks/ against the pinned version** rather than
  assuming left- or right-handed.
- Optional generator: the `lowpoly-reference-to-blender` skill can produce
  the source asset; it is not a Defold dependency.

## Failure modes

- Z-fighting/placement drift after reimport → transforms changed in DCC;
  re-export (documented remedy, /manuals/importing-models/).
- Animated model invisible on WebGL1 → RGBA32F skin cache unsupported;
  switch to world-space material or drop GLES2 target.
- "Lights do nothing" → material doesn't read the light buffer; lights are
  opt-in in shader code (/manuals/light/).
