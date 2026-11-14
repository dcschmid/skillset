# Language & Framework Adapters

Detection is universal; deep verification is adapter-based. Unknown language →
generic cautious mode (metrics + clones + debt markers only, no auto-edits).

## Adapter selection

Run `detect_project.py`, then per detected language use ONLY tools that exist
in the project (lockfile/manifest-gated). Verify tool version support BEFORE
running; never assume a subcommand exists.

| Stack | Verify/measure | Refactor aid (if present) |
|---|---|---|
| JS/TS | `eslint`, `biome`, `tsc --noEmit`, project test runner | ts-morph, jscodeshift, ast-grep |
| React/Next | component/lint rules + render tests | framework codemods only on request |
| Astro | `astro check`, island hydration + client-JS weight | — |
| Vue/Svelte | `vue-tsc`/`svelte-check` | — |
| Python | `ruff`, `mypy`/`pyright`, `pytest` | ast-grep |
| Go | `go vet`, `go test`, `golangci-lint` | `gofmt` (stdlib) |
| Rust | `cargo fmt --check`, `clippy`, `cargo test` | `rustfmt` |
| Java/Kotlin/C# | Maven/Gradle/dotnet checks, OpenRewrite | OpenRewrite recipes |
| PHP | existing phpstan/php-cs-fixer | — |
| Lua/Defold | game.project + module load, headless editor check | — |
| GDScript/Godot | `godot --headless --import` / `--quit-after` | — |
| Blender Python | runs INSIDE Blender (bundled Python); system python has no bpy | — |
| C/C++ | clang-format/clang-tidy if configured | — |
| SQL/shell/config | syntax-only via existing linters | — |

## Game-specific verification surfaces

- Defold: scene/resource load paths, message passing order, go lifecycle,
  update-loop allocations, save/load compat.
- Godot: node/scene deps, signal wiring, `_process`/`_physics_process` costs,
  resource (`.tres`) references.
- Blender: context dependence, bpy data-block ownership, operator reuse.

Web architecture patterns do NOT apply to game projects; game patterns do NOT
apply to websites. Keep the analysis in the project's own domain.

## Fallback ladder (missing tool)

1. Project's own equivalent command.
2. Generic static pass (collect_metrics, detect_duplicates).
3. Report the gap: "MISSING: <tool> — <check> UNVERIFIED". Never fake a result.
