# Materials — types, audits, repairs

Engine support per material type is adapter data
(`engine-adapters.md`); this file is the engine-agnostic model plus audit
rules. `scripts/material_audit.py` implements the checks below and emits
findings; it distinguishes technical defects from deliberate style choices
via the project's declared art style.

## Material model (engine-agnostic)

| Type | Inputs | Common defects | Style contexts |
|---|---|---|---|
| PBR metallic-roughness | albedo, normal, roughness, metallic, (ao) | ao in roughness slot; linear albedo; sRGB normal | realistic, hand-painted (Godot `ORMMaterial3D`, Defold PBR) |
| Unlit | albedo (+alpha) | accidental lighting still applied | pixel-art, UI, mobile low-end |
| Flat shading | none/fixed color | smooth normals left on mesh | low-poly |
| Toon/cel | ramp texture | ramp filtered linear → banding | toon, cel |
| Vertex color | mesh CDEX | lost on export (no CD slot) | stylized, retro |
| Emissive | emission map/color | emission in albedo alpha | sci-fi, neon |
| Transparent | albedo+alpha | sort/passes wrong; premultiplied mismatch | FX, water |
| Alpha cutout | alpha threshold | soft alpha + hard threshold = fringe | foliage, pixel-art |
| Decal | projection | z-fighting, wrong pass count | environment |
| Terrain/Water/Glass | engine-specific | unsupported in target adapter | environment |
| SSS | engine-specific | heavy on mobile | organic, stylized |
| Triplanar | 2–3 texture sets | 3× sample cost | terrain, modular kits |

## Audit checks (severity default)

- **Critical**: missing material file / broken reference; shader does not
  compile in target engine; texture slot points at wrong map kind.
- **High**: wrong color space (normal map authored sRGB, albedo authored
  linear); transparency without depth-sort plan; duplicate materials that
  differ only by name.
- **Medium**: unused material variants; shader samples a texture twice with
  identical coordinates; metallic slider at 0.5 (neither metal nor dielectric).
- **Low**: redundant parameter overrides; material count above profile budget.
- **Informational**: style-consistent deviations — flat shading on low-poly is
  a choice, not a defect; hand-painted "missing" normal map is a feature.

Style-aware suppression: when `art_style` in `asset-pipeline.yaml` is
`pixel-art` or `voxel`, "no normal map" and "nearest filtering" are expected;
when `hand-painted`, missing roughness variation is expected. Report under
`Informational (style)`, never as a repair candidate.

## Repair ladder (each rung reversible, dry-run first)

1. Re-point broken texture slots by filename+hash match against asset index.
2. Consolidate byte-identical materials to one file + updated references.
3. Reset default-drifted parameters (metallic 0.5 → 0/1) — only when the
   material is not hand-tuned (diff against VCS or checksum log).
4. Strip provably unused material slots (zero mesh references project-wide).
5. Engine-format conversion (e.g. StandardMaterial3D → ORMMaterial3D) —
   output a new file, never overwrite; requires approval in `fix` mode.

NEVER change base color, shader look, or blend mode to "fix" a finding —
that is style drift; report as suggestion instead.
