# Asset Pipelines — Defold 1.14.1 baseline

Load when setting up or debugging an art→engine flow. Four gated flows;
each gate is a check that must pass before the next stage. Import-time vs
runtime support is called out per stage — never promise runtime decoding.

## Coordinates, stated honestly

- glTF 2.0 is Y-up, right-handed; Blender's exporter emits Y-up by default
  (`export_yup` in the glTF exporter — a DCC-side option, not an engine one).
- Defold **preserves imported glTF transforms and does not re-center**;
  editor preview and runtime agree; skinned/bone-parented meshes keep
  skeleton-relative transforms, rigid meshes keep flattened placement
  (/manuals/importing-models/, checked 2026-11-13). Reimport drift = fix in
  the DCC tool, re-export.
- Engine-space handedness for authored (non-imported) transforms is not
  spelled out on the import page — **verify at /manuals/gltf/ /
  /manuals/importing-models/ / /manuals/building-blocks/ against the pinned
  version** instead of asserting left/right-handed in code comments.
  Old-Defold models that shifted on reimport: re-export is the documented
  fix.

## Pipeline 1 — Pixel art → 2D

```
PNG (integer scale, no AA) → Atlas / Tile source → build → render check
```

| Stage | Inputs | Check | Fail mode |
|---|---|---|---|
| Author | PNG, palette-locked | dimensions even/power-of-two where profiles require | semi-transparent edges from export AA |
| Import | images → Atlas (animated sprites) / Tile source (tilesets) | preview in editor | packing bleed on polygon-packed atlases |
| Build | texture profiles compression on | ETC/ASTC/Basis output per platform | build time blowup (compression is build-time, CPU-heavy — /manuals/texture-profiles/) |
| Verify | run on target | crisp at native res | filtering set to linear somewhere |

Runtime does not re-compress; formats chosen at build. Filter settings:
/manuals/texture-filtering/.

## Pipeline 2 — Blender → glTF/GLB → 3D

```
glTF 2.0 export → drop .glb/.gltf in Assets → Model component → in-game check
```

| Stage | Inputs | Check | Fail mode |
|---|---|---|---|
| Export | `.glb` or `.gltf+.bin+images`; baked animations (matrices/key); UVs; Y-up default | file lists in /manuals/importing-models/ | unbaked curves lost; missing external buffers (keep relative paths!) |
| Compress | Draco `KHR_draco_mesh_compression`, Meshopt `EXT_/KHR_meshopt_compression`, `.ktx2` images | **1.14.1 IMPORT-TIME only** — runtime uses normal geometry; smaller source ≠ smaller bundle | expecting runtime Draco decode |
| Import | drag into Assets; embedded images browsable, read-only; copy-mesh → editable `.model` | Auto Fill binds generated `gltf.*` materials | hand-editing read-only resources (edit DCC source, re-export) |
| Use | Model component: Scene/Skeleton/Animations + Animation Set | `model.play_anim` in game | morph+skeletal dual play (one anim at a time, /manuals/model-animation/) |
| Verify | device run; profile draw calls | light buffer consumed by material | "unlit" = material ignores lights (/manuals/light/) |

Optional, not a dependency: the separate `lowpoly-reference-to-blender`
skill can generate the source model; the pipeline above doesn't change.

## Pipeline 3 — Voxel/heightfield editors → mesh

Defold has **no voxel runtime and no voxel importer** — every voxel/editor
tool exits through a mesh converter:

```
MagicaVoxel/MagicaCSG/etc → glTF (or OBJ→glTF); merged quads, palette texture baked
```

| Stage | Check | Fail mode |
|---|---|---|
| Convert | voxels → merged mesh (one mesh per material page), chunk-sized pieces | per-voxel geometry = millions of tris |
| Texture | palette atlas baked to PNG/KTX2 before import | runtime atlas assumptions |
| Runtime edit | generate `.buffer`/procedural meshes in Lua if worlds are editable — extension work, not built-in | promising editable voxel worlds |

Verification level: same in-game check as Pipeline 2.

## Pipeline 4 — Procedural generation

```
seeded Lua gen → data (tables/.buffer) or mesh → runtime integration → perf gate
```

| Stage | Check | Fail mode |
|---|---|---|
| Generate | deterministic (seed in save); bounded time slice | per-frame regeneration |
| Serialize | version-tagged data; `load()` banned on untrusted strings | non-reproducible worlds |
| Integrate | factories for instances; async/proxy load for chunks | sync load hitches |
| Perf | frame graph + memory on weakest target | "it generated" ≠ "it ships" |

See `procedural-generation.md` for the generation side.

## Gate vocabulary (report these levels)

1. **Import-clean** — resource parses, editor preview OK.
2. **Bind-clean** — materials/textures/animations bound, no nil samplers.
3. **Run-clean** — correct on desktop run.
4. **Device-clean** — correct + in-budget on the weakest target (the only
   level that counts for shipping).

Common cross-pipeline failure modes: relative-path breakage on `.gltf`
externals; treating import-time codecs (Draco/Meshopt/KTX2 re-encode) as
runtime features; assuming built-in shadows/IBL exist to match DCC renders
(they don't — /manuals/physically-based-rendering/); texture compression
making build times explode without profiles scoped per platform.
