# Budgets, profiles, optimization reports

All numbers live in `asset-pipeline.yaml` (defaults + project overrides).
No fixed per-game or per-hardware constants; profiles are starting points
for measurement, not law.

## Profiles (config keys, editable)

`low-end · integrated-gpu · midrange · high-end · mobile · web`
Per profile: texture max size, texture VRAM, mesh tris per asset/scene,
material count, draw calls, shader cost class, transparency layers,
package size, load-time target. Values ship blank-ish in the template;
projects fill them from measurement.

## Measurement vs estimation

| Metric | Estimated by | Measured by |
|---|---|---|
| texture VRAM | w·h·bpp·mip math | profiler/GPU capture |
| mesh GPU verts | export log (seams split verts!) | profiler |
| draw calls | batch analysis | profiler/engine stats |
| load time | file bytes | timed headless run |
| shader cost | instruction/sample count | frame capture |

Report columns carry `(est)` or `(meas@<tool>)`. Never present estimate as
measurement.

## Mesh pass rules

- Blender poly count ≠ GPU vertex count: UV seams, hard edges, material
  splits multiply verts — measure post-export.
- LODs: generate to profile steps, quality-compare at each step; protect
  faces/silhouettes/joints/wheels/thin geometry/collision/gameplay meshes
  from aggressive decimation (report, don't crush).
- vertex-cache/fetch optimize: reversible reindex, verify render unchanged.
- instancing: identical meshes report; merge only with approval.

## Optimization report (every optimize/benchmark/compare run)

before/after per asset: file size · VRAM (est/meas) · verts · tris · draw
calls (if measurable) · load time (if measurable) · pixel diff/SSIM (if
RENDER possible) · style risk · residual findings. Delivered JSON + Markdown
(`asset_report.py`), HTML optional.
