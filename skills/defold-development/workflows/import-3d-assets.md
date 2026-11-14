# Workflow: 3D Asset Intake (glTF/GLB, models, animations)

Gate every batch with `templates/import-checklist.md` Gate 3D +
`scripts/gltf_preflight.py <file>`.

## Steps

1. **Source contract** — DCC + version; export convention recorded in the
   project (Blender side: the separate `lowpoly-reference-to-blender` skill
   is OPTIONAL, never a dependency of this workflow). glTF 2.0 / GLB is the
   intake format.
2. **Preflight** — `scripts/gltf_preflight.py`: container, extensions
   (Draco/Meshopt/KTX2 = Defold ≥ 1.14.1, **import-time only**), tri count,
   materials, animations. Triage every NOTE before import.
3. **Coordinate/unit truth** — verify export-axis handling and scale IN
   ENGINE (measure world bounding box), never assume from DCC viewport.
4. **Engine placement** — model/mesh + material resources in the project's
   asset root; texture compression profiles per asset class (KTX2 recompress
   policy on 1.14.1 can be lossy — check after import).
5. **Materials** — confirm PBR slots and any custom shader survive import;
   missing = fix source export settings first, engine patch second.
6. **Animations** — play each animation in a throwaway scene; rig/bone count
   within profile budget.
7. **Validate** — STATIC: preflight + build; RUNTIME: log clean;
   VISUAL: in-engine screenshot vs reference render, correct lighting.

## Failure modes

Invisible model = scale/axis mismatch · stretched UVs = export tangents/UV
settings · flat colors = material export dropped · "Draco unsupported" =
engine < 1.14.1 — re-export uncompressed, do not upgrade the project silently.
