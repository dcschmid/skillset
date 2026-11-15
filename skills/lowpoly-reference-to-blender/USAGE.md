# Using the `lowpoly-reference-to-blender` skill in your agents

Reference image → stylized low-poly Blender asset → validated GLB for
real-time engines (Defold and friends). Workflow: analyze reference → plan →
category build path (characters/faces, vehicles/karts, environments, props) →
multi-view blueprint gate → mesh validation → 0–100 quality score → export.
Requires live Blender MCP or background Blender Python (Blender 5.3 on this
machine; conventions +Z up, +Y facing, 1 BU = 1 m).

## Install (this skill only)

```bash
tools/install-skills.sh lowpoly-reference-to-blender
```

Symlinks EXCLUSIVELY into the Private profile roots
(`~/.omp/profiles/private/agent/skills`, `~/.codex/skills` —
`tools/profile-map.tsv`), never the shared roots; remove with
`tools/uninstall-skills.sh lowpoly-reference-to-blender`.

## Claude Code

Discovered from `~/.claude/skills/`; activate by referencing it with the
concept art attached or pathed:

```
Use lowpoly-reference-to-blender to build a high-quality game-ready
low-poly character from this concept art. asset_type=character,
polygon_budget=2500, quality_profile=hero.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use lowpoly-reference-to-blender: refine the kart in the open Blender
scene toward these three views, then export a validated GLB to output/.
```

## oh-my-pi (omp)

omp keeps Blender MCP available in session; invoke the skill by name and
hand it the reference:

```
Use lowpoly-reference-to-blender on ./ref/hero-front.png — hero profile,
keep silhouette, GLB out, report the quality score with observations.
```

## Working style (all hosts)

- Reference art is the design authority: simplification allowed,
  substitution forbidden; reconstructed views are flagged.
- Quality scores cite observations; without visual comparison the skill
  emits `VISUAL_REVIEW_REQUIRED` instead of a number.
- Outputs are non-destructive; collisions get dated suffixes.
- Scripts run inside Blender (anything importing `bpy`); `detect_blender.py`
  runs on system Python. Direct calls:
  `python3 skills/lowpoly-reference-to-blender/scripts/detect_blender.py`,
  then `inspect_scene.py`, `validate_mesh.py`, `export_glb.py`,
  `verify_export.py` inside Blender (MCP or `blender -b --python`).

## Examples that work verbatim

```
Use lowpoly-reference-to-blender: model an environment prop (crate stack)
from this photo, stay under 800 tris, manifold, GLB export verified.
```

## Verify the skill itself

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
```

Exit 0 on PASS; needs the local Blender binary.
