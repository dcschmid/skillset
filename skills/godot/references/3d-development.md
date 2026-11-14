# 3D projects & renderer choice (4.7 baseline)

## Renderer selection (project setting `rendering/renderer/rendering_method`)

| Renderer | Target | Tradeoffs |
|---|---|---|
| Forward+ `forward_plus` | desktop / console GPUs | full feature stack (SDFGI, probes, SSR…), highest floor |
| Mobile `mobile` | mid GPUs, handheld, VR | clustered-lite path, fewer features, cheaper |
| Compatibility `gl_compatibility` | web/GL2, old GPUs, iGPU-safe | GL-era limits, smallest shader set |

Pick from the DETECTED platform matrix; stylized/pixel projects often prefer
Compatibility or Mobile for consistency + floor. One renderer per project;
switching mid-project = re-verify every material/shader (big-bang change).
Web export: verify per-version WebGPU/GL support status of the target minor.

## 3D scene spine

`Node3D` transforms (1 BU = 1 m repo convention); `WorldEnvironment` for
environment/tonemap; `DirectionalLight3D` default sun; `Marker3D`/`OmniLight3D`
as needed; `_draw()`/`MultiMeshInstance3D` for mass visuals.

## Import & materials

GLB/FBX via `ImportLibrary`/`.import` (verify 4.7 importer keys at use);
materials: `StandardMaterial3D` feature flags cost shader variants —
enable per need. `MeshInstance3D` + `CollisionShape3D` pairing in every
physical entity scene.

## Level streaming & perf

`VisibleOnScreenNotifier3D` culling, `OccluderInstance3D` for blockers,
LODs on heroes, instancing (`MultiMeshInstance3D`) for repeats. Memory:
VRAM report gate before "done" (`references/performance.md`).

## Gates

IMPORTED clean → RUNTIME frame log → VISUAL on lowest target GPU.
