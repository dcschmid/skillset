# 2D Rendering Pipeline — Defold 1.14.1 baseline

Load for pipeline-level 2D work: draw order, render scripts, texture
import settings, batching, screen adaptation. Pixel-art crispness rules are
in `2d-pixel-art.md`; Lua patterns in `lua-engineering.md`.

## Custom render scripts

Boot: `[bootstrap]` in `game.project` names the default; projects doing
anything beyond stock 2D replace it (`/manuals/render-scripts/`).
`render.set_render_script("my.render_script")` swaps at runtime; script is
compiled **load-time**, Lua logic inside is runtime.

Lifecycle (verify exact names against `/ref/render-script-lua` before
writing — this is the shape, not a substitute for the ref page):

```lua
function init(self)      -- builds render predicates, targets
function update(self, dt)-- draw loop: clear, set_camera, draw
function pred_draw(self, function_name, context) -- per-predicate pass
```

- You own the camera transform (`render.set_camera_transform(m)`) and the
  projection (`render.set_projection(p)`, rebuild on resize).
- Render predicates filter by material tag; your materials declare
  `tags {}` in `.material`. This is the layering mechanism — not z.

## Draw order / layering

Defold 2D sorts, it doesn't depth-test by default:

1. Predicate tags split groups first (sprites before labels before GUI).
2. Within a batch: `z_ratio`/material order, then **embedding order**
   (script/component order in the GO and creation order at runtime).
3. `go.set_update_frequency`, component sort order, and render script
   predicate iteration are your knobs.

Deterministic rule for the project: assign each band a tag or an integer
`z` in one module; two systems choosing depth ad hoc is the classic 2D
artifact source.

## Texture filtering modes

Per-source, import-time (`/manuals/texture-filtering/`, texture profiles in
`game.project` `[texture]`):

| Setting | Values | 2D note |
|---|---|---|
| `min_filter`/`mag_filter` | nearest / linear | pixel art = nearest |
| `mip_filter` | on/off | off for atlases & UI |
| wrap | clamp/repeat | tilemaps & shaders: repeat |

Post-import you change filtering only via `resource`/texture profile swap —
plan per-project, not per-frame.

## Compression profiles

Import-time again: profiles in `game.project`; per-engine caps listed in
`version-compatibility.md`. Practical rule: lossy block compression is for
large photographic atlases; nearest-filtered pixel atlases want lossless or
uncompressed (DXT/ETC ringing kills pixel edges). KTX2 applies to
gltf/glb-imported textures (import-time only). Verify enum names in the
current docs; they moved once.

## Batching reality

| Source | Batch behavior |
|---|---|
| sprite + shared atlas + shared material | batches |
| tilemap + tile_source | batches internally per layer |
| mesh component (`/ref/mesh-lua`, `/manuals/meshes/`) | one draw, CPU-updated verts — cheap for deformation, budget vertex count |
| label | batches by font/material |
| cross-atlas or cross-material neighbors | break the batch |

Diagnose with the engine profiler and `render_stats` before restructuring
anything.

## Screen-size adaptation

Strategies, pick per project and document in one place
(`/manuals/adapting-graphics-to-screen-size/`):

- **Fixed logical size + letterbox** (retro/pixel games) — snap rules in
  `2d-pixel-art.md`.
- **Stretch projection** (render script recomputes ortho bounds from
  window aspect) — content-safe for flow-field UI.
- **Fixed width / expanding height** — HUD anchored in GUI (`/manuals/gui/`),
  world extends.

GUI (`.gui` files) uses its own fit modes; don't mix GUI fit with render
script projection math, you'll fight two systems.

## Artifacts → fixes

| Artifact | Cause | Fix |
|---|---|---|
| Sprites pop over labels | embedding order ties | tag predicate or explicit order |
| Flicker between two overlapping sprites | unstable sort tie | unique z/order per object |
| Blurry scaled art | linear filter, mips | nearest, mips off (`2d-pixel-art.md`) |
| Seams in tiled shader look | clamp vs repeat, half-texel | repeat + integer UV math |
| Frame hitch on scene load | atlas bake at load | preload via proxy (see architecture.md) |
| HiDPI labels crisp, world blurry | mixed resolutions | one pixel grid |

## Checklist

- [ ] One render script owns camera/projection/predicates
- [ ] Layering rule stated in one module (tags or z bands)
- [ ] Filtering/compression decided per asset class, at import
- [ ] Resize policy chosen; GUI and world don't fight over aspect
- [ ] Profiler output (batch count, draw calls) recorded, not guessed
