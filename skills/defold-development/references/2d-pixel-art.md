# 2D Pixel Art — Defold 1.14.1 baseline

Load when the project draws pixel art: sprites, tilemaps, fixed-resolution
cameras, or any "crisp pixels on modern displays" requirement. Pipeline-level
concerns (draw order, texture profiles) live in `2d-rendering.md`; mixed
2D/3D setups in `hybrid-2-5d.md`.

## Sprites and flipbook animation

- `.sprite` component + `.atlas` (see `/manuals/sprite-component/`,
  `/manuals/atlas/`). Animations live in the `.sprite` file; playback from
  Lua is `sprite.play_flipbook(url, hash("anim"), [opts_or_on_done])`
  (`/ref/sprite-lua`). Hash animation ids once at init.
- Atlas contents (images, embedded `.animation` clips) are assembled at
  **import time**; runtime you swap data (`atlas.set_animation` if you must,
  prefer separate atlases) — you cannot hot-load new art into a baked page
  without a rebuild of your own.
- Multiple atlases → more draw calls. One atlas per page-turn/character set;
  `max_size` per engine version in `game.project` `[graphics]` — read the
  project's limit before packing, don't guess 2048.

## Tilemaps

- `.tilemap` + `.tile_source` (`/manuals/tile-map/`). Tiles, per-tile
  animation frames, and per-tile flags are authored in the tile source;
  runtime edits via `tilemap.set_tile` / reads via `tilemap.get_tile` —
  verify exact tile-table fields in `/ref/tilemap-lua` before coding against
  them.
- Tile collision data is grid data the physics system understands for
  tile-based checks; for anything exotic (pixel-perfect terrain) read tiles
  in Lua and decide in your own code instead of fighting the collider.
- Tilemaps batch efficiently; prefer one tilemap layer per depth band over
  hundreds of sprites.

## Pixel-exact camera — the actual rules

Blurry pixel art is a bug list, not a taste issue. Checklist, in the order
you should audit it:

1. **Linear filtering.** Magnification must be nearest. Set on the texture
   profile / atlas import settings (`/manuals/texture-filtering/`):
   `min_filter`/`mag_filter` = nearest for all pixel sources. Mipmaps OFF for
   pixel atlases (mips average neighbors at distance).
2. **Subpixel camera drift.** Camera position must land on integer device
   pixels. `render.set_camera_transform` with a float camera from smooth
   follow = shimmering. Round in the render script: positions
   `math.floor(x + 0.5)` at the *world* level, before projection.
3. **Fractional zoom.** Scale = integer only (1, 2, 3...). Non-integer zoom
   resamples. If the design demands smooth zoom, accept blur or do it in
   discrete steps with a tween snapping to whole factors.
4. **Mixed resolutions.** Art at 16px inside a scene lit/shaded at screen
   res, labels drawn at screen res over 1x art — every raster stage must
   agree on the pixel grid. Pick one art unit (e.g. 1 texel = 1 world unit)
   and derive camera from it.

Camera specifics (`/manuals/camera/`): orthographic, integer projection
bounds; `camera.acquire()` cost is why you use one camera, snap it, never
acquire per frame.

## Retro resolution on modern displays

```
[display] width/height (game.project) = logical size (e.g. 480x270).
Render target sized in the render script; blit to window with nearest.
Integer window scale = target * N. Non-integer = letterbox or bleed; pick
the policy before writing the render script.
```

Aspect and size adaptation across devices: `/manuals/adapting-graphics-to-screen-size/`
— render script rebuilds projection on resize; verify current resize
callbacks in `/ref/render-script-lua` before relying on specific function
names.

## Collision for pixel art

Options, cheapest first:

| Shape of check | Mechanism | Cost |
|---|---|---|
| Grid/rect logic | read `tilemap` flags in Lua, no physics | near-free |
| Coarse bodies | `.collisionobject` + box2d shapes (`/manuals/physics-2d/`) | low |
| Art-accurate | polygon approximating silhouette, authored | low, manual |
| True pixel-perfect | sample alpha in your own Lua/C, no engine feature | yours |

There is **no built-in pixel-perfect 2D collision**. Approximate or
implement; don't promise per-pixel physics.

## Parallax, lights, particles

- Parallax: no built-in layers-with-speeds. Standard shape: move background
  GOs at `cam.pos * depth_factor`, snap to integer pixels after scaling or
  rule 2 above bites you mid-scroll. Depth bands + integer snap per band.
- 2D lighting: no dedicated 2D light system. Options: material shader
  sampling a light/normal texture (authored, import-time), additive
  sprites/particlefx for glows, or pre-baked lightmaps in the atlas. Budget
  shader work; don't fake it with dozens of additive sprites.
- Particles: `.particlefx` (`/manuals/particle-effects/`) with nearest-filter
  atlases, low fps emitters; sprite-sheet particle frames are import-time.

## Pixel-art UI

Labels/vector text renders at screen res, not art res — on 1x pixel art this
is the #1 "wrong" look. Use a bitmap-font-style texture in an atlas drawn as
sprites, or draw text into a target snapped to the grid. Vector fonts are
fine at HiDPI but note the format constraint from `version-compatibility.md`
(RGBA16F/R32UI, no GLES2/WebGL1 path). UI layering/sorting: `2d-rendering.md`
and `lua-engineering.md` for the Lua side.

## Audit before shipping a pixel build

- [ ] All pixel sources: nearest filter, no mips
- [ ] Camera and every parallax band snapped to integer pixels
- [ ] Zoom levels integer; resize policy chosen (letterbox vs bleed)
- [ ] One texel-to-pixel ratio documented per scene
- [ ] Text drawn on the grid (or explicitly exempted with reason)
