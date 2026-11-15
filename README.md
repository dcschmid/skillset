# skillset

Central repository of reusable AI-agent skills for Claude Code and Codex.
Skills are plain directories with `SKILL.md` (YAML frontmatter + workflow),
installed into both agents via symlinks — one source, many consumers.

Every skill follows the same contract: `SKILL.md` is the router (trigger,
workflow, gates, routing tables); `references/` holds depth loaded on demand;
`scripts/` holds zero-dependency (or stdlib-only) automation that runs on
this machine; `tests/` holds static validation that exits 0 on PASS. No skill
requires another skill to work; cross-skill handoffs are named, never load-
bearing.

## Layout

```
skills/<name>/SKILL.md      entry point + progressive-disclosure root
skills/<name>/USAGE.md      usage guide mirrored from this README's skill section
skills/<name>/references/   deep docs, loaded on demand
skills/<name>/scripts/      working automation (Blender Python, system Python)
skills/<name>/assets/       templates reused per run
skills/<name>/tests/        runnable validation
profiles/<project>.md       optional project overlays (never auto-applied)
tools/                      installer / uninstaller / installer tests
docs/                       architecture + authoring guides
```

## Skills

Twenty skills. The index below is navigation only; each skill then gets
its own detailed section — scope, shipped automation, how to invoke it in
Claude Code, Codex, and oh-my-pi (omp), copy-paste examples, and its own
verify command. `skills/<name>/USAGE.md` is the same guide, mirrored into
the symlinked skill directory for agents browsing the folder locally; the
README is the canonical copy.

