# 2.5D & hybrid projects (4.7 baseline)

"2.5D" = mixed dimensionality. Identify which hybrid the project is before
loading this; then route deeper into the component refs it needs.

## Variants & their engineering

| Hybrid | Core technique | Key refs |
|---|---|---|
| Sprites in 3D (cross-render, DDO-like) | `Sprite3D`/billboards on `QuadMesh` billboard materials | pixel-art.md, 3d-development.md |
| Pixel-textured 3D (HD-2D-ish) | 3D scene, textures nearest/no-mip, camera-controlled scale | pixel-art.md, shaders.md |
| Isometric 2D | pure 2D + iso transform or iso tileset; `YSort` depth | 2d-development.md |
| 3D world, 2D UI/HUD | separate `CanvasLayer`; screen-space UI independent of style | ui-and-accessibility.md |
| 2D gameplay, 3D backdrop | parallel `World2D`+`World3D` containers (4.x supports both in one tree) | 3d-development.md |

## Sprite-in-3D specifics

`Sprite3D` (billboard modes) or `QuadMesh` + `StandardMaterial3D` billboard
mode; shaded vs `shaded=false` unlit for flat pixel look; distance-dependent
pixel size = viewport scale math, verify at target resolutions.

## Parallel worlds

`Node2D` and `Node3D` branches coexist under a common root; 2D UI in
`CanvasLayer` above `World3D` camera. Coordinate conversion via camera
`unproject_position` (3D→screen) / `project_ray_*` (screen→3D) — the API for
"click 3D from UI" patterns.

## Pixel-art integrity in 3D

Texture filter nearest + no mipmaps per material; fractional viewport scale
breaks grid → pick integer viewport scale or accept documented filtering
compromise (VISUAL gate decides).
