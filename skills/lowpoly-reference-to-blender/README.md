# lowpoly-reference-to-blender — reference art to game-ready GLB

Human-facing guide. The agent entry point is [`SKILL.md`](SKILL.md); usage
prompts for hosts live in [`USAGE.md`](USAGE.md).

Builds stylized low-poly 3D assets in Blender from 2D concept art:
characters, faces, vehicles, karts, environments, props. Pipeline: analyze
reference → plan → category build path → multi-view blueprint gate → mesh
validation → 0–100 quality score → validated GLB export (Defold-ready).
Requires live Blender MCP or background Blender Python. Conventions: +Z up,
+Y facing, 1 BU = 1 m (Blender 5.3.0 on this machine).

## Layout

```
SKILL.md                     prerequisites + workflow + parameters + Blender 5.3 truths
references/                  10 docs: analysis, workflow, character/face/environment
                             modeling, materials-UV, QA, game-engine-export
scripts/                     detect_blender.py (system Python) · inspect_scene.py ·
                             render_reference_views.py · validate_mesh.py ·
                             export_glb.py · verify_export.py (last five run INSIDE Blender)
assets/                      quality-report-template.md
tests/test_e2e_pipeline.py   headless end-to-end run, exit 0 = PASS
USAGE.md                     host invocation guide (mirror of repo README section)
```

## Use (Claude Code / Codex / oh-my-pi)

Install: `tools/install-skills.sh lowpoly-reference-to-blender` — symlinks
into `~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex);
oh-my-pi loads the same roots and keeps Blender MCP live in session. Then
invoke by name with the reference attached or pathed:

```text
Use lowpoly-reference-to-blender to build a high-quality game-ready low-poly
character from this concept art. asset_type=character, polygon_budget=2500,
quality_profile=hero.
Use lowpoly-reference-to-blender on ./ref/hero-front.png — hero profile, keep
silhouette, GLB out, report the quality score with observations.
```

Reference art is the design authority: simplify allowed, substitute
forbidden. Without visual comparison the skill emits
`VISUAL_REVIEW_REQUIRED` instead of a number. Outputs non-destructive, dated
suffix on collision.

## Run the scripts

```bash
python3 scripts/detect_blender.py           # where is Blender, which Python
# inside Blender (MCP exec or `blender -b --python`):
#   inspect_scene.py → validate_mesh.py → export_glb.py → verify_export.py
```

`Mesh.is_manifold`, `use_auto_smooth`, `area_tri_loop` are REMOVED in 5.3 —
the scripts use the verified replacements.

## Validate

```bash
blender -b --python tests/test_e2e_pipeline.py
```
