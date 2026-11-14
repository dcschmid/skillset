# Shaders & Materials — Defold 1.14.1 baseline

Load when writing `.vp`/`.fp`/`.material` files, post-effects, custom
render scripts, or platform-conditional rendering. GLSL details are per
the Shader manual (https://defold.com/manuals/shader/, checked 2026-11-13).

## Language & backend ground rules

- Shader programs are GLSL. Baseline spec: **OpenGL ES 2.0 / GLES SL**
  (Khronos registry linked from /manuals/shader/). Desktop drivers compile
  newer features happily and **then fail on mobile** — author to ES 2.0
  unless every target is known-good.
- 1.14.1: GLES2/WebGL1 shader variants **excluded by default**
  (`[shader] exclude_gles_sm100`); set `exclude_gles_sm100 = 0` to ship
  WebGL1/GLES2 (HTML5 `webgl_version_hint = 1` needs it too). Vector fonts,
  RGBA32F skin cache etc. require float-texture formats GLES2 lacks.
- Backends: desktop OpenGL; Android GLES; HTML5 WebGL1/2 via hint;
  iOS/Android/HTML5 use the engine-native platform layer since 1.14.1
  (GLFW2 removed; GLFW3 remains on desktop). Per-platform ceilings: read
  the platform manual (/manuals/html5/, /manuals/android/, /manuals/ios/)
  — do not assume Metal/Vulkan from memory (UNVERIFIED here).
- Compute programs exist (/manuals/compute/); platform availability is not
  uniform — verify per target before designing around them.

## Shader contract essentials

- Vertex: `attribute`/`in` inputs = **component-provided**, declared in the
  shader; per-component sets (/manuals/shader/): Sprite/Tilegrid
  `position,texcoord0`; GUI/ParticleFX add `color`; Model
  `position,texcoord0,normal`. You get what the component sends — no
  arbitrary attributes without buffer components.
- Varyings: prefix `var_` recommended; `out` in `.vp`, `in` in `.fp`.
- Sprites/GUI/particles/tilemaps bind their image to the **first declared
  `sampler2D`**; extra samplers need material-file sampler entries and, if
  the component has no slot, `render.enable_texture()` from the render
  script (/manuals/material/).
- Model samplers must be declared in the material (name + wrap/filter);
  the editor then exposes texture fields. Max **16 textures/draw**
  (`texture0-15`), lower on tiny sampler-limit adapters (/manuals/model/).
- Material = shader pair + samplers + constants + **tags** (bitmask for
  `render.predicate()`; **max 32 tags/project**). Sprite supports multiple
  textures (multi-textured sprites, /manuals/sprite/).

## 2D vs 3D materials

| Need | Route |
|---|---|
| Sprites/tilemaps/GUI | tiny `.fp` on auto-bound sampler; constants via `go.set`/`gui` |
| 3D unlit/stylized | copy built-in `model*.material` variants (Local vs World space!) |
| 3D PBR | copy `gltf*.material`, keep `gltf_sampling.glsl`/`gltf_lighting.glsl` interfaces |
| Screen effects | render target + fullscreen draw in render script |

## Toon shading recipe (custom .fp sketch)

Lights are data; you shade them (pattern from /manuals/light/):

```glsl
// fragment loop sketch — lights[i].params: x=type(0 dir,1 point,2 spot)
for (int i = 0; i < active_light_count; i++) {
    if (i >= MAX_LIGHT_COUNT) break;
    vec3 L = light_dir(i, v_position);          // normalize(-lights[i].direction_range.xyz) for dir
    float ndl = max(dot(v_normal, L), 0.0);
    float band = ndl < 0.4 ? 0.4 : (ndl < 0.75 ? 0.7 : 1.0);  // steps = the "toon"
    result += lights[i].color.rgb * lights[i].params.y * band;
}
```
`MAX_LIGHT_COUNT` = project light cap (`light.max_count`, default 64 —
/manuals/light/); loop only what the scene shades. Attenuation/range and
spot cones come from `position`/`direction_range.w`/`params.zw`.

## Screen-space & post-effects

Documented pattern (/manuals/render/, checked 2026-11-13):

```lua
render.set_render_target(self.rt)      -- draw scene low-res or normal
render.draw(self.scene_predicate)
render.set_render_target(render.RENDER_TARGET_DEFAULT)
render.enable_texture(0, self.rt, graphics.BUFFER_TYPE_COLOR0_BIT)
render.draw(self.post_predicate)       -- fullscreen quad, samples COLOR0
render.disable_material()              -- + matching disable_texture
```

- **Pixelation/retro**: create the RT at 1/N resolution, sample with
  nearest filtering in the `.fp` (or rely on RT filter settings), then
  draw upscaled. Palettes/dither are pure fragment math on the sample.
- **Color grading**: LUT texture + fullscreen pass — official route is the
  Grading tutorial (linked from /manuals/shader/ "Further study").
- Predicates: `render.predicate({"tag"})`, AND-semantics on multiple tags;
  draw order = your `render.draw` order; frustum culling available per
  predicate (/manuals/render/).

## Custom render pipeline

`.render` resource points to a Lua render script (`init/update`, predicates
created in `init` — example in /manuals/render/). You own: clear color,
camera/projection, RT setup, blend/depth state between draws, material
overrides (`render.enable_material`), texture binds. That is also the
insertion point for shadow passes, outlines, and HDR (write linear to the
RT, convert to sRGB in the final pass — PBR manual note).

## Shader-driven animation & particles

- ParticleFX: component animates CPU-side; material gets
  `position,texcoord0,color`; first sampler = particle image. Motion in
  the shader = time constants + vertex displacement; keep it stateless.
- Model "shader animation": drive `cursor` with `go.animate` (documented
  in /manuals/model-animation/), tween material constants with `go.set`
  on hashed names; per-frame string keys/concat are forbidden in hot paths.

## Honest ceilings

No deferred pipeline shipped; no compute-on-mobile guarantee; no
automatic shader fallback — if GLES2 support matters, author ES2-safe GLSL
and re-enable `exclude_gles_sm100`. Anything beyond metal/rough+maps is
custom code on your pipeline, not a toggle.
