# glTF 2.0 / GLB pipeline

`scripts/gltf_validate.py` does the JSON/container checks; this file carries
the rules. Primary interchange = glTF 2.0/GLB; others only when the adapter
proves reliability.

## Extension gate (each: engine + version + platform before use)

| Extension | Domain | Notes |
|---|---|---|
| KHR_draco / (E)XT_meshopt / KHR_mesh_quantization | MESH geometry only | NEVER claim texture effect |
| KHR_texture_basisu | TEXTURES (KTX2/Basis) | independent of mesh codecs |
| EXT_mesh_gpu_instancing | instancing | engine+GPU feature |
| KHR_materials_* | material extras | per-engine support varies |

Unknown support → UNVERIFIED → engine docs or import test decides.

## Validate before shipping

container magic/version · buffers resolve · images resolve · accessors
in-range · materials reference existing textures · UVs present where sampled
· normals where lit · skins joint count = joints · animations target live
nodes · quantization/draco requires decoder at import. `KHR_materials_*`
passthrough gaps degrade visually, not fatally — report class.

## Round-trip protocol

Blender export → `gltf_validate.py` → engine headless import → render
`RENDER` screenshot → `pipeline_runner.py compare`. Assert: materials visually
equal, transforms, anim plays, skin complete, textures load, references
stable. Any level not run = `NOT_RUN` in report.
