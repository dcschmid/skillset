# Quality Report — {{ASSET_NAME}}

Date: {{DATE}} · Blender: {{BLENDER_VERSION}} · Pipeline: lowpoly-reference-to-blender
Reference(s): {{REFERENCE_FILES}} · Profile: {{PROFILE or "standard"}}

## Design Authority

Reference concept art is binding. Simplification allowed; substitution is not.

## FEATURE INVENTORY

| Feature | Reference view | Status |
|---|---|---|
| {{feature}} | {{front/side/back/reconstructed}} | replicated / reconstructed / MISSING |

## Technical Gate — validate_mesh.py

RESULT: {{PASS/WARNING/FAIL}}

| Object | Tris | Status | Notes |
|---|---:|---|---|
| {{object}} | {{n}} | {{lvl}} | {{justification for WARNINGs}} |

## Multi-View Blueprint Gate

Convention: +Z up, +Y facing. Renders: {{view}} → `out/{{asset}}_{{view}}.png`

| View | Compared to | Result | Deviations |
|---|---|---|---|
| Front | {{ref}} | pass/fail | {{list}} |
| Side | {{ref}} | pass/fail/reconstructed | {{list}} |
| Back | {{ref}} | pass/fail/reconstructed | {{list}} |

## Iteration log

round N — deviations: … — fixes: … — next: rerender/pass

## Quality Score (0–100) — from render comparison only

| Category | Pts | Score | Evidence |
|---|---:|---:|---|
| Silhouette & proportions | 25 | | |
| Identity & features | 25 | | |
| Form & detail fidelity | 20 | | |
| Materials & colors | 15 | | |
| Multi-view consistency | 15 | | |
| **Total** | **100** | **{{n or VISUAL_REVIEW_REQUIRED}}** | |

Target ≥ 90 (final characters/karts). Missing visual comparison →
`VISUAL_REVIEW_REQUIRED`, never an invented number.

## Export

GLB: `{{path}}` ({{bytes}}) · Reimport verify: {{PASS/FAIL}} · BLEND: `{{path}}`
Engine: {{target}} · Notes: {{axis/pivot/LOD decisions}}

## Verdict

{{DELIVERED / RETURNED_FOR_CORRECTION / VISUAL_REVIEW_REQUIRED}}
Human reviewer sign-off: ____________________
