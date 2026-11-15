# game-asset-pipeline-shaders

Audit the technical path from authored assets to runtime: materials, textures, shaders, glTF/GLB, and memory budgets. Defold and Godot adapters are included.

Profile: Private. Preparation: Provide the asset directory, engine, art style, target device, budget, and any protected source files.

Expected result: File and reference findings, separate disk-size and estimated VRAM figures, and a repair or optimization plan.

Requirements and limits: Start repairs with a dry run and back up originals. Preserve appropriate lossless sources and filtering for pixel art. Blender preflight runs inside Blender. Deep glTF specification checks require a suitable validator; other engines are extension points.

## game-asset-pipeline-shaders: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh game-asset-pipeline-shaders
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the game-asset-pipeline-shaders skill. Audit assets/ in our Godot game for broken references, incorrect color spaces, and oversized textures. Report disk size and estimated VRAM separately. Do not edit files yet.
```

**Codex:**

```text
Use the game-asset-pipeline-shaders skill. Plan texture optimization for mobile devices. Preserve pixel-art sources and explain the expected benefit for each file.
```

**oh-my-pi:**

```text
Use the game-asset-pipeline-shaders skill. Validate ./assets/vehicle.glb for material and reference errors. Separate static checks from results obtained in an actual engine run.
```

## game-asset-pipeline-shaders: Self-test

Run from the repository root:

```bash
python3 skills/game-asset-pipeline-shaders/tests/test_skill.py
```

The modes `audit`, `validate`, `fix`, `optimize`, `material`, `textures`, `shader`, `export`, `benchmark`, and `compare` describe workflows. Local installation targets are recorded in `.installed-manifest`.

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [assets/](assets/): Support files and templates.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [asset_audit.py](scripts/asset_audit.py)
- [asset_report.py](scripts/asset_report.py)
- [blender_preflight.py](scripts/blender_preflight.py)
- [gltf_validate.py](scripts/gltf_validate.py)
- [material_audit.py](scripts/material_audit.py)
- [pipeline_lib.py](scripts/pipeline_lib.py)
- [pipeline_runner.py](scripts/pipeline_runner.py)
- [texture_analyze.py](scripts/texture_analyze.py)
- [tool_probe.py](scripts/tool_probe.py)
