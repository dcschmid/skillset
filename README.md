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
skills/<name>/USAGE.md      per-skill usage guide (Claude Code/Codex/omp, examples)
skills/<name>/references/   deep docs, loaded on demand
skills/<name>/scripts/      working automation (Blender Python, system Python)
skills/<name>/assets/       templates reused per run
skills/<name>/tests/        runnable validation
profiles/<project>.md       optional project overlays (never auto-applied)
tools/                      installer / uninstaller / installer tests
docs/                       architecture + authoring guides
```

## Skills

Seventeen skills, grouped by domain. "Ships" lists the automation each skill
carries; "Verify" is its own validation entry point (runnable from the repo
root; all exit 0 on PASS).

### Game development

| Skill | Scope | Ships | Verify |
|---|---|---|---|
| [lowpoly-reference-to-blender](skills/lowpoly-reference-to-blender/SKILL.md) | Reference image → stylized low-poly Blender asset → validated GLB (Defold-ready). Workflow: analyze reference → plan → category build path → multi-view blueprint gate → mesh validation → 0–100 quality score → export. Requires live Blender MCP or background Blender Python. | `detect_blender.py`, `inspect_scene.py`, `render_reference_views.py`, `validate_mesh.py`, `export_glb.py`, `verify_export.py` | `blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py` |
| [defold-development](skills/defold-development/SKILL.md) | Universal Defold 1.14.1 game development, genre- and art-style-agnostic: rendering, Lua lifecycle, game objects/collections, physics, shaders, glTF import, GUI/fonts, audio, profiling, `bob.jar` builds, DAP debugging. Engine claims are version-gated; unverified items marked, never invented. | `audit_defold_project.py`, `bob_build.sh`, `check_build.sh`, `check_version.py`, `gltf_preflight.py`, `validate_skill.py` | `python3 skills/defold-development/tests/test_skill.py` |
| [godot](skills/godot/SKILL.md) | Universal Godot 4.7.2 game development, genre- and art-style-agnostic: renderer choice, scenes/nodes/resources, GDScript static typing and C#, gameplay systems, Jolt/classic physics, shaders, TileMapLayer, Control a11y, multiplayer RPC, headless CI, export pipelines, glTF/Blender intake. | `audit_godot_project.py`, `check_version.py`, `headless_check.sh`, `validate_skill.py` | `python3 skills/godot/tests/test_skill.py` |

The two engine skills stay engine-neutral about each other; assets move
between them through the GLB pipeline verified by
lowpoly-reference-to-blender.

### Web frameworks

| Skill | Scope | Ships | Verify |
|---|---|---|---|
| [astro](skills/astro/SKILL.md) | Astro 7.4.x project work of any type (portfolio, blog, docs, product, SSR dashboards): rendering modes, islands/hydration, Actions, sessions, middleware, Content Layer, MDX, `astro:assets`, SEO, Core Web Vitals, adapters. Detects project type and loads only matching references; Astro is never forced onto stacks that fit it worse. | `audit_astro_project.mjs` | `python3 skills/astro/tests/test_skill.py` |
| [react-nextjs](skills/react-nextjs/SKILL.md) | React 19.3 / Next.js 16.4 project work of any type: Server vs Client Components, Suspense/streaming, Cache Components, Server Functions, Compiler, hooks/typing/state tooling, testing stacks, CWV, SEO/metadata, deployment adapters. Version-gated against the project lockfile; Next.js is never forced. | `audit_react_project.mjs`, `check-versions.sh` | `python3 skills/react-nextjs/tests/test_skill.py` |

### Engineering disciplines (framework-agnostic)

| Skill | Scope | Ships | Verify |
|---|---|---|---|
| [backend-api-engineering](skills/backend-api-engineering/SKILL.md) | Backend/API CREATE·AUDIT·FIX·OPTIMIZE across Node/Python/Go/Rust/Java/C#/PHP stacks, SQL/NoSQL, REST/GraphQL/gRPC/WebSocket/SSE. Authn/authz, schema + expand-contract migrations, architecture, deploy prep. Detects and fixes (authz gaps, N+1, missing indexes) instead of only reporting; hands deep security to ultimate-security-hardening, test strategy to ultimate-testing-qa. | `detect-project.sh`, `migration-review.sh`, `validate-openapi.py` | `python3 skills/backend-api-engineering/tests/test_skill.py` |
| [ultimate-security-hardening](skills/ultimate-security-hardening/SKILL.md) | Security audit + hardening for any project: OWASP Top 10 2025, ASVS 5, API Security Top 10, WSTG, CWE Top 25. Spine DISCOVER→THREAT MODEL→AUDIT→VALIDATE→PRIORITIZE→FIX→REGRESSION TEST→RE-SCAN→REPORT. Orchestrates semgrep/gitleaks/osv-scanner/trivy/ZAP with zero-dep fallbacks; a missing tool is a coverage gap, never a pass. | `check-tools.sh`, `detect-project.sh`, `run-security-audit.sh`, `validate-report.py` | `python3 skills/ultimate-security-hardening/tests/test_skill.py` |
| [ultimate-testing-qa](skills/ultimate-testing-qa/SKILL.md) | Testing/QA engineering for any web surface: test architecture, E2E and cross-browser flows, unit/component/integration suites, live-site runtime audits, visual/responsive regression, bug reproduction → root-cause fix → retest, CI gates. Existing setups extended, never replaced without cause; untested paths report NOT TESTED. | `qa.mjs` (framework/runner/routes/CI analyzer) | `node skills/ultimate-testing-qa/tests/run.mjs` |
| [ultimate-code-quality-refactoring](skills/ultimate-code-quality-refactoring/SKILL.md) | Tech-debt/smell/complexity/dead-code audits for any language, and behavior-preserving refactors with baseline→change→verify per step. Risk-tiered autonomy (LOW auto-fix, HIGH approval), rollback protecting uncommitted work, evidence-only PASS/FAIL/UNVERIFIED reports. Read-only AUDIT is the default. | `detect_project.py`, `run_audit.py`, `collect_metrics.py`, `detect_duplicates.py`, `compare_baseline.py`, `verify_changes.py`, `generate_report.py` | `python3 skills/ultimate-code-quality-refactoring/tests/test_skill.py` |
| [ultimate-i18n-localization](skills/ultimate-i18n-localization/SKILL.md) | i18n/l10n for web frameworks and Godot/Defold plus JSON/YAML/CSV/PO/FTL/XLIFF catalogs: CREATE·AUDIT·FIX·TRANSLATE·VALIDATE·PSEUDO·REPORT. Key/placeholder/plural parity across locales, hreflang per Google rules, engine probes where the runtime exists; never overwrites translations or ships machine text as approved. | `i18n` CLI (`audit|check|fix|validate|pseudo|extract|report|plan`) | `node skills/ultimate-i18n-localization/tests/run.mjs` |
| [documentation-technical-writing](skills/documentation-technical-writing/SKILL.md) | Documentation engineering: CREATE/AUDIT/FIX/SYNC/GATE READMEs, API/arch/ADR/guides against real project state. P0–P4 fix ladder, evidence tiers VERIFIED/DOCUMENTED/PLAUSIBLE/UNKNOWN, honest NOT RUN verdicts; docs-first changes never touch source unless asked. | `docs_audit.py`, `docs_check.py`, `docs_sync.py`, `docs_lib.py` | `python3 skills/documentation-technical-writing/tests/test_skill.py` |
| [accessibility](skills/accessibility/SKILL.md) | WCAG 2.2 A/AA engineering and audits on any web surface (AAA as separate tier): build/review/test/fix, WCAG-EM audit slices, remediation. Ships a runnable axe+Playwright auditor (JSON/HTML/JUnit/SARIF, CI exit codes), keyboard/focus auditor, screenreader harness with environment gating. Automated PASS ≠ conformance: reports always separate automated, manual, and SR evidence. | `check-standards.mjs`, `setup-check.sh` | `python3 skills/accessibility/tests/test_skill.py` |
| [seo-performance](skills/seo-performance/SKILL.md) | Technical SEO + Core Web Vitals for any framework: crawling/indexability/canonicals/sitemaps/hreflang, LCP/INP/CLS/TTFB/TBT with lab-vs-field discipline, schema.org validation, AI-search readiness, approval-gated auto-fixes, CI gates, regression monitoring. Works offline, no API keys, never invents scores. | `seo.mjs` (`audit|fix|performance|technical|content|schema|monitor|ci|compare|serve`) | `node skills/seo-performance/tests/run.mjs` |

### Design

| Skill | Scope | Ships | Verify |
|---|---|---|---|
| [design-authenticity](skills/design-authenticity/SKILL.md) | Anti-AI-slop visual discipline for any UI: CREATE/REVIEW/REFACTOR/GUARD. Product-context-first identity, originality gates, 100-pt rubric (target ≥90), screenshot review when a browser exists, WCAG AA as hard floor. Framework skills own architecture; accessibility owns a11y; this owns originality and product-fit. | `screenshot_audit.sh`, `validate_config.mjs` | `python3 skills/design-authenticity/tests/test_skill.py` |
| [design-system-ui](skills/design-system-ui/SKILL.md) | Token and component-system engineering: CREATE DTCG v2025.10 systems, AUDIT inconsistency (duplicate colors/buttons, broken dark mode, scattered values), FIX safely, MIGRATE, VALIDATE, DOCUMENT; game-UI token concepts for Godot/Defold. Not for one-off styling (→ style it), deep a11y (→ accessibility), originality (→ design-authenticity). | `ds.mjs` (zero-dep detect/tokens/audit/report + token build) | `node skills/design-system-ui/tests/run.mjs` |

### Writing & meta

| Skill | Scope | Ships | Verify |
|---|---|---|---|
| [human-writing](skills/human-writing/SKILL.md) | Human prose in DE/EN: generate/rewrite/audit/calibrate for docs, READMEs, marketing, UX copy, creative text; anti-AI-slop rules; voice preservation. Reports never assert authorship; rewriting is applied only after approval. Python 3.10+, stdlib only, offline-first. | `lint_text.py`, `website_audit.py` (SSRF-guarded crawler), `project_audit.py` (dry-run default), `hw_*` libs | `python3 skills/human-writing/tests/test_lint_text.py` (also `test_project_audit.py`, `test_website_audit.py`) |
| [skill-orchestrator](skills/skill-orchestrator/SKILL.md) | Meta-manager of this repo: discovery, inventory, validation, routing plans, overlap truth, scoring, regression snapshots, repair proposals. Deterministic Python 3 CLI over real files; read-only by default; agent-evals report UNAVAILABLE instead of faking passes. | `skill-orchestrator` CLI | `python3 skills/skill-orchestrator/tests/test_orchestrator.py` |

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

Verify what is installed: `cat .installed-manifest` (untracked, local state).

## Use

Each skill ships `skills/<name>/USAGE.md`: how to invoke that skill in
Claude Code, Codex, and oh-my-pi (omp), copy-paste prompt examples, and how
to run its own validation. See also the Verify column in the skill tables
above.

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
