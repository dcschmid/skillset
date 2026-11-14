# High-poly & detailed 3D (4.7 baseline)

Load when the style gate says detailed/PBR-realistic-adjacent 3D.

## Materials

- `StandardMaterial3D` PBR metallic/roughness; albedo/normal/ORM texture sets;
  `ORM` packing (AO=R, Rough=G, Metal=B) as Godot expects — verify page
  "Standard Material" 4.7 docs. KTX2/VRAM compression via import presets
  (`compress/...` per-platform), verify web support caveats.
- Triplanar/detail-blend where seams unacceptable; clearcoat/etc. per material
  cost budget (each feature = shader variant).

## Geometry & streaming

- Import: GLB/FBX with LODs optional; `MeshLibrary` + `MultiMeshInstance3D`
  for forests/cities; `GeometryInstance3D` LOD paths for heroes.
- Occlusion: `OccluderInstance3D` for large blockers; verify occlusion culling
  enabled in environment (4.x supports; check per renderer).
- Textures: power-of-two, mipmaps on, VRAM compress desktop defaults; per
  platform override for mobile/web.

## Lighting

- Baked lightmaps or `LightmapGI` for static geometry + realtime for actors;
  SDFGI (Forward+ desktop) for open dynamic worlds — verify perf target first;
  Mobile renderer: baked + probes.

## Budgets & verification

Tri budget per scene bucket (iGPU 1080p ≈ 200–500k visible tris, mid GPU
higher — measure with profiler). Draw calls via mesh merges/atlases.
Gates: import clean; profiler memory/GPU inside target; visual pass on the
LOWEST target GPU.
