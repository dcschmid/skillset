# Pixel art (universal pixel-style workflow, 4.7 baseline)

Style gate first: pixel art means NEAREST filtering, fixed base resolution,
integer scaling. Verify each claim against
https://docs.godotengine.org/en/4.7/tutorials/rendering/multiple_resolutions.html
and class pages before pinning into a project.

## Project settings (Project Settings > …)

| Setting | Value | Why |
|---|---|---|
| `rendering/textures/canvas_textures/default_texture_filter` | `Nearest` | global default for 2D |
| `display/window/size/viewport_width/height` | base res (e.g. 640×360, 320×180) | logical pixel grid |
| `display/window/stretch/mode` | `canvas_items` (+ `integer` scale optional) | crisp upscale, UI + 2D |
| `display/window/handheld/orientation` etc. per platform | — | mobile targets |
| `rendering/2d/snap/snap_2d_transforms_to_pixel` | true when shimmering | transform snap |
| `rendering/2d/snap/snap_2d_vertices_to_pixel` | cautiously | can warp rotated sprites |

Per-texture override wins: import dropdown Filter = Nearest for anything
mixed-style. `.import` defaults: no mipmaps for 2D pixel sources.

## Camera & motion

- `Camera2D.position_smoothing_enabled` + `pixel_snap` options; snap camera to
  grid step or round final position — subpixel camera = shimmering tiles.
- Parallax: `Parallax2D` (repeat wraps) with layer speeds as integer-ish
  ratios at the base resolution; scroll offsets rounded.
- Velocity math at base res; no fractional per-frame positions on screen space.

## Content pipeline

- Sources: Aseprite/Libresprite/GIMP/Krita → PNG (lossless, alpha).
- Sheets: fixed cell grid → `SpriteFrames` (AnimatedSprite2D) or atlas +
  `AtlasTexture`; keep sheet dims multiples of cell size.
- TileSets: `TileMapLayer` nodes (4.3+; one node per layer, independent
  scroll/visibility); TileSet resource = physics/materials/collection
  per-tile; terrain sets for autotiling.
- Palettes: `PackedColorArray`/palette `.tres`; constrained palettes are a
  content convention the engine does not enforce — lint on import if needed.
- Dithering/AA: author in the art tool or a CanvasItem shader; no engine AA
  over nearest.

## 2D lighting & effects without breaking the look

`PointLight2D`/`DirectionalLight2D` + `CanvasModulate`; light textures =
low-res nearest sources; `OccluderPolygon2D` shadows keep hard edges.
Post FX via `WorldEnvironment`/shaders on CanvasLayer with nearest-safe
sampling — pixelation shader for 3D-in-pixel projects
(`references/2-5d-development.md`).

## Verification gates

1. STATIC: audit filter/stretch settings present in `project.godot`.
2. IMPORTED: `--headless --import` clean.
3. RUNTIME: run at base res and 2×/3× — no mixed filter, no shimmering while
   scrolling/standing.
4. VISUAL: screenshot at target scale; grid test pattern aligns.

## Hybrid rules

3D geometry wearing pixel clothing: texture Filter Nearest + no mipmaps +
scaled viewport or `--fixed-fps`-tested 3D viewport scale
(`references/2-5d-development.md`). UI bitmap fonts: nearest, no mipmaps,
`msdf` avoided for true pixel fonts (verify per version docs).
