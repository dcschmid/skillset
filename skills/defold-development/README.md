# defold-development

Work on Defold gameplay, Lua lifecycle, GUI, rendering, imports, and builds using the existing project architecture and art style.

Profile: Private. Preparation: Provide game.project, the target platform, expected behavior, and reproduction steps for bugs.

Expected result: A gameplay change or evidence-backed finding with relevant build and runtime checks.

Requirements and limits: Check engine APIs against the project version. Load project profiles only when named. Prefer official automation; community MCP integration requires explicit opt-in.

## defold-development: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh defold-development
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the defold-development skill. Add versioned save games to this Defold project. Keep old save files readable and test saving, loading, and a schema upgrade.
```

**Codex:**

```text
Use the defold-development skill. Music plays twice after a scene change. Reproduce the bug, inspect Lua lifecycle handling, and fix the cause.
```

**oh-my-pi:**

```text
Use the defold-development skill. Check GLB imports for our HTML5 build. Identify compression supported by the project version and list missing verification.
```

## defold-development: Self-test

Run from the repository root:

```bash
python3 skills/defold-development/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [workflows/](workflows/): Task-specific procedures.
- [templates/](templates/): Templates for the target project.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [audit_defold_project.py](scripts/audit_defold_project.py)
- [bob_build.sh](scripts/bob_build.sh)
- [check_build.sh](scripts/check_build.sh)
- [check_version.py](scripts/check_version.py)
- [gltf_preflight.py](scripts/gltf_preflight.py)
- [validate_skill.py](scripts/validate_skill.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/defold-development` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
python3 scripts/audit_defold_project.py /path/to/game
python3 scripts/gltf_preflight.py /path/to/asset.glb
```
