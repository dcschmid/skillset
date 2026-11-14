# Workflow: Pixel-art project setup / pass

Style gate says pixel art (pure or hybrid). Applies `references/pixel-art.md`.

## Steps

1. **Detect state** — new project or existing? Existing: audit current
   filtering/stretch (never reset authored settings; fix per-asset exceptions).
2. **Project truth** — base resolution + stretch (`canvas_items`, integer
   optional), `default_texture_filter = Nearest`, snap settings, physics tick
   if motion-sensitive.
3. **Content** — sources → PNG (nearest-safe), sheets/TileSet per refs;
   `.import` committed; no mips anywhere in 2D pixel path.
4. **Camera** — `Camera2D` smoothing + pixel snap; parallax integer-ish;
   test stand-still shimmering at base AND upscale factors.
5. **Effects** — 2D lights/hard shadows or nearest-safe post FX; bitmap UI
   fonts, theme nearest-filtered.
6. **Gates** — STATIC settings audit; IMPORTED clean; RUNTIME shimmer check;
   VISUAL grid test at each target scale (desktop 2×/3×, native phone res).

## Hybrid branches

Pixel-in-3D → `2-5d-development.md` viewport/sampling rules. Voxel+pixel mix →
each family keeps its own import truth. Blender optional (skip for 2D).
