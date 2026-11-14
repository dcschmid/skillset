# Stylized / cartoon / hand-painted (4.7 baseline)

Cel/toon/anime/hand-painted looks. Load only when the style gate matches.

## Shading approaches (verify each page in 4.7 docs before shipping)

- **Cheap toon**: `BaseMaterial3D`/`ShaderMaterial` — quantized ramp lighting
  via a custom `shade_parameter` 1D gradient texture on `StandardMaterial3D`
  (`use_1d_sampler` + `shade_parameter_1d`), or a small Spatial/CanvasItem
  shader (toon ramp = `smoothstep` bands on NdotL).
- **Outlines**: inverted-hull second pass (flipped normals, solid color) for
  characters; post-process depth/normal edge shader for scenes; per-style
  pick — hull cost = +1 draw per outlined mesh.
- **Hand-painted**: albedo carries lighting intent (pre-shaded textures);
  keep engine lights low-contrast to preserve paint; `vertex_light_mode`/
  bake OFF where paint already implies shadow.
- **NPR lighting**: `WorldEnvironment` low ambient, few real lights; disable
  photometric bloom/DOF stacks that fight flat aesthetics.

## Implementation notes

- Custom `ShaderMaterial` with shared `.gdshaderinc` palette so all props
  restyle from one file; VisualShader for artist-tunable variants.
- 2D side: `CanvasItem` shaders + `CanvasItem` `material` on nodes; palette
  swap via shader uniforms (`PackedColorArray`).
- Animation: stepped/held frames (spaced-key feel) — `Animation` playback
  with discrete tracks or `AnimationTree` at reduced tick rate for anime feel.

## Gates

VISUAL review is the gate (style is subjective): side-by-side with reference;
outline weight consistent across camera distances; palette swaps verified per
material instance. `references/shaders.md` for shader mechanics.
