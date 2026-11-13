---
name: lowpoly-reference-to-blender
description: >
  Build stylized low-poly 3D assets in Blender from 2D concept art or reference
  images. Characters, faces, vehicles, karts, environments, props. Multi-view
  blueprint gates, quality scoring, GLB export for Defold and other real-time
  engines. Use when modeling any 3D asset from a reference image, refining an
  existing Blender scene toward a reference, or preparing a Blender asset for a
  game engine. Requires live Blender MCP or background Blender Python access.
---

# Low-Poly Reference to Blender Asset

> **Reference image is the design authority.** You may simplify a form for the
> low-poly style. You may NOT replace or invent a feature the reference shows.
> Reconstruct a missing view, do not invent a second design.

## Prerequisites

Blender MCP live connection or `blender --background --python-expr` access.
Verify before modeling:
```python
import bpy
print(bpy.app.version_string)       # "5.3.0"
print(bpy.app.build_hash[:8])       # "02f0899d"
```

If neither path is available, stop. Do not claim you modeled anything.

---

## Workflow

### 1. Analyze the Reference

Before touching Blender:
- Classify: character / vehicle / environment / prop
- Capture main silhouette, material colors, proportions, distinguishing features
- List which views exist in the reference
- Check reference resolution; if < 512px wide, note low detail in report
- Read `references/reference-analysis.md` for the analysis checklist

### 2. Plan the Build

Record before modeling:
- Asset type, polygon budget, export target
- View list (what can be verified vs reconstructed)
- Object hierarchy: root name, part names, materials

Use `scripts/inspect_scene.py` before editing to capture starting state.

### 3. Build — Category Path

| Type | Primary Reference |
|---|---|
| Character | `references/character-modeling.md` → `face-modeling.md` |
| Vehicle / Kart | `references/vehicle-modeling.md` |
| Environment / Prop | `references/environment-modeling.md` |
| General mesh | `references/modeling-workflow.md` |

**Modeling passes for characters (mandatory for faces):**

| Pass | Focus | Never |
|---|---|---|
| Pass 1 | Silhouette, head proportions, face structure grid | Materials, details |
| Pass 2 | Character identity: eyes, brow, nose, mouth, ears, hair, helm | Polish |
| Pass 3 | Materials, edge transitions, small details, corrections | Reshaping core geometry |

A character is not finished from one camera angle.

For vehicles: chassis, wheels, wheel arches, front/rear, spoiler, cockpit,
materials. Animate-ready parts must have clean named pivots.

### 4. Multi-View Blueprint Gate

Mandatory before any quality score. Orthographic cameras, axis convention
**+Z = up, +Y = forward, +X = right**.

Characters: Front, Left Side, Back, (+Hero).  
Karts: Front, Left Side, Back, Top, (+Hero).

Camera setup: see `scripts/render_reference_views.py`.

Each view must show exactly its named direction.
Back camera ≠ front view. Side camera ≠ 3/4 view.
For each view render, compare to reference. Log every deviation.
Fix the largest deviation first. Re-render. Repeat.

### 5. Mesh Validation

Run `scripts/validate_mesh.py` on every object before export.

PASS criteria: no degenerate faces, correct normals, manifold where required,
no unapplied transforms, valid UVs, reasonable polycount for the type.
WARNING: open mesh where open is intentional design choice.
FAIL: any FAIL → fix before export.

### 6. Quality Score (0–100)

| Category | Points | Basis |
|---|---:|---|
| Silhouette and proportions | 25 | Multi-view comparison to reference |
| Identity and characteristic features | 25 | Specific named features present |
| Form and detail fidelity | 20 | Bevels, hard edges, detail count |
| Materials and colors | 15 | Palette match, material count |
| Multi-view consistency | 15 | No view shows wrong side |

Target: **≥ 90 for final characters and karts.**

Score only from observable comparisons. If no visual comparison is possible,
output `VISUAL_REVIEW_REQUIRED`. Do not invent a number.

See `references/quality-assurance.md` for the scoring rubric and
`assets/quality-report-template.md` for the report format.

### 7. Game-Ready Export

See `references/game-engine-export.md` for engine-specific notes.

Primary target: Defold (glTF 2.0 / GLB, Y-up, meter=1 unit).
GLB export via `scripts/export_glb.py` — reimport-validated.

### 8. Deliverables

Every run produces:
1. Updated or new `.blend` file (BLEND project)
2. Validated `.glb` (GLB binary, Y-up, PBR)
3. Comparison renders (all named ortho views)
4. Quality report (PASS/WARNING/FAIL per object + score or VISUAL_REVIEW_REQUIRED)

Use `scripts/export_glb.py` then `scripts/verify_export.py` for the final gate.

---

## Optional Parameters

Accept these when provided in the prompt; use defaults when absent.

| Parameter | Default |
|---|---|
| `asset_type` | infer from reference |
| `reference_images` | required |
| `target_project` | none (no profile) |
| `quality_profile` | standard |
| `polygon_budget` | type-appropriate; see profiles/ |
| `target_platform` | Defold / iGPU-capable |
| `export_format` | GLB + BLEND |
| `output_dir` | `./out/` relative to scene file |
| `views` | Front, Side, Back |

For Riff Racers: load `profiles/riff-racers.md` after reading this file.
The profile overrides polygon budgets and identity priorities only for that project.

---

## Known Blender 5.3.0 Constraints

- `render.engine` enum reports only `BLENDER_EEVEE` in `enum_items`;
  `BLENDER_WORKBENCH` assignment works and is the correct choice for fast ortho renders
- `Mesh.is_manifold` and `Mesh.use_auto_smooth` removed; use bmesh manifold check
- `mathutils.geometry.area_tri_loop` removed; use `bmesh.calc_area()` or manual cross product
- Python 3.13 embedded — do not call system `python3` for bpy scripts
- `bpy` not available in system Python; all bpy code must go via `blender --background` or MCP

---

## References

- `references/reference-analysis.md` — reference analysis and feature checklist
- `references/modeling-workflow.md` — general Blender modeling procedure
- `references/character-modeling.md` — full character modeling workflow
- `references/face-modeling.md` — face passes, identity preservation
- `references/vehicle-modeling.md` — kart and vehicle strategies
- `references/environment-modeling.md` — modular environment and props
- `references/topology-and-optimization.md` — poly budget, bevels, normals
- `references/materials-and-uv.md` — PBR, atlases, UV workflow
- `references/quality-assurance.md` — scoring, gates, multi-view rubric
- `references/game-engine-export.md` — export targets and Defold notes

## Scripts

- `scripts/detect_blender.py` — environment and Blender detection
- `scripts/inspect_scene.py` — scene state snapshot
- `scripts/validate_mesh.py` — mesh validation
- `scripts/render_reference_views.py` — orthographic multi-view renders
- `scripts/export_glb.py` — GLB export with pre-export checks
- `scripts/verify_export.py` — GLB reimport verification
