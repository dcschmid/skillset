# Materials and UV

## Material philosophy for stylized low-poly

- A small set of flat or near-flat PBR materials beats many texture sets.
  Target ≤ 4 materials per character, ≤ 6 per vehicle/prop set.
- Colors come from the reference palette (`reference-analysis.md`). Inventing
  palette entries outside the sampled set is a defect.
- `material.diffuse_color` affects viewport only; shader node inputs are the
  export truth. glTF exports Principled BSDF inputs.

## Build materials via nodes (5.3 API)

```python
mat = bpy.data.materials.new("kart_body")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6
bsdf.inputs["Metallic"].default_value = 0.0
```

- Look shaders up by `n.type`, never by display name (localized).
- glTF-2.0 compatible = Principled BSDF with base color / metallic / roughness
  + optionally normal, emission, alpha. Avoid Blender-only node graphs
  (mix-with-math chains survive export inconsistently).

## PBR for real-time / Defold

- Defold's PBR shader consumes: base color (+alpha), metallic, roughness,
  normal, occlusion, emissive. Anything beyond this in the source material is
  silently dropped — keep it simple upstream.
- Metallic workflow: 0.0 or 1.0 per material at stylized low-poly. No
  half-metallic paint decisions at this fidelity level.

## Textures

- Prefer vertex-color-free, texture-free flat materials where the style allows.
- When a texture set exists: one atlas per asset family, power-of-two
  (512/1024/2048), PNG source, margin ≥ 4 px.
- Every texture used must be packed in the .blend and exported with the GLB
  (glTF exporter embeds PNGs; `export_image_format` is the fallback control).

## UV

- Clean, non-overlapping islands; overlapping only for mirrored symmetrical
  parts when the project accepts it.
- Lightmap/second UV channel only if the target project requests baked
  lighting; otherwise one UV map, channel index 0, name "UVMap".
- After UV work, re-run `validate_mesh.py` — bad UVs are reported per object.

## Naming

Material names: `<asset>_<purpose>` (`riffdriver_suit_blue`, `kart_trim_yellow`).
Engine-side material sorting and dedupe depend on stable names.
