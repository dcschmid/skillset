# Hybrid 2.5D — Defold 1.14.1 baseline

Load when 2D and 3D share a screen: sprites in 3D worlds, 3D over painted
backdrops, isometric, billboards, mixed pixel/voxel/3D art. Depth-crispness
rules: `2d-pixel-art.md`; pipeline: `2d-rendering.md`.

## The four shapes (pick one, document it)

| Shape | Engine support | Notes |
|---|---|---|
| 2D sprites/characters in a 3D world | native | sprite components live in 3D; orientation is yours |
| 3D characters over 2D/painted backgrounds | native | background = textured quad near camera plane or a separate predicate pass |
| Isometric (2.5D look, 2D logic) | native | ortho camera at 30°/45° or pure-2D with iso-sorted sprites — don't pay 3D for a 2D game |
| Ortho 3D scene, 2D HUD | native | one render script, predicate split (below) |

## Camera and projection facts

`/manuals/camera/` + `/manuals/orthographic-rendering/`:

- Orthographic projection: constant world-unit→pixel ratio; the projection
  matrix maps view volume to NDC. Aspect: rebuild projection on resize
  (`2d-rendering.md` adaptation policy).
- Perspective for 2.5D: fov + near/far are yours in the render script;
  near/far spread tightly around *your* content band — 0.1..1000 defaults
  eat depth precision at iso distances.
- One camera drives world+actors; GUI layer bypasses it. Two cameras means
  two passes over the same geometry — a design smell, not a feature.

## Billboards

No built-in billboard component flag for sprites at arbitrary axes; the
standard shapes:

- **Axis-lock**: sprite rotation = camera yaw (2D chars facing camera in 3D
  yard): set `go.set_rotation` from camera each frame — cheap, snap angles
  if art is a flipbook (8-direction sprite sheets beat smooth yaw: rotate
  *nothing*, pick the frame).
- **Shader-side**: material rotates quads to camera in vertex shader
  (true billboard, more shader work).
- Pixel art billboards: keep nearest filtering + integer-ish screen
  footprint, else `2d-pixel-art.md` blur list applies through the 3D path.

## 2D/3D layering and draw order

Render script predicates are the border
(`/manuals/render-scripts/`, tags in `.material`):

1. Opaque 3D pass: depth test ON, sorted front-to-back by engine.
2. Sprites in-world: same pass but materials with depth write off / test on
   for "in the world" feel, or own predicate for "painted onto screen".
3. 2D world layer (if any): separate predicate, no depth, order per
   `2d-rendering.md`.
4. GUI last, own pass, no camera.

Rule: **depth testing across the 2D/3D border is either fully on or fully
off per band, never negotiated per object.**

## z-fighting and sorting pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Background texture shimmers over geometry | near/far too wide for scene scale | tighten near/far to content band |
| Coplanar decals/labels flicker on 3D | true coplanar polygons | offset along normal, or polygon offset in material, or render as own pass |
| Sprites pop in front of/behind wrong models | transparent pass has no reliable depth for sprites | sort key (distance) in your own order field, or predicate split |
| Iso tiles overlap wrongly on resize | float depth ties | integer grid depth = fixed function of tile coords, not world pos |
| Pixel HUD blurs over crisp 3D | GUI and world pixel grids disagree | `2d-pixel-art.md` audit through the render script |

## Parallax + depth effects (2.5D flavor)

- Layered quads at fixed z with per-layer camera scale = painted parallax in
  a 3D scene — snap layer camera math to integers for pixel art layers.
- Depth-of-field/DOF-blur lookalikes: per-layer alpha/fog in material, not
  post processing stack; verify what the current render pipeline exposes
  before promising post effects.

## Mixed pixel-art / voxel / 3D projects

- One grid contract: texel grid (pixel art, `2d-pixel-art.md`), block grid
  (`voxel-development.md`), world units — derive all from a single
  `WORLD_UNIT` constant module.
- Nearest filtering is a project default for pixel and voxel sources;
  smooth 3D sources opt *out* explicitly.
- Sprite shadows onto 3D: baked blobs or projected quads with multiply
  blend — a shader/material decision, decide once, in materials.

## Checklist

- [ ] One shape chosen (table above), stated in project docs
- [ ] near/far scoped to content band; resize policy shared with `2d-rendering.md`
- [ ] Every 2D/3D border assigned to a predicate, depth on/off per band
- [ ] Billboard strategy = frames or shader, not per-frame free rotation of pixel art
- [ ] WORLD_UNIT/texel/block constants in one module, grep-verifiable