| Skill | Domain | Verify (exit 0 = PASS) |
|---|---|---|
| [lowpoly-reference-to-blender](#lowpoly-reference-to-blender) | Game dev | `blender -b --python …/tests/test_e2e_pipeline.py` |
| [defold-development](#defold-development) | Game dev | `python3 …/tests/test_skill.py` |
| [game-asset-pipeline-shaders](#game-asset-pipeline-shaders) | Game dev | `python3 …/tests/test_skill.py` |
| [game-audio-sound-design](#game-audio-sound-design) | Game dev | `python3 …/tests/test_skill.py` |
| [godot](#godot) | Game dev | `python3 …/tests/test_skill.py` |
| [astro](#astro) | Web frameworks | `python3 …/tests/test_skill.py` |
| [react-nextjs](#react-nextjs) | Web frameworks | `python3 …/tests/test_skill.py` |
| [backend-api-engineering](#backend-api-engineering) | Engineering | `python3 …/tests/test_skill.py` |
| [ultimate-security-hardening](#ultimate-security-hardening) | Engineering | `python3 …/tests/test_skill.py` |
| [ultimate-testing-qa](#ultimate-testing-qa) | Engineering | `node …/tests/run.mjs` |
| [ultimate-code-quality-refactoring](#ultimate-code-quality-refactoring) | Engineering | `python3 …/tests/test_skill.py` |
| [ultimate-i18n-localization](#ultimate-i18n-localization) | Engineering | `node …/tests/run.mjs` |
| [documentation-technical-writing](#documentation-technical-writing) | Engineering | `python3 …/tests/test_skill.py` |
| [accessibility](#accessibility) | Engineering | `python3 …/tests/test_skill.py` |
| [seo-performance](#seo-performance) | Engineering | `node …/tests/run.mjs` |
| [design-authenticity](#design-authenticity) | Design | `python3 …/tests/test_skill.py` |
| [design-system-ui](#design-system-ui) | Design | `node …/tests/run.mjs` |
| [figma-source-of-truth](#figma-source-of-truth) | Design | `python3 …/tests/test_skill.py` |
| [human-writing](#human-writing) | Writing/meta | `python3 …/tests/test_lint_text.py` |
| [skill-orchestrator](#skill-orchestrator) | Writing/meta | `python3 …/tests/test_orchestrator.py` |

Invoke convention used by all three hosts: name the skill with its exact
directory name and describe the task. Claude Code reads
`~/.claude/skills/`, Codex reads `~/.agents/skills/`, oh-my-pi loads both
roots plus its own managed skills; naming the skill keeps activation
deterministic instead of relying on description matching. Explicit parameter
lists (asset_type, polygon_budget, quality_profile, …) live in each
`SKILL.md`; defaults are sane — the agent stops only for missing references
or contradictory specs.

---

### `lowpoly-reference-to-blender`

Reference image → stylized low-poly Blender asset → validated GLB for
real-time engines (Defold and friends). Workflow: analyze reference → plan →
category build path (characters/faces, vehicles/karts, environments, props) →
multi-view blueprint gate → mesh validation → 0–100 quality score → export.
Needs live Blender MCP or background Blender Python (Blender 5.3 here; +Z up,
+Y facing, 1 BU = 1 m).

Install only this skill: `tools/install-skills.sh lowpoly-reference-to-blender`

- **Claude Code** (`~/.claude/skills/`): attaches to any 3D-from-reference
  ask; give it the concept art path or paste.
- **Codex** (`~/.agents/skills/`): same content, reference by name in the
  prompt; Codex surfaces it through its skills list.
- **oh-my-pi**: keeps Blender MCP live in-session — hand it the reference and
  the profile.

Shipped: `scripts/detect_blender.py` (system Python) + `inspect_scene.py`,
`render_reference_views.py`, `validate_mesh.py`, `export_glb.py`,
`verify_export.py` (run inside Blender: MCP or `blender -b --python`).
Reference art is the design authority — simplify allowed, substitute
forbidden; without visual comparison the skill emits `VISUAL_REVIEW_REQUIRED`
instead of a number. Outputs non-destructive, dated suffix on collision.

```text
Use lowpoly-reference-to-blender to build a high-quality game-ready low-poly
character from this concept art. asset_type=character, polygon_budget=2500,
quality_profile=hero.
```

```text
Use lowpoly-reference-to-blender on ./ref/hero-front.png — hero profile, keep
silhouette, GLB out, report the quality score with observations.
```

Verify: `blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py`

---

### `defold-development`

Universal Defold 1.14.1 game development, genre- and art-style-agnostic:
rendering (2D/pixel/voxel/2.5D/3D), Lua scripts and lifecycle, game
objects/collections/factories/proxies, physics, shaders/materials/PBR,
glTF/GLB with Draco/Meshopt/KTX2, local multiplayer, replay, GUI/fonts,
audio, profiling, `bob.jar` builds, DAP debugging. Engine claims are
version-gated; unverified items are marked, never invented.

Install only this skill: `tools/install-skills.sh defold-development`

- **Claude Code** (`~/.claude/skills/`): fires on any Defold task in a
  Defold project or a Defold question.
- **Codex** (`~/.agents/skills/`): name `defold-development` in the prompt.
- **oh-my-pi**: routes from the skill list; state the version when it matters.

Shipped: `scripts/audit_defold_project.py`, `bob_build.sh`, `check_build.sh`,
`check_version.py`, `gltf_preflight.py`, `validate_skill.py`. Routing loads
one reference set per task (21 references, never all).

```text
Use the defold-development skill to add split-screen local co-op to this
top-down shooter (Defold 1.14.1, Lua), with camera proxies and a focus plan.
```

```text
Use the defold-development skill: run a preflight on my glTF pipeline and tell
me which Draco/Meshopt flags are safe for the HTML5 target.
```

```text
Use the defold-development skill: implement save games with versioned schema
migration for this roguelike, non-destructive on old saves.
```

Verify: `python3 skills/defold-development/tests/test_skill.py`

---

### `godot`

Universal Godot 4.7.2 game development, genre- and art-style-agnostic:
renderer choice (Forward+/Mobile/Compatibility), scenes/nodes/resources,
GDScript static typing and C#, gameplay systems (movement, FSM/AI, save
games, input abstraction, cameras), Jolt/classic physics, navigation,
AnimationPlayer/AnimationTree, CanvasItem/Spatial shaders, TileMapLayer,
Control accessibility, audio buses, multiplayer RPC, headless CI/testing,
export to Linux/Windows/macOS/Web/mobile, glTF/Blender intake. Version-gated
claims; unverified items marked, never invented. The engine skills stay
neutral about each other; assets move through the GLB pipeline.

Install only this skill: `tools/install-skills.sh godot`

- **Claude Code** (`~/.claude/skills/`): activates on Godot work inside a
  `.godot`/`.tscn`/`.gd` project or a Godot question.
- **Codex** (`~/.agents/skills/`): reference `godot` explicitly.
- **oh-my-pi**: routes from the skill list; the local `godot` binary backs
  headless checks.

Shipped: `scripts/audit_godot_project.py`, `check_version.py`,
`headless_check.sh`, `validate_skill.py`. References (27) load per task.

```text
Use the godot skill to add coyote-time jumping to the player controller
(Godot 4.7, GDScript, static typing).
```

```text
Use the godot skill: implement a Jolt character body with input-buffered
double jump plus a headless test.
```

```text
Use the godot skill to review my AnimationTree: signals fire twice on scene
reload — find the root cause and fix it with a regression test.
```

Verify: `python3 skills/godot/tests/test_skill.py` ·
`bash skills/godot/scripts/headless_check.sh skills/godot/examples/base-project`

---

### `game-asset-pipeline-shaders`

Technical asset pipeline between asset creation and engine runtime, engine-
agnostic with Defold 1.14.1 + Godot 4.7.2 adapters (adapter contract extends
to Unity/Unreal/Bevy/custom renderers, WebGL/WebGPU): material/texture/shader
audits, glTF 2.0/GLB validation (mesh-codec vs KTX2 lanes kept separate),
safe dry-run-first repairs with `.orig` backups, art-style-aware rules
(pixel-art keeps lossless + nearest), disk-vs-VRAM budget reports, CI-ready
headless gates. Owns materials/textures/shaders/export; modeling stays in
`lowpoly-reference-to-blender`, engine APIs in `defold-development`/`godot`.
Estimates labeled `estimated`, unrun tests reported `NOT_RUN`.

Install only this skill: `tools/install-skills.sh game-asset-pipeline-shaders`

- **Claude Code** (`~/.claude/skills/`): activates on asset-pipeline tasks —
  textures, materials, shaders, glTF, export, VRAM budgets.
- **Codex** (`~/.agents/skills/`): reference `game-asset-pipeline-shaders`
  explicitly; modes (`audit|fix|optimize|shader|material|textures|export|
  validate|benchmark|compare`) travel in the request, not as slash-commands.
- **oh-my-pi**: routes from the skill list; Blender/Godot binaries back the
  HEADLESS lanes when present.

Shipped: `scripts/` — `asset_audit.py`, `gltf_validate.py`,
`texture_analyze.py`, `material_audit.py`, `pipeline_runner.py` (mode
dispatcher incl. validate/compare), `asset_report.py`, `tool_probe.py`,
`blender_preflight.py` (runs inside Blender 5.3). References (12) load per
mode; `assets/templates/asset-pipeline.yaml` is the project config.

```text
Use the game-asset-pipeline-shaders skill to audit this project's asset
pipeline — findings by severity, no writes, report what stayed NOT_RUN.
```

```text
Use the game-asset-pipeline-shaders skill: optimize mode on assets/textures,
profile mobile; disk vs VRAM separately, pixel-art keeps lossless sources.
```

Verify: `python3 skills/game-asset-pipeline-shaders/tests/test_skill.py` ·
`blender -b --python-expr "import sys; sys.path.insert(0,'skills/game-asset-pipeline-shaders/scripts'); import blender_preflight; blender_preflight.main()"`

---

### `game-audio-sound-design`

Game audio production + QA on top of the game-audio-forge backend (mandatory
prerequisite, separate repo, `~/dev/github/game-audio-forge`): SFX/music
generation driving `gaf`, adaptive-music and spatial-audio architectures,
mixing guidance with measured loudness gates, asset+engine audits
(`analyze|fix|optimize`, safe repairs → new files), performance budgets,
per-asset license statuses, engine adapters (Defold 1.14.1, Godot 4.7.2 —
verified APIs only). Doctor reports READY|PARTIALLY_READY|NOT_READY;
measurement states PASS|WARNING|FAIL|NOT_TESTED, creative quality always
`AUDIO_REVIEW_REQUIRED`. Offline LUFS honestly reported NOT_TESTED. Owns
audio assets/QA/integration; backend internals stay in game-audio-forge,
cross-cutting a11y in `accessibility`.

Install only this skill: `tools/install-skills.sh game-audio-sound-design`

- **Claude Code** (`~/.claude/skills/`): activates on audio/music/SFX/mix/
  audio-audit tasks; requires the forge backend for generation.
- **Codex** (`~/.agents/skills/`): reference `game-audio-sound-design`;
  modes (doctor/audit/fix/optimize/validate/manifest) travel in the request.
- **oh-my-pi**: routes from the skill list; ffmpeg + game-audio-forge back
  the live lanes.

Shipped: `scripts/` — `audio_doctor.py`, `audio_audit.py`, `audio_process.py`,
`audio_batch.py`, `audio_validate.py`, `audio_manifest.py`, `gaf_adapter.py`,
`engine_defold.py`, `engine_godot.py` (+ `audio_common.py`); `references/`
(15) load per step; `templates/` config/manifest/budget JSON.

```text
Use the game-audio-sound-design skill: audit this project's audio, fix mode
into a new directory, originals untouched, findings with severities and the
doctor verdict included.
```

```text
Use the game-audio-sound-design skill: generate a boss-fight music loop via
game-audio-forge, verify measured BPM and loop seam, manifest it with license
status.
```

Verify: `python3 skills/game-audio-sound-design/tests/test_skill.py`

---

### `astro`

Project-type-agnostic Astro development (baseline Astro 7.4.x, version-gated
against npm at task time): SSG/on-demand/mixed rendering, route caching,
islands and hydration directives, Actions, sessions, middleware, Content
Layer, MDX, headless CMS intake, `astro:assets`, Fonts API, SEO, Core Web
Vitals, WCAG 2.2 AA, CSP/adapters (node/netlify/vercel/cloudflare/static/
docker)/upgrades. Detects project type and loads only matching references
(17); Astro is never forced onto stacks that fit it better.

Install only this skill: `tools/install-skills.sh astro`

- **Claude Code** (`~/.claude/skills/`): attaches inside any Astro project.
- **Codex** (`~/.agents/skills/`): name `astro` in the prompt.
- **oh-my-pi**: private work is Astro-first by profile; routes automatically.

Shipped: `scripts/audit_astro_project.mjs` — project shape, versions, warnings
as evidence.

```text
Use the astro skill: this marketing site ships 400 KB of JS on the landing
page — find the islands that should be static and cut hydration, keep Actions
working.
```

```text
Use the astro skill: migrate Content Collections config to the Content Layer
without breaking routes; show the diff and the verification command.
```

```text
Use the astro skill: add session auth + middleware redirect for the dashboard,
SSR only where needed, static elsewhere.
```

Verify: `python3 skills/astro/tests/test_skill.py`

---

### `react-nextjs`

Project-type-agnostic React/Next.js development (baselines React 19.3.1,
Next.js 16.4.6, version-gated against the project lockfile): SPA/Vite, App/
Pages Router, Server vs Client Components, Suspense/streaming, Cache
Components and `use cache`, `proxy.ts` vs middleware, Server Functions,
Compiler memoization, hooks/TypeScript/state tooling, design systems, WCAG
2.2 AA, CWV, SEO/metadata, testing (Vitest/RTL/Playwright/axe), route/action/
cache security, deployment adapters, upgrades. Next.js is never forced.

Install only this skill: `tools/install-skills.sh react-nextjs`

- **Claude Code** (`~/.claude/skills/`): activates in any React/Next project.
- **Codex** (`~/.agents/skills/`): reference `react-nextjs` by name.
- **oh-my-pi**: routes from the skill list; Astro stays preferred for private
  frontend unless the repo already uses React/Next.

Mode gate → stack gate → version gate before any code; references (22) load
per task; ship gate uses real test/build output. Shipped:
`scripts/audit_react_project.mjs`, `check-versions.sh`.

```text
Use the react-nextjs skill: this dashboard re-renders the whole table on
filter change. Profile, then fix with memoization boundaries — behavior must
not change, show before/after flame evidence.
```

```text
Use the react-nextjs skill: audit App Router cache use against Cache
Components, list violations file:line, fix the P0s.
```

```text
Use the react-nextjs skill: add i18n (next-intl) with hreflang and locale
routing; keep CWV green, report LCP before/after.
```

Verify: `python3 skills/react-nextjs/tests/test_skill.py`

---

### `backend-api-engineering`

Framework-agnostic backend/API engineering: CREATE, AUDIT, FIX, OPTIMIZE
across Node (Fastify/NestJS/Express/Hono), Python (FastAPI/Django/DRF/Flask),
Go, Rust (Axum/Actix), Java/Kotlin, C#, PHP; PostgreSQL/MySQL/SQLite,
Mongo/Redis/search/vector; REST/GraphQL/gRPC/WebSocket/SSE. RFC 9457 errors,
OpenAPI validation, OWASP API Top 10, expand-contract migrations. Detects and
fixes (authz gaps, N+1, missing indexes, unvalidated input, tenancy gaps)
instead of only reporting. Unverified = NOT TESTED, never "working". Deep
security → ultimate-security-hardening; test strategy → ultimate-testing-qa;
refactors → ultimate-code-quality-refactoring.

Install only this skill: `tools/install-skills.sh backend-api-engineering`

- **Claude Code** (`~/.claude/skills/`): fires on backend/API work in any
  stack, any project age.
- **Codex** (`~/.agents/skills/`): name `backend-api-engineering`.
- **oh-my-pi**: routes from the skill list; reuses the project's real stack.

Shipped: `scripts/detect-project.sh`, `migration-review.sh`,
`validate-openapi.py`.

```text
Use the backend-api-engineering skill: audit the Fastify service in
services/api — authz per route, N+1 in listings, migration safety. Fix with
tests, show measurements.
```

```text
Use the backend-api-engineering skill: design schema + expand-contract
migration for multi-tenancy on this Django app; validate the OpenAPI output.
```

```text
Use the backend-api-engineering skill: optimize the top-3 slow Axum endpoints
— baseline, change, re-measure, report deltas.
```

Verify: `python3 skills/backend-api-engineering/tests/test_skill.py`

---

### `ultimate-security-hardening`

Security audit, hardening, remediation for any project (web, API, CLI, game
backends, containers, IaC; any language). Baselines: OWASP Top 10 2025, ASVS
5.0.0, API Security Top 10 2023, WSTG 4.2, CWE Top 25, SSDF, KEV/EPSS/CVSS,
CycloneDX. Spine: DISCOVER → THREAT MODEL → AUDIT → VALIDATE → PRIORITIZE →
FIX → REGRESSION TEST → RE-SCAN → REPORT. Orchestrates semgrep, gitleaks,
osv-scanner, trivy, ZAP with zero-dep fallbacks — a missing tool is a coverage
gap, never a pass. Never claims "secure"; secrets never leave the repo; errors
surface as INCOMPLETE.

Install only this skill: `tools/install-skills.sh ultimate-security-hardening`

- **Claude Code** (`~/.claude/skills/`): activates on any security task;
  Semgrep is the deterministic lane by profile, repo config wins.
- **Codex** (`~/.agents/skills/`): name `ultimate-security-hardening`.
- **oh-my-pi**: routes from the skill list; local tools + fallback scanners.

Shipped: `scripts/check-tools.sh`, `detect-project.sh`,
`run-security-audit.sh`, `validate-report.py`. Only confirmed findings get
fixes.

```text
Use the ultimate-security-hardening skill: audit services/api for authz,
injection, secrets exposure; fix confirmed findings with minimal diffs and
re-scan to prove them closed.
```

```text
Use the ultimate-security-hardening skill: threat-model the checkout flow,
then the dependency/supply-chain lane, report with CVSS + evidence file:line.
```

```text
Use the ultimate-security-hardening skill: audit infra/ for misconfig and
drift before release; patch only what you can prove.
```

Verify: `python3 skills/ultimate-security-hardening/tests/test_skill.py`

---

### `ultimate-testing-qa`

Testing/QA engineering for any web surface (Astro, React, Next.js, Vue/Nuxt,
Svelte/SvelteKit, Vite, vanilla, static; baselines Playwright, Vitest,
axe-core re-probed against the lockfile): test architecture, E2E and
cross-browser flows, unit/integration/component suites, live-site runtime/
console/network audits, visual/responsive regression, form testing, API checks,
bug reproduction → root-cause fix → retest, CI/CD gates. Existing setups
extended, never replaced without cause; untested paths report NOT TESTED.

Install only this skill: `tools/install-skills.sh ultimate-testing-qa`

- **Claude Code** (`~/.claude/skills/`): activates on any testing/QA task;
  Playwright uses Firefox per profile unless the repo demands otherwise.
- **Codex** (`~/.agents/skills/`): name `ultimate-testing-qa`.
- **oh-my-pi**: routes from the skill list; Firefox-default browser.

Shipped: `scripts/qa.mjs analyze <project>` — framework, package manager,
runners, routes, CI, evidence-only.

```text
Use the ultimate-testing-qa skill: equip this SvelteKit app with a test
architecture — Vitest units, Playwright E2E for checkout, CI gates — extend
the existing setup, never replace it.
```

```text
Use the ultimate-testing-qa skill: reproduce "form submits twice" on staging,
fix the root cause in source, retest, report what stayed untested.
```

```text
Use the ultimate-testing-qa skill: audit the live site — console errors,
network failures, visual regression on three breakpoints — then the QA report.
```

Verify: `node skills/ultimate-testing-qa/tests/run.mjs`

---

### `ultimate-code-quality-refactoring`

Code quality audit and controlled refactoring for any codebase (JS/TS,
React/Next, Astro, Vue/Svelte, Python, Go, Rust, Java/Kotlin, C#, PHP,
Lua/Defold, GDScript/Godot, Blender Python, C/C++; unknown → cautious generic
mode). Audits tech debt, smells, duplication, complexity hotspots, dead code,
architecture boundaries, perf suspects; refactors behavior-preservingly with
baseline→change→verify per step through the project's own lint/typecheck/test
tools. Risk-tiered autonomy (LOW auto-fix, HIGH approval), rollback protecting
uncommitted work, evidence-only PASS/FAIL/UNVERIFIED reports. Read-only AUDIT
is the default. Triggers include `/quality-audit`, `/quality-verify`.

Install only this skill: `tools/install-skills.sh ultimate-code-quality-refactoring`

- **Claude Code** (`~/.claude/skills/`): fires on "quality audit", "find
  technical debt", "/quality-audit".
- **Codex** (`~/.agents/skills/`): name `ultimate-code-quality-refactoring`.
- **oh-my-pi**: routes from the skill list; the project's own tools are the
  verification lane.

BUG FIX and FEATURE CHANGE refactors are separate lanes. Shipped:
`scripts/detect_project.py`, `run_audit.py`, `collect_metrics.py`,
`detect_duplicates.py`, `compare_baseline.py`, `verify_changes.py`,
`generate_report.py`.

```text
Use the ultimate-code-quality-refactoring skill: audit packages/core for
complexity hotspots and dead code; PASS/FAIL/UNVERIFIED only, no invented
scores.
```

```text
Use the ultimate-code-quality-refactoring skill: refactor the pricing module
without changing behavior — baseline, per-step verify, evidence report, keep
my uncommitted changes intact.
```

```text
Use the ultimate-code-quality-refactoring skill: /quality-verify — check the
staged diff against baseline before merge; FAIL the lane on behavior drift.
```

Verify: `python3 skills/ultimate-code-quality-refactoring/tests/test_skill.py`

---

### `ultimate-i18n-localization`

i18n/l10n for web (Astro, Next.js/next-intl, React/i18next, Vue/Nuxt, Svelte,
vanilla) and games (Godot, Defold), plus JSON/YAML/CSV/PO/FTL/XLIFF catalogs.
Modes: CREATE, AUDIT, FIX (additive-only, re-audited), TRANSLATE (plan+draft,
human approves), VALIDATE, PSEUDO (grapheme-based expansion stress), REPORT.
Key/placeholder/plural parity across locales, hreflang per Google rules,
engine probes where the runtime exists. de/en core, any CLDR language addable
(ar/he RTL). Never overwrites translations, never ships machine text as
approved, absent engines report NOT TESTED.

Install only this skill: `tools/install-skills.sh ultimate-i18n-localization`

- **Claude Code** (`~/.claude/skills/`): activates on i18n/l10n tasks;
  TRANSLATE output is a draft until a human approves.
- **Codex** (`~/.agents/skills/`): name `ultimate-i18n-localization`.
- **oh-my-pi**: routes from the skill list; `i18n` CLI is the deterministic
  lane.

Shipped: `scripts/i18n` CLI (`audit|check|fix|validate|pseudo|extract|report|
plan` — stack + locale dir + reference-locale detection, Godot/Lua probes where
the runtime exists).

```text
Use the ultimate-i18n-localization skill: audit locales/de.json vs en.json
parity — keys, placeholders, plurals — and fix drift additively.
```

```text
Use the ultimate-i18n-localization skill: CREATE the i18n stack for this Astro
site (de/en, hreflang, routing) and gate CI on confirmed blockers.
```

```text
Use the ultimate-i18n-localization skill: add Hebrew as RTL locale — parity
plan, pseudo stress, hreflang update, nothing shipped untranslated.
```

Verify: `node skills/ultimate-i18n-localization/tests/run.mjs`

---

### `documentation-technical-writing`

Documentation engineering for any project (web, backend, API, CLI, games,
pipelines, infra, monorepos): CREATE READMEs, API docs, architecture docs,
ADRs, guides, troubleshooting, tutorials; AUDIT against real project state
(completeness, correctness, quality, links, secrets); FIX with a P0–P4 ladder;
SYNC drift; GATE with checks. Evidence tiers
VERIFIED/DOCUMENTED/PLAUSIBLE/UNKNOWN — endpoints, commands, versions never
invented. Docs-first changes keep source out of scope unless asked. DE/EN
follows the project.

Install only this skill: `tools/install-skills.sh documentation-technical-writing`

- **Claude Code** (`~/.claude/skills/`): fires on "write a README", "document
  my API", "audit the docs", "is the documentation still true".
- **Codex** (`~/.agents/skills/`): name `documentation-technical-writing`.
- **oh-my-pi**: routes from the skill list; zero-dep Python CLIs carry JSON
  reports + exit codes.

Shipped: `scripts/docs_audit.py`, `docs_check.py`, `docs_sync.py`, `docs_lib.py`.

```text
Use the documentation-technical-writing skill: audit docs/ against src/ — which
endpoints and commands are still true? P0-P4 fix list, honest NOT RUN for what
you cannot execute.
```

```text
Use the documentation-technical-writing skill: SYNC changelog and README after
the v2 migration, then GATE before release.
```

```text
Use the documentation-technical-writing skill: CREATE the ADR set for the new
caching layer — decisions against the real code, tiers labeled.
```

Verify: `python3 skills/documentation-technical-writing/tests/test_skill.py`

---

### `accessibility`

Accessibility engineering and auditing across every web surface (HTML/CSS/
JS/TS, React, Next.js, Astro, Vue/Svelte, SPAs/SSR/SSG, webshops, dashboards,
forms, design systems). WCAG 2.2 A/AA binding, AAA as a separate tier. Owns
the a11y layer across framework skills. Automated PASS ≠ conformance: reports
always separate automated gate from manual and screenreader evidence.

Install only this skill: `tools/install-skills.sh accessibility`

- **Claude Code** (`~/.claude/skills/`): activates on a11y/WCAG tasks; the SR
  harness gates its own environment (Orca/Guidepup) rather than faking passes.
- **Codex** (`~/.agents/skills/`): name `accessibility`.
- **oh-my-pi**: routes from the skill list; repo config (Semgrep lane,
  Playwright Firefox) stays authoritative.

Mode gate first: Build / Audit (WCAG-EM 2.0 slice) / Remediate. Shipped:
`scripts/check-standards.mjs <url>` (axe + Playwright audit; JSON/HTML/JUnit/
SARIF, CI exit codes), `scripts/setup-check.sh` (environment gating).

```text
Use the accessibility skill: audit /checkout for WCAG 2.2 AA — automated axe
gate plus keyboard/focus evidence, and list what needs manual review.
```

```text
Use the accessibility skill: build the modal keyboard-first (focus trap, ESC,
restore focus) and prove it with the SR harness or mark the gap honestly.
```

```text
Use the accessibility skill: is this form WCAG 2.2 AA — labels, errors, focus
order, contrast? Automated gate and manual checklist, separately.
```

Verify: `python3 skills/accessibility/tests/test_skill.py`

---

### `seo-performance`

Technical SEO and web performance for any framework (Astro, Next.js app/pages,
React/Vite/CSR, static, CMS via URL): crawling, indexability, canonicals,
sitemaps, robots, hreflang; Core Web Vitals (LCP/INP/CLS/TTFB/TBT) with
lab-vs-field discipline; delivered-HTML vs JS-rendered DOM checks;
schema.org/JSON-LD validation; AI-search readiness; approval-gated auto-fixes;
CI gates; regression monitoring. Works offline, no API keys, never invents
scores.

Install only this skill: `tools/install-skills.sh seo-performance`

- **Claude Code** (`~/.claude/skills/`): activates on SEO/speed asks ("why is
  LCP bad", indexation/schema/hreflang, CI SEO gates).
- **Codex** (`~/.agents/skills/`): name `seo-performance`.
- **oh-my-pi**: routes from the skill list; the auditor is zero-dependency
  Node.

Entry picks one workflow, loads ONE reference (12); audit levels
auto-escalate, never silently. Shipped: `scripts/seo.mjs <url>` —
`audit|fix|performance|technical|content|schema|monitor|ci|compare|serve` +
optional Lighthouse/Unlighthouse/LHCI/Playwright when present.

```text
Use the seo-performance skill: audit https://example.com — indexation,
canonicals, schema, LCP/INP — then the fix list with approval gates.
```

```text
Use the seo-performance skill: why is LCP bad on the product page? Lab + field
comparison, delivered-HTML check, minimal fixes only.
```

```text
Use the seo-performance skill: hreflang + canonical audit for the de/en locale
pair per Google rules, then validate the JSON-LD blocks.
```

Verify: `node skills/seo-performance/tests/run.mjs`

---

### `design-authenticity`

Design authenticity and anti-AI-slop discipline for any UI (websites, SaaS,
dashboards, docs, PWAs, game menus/HUDs; audits of React/Next/Astro projects).
Modes CREATE / REVIEW / REFACTOR / GUARD. Product-context-first identity, a
Design Identity Engine, Anti-AI-Slop detection (default gradients, hero+card
templates, glass/glow blobs, decoration without purpose), a 100-pt visual gate
(target ≥90), screenshot review when a browser exists, WCAG AA as hard floor.
Framework skills own architecture, accessibility owns a11y; this owns
originality, coherence, product-fit. Zero external services.

Install only this skill: `tools/install-skills.sh design-authenticity`

- **Claude Code** (`~/.claude/skills/`): activates on design/identity/review;
  scores only with visual comparison, else flags for review.
- **Codex** (`~/.agents/skills/`): name `design-authenticity`.
- **oh-my-pi**: routes from the skill list; screenshot review when a browser
  exists, otherwise flagged, not scored.

Shipped: `scripts/validate_config.mjs` (identity-config schema),
`scripts/screenshot_audit.sh <url>` when a browser is available.

```text
Use the design-authenticity skill: REVIEW the landing page — score on the
100-pt gate, flag every generic pattern with file:line, propose product-fit
replacements.
```

```text
Use the design-authenticity skill: CREATE the visual identity for a docs
product — typography, color, layout rationale — brand-preserving, no templates.
```

```text
Use the design-authenticity skill: GUARD — check my next component PR against
the identity rules before I merge.
```

Verify: `python3 skills/design-authenticity/tests/test_skill.py`

---

### `design-system-ui`

Design-system and UI-component engineering for any web project (plus game-UI
token concepts for Godot/Defold). CREATE token systems (DTCG v2025.10), AUDIT
inconsistency (duplicate colors/buttons/spacing, broken dark mode, unused
tokens), FIX safely, MIGRATE legacy UI, VALIDATE tokens/themes, DOCUMENT
components. Boundaries: one-off styling is not a system (just style it); deep
a11y → accessibility; aesthetic originality → design-authenticity; E2E/browser
QA → ultimate-testing-qa.

Install only this skill: `tools/install-skills.sh design-system-ui`

- **Claude Code** (`~/.claude/skills/`): triggers on "design system", "design
  tokens", "dark mode broken", "duplicate components".
- **Codex** (`~/.agents/skills/`): name `design-system-ui`.
- **oh-my-pi**: routes from the skill list; `ds.mjs` is the deterministic lane.

Evidence before edits; token builds run through the shipped pipeline. Shipped:
`scripts/ds.mjs` (zero-dep `detect|tokens|audit|report` + token build,
file:line evidence).

```text
Use the design-system-ui skill: audit this Astro project for duplicate colors
and spacing — file:line evidence, then the safe fix order.
```

```text
Use the design-system-ui skill: CREATE a DTCG token system from our exported
palette; build step, no runtime dependency.
```

```text
Use the design-system-ui skill: dark mode breaks in three components — audit,
fix, and document the token contract that prevents regressions.
```

Verify: `node skills/design-system-ui/tests/run.mjs`

---

### `figma-source-of-truth`

Figma-as-source-of-truth UI policy for projects that have a Figma design
system: Figma and Code Connect decisions outrank general frontend guidance;
implementation must not invent a competing design system. Tokens come from
the Figma library, production components get reused, divergence is reported
with node names — never silently redesigned. Inert without Figma:
`design-authenticity` and `design-system-ui` stay in charge there.

Install only this skill: `tools/install-skills.sh figma-source-of-truth`

- **Claude Code** (`~/.claude/skills/`): activates on UI work in projects
  with Figma files or Code Connect mappings.
- **Codex** (`~/.agents/skills/`): name `figma-source-of-truth`.
- **oh-my-pi**: routes from the skill list; the scope gate keeps it inert
  without Figma.

```text
Use the figma-source-of-truth skill: build the checkout component against
Figma node 12:340; Code Connect maps it to <CheckoutSummary>.
```

```text
Use the figma-source-of-truth skill: our button diverges from the library —
report the mismatch against the named nodes, do not redesign.
```

Verify: `python3 skills/figma-source-of-truth/tests/test_skill.py`

---

### `human-writing`

Human prose in German and English: generate, rewrite, audit, calibrate blog
posts, docs, READMEs, marketing copy, UX texts, creative writing, dialogue,
emails, reports. Anti-AI-slop rules and personal-voice preservation. Detection
and rules only — reports never assert authorship; rewriting is authored by the
agent and applied only after approval. Python 3.10+, stdlib only, offline
(network only for public URL audits).

Install only this skill: `tools/install-skills.sh human-writing`

- **Claude Code** (`~/.claude/skills/`): activates on write/humanize/de-slop/
  audit-text; reports stay authorship-free.
- **Codex** (`~/.agents/skills/`): name `human-writing`; rewrite applies only
  after you approve the diff.
- **oh-my-pi**: routes from the skill list; project rewrite defaults to
  dry-run.

Mode selection first (generate/rewrite/audit/calibrate). Shipped:
`scripts/lint_text.py` (offline), `website_audit.py` (SSRF-guarded crawler,
fixtures mode), `project_audit.py` (safe rewrite, dry-run default; `hw_*.py`
libs).

```text
Use the human-writing skill: audit the prose on https://example.com/blog —
slop patterns, rhythm, voice — report only, no edits.
```

```text
Use the human-writing skill: de-slop docs/README.md EN + DE, keep terminology,
show the lint verdict before and after.
```

```text
Use the human-writing skill: rewrite these three changelog versions against my
previous posts — which is most me? Evidence, not vibes.
```

Verify: `python3 skills/human-writing/tests/test_lint_text.py` (also
`test_project_audit.py`, `test_website_audit.py`)

---

### `skill-orchestrator`

Quality and orchestration manager for this repository itself: discovery,
inventory, validation, audit, scoring, routing plans, overlap truth,
regression snapshots, repair proposals. Deterministic Python 3 CLI over real
files — discovery never invents skills, scoring never credits unchecked areas,
agent-evals report UNAVAILABLE instead of faking passes. Read-only by default;
repairs are proposals until approved. Coordinates other skills without
duplicating their domains.

Install only this skill: `tools/install-skills.sh skill-orchestrator`
(inside this checkout the CLI also runs directly from `scripts/`, installed or
not).

- **Claude Code** (`~/.claude/skills/`): activates on repo-level questions
  ("audit my skill collection", "is skill X valid?", "which skills serve
  this?").
- **Codex** (`~/.agents/skills/`): name `skill-orchestrator`.
- **oh-my-pi**: routes from the skill list; plans stay honest about what was
  evaluated.

Commands `scan|audit|overlap|route|plan|test|eval|fix|report|doctor`, profiles
`portable|claude|codex`, `--json` for machine output; `fix` rewrites nothing
without approval.

```text
Use the skill-orchestrator skill: audit the collection, profile portable, show
the regression diff against the stored baseline.
```

```text
Use the skill-orchestrator skill: route "accessible Astro marketing site with
i18n and SEO gates" — which skills, in which order, why.
```

Verify: `python3 skills/skill-orchestrator/tests/test_orchestrator.py`

This suite also validates collection metadata with the shared validator.
Static audits award at most 5/15 test points for test structure; test
execution and behavior remain NOT RUN and earn no points until verified.

---

Every skill additionally carries `references/` deep docs (5–27 files each),
loaded by its SKILL.md routing tables only when the task needs them.

## Install (Claude Code + Codex)

```bash
tools/install-skills.sh                  # symlink ALL skills into ~/.claude/skills and ~/.agents/skills
tools/install-skills.sh godot astro      # symlink ONLY the named skills
tools/uninstall-skills.sh                # remove ONLY links this repo created
tools/uninstall-skills.sh godot          # remove ONLY the named skills
```

Idempotent; foreign skills in the target dirs are never modified. Skill names
are the directory names under `skills/`; an unknown name aborts the install
before anything is linked. Installed links are recorded in
`.installed-manifest` (`<skill-name><TAB><target-root>` per line); the
uninstaller trusts only that manifest and keeps entries for skills that
remain installed.

Installer and uninstaller require `flock`, share a repository lock, and
replace the manifest atomically. Installer tests use a temporary repository
and leave the live installation manifest untouched.

Verify what is installed: `cat .installed-manifest` (untracked, local state).

## Use

Detailed per-skill usage (Claude Code, Codex, oh-my-pi invocation plus
copy-paste examples) lives in the [Skills](#skills) sections above — that is
the canonical text. `skills/<name>/USAGE.md` mirrors the same guide into the
symlinked skill folder so an agent browsing the directory locally sees it too.
When a skill's scripts or entry points change, update both.

```
Use lowpoly-reference-to-blender to build a high-quality game-ready low-poly
character for Riff Racers from this concept art.
```

Optional parameters (asset_type, polygon_budget, quality_profile, views, …)
are documented in each SKILL.md; defaults are sane, the agent only stops for
missing references or contradictory specs.

## Validate

Full-suite runs (from the repo root):

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
python3 -m py_compile skills/*/scripts/*.py skills/*/tests/*.py
TEST_HOME=$(mktemp -d) bash tools/test_installer.sh
python3 skills/godot/tests/test_skill.py
bash skills/godot/scripts/headless_check.sh skills/godot/examples/base-project
```

Per-skill entry points are in the Verify column of each table above. Each
skill is independently installable, independently testable, and versionable
on its own.

## Adding skills

`docs/adding-new-skills.md`. Each skill stays independent: its own directory,
testable on its own, versionable on its own.

## Environment truth (last probe: 2026-11-13)

Blender **5.3.0** (`02f0899d`, bundled Python 3.13) at
`~/.local/opt/blender-5.3.0-linux-x64/blender`; BlenderMCP addon 1.8 live
(protocol 15); system `python3` 3.14 without `bpy`.
Godot **4.7.2-stable** (`ed1daf0b`) at `~/.local/opt/godot-4.7.2/godot`,
on PATH as `godot`; headless import/run verified.
