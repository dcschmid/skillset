# lowpoly-reference-to-blender

Turn concept art into a stylized low-poly Blender asset, from reference analysis and reconstructed views to mesh validation and GLB export.

Profile: Private. Preparation: Provide the reference image, asset type, polygon budget, and target engine. Extra views help resolve hidden shapes.

Expected result: A model, comparison views, mesh checks, and an export report. Quality scores require visual comparison with the reference.

Requirements and limits: Requires Blender Python through the private Blender MCP or a background process. System Python cannot import bpy here. Use +Z up, +Y forward, +X right; 1 BU = 1 m. Without visual comparison, report VISUAL_REVIEW_REQUIRED. Use dated names when outputs collide.

## lowpoly-reference-to-blender: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh lowpoly-reference-to-blender
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the lowpoly-reference-to-blender skill. Build a low-poly Godot character from ./ref/hero-front.png with a 2500-polygon budget. Preserve the silhouette and colors, label reconstructed views, and export a validated GLB.
```

**Codex:**

```text
Use the lowpoly-reference-to-blender skill. Compare ./assets/kart.blend with ./ref/kart.png. Check proportions and materials, describe mismatches, and propose the next modeling corrections.
```

**oh-my-pi:**

```text
Use the lowpoly-reference-to-blender skill. Check the existing prop export for Defold. Verify scale, axes, and mesh integrity, and keep new outputs separate.
```

## lowpoly-reference-to-blender: Self-test

Run from the repository root:

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [detect_blender.py](scripts/detect_blender.py)
- [export_glb.py](scripts/export_glb.py)
- [inspect_scene.py](scripts/inspect_scene.py)
- [render_reference_views.py](scripts/render_reference_views.py)
- [validate_mesh.py](scripts/validate_mesh.py)
- [verify_export.py](scripts/verify_export.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/lowpoly-reference-to-blender` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/detect_blender.py
```
