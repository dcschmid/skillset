# Tool Integration

Use what exists. Install nothing without approval. Verify options/versions
before invoking; an unknown flag is a crash in CI.

## Preferred stack (presence-gated)

| Purpose | Tool | Gate |
|---|---|---|
| structural search | ast-grep | on PATH or project dep |
| clone detection | jscpd | project dep; else `detect_duplicates.py` |
| metrics | SonarQube/sonar-scanner | project config present; else `collect_metrics.py` proxies, labeled |
| codemods | OpenRewrite (JVM), ts-morph/jscodeshift (TS/JS), ast-grep rewrite | tech stack + dep present |
| JS/TS gates | eslint/biome/tsc | manifest-declared |
| Python gates | ruff, mypy/pyright, pytest | pyproject/lockfile-declared |
| Rust | cargo fmt/clippy/test | Cargo.toml |
| Go | go vet/test, golangci-lint | go.mod; lint only if configured |
| JVM | existing mvn/gradle tasks | wrapper present |
| Games | Defold headless, Godot `--headless`, luacheck, ruff for Blender-py | engine binary/deps present |

## Rules

1. Probe: `command -v tool && tool --version` (or project-local `npx tool`)
   BEFORE first use; record version in the report.
2. Options: read `tool --help`/project config; never pass a flag you have not
   seen work with the installed version.
3. No global installs, no new devDependencies, no lockfile churn, no CI
   activation without explicit request.
4. Missing tool chain: use the project's own check command → generic
   collectors → document "UNVERIFIED: <check> (no <tool>)".
5. AST tools beat regex for semantic rewrites; regex is for locating, not
   rewriting. Never hand-roll a parser when a real one is present.
6. Read-only always: analysis tools get read commands; write-capable tools
   (formatters with `--fix`, codemods) run in fix modes only, per-change.
