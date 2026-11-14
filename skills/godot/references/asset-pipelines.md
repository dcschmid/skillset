# Asset pipelines (universal intake, 4.7 baseline)

Pick the pipeline per asset family from the detected style
(`references/pixel-art.md`, `voxel-art.md`, `low-poly.md`, …). Every pipeline
ends the same way: committed source + `.import` → `--headless --import` clean →
in-engine visual gate.

## Family intake

| Family | Source | Import note |
|---|---|---|
| Sprites/sheets | Aseprite/Krita/GIMP → PNG | nearest filter, no mips (pixel); committed sheet layout doc |
| Vector UI | SVG → import SVG as texture (verify SVG importer per version) | scale-independent UI |
| 3D meshes | Blender → GLB (`blender-integration.md`) | +Z up/Y facing repo convention; embedded textures |
| Voxel models | MagicaVoxel/Blockbench → mesh/GLB or nearest-textured cube | `voxel-art.md` |
| Audio | DAW → OGG music (loop pts) / WAV SFX | bus + loop verified in editor |
| Fonts | TTF/OTF; bitmap for pixel UI | `ui-and-accessibility.md` |
| Tile sources | tile sheet + set doc → TileSet resource | collection shapes/phys authored in editor |
| Procedural | in-engine (noise, `SurfaceTool`) | deterministic seed; output versioned |

## Rules

- Sources live in `assets/<family>/`; committed WITH `.import` sidecars —
  import settings are project truth (4.x stores them there).
- No hand-edited generated `.godot/` cache (never in VCS).
- Filename = identity: stable ids for savegame refs; renames = migration.
- External packs (asset store, Kenney): copy into project, re-import, license
  noted in `assets/CREDITS.md` — blind addon install forbidden.
- Batch ops run headless: reimport-all, `--export-pack` smoke.

## Pipeline choice per project size

Prototype: engine primitives + placeholder art. Medium: authored assets,
shared material/theme files. Large: pipeline docs per family + import
smoke tests in CI (`references/testing.md`).
