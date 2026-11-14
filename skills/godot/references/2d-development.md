# 2D projects (4.7 baseline)

Pure-2D architecture and rendering. Styles (pixel etc.) add their own refs.

## Nodes & pipeline

- `Node2D`/`Control` tree; z-index/y-sort for depth; `CanvasLayer` for HUD.
- Rendering is the Compatibility/OpenGL path on web/mobile — shader and
  texture-feature differences from 3D renderer (verify per platform docs).
- Batch discipline: same texture + same material = batched draws; mix texture
  atlases per scene; `CanvasItem` `show_behind_parent`, `z_index` over
  reparenting.
- `TileMapLayer` nodes for tiles; `AnimatedSprite2D`/`SpriteFrames` for flips;
  `GPUParticles2D`/`CPUParticles2D` pick per platform (web: test).
- Lights: `PointLight2D`/`DirectionalLight2D` + normals are available but
  cost extra passes; `CanvasModulate` for global mood.

## Physics & motion

`CharacterBody2D`/`RigidBody2D`/`Area2D`; collision layers bitmask planned in
project settings early (1–32 slots, name them). Fixed `physics_ticks_per_second`
before prototyping physics-heavy mechanics.

## Cameras

`Camera2D` (limit, smoothing, drag margins); multiple cameras per screen via
`SubViewport`/split-screen = viewport rects; `CanvasLayer` for fixed UI.

## Resolution & scaling

Even non-pixel 2D: pick base resolution + stretch mode deliberately
(`canvas_items` most common); author vector (`TextureRect` `STRETCH_KEEP_ASPECT_CENTERED`)
content to survive aspect range; ultrawide = background bleed plan.

## Mobile/web notes

Touch = emulate-mouse or raw `InputEventScreenTouch`; portrait/landscape
relayout via anchors; texture compression per platform (verify importer).
