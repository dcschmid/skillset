# Quality Assurance

Two independent gates. A model passes technical validation and still fails
visual review — both must pass before "game-ready".

## Gate 1 — Technical (automated)

`scripts/validate_mesh.py` → PASS / WARNING / FAIL per object. FAIL blocks
export. WARNING requires a one-line justification in the report (e.g. "open
mesh: road strip, intentional").

## Gate 2 — Visual (multi-view comparison)

Run `scripts/render_reference_views.py`, place each render against its
reference, score.

### Scoring (0–100)

| Category | Points | Full-mark evidence |
|---|---:|---|
| Silhouette & proportions | 25 | front/side/back silhouettes match reference within ~5% on key ratios |
| Identity & characteristic features | 25 | every feature-inventory item present or documented-reconstruction |
| Form & detail fidelity | 20 | bevels/edges/detail density match reference's detail level |
| Materials & colors | 15 | palette hexes match samples; material count in budget |
| Multi-view consistency | 15 | every named view shows its named side; no drift between views |

Target for final characters and karts: **≥ 90**.

### Scoring honesty

- Each number cites a concrete observation: "side view jaw angle shallower
  than reference" — not "looks good".
- No visual comparison available → score field = `VISUAL_REVIEW_REQUIRED`,
  never an invented number.
- A human reviewer's acceptance note overrides the model's self-score.

### Pass/fail rules

- Any identity feature missing → cap score at 70, return for correction —
  even with perfect mesh stats.
- Any view gate failure (back shows front, side is 3/4) → visual gate fails.
- Reconstructed (unseen) views: score the reconstruction on internal
  consistency, mark interpretation in the report; do not demand reference
  match you cannot have.

## Iteration record

Every QA round appends to the run's report:

```
round N — deviations: [list] — fixes applied: [list] — next: [rerender|pass]
```

## Final deliverable checklist

- [ ] validate_mesh.py: no FAILs; WARNINGs justified
- [ ] All gate views rendered and compared
- [ ] Score ≥ 90 (characters/karts) or documented exception
- [ ] GLB reimport verified (`verify_export.py`)
- [ ] Report complete per `assets/quality-report-template.md`
