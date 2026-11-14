# Godot adapter — baseline 4.7.2 stable (ed1daf0b)

Version-gated; official docs (https://docs.godotengine.org/en/4.7/) beat this
file. 4.8 is beta — never default. Engine gameplay/API depth → `godot` skill;
this adapter maps asset-pipeline facts; probes below verify per project.

- **glTF/GLB**: `.import` presets control compression/LOD; import scripts for
  batch policy. Verify project's `project.godot` `config/features` version.
- **Materials**: `StandardMaterial3D` / `ORMMaterial3D` (packed ORM — packing
  is engine-correct there; foreign packing = finding), `ShaderMaterial` for
  custom; Spatial vs CanvasItem dialects do not mix.
- **Renderers**: Forward+ / Mobile / Compatibility change texture compression
  defaults and shader feature sets — the renderer in `project.godot` decides
  budgets (mobile/Compatibility → `shaders.md` mobile tier).
- **Textures**: engine import compresses per platform (ETC2/ASTC/BPTC/S3TC);
  import-time detection via `godot --headless --import`; lossless source for
  pixel-art, nearest mipmaps off.
- **LODs**: mesh-generated LODs in import settings; quality-gate per profile.
- **Verify**: `godot --headless --import` exit 0 = HEADLESS;
  `--quit-after`/screenshot run = RENDER.
