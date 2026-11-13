# Reference Analysis

Run this before any modeling. The output goes into the model plan and the
final quality report.

## 1. Classification

Decide the category first — it selects the reference doc and the polygon budget:

| Category | Signals | Modeling reference |
|---|---|---|
| Character | humanoid, face visible, head/torso ratio | `character-modeling.md` |
| Vehicle / Kart | wheels, chassis, driver seat | `vehicle-modeling.md` |
| Environment | architecture, terrain, modular pieces | `environment-modeling.md` |
| Prop | standalone object, single material set | `environment-modeling.md` |

## 2. Feature Inventory

List, per reference image, the features that MUST appear in the model:

```
FEATURE INVENTORY — <asset name>
- silhouette: <overall shape, e.g. "wide-hip compact torso, oversized helmet">
- head/cockpit: <shape, distinctive elements>
- identifying marks: <logo, stripes, color blocks, goggles, scars>
- color blocks: <name → hex approximation from reference>
- proportions: <head:body ratio, wheelbase, relative part sizes>
- facing direction: <which way the subject looks in the image>
```

Every entry here becomes a checkable item in the quality report. If a feature
is in the reference but missing from the inventory, the inventory is wrong —
look again.

## 3. View Coverage

For each image, name the view: front / side / back / top / 3-quarter / hero.

- Features visible in ≥ 1 image: **replication required**.
- Features in no view (e.g. back of head when only a front image exists):
  **reconstruction** — must be consistent with the design language; mark as
  interpretation in the report.

NEVER claim a match against a view you do not have.

## 4. Palette

Sample 3–8 dominant colors. Write them as hex. This list constrains the
material setup — the agent may not invent palette entries that appear nowhere
in the reference.

## 5. Scale Plan

Pick a unit convention before modeling: 1 Blender unit = 1 meter, character
heights ~1.5–2.0 units, kart ~2.0–2.5 units long. Write it into the plan so
imports and pivots stay consistent.

## 6. Readability Test

Squint at the reference. What survives as pure silhouette? Those shapes carry
the identity — they get the polygon budget first. Things that vanish at squint
distance are candidates for texture or removal, not geometry.
