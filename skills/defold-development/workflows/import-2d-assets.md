# Workflow: 2D Asset Intake (pixel art, sprites, tiles)

Gate every batch with `templates/import-checklist.md` Gate 2D.

## Steps

1. **Classify** — sprite sheet/flipbook · atlas page · tile source/tilemap ·
   standalone texture. Confirm art style resolution + pixel grid from the
   project (or its profile).
2. **Source hygiene** — power-of-two-friendly sizes where the pipeline asks;
   no mixed DPI; consistent pivot convention (bottom-center default);
   animation frame names → script constants (greppable).
3. **Engine placement** — atlas/tile source resource in the project's asset
   root; texture filter **nearest** for pixel assets (project texture
   profile, not per-call guesswork).
4. **1.14.1 gates** — compression profile recompress may blur pixel edges →
   check profile per asset class; vector fonts never applied to pixel art.
5. **Wire** — component references (`sprite`, `tilemap`), animation
   playback from centralized ids.
6. **Validate** — STATIC: resource paths exist; BUILT: project builds;
   VISUAL: in-engine screenshot vs source art, camera at native/integer
   scale (shimmering + blur checklist in `references/2d-pixel-art.md`).

## Failure modes

Blurry = linear filtering or fractional scale · half-pixel jitter = subpixel
camera · seams = atlas padding · missing anim = id mismatch (log actual ids).
