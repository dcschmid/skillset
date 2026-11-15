# godot

Build and maintain Godot scenes, controls, physics, UI, audio, shaders, and exports in GDScript or C#. Choose rendering and gameplay systems to suit the project.

Profile: Private. Preparation: Provide project.godot, the affected scene, engine version, target platform, and expected behavior.

Expected result: A verified scene or script change with results from the available engine checks.

Requirements and limits: Headless checks do not replace visual review. Renderer, physics, and API choices must match the installed Godot version.

## godot: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh godot
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the godot skill. Add coyote time and input buffering to the existing player controller. Reuse the input abstraction and test ledge departure and landing.
```

**Codex:**

```text
Use the godot skill. A signal is handled twice after reloading the scene. Find the duplicate connection and verify several restart cycles.
```

**oh-my-pi:**

```text
Use the godot skill. Check this project for web export. Inspect the renderer, resources, and export configuration, and identify untested browser paths.
```

## godot: Self-test

Run from the repository root:

```bash
python3 skills/godot/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [workflows/](workflows/): Task-specific procedures.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [audit_godot_project.py](scripts/audit_godot_project.py)
- [check_version.py](scripts/check_version.py)
- [headless_check.sh](scripts/headless_check.sh)
- [validate_skill.py](scripts/validate_skill.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/godot` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/audit_godot_project.py /path/to/game
bash scripts/headless_check.sh examples/base-project
```
