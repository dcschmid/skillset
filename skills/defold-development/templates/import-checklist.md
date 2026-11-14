# Asset Import Gate — <asset> — <project> — <date>

Type: pixel-sheet | atlas | tilesource | glTF/GLB | voxel-mesh | audio
Source tool + version: ______ · Engine version: ______

## Gate 2D (pixel/sprite/tile)

- [ ] source resolution matches project pixel grid; no fractional scaling
- [ ] filtering: nearest on all pixel textures (texture profile checked)
- [ ] atlas: padding/bleed set; no bleed-through after compression
- [ ] animation names match script call sites (greppable constants)
- [ ] VISUAL: in-engine screenshot compared against source art

## Gate 3D (glTF/GLB)

- [ ] `scripts/gltf_preflight.py` run, notes triaged
- [ ] up-axis/units: export +Y up handling verified in engine (not assumed)
- [ ] materials survive import (PBR slots, colors, textures linked)
- [ ] Draco/Meshopt/KTX2: engine >= 1.14.1, IMPORT-TIME only
- [ ] scale in engine == design intent (measure bounding box)
- [ ] animations play; rig bones within budget
- [ ] poly count within profile's budget table (project-profiles/*)
- [ ] VISUAL: in-engine screenshot vs reference render

## Gate audio

- [ ] format/bitrate per platform target; streaming decision made
- [ ] gain/loop flags set; in-engine level check (RUNTIME)

## Verdict

Levels reached: STATIC/AUTOTEST/BUILT/RUNTIME/VISUAL: ______
Failures + diagnosis: ______ (fix source, do not patch blindly in engine)
