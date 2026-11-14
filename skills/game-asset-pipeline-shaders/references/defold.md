# Defold adapter — baseline 1.14.1 Stable (ee283d4, 2026-11-10)

Version-gated; official docs (https://defold.com/ref/) beat this file.
Engine gameplay/API depth → `defold-development` skill; this adapter maps
only asset-pipeline facts and its scripts/probes verify them per project.

- **glTF/GLB**: model components import glTF; Draco/Meshopt/KTX2 import-time
  support is version-sensitive — `gltf_preflight.py`-style gate before use;
  1.14.1-era builds verify against docs, older projects may need pre-baked
  uncompressed fallbacks.
- **Materials**: `.material` + shader `.fragment/.vertex` GLSL ES; PBR
  support exists in the modern render pipeline — probe `render.*` capabilities
  and engine build, never assume per style.
- **Textures**: engine compresses at build for targets; KTX2 path only when
  engine version proves decode; pixel-art = nearest filtering set on the
  texture/resource side.
- **HTML5 builds**: bundle format and codec support differ from native;
  web profile budgets apply (`optimization.md`).
- **Verify**: `bob.jar` build exit 0 = BUILT level; runtime logs for
  import errors; screenshot only via engine run = RENDER.
