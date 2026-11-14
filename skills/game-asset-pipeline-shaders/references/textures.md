# Textures — types, formats, compression, color space

`scripts/texture_analyze.py` implements detection; this file carries the
rules. File size and VRAM are separate numbers — always report both.

## Type → color space → sampler

| Map kind | Color space | Filter default | Notes |
|---|---|---|---|
| Albedo/BaseColor/Diffuse | sRGB | project default | pixel-art: nearest, no mip |
| Normal | Linear | linear | OpenGL +Y up unless engine says else |
| Roughness / Metallic / AO | Linear | linear | never sRGB; packing per adapter |
| Height/Displacement | Linear | linear | 16-bit if precision matters |
| Emissive | sRGB | linear | HDR source → engine HDR path |
| Opacity/Masks | Linear (data) | nearest if pixel-art | channel-packed masks linear |
| Lightmap | Linear (usually) | project-specific | check engine lightmap pipeline |
| Sprite sheet / atlas | sRGB | nearest for pixel-art | padding ≥1px, no bleed |
| HDR env | float/half | linear | `.hdr`/`.exr` → engine import |

Alpha bleeding: premultiply on resize or crop atlases with 1px border, or
pad with edge color — report when atlas gutter is 0 and filter is linear.

## Container formats

PNG (lossless, default source) · JPEG (photos only, no alpha) · WebP (lossy/
lossless+alpha; check engine decode support) · TGA (legacy; avoid new) ·
EXR/HDR (HDR sources, engine-compressed at import) · DDS (D3D block formats,
Windows/older pipelines) · KTX2 (Basis; transcode-time engine choice).
Per-engine import support = adapter (`engine-adapters.md`).

## Compression decision order

1. Does the **target engine version** decode the format at runtime or
   import-time? (probe adapter table; unknown → UNVERIFIED)
2. Does the **GPU** provide native block support, or must the engine transcode
   (Basis UASTC→ETC2 costs CPU on load)?
3. Quality gate: run comparison (SSIM + pixel diff + perceptual check) —
   pixel-art and hand-painted assets keep lossless or nearest-quantized paths.
4. Report: disk bytes (file), VRAM bytes (uncompressed block size at max mip
   level = w·h·bpp/8 × mip factor ≈ ×4/3), decode/load cost class.

| Codec | Domain | Typical use | Watch |
|---|---|---|---|
| BC1/BC3 | desktop GL/D3D | albedo/normal desktop | no mobile |
| BC7 | modern desktop | high-quality PBR sets | encode slow |
| ASTC 4×4/6×6 | mobile/modern desktop | all maps | not on old GL |
| ETC2 | GLES3/mobile | default mobile fallback | no alpha on ETC1 |
| Basis ETC1S | KTX2 transcode | small web/mobile builds | quality ceiling |
| Basis UASTC | KTX2 transcode | quality + flexibility | larger source |
| raw RGBA8 | universal | pixel-art, tiny textures | VRAM heavy |

VRAM math: `w*h*bpp/8*1.333` (mips) — estimated unless read from profiler.
`texture_analyze.py` prints both disk and estimated-VRAM columns labeled
`[estimated]`.

## Auto-optimization rules (dry-run + backup enforced)

- oversized → flag at >2× profile cap (`texture_size_profile`)
- unneeded alpha (fully opaque) → report; strip only on approval
- duplicate hashes → consolidate; keep first, repoint refs, verify diff empty
- channel packing (M/R/A) only when adapter confirms slot convention
- mipmaps off for pixel-art/UI; anisotropy per profile budget
- no irreversible write ever: output next to input or `_processed/` dir,
  original retained (`.orig` only if in-place was explicitly approved)
