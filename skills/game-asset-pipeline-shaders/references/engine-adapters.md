# Engine adapter contract

An adapter answers exactly these questions for one engine@version; adapters
are the ONLY place engine specifics enter the pipeline. Defold/Godot adapters
ship as files; Unity/Unreal/Bevy/custom = same contract, filled from official
docs or a live probe, marked UNVERIFIED until probed.

```
adapter:
  engine: <name>            engine_version: <probed, not assumed>
  texture_formats: {import, runtime_compressed, hdr_source}
  material_types: {supported, unsupported_fallback}
  shader_dialect: <GLSL ES x.y | HLSL | WGSL | GDShader | ...>
  mesh_io: {primary, extensions_gated}   # draco/meshopt = mesh-only
  instancing: <api or none>
  color_space_policy: {srgb_slots, linear_slots}
  verification: {headless_cmd, render_cmd}   # empty = level cap HEADLESS
  budgets_profile: <profile name from asset-pipeline.yaml>
```

Rules: (1) fill from installed engine or official docs for that version;
(2) unfilled = `UNVERIFIED` → conservative default + report; (3) unsupported
material/shader feature → named fallback or blocking finding, never silent
substitution; (4) Unity: import pipeline/version tags per asset; Unreal:
build-hosted cooked formats — treat external tools as pre-filters.
