# skillset

Reusable skills for Claude Code, Codex, and oh-my-pi. Each skill gives an agent
a workflow for a particular job: what to inspect first, how to proceed, and how
to verify the result. Name the skill and describe your goal; the agent works in
your current project using its rules and tools.

The collection contains **27 skills** covering web development, backends, games,
design, security, testing, and writing. These guides are for people. Each
`SKILL.md` contains the binding agent instructions.

## Get started

Run the installer from this checkout. The shell scripts require Bash and
`flock`; other requirements depend on the selected skill.

```bash
# Install selected skills:
tools/install-skills.sh documentation-technical-writing human-writing

# Or install the whole collection according to its profile routing:
tools/install-skills.sh
```

Open your target project in Claude Code, Codex, or oh-my-pi and enter a prompt:

```text
Use documentation-technical-writing and human-writing.
Rewrite README.md in English for new developers.
Check installation, start, and test instructions against the project files.
Add a getting-started example and identify checks you could not run.
```

This is a prompt in the client, not a terminal command. Naming the skill makes
your intended workflow explicit. Installing it does not activate it for every
subsequent task.

## Choose a skill

| Task | Start with |
|---|---|
| Build an Astro site | `astro` |
| Maintain an existing React or Next.js project | `react-nextjs` |
| Work on an API, database, or migration | `backend-api-engineering` |
| Reproduce a problem in the browser | `playwright` |
| Add tests or fix and retest a web bug | `ultimate-testing-qa` |
| Audit or improve accessibility | `accessibility` |
| Investigate SEO or loading performance | `seo-performance` |
| Develop a visual identity, maintain tokens, or implement Figma requirements | `design-authenticity`, `design-system-ui`, `figma-source-of-truth` |
| Build gameplay | `godot` or `defold-development` |
| Work on 3D assets, textures, or audio | `lowpoly-reference-to-blender`, `game-asset-pipeline-shaders`, `game-audio-sound-design` |
| Review, simplify, or harden code | `ultimate-code-review`, `ultimate-code-quality-refactoring`, `lean-engineering`, `ultimate-security-hardening` |
| Address failing CI or review comments | `ci-triage`, `review-followup` |
| Check security-relevant changes with Semgrep | `semgrep-security` |
| Add or validate localization | `ultimate-i18n-localization` |
| Improve documentation or prose | `documentation-technical-writing`, `human-writing` |
| Inspect an agent runtime or the skill collection | `agent-harness-engineering`, `skill-orchestrator` |

Choose the skill needed for the current step. Add another when the task calls
for its expertise; you do not need to load an entire group.

## Installation and profiles

The installer creates symlinks to this repository rather than copying files.
Edits here become visible through those links. Keep the checkout in place
while using the installation.

Routing is defined in [tools/profile-map.tsv](tools/profile-map.tsv). Skills
without an entry default to both profiles.

| Scope | Persistent target directories |
|---|---|
| `both` | `~/.claude/skills`, `~/.agents/skills`, `~/.omp/profiles/private/agent/skills`, `~/.omp/profiles/working/agent/skills` |
| `private` | `~/.codex/skills`, `~/.omp/profiles/private/agent/skills` |
| `working` | `$MM_CODEX_WORKING_HOME/skills`, `~/.omp/profiles/working/agent/skills` |

Without `MM_CODEX_WORKING_HOME`, the installer uses
`$MM_STACK_DATA_HOME/codex-working-home/skills`. Without `MM_STACK_DATA_HOME`,
the stack root is `${XDG_DATA_HOME:-$HOME/.local/share}/frontend-ai-stack`.
These variables come from the existing profile setup or an explicit override.

Claude Code has one shared skill directory. Synchronize profile-specific skills
when choosing the profile:

```bash
tools/install-skills.sh --claude private
# When switching to Working:
tools/install-skills.sh --claude working
```

The last synchronization determines the contents of Claude's shared directory.
Persistent Codex and OMP roots are unaffected. `--claude` accepts no extra skill
names and synchronizes the entire profile. Foreign files and links are left
alone; the installer reports conflicts.

Private includes game development, Astro, `design-authenticity`, and
`design-system-ui`. Working includes `react-nextjs` and `figma-source-of-truth`.
All remaining skills support both profiles. OMP uses its native profile roots
and its own credentials. OMP work stays in OMP and is not routed to Codex or Claude.

### Inspect or remove an installation

```bash
# Inspect locally recorded installation targets:
cat .installed-manifest

# Remove one skill:
tools/uninstall-skills.sh godot

# Remove all links managed by this repository:
tools/uninstall-skills.sh
```

The manifest stores a skill name and target root per line, separated by a tab.
The installer and uninstaller manage their own links. Unknown names abort
installation before links are created. After changing a skill's scope, reinstall
it to prune stale persistent links.

## Write a useful request

Specify the goal, location, expected behavior, and constraints. For bugs, add
reproduction steps. For audits, say whether you want findings only or fixes too.

```text
Use ultimate-testing-qa.
Project: current repository; start it with the existing dev script.
Bug: double-clicking “Place order” creates two orders.
Reproduce the flow, fix the cause, and retest it.
Use existing tests and report any checks left open.
```

The examples use ordinary prompts and exact skill names. Labels such as
`/lean audit` or `/docs-check` in individual skills identify workflows.
Registered slash-command support depends on the host; spelling out the task
works without that registration.

### Combine skills when the task needs it

```text
Use astro for implementation and accessibility for accessibility checks.
Add a contact form with validation states to the existing project.
Check the build, keyboard interaction, focus, and useful error messages.
```

```text
Use backend-api-engineering for the authorization fix and semgrep-security
for the follow-up security check. Preserve the API contract and test access
to another user's data.
```

Every skill works independently. A skill supplies instructions, not missing
programs, runtimes, or authenticated access. Existing authorization remains
valid; external publishing and high-risk actions must be covered by the request.

## Repository layout

```text
skills/<name>/SKILL.md     Agent entry point and binding workflow
skills/<name>/README.md    Human-facing guide and technical details
skills/<name>/references/  Detail loaded only when needed
skills/<name>/scripts/     Executable tools, where provided
skills/<name>/assets/      Templates and support files, where provided
skills/<name>/tests/       Self-tests and validation
profiles/                 Optional project requirements
tools/                    Installation, routing, and installer tests
docs/                     Architecture and authoring guidance
```

Skills do not all need scripts or the same subdirectories. Project-specific
instructions load only when the task names the project.

## Skills

The sections below introduce every skill with practical usage examples. Each
skill’s README combines its usage guide, host examples, and technical details.
Prompts can be used in any of the three clients when the skill and required
tools are available. Self-tests check the skill and its supplied checks; changes
to your target project still need that project's own verification.

| Skill | Purpose | Profile |
|---|---|---|
| [lowpoly-reference-to-blender](#lowpoly-reference-to-blender) | Build 3D assets from reference images | private |
| [defold-development](#defold-development) | Develop games with Defold | private |
| [godot](#godot) | Develop games with Godot | private |
| [game-asset-pipeline-shaders](#game-asset-pipeline-shaders) | Check materials, textures, and exports | private |
| [game-audio-sound-design](#game-audio-sound-design) | Generate and validate game audio | private |
| [astro](#astro) | Build websites with Astro | private |
| [react-nextjs](#react-nextjs) | Maintain React and Next.js projects | working |
| [backend-api-engineering](#backend-api-engineering) | Build and repair backends and APIs | both |
| [ultimate-security-hardening](#ultimate-security-hardening) | Investigate and fix security issues | both |
| [ultimate-testing-qa](#ultimate-testing-qa) | Test web applications and verify fixes | both |
| [ultimate-code-quality-refactoring](#ultimate-code-quality-refactoring) | Audit code quality and refactor safely | both |
| [ultimate-code-review](#ultimate-code-review) | Review changes with concrete evidence | both |
| [ultimate-i18n-localization](#ultimate-i18n-localization) | Build and validate localization | both |
| [documentation-technical-writing](#documentation-technical-writing) | Keep technical documentation useful and accurate | both |
| [accessibility](#accessibility) | Build and audit accessible interfaces | both |
| [seo-performance](#seo-performance) | Investigate discoverability and loading performance | both |
| [ci-triage](#ci-triage) | Diagnose failing CI jobs | both |
| [review-followup](#review-followup) | Address review comments against current code | both |
| [semgrep-security](#semgrep-security) | Verify security-relevant changes with Semgrep | both |
| [playwright](#playwright) | Inspect interfaces in a real browser | both |
| [agent-harness-engineering](#agent-harness-engineering) | Inspect agent runtimes and tool contracts | both |
| [lean-engineering](#lean-engineering) | Deliver complete solutions with less complexity | both |
| [design-authenticity](#design-authenticity) | Develop a visual identity that fits the product | private |
| [design-system-ui](#design-system-ui) | Keep tokens, themes, and components consistent | private |
| [figma-source-of-truth](#figma-source-of-truth) | Preserve Figma requirements in implementation | working |
| [human-writing](#human-writing) | Write clear, natural prose | both |
| [skill-orchestrator](#skill-orchestrator) | Inspect the collection and route tasks | both |

### `lowpoly-reference-to-blender`

Turn concept art into a stylized low-poly Blender asset, from reference analysis and reconstructed views to mesh validation and GLB export.

Profile: Private. Preparation: Provide the reference image, asset type, polygon budget, and target engine. Extra views help resolve hidden shapes.

Expected result: A model, comparison views, mesh checks, and an export report. Quality scores require visual comparison with the reference.

Requirements and limits: Requires Blender Python through the private Blender MCP or a background process. System Python cannot import bpy here. Use +Z up, +Y forward, +X right; 1 BU = 1 m. Without visual comparison, report VISUAL_REVIEW_REQUIRED. Use dated names when outputs collide.

#### lowpoly-reference-to-blender: Installation and examples

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

#### lowpoly-reference-to-blender: Self-test

Run from the repository root:

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
```

### `defold-development`

Work on Defold gameplay, Lua lifecycle, GUI, rendering, imports, and builds using the existing project architecture and art style.

Profile: Private. Preparation: Provide game.project, the target platform, expected behavior, and reproduction steps for bugs.

Expected result: A gameplay change or evidence-backed finding with relevant build and runtime checks.

Requirements and limits: Check engine APIs against the project version. Load project profiles only when named. Prefer official automation; community MCP integration requires explicit opt-in.

#### defold-development: Installation and examples

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

#### defold-development: Self-test

Run from the repository root:

```bash
python3 skills/defold-development/tests/test_skill.py
```

### `godot`

Build and maintain Godot scenes, controls, physics, UI, audio, shaders, and exports in GDScript or C#. Choose rendering and gameplay systems to suit the project.

Profile: Private. Preparation: Provide project.godot, the affected scene, engine version, target platform, and expected behavior.

Expected result: A verified scene or script change with results from the available engine checks.

Requirements and limits: Headless checks do not replace visual review. Renderer, physics, and API choices must match the installed Godot version.

#### godot: Installation and examples

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

#### godot: Self-test

Run from the repository root:

```bash
python3 skills/godot/tests/test_skill.py
```

### `game-asset-pipeline-shaders`

Audit the technical path from authored assets to runtime: materials, textures, shaders, glTF/GLB, and memory budgets. Defold and Godot adapters are included.

Profile: Private. Preparation: Provide the asset directory, engine, art style, target device, budget, and any protected source files.

Expected result: File and reference findings, separate disk-size and estimated VRAM figures, and a repair or optimization plan.

Requirements and limits: Start repairs with a dry run and back up originals. Preserve appropriate lossless sources and filtering for pixel art. Blender preflight runs inside Blender. Deep glTF specification checks require a suitable validator; other engines are extension points.

#### game-asset-pipeline-shaders: Installation and examples

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

#### game-asset-pipeline-shaders: Self-test

Run from the repository root:

```bash
python3 skills/game-asset-pipeline-shaders/tests/test_skill.py
```

The modes `audit`, `validate`, `fix`, `optimize`, `material`, `textures`, `shader`, `export`, `benchmark`, and `compare` describe workflows. Local installation targets are recorded in `.installed-manifest`.

### `game-audio-sound-design`

Manage sound effects, music, mixing, and audio QA. Generate audio through game-audio-forge; use ffmpeg and ffprobe for analysis and repairs.

Profile: Private. Preparation: Provide the game project, audio category, mood, duration, and output format. Use a separate output directory for repairs.

Expected result: A readiness report, measured findings, repaired files, or generated assets with provenance and license status.

Requirements and limits: Generation requires a separately configured game-audio-forge backend. The doctor installs nothing. Defold and Godot adapters are included; Unity and Unreal adapters are not implemented. Creative quality remains AUDIO_REVIEW_REQUIRED; unmeasured checks remain NOT_TESTED. Recheck licensing before release.

#### game-audio-sound-design: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh game-audio-sound-design
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the game-audio-sound-design skill. Check the audio environment, then audit assets/audio for silence, clipping, and loop seams. List missing tools and write repairs only to audio-fixes/.
```

**Codex:**

```text
Use the game-audio-sound-design skill. Generate a 45-second boss-fight loop through game-audio-forge with a mechanical, tense mood. Check measured tempo, loop seam, and provenance; leave listening review explicitly pending.
```

**oh-my-pi:**

```text
Use the game-audio-sound-design skill. Plan adaptive exploration, combat, and pause music for this Godot project. Verify scene changes and restart behavior against the installed engine version.
```

#### game-audio-sound-design: Self-test

Run from the repository root:

```bash
python3 skills/game-audio-sound-design/tests/test_skill.py
```

Prerequisites: configure game-audio-forge before generating audio. Installing this skill alone does not make generation available.

### `astro`

Develop new and existing Astro sites, including content, routing, islands, server features, and deployment. Start by inspecting the project and installed version.

Profile: Private. Preparation: Provide the project, affected route, and task. Include measurements and target devices for performance work.

Expected result: An implementation that fits the existing Astro project, build results, and clearly identified runtime checks still pending.

Requirements and limits: Reference versions are starting points. Verify APIs against the project. Add integrations, UI frameworks, and hosting dependencies only when the task calls for them.

#### astro: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh astro
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the astro skill. The home page ships too much JavaScript. Inspect islands and remove unnecessary hydration while preserving interactive behavior. Compare delivered JavaScript before and after.
```

**Codex:**

```text
Use the astro skill. Add an article page backed by the existing content collection. Reuse layouts and verify invalid slugs and the build.
```

**oh-my-pi:**

```text
Use the astro skill. Migrate content configuration for the installed Astro version. Preserve existing URLs and content.
```

#### astro: Self-test

Run from the repository root:

```bash
python3 skills/astro/tests/test_skill.py
```

### `react-nextjs`

Work on React SPAs and Next.js App or Pages Router projects, including components, data flow, caching, forms, and server boundaries.

Profile: Working. Preparation: Provide the project, router, affected component, and observed behavior. Read installed versions from manifests and lockfiles.

Expected result: A change within the existing stack, checked with relevant component, integration, or build commands.

Requirements and limits: This skill belongs to the Working profile. Private frontend work remains Astro-first under repository policy. Adapt examples to the actual React and Next.js versions.

#### react-nextjs: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh react-nextjs
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude working
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the react-nextjs skill. The whole table rerenders when a filter changes. Measure the cause and improve the affected data flow without changing behavior.
```

**Codex:**

```text
Use the react-nextjs skill. Audit cache usage in this Next.js App Router project. Identify concrete locations and fix confirmed defects with appropriate tests.
```

**oh-my-pi:**

```text
Use the react-nextjs skill. Fix the form that hides server errors. Preserve existing validation and test success, invalid input, and server failure.
```

#### react-nextjs: Self-test

Run from the repository root:

```bash
python3 skills/react-nextjs/tests/test_skill.py
```

### `backend-api-engineering`

Implement APIs, authentication, authorization, databases, migrations, and background jobs using the existing stack and contracts.

Profile: Private and Working. Preparation: Provide the service path, route or job, expected behavior, and relevant database structure.

Expected result: A feature or fix backed by API, database, or migration tests and observable results.

Requirements and limits: Production database operations, deployments, and breaking contracts require authorization covering those actions. Local checks do not prove a migration works on production data.

#### backend-api-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh backend-api-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the backend-api-engineering skill. Audit services/api for missing object authorization and N+1 queries. Fix confirmed issues and add tests for access across tenant boundaries.
```

**Codex:**

```text
Use the backend-api-engineering skill. Add pagination to the existing order list. Follow the API contract and test empty results, boundaries, and invalid parameters.
```

**oh-my-pi:**

```text
Use the backend-api-engineering skill. Plan an expand-and-contract migration for a new tenant ID. Check backward compatibility and show deployment steps without changing production data.
```

#### backend-api-engineering: Self-test

Run from the repository root:

```bash
python3 skills/backend-api-engineering/tests/test_skill.py
```

### `ultimate-security-hardening`

Inspect attack surfaces, confirm suspected vulnerabilities in code, and verify fixes with regression tests and another scan. Cover application code, dependencies, and infrastructure as needed.

Profile: Private and Working. Preparation: Specify the project and relevant features. State whether you want findings only or local fixes as well.

Expected result: Prioritized findings with code evidence, tool coverage, fix status, and verification results.

Requirements and limits: Missing scanners and untested areas remain coverage gaps. A report does not guarantee complete security. Keep secrets out of output; high-risk actions require appropriate authorization.

#### ultimate-security-hardening: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-security-hardening
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-security-hardening skill. Audit the API service for authentication and authorization defects. Confirm findings with code evidence and report without editing files.
```

**Codex:**

```text
Use the ultimate-security-hardening skill. Fix the confirmed IDOR in order access. Add a regression test for another user and rerun the relevant security check.
```

**oh-my-pi:**

```text
Use the ultimate-security-hardening skill. Check dependencies, containers, and configuration before release. List available scanners, missing coverage, and remaining blockers.
```

#### ultimate-security-hardening: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-security-hardening/tests/test_skill.py
```

### `ultimate-testing-qa`

Inspect existing tests, fill meaningful coverage gaps, and reproduce bugs in real browser flows. Follow issues through reproduction, repair, and retesting.

Profile: Private and Working. Preparation: Provide the URL or project path, start command, and critical user flow. Describe expected and actual results for bugs.

Expected result: A reproducible finding, an in-scope fix where applicable, relevant tests, and a record of checked and untested paths.

Requirements and limits: Existing runners and configuration take precedence. Playwright defaults to Firefox unless the project requires another browser. Automated checks do not establish overall product quality.

#### ultimate-testing-qa: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-testing-qa
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-testing-qa skill. Double-clicking the form creates two orders. Reproduce the flow, fix the cause, and verify protection against duplicate submission.
```

**Codex:**

```text
Use the ultimate-testing-qa skill. Review existing login and checkout tests. Add the most important missing error paths within the current test setup.
```

**oh-my-pi:**

```text
Use the ultimate-testing-qa skill. Inspect the running site for console errors and failed requests. Test navigation and forms at narrow and wide viewports.
```

#### ultimate-testing-qa: Self-test

Run from the repository root:

```bash
node skills/ultimate-testing-qa/tests/run.mjs
```

### `ultimate-code-quality-refactoring`

Find complex code, duplication, dead code, and problematic module boundaries. Preserve behavior during refactoring and verify each step against a baseline.

Profile: Private and Working. Preparation: Specify directories or files, audit versus implementation, and public interfaces that must remain stable.

Expected result: Evidence-backed findings or a verified refactoring with focused steps, preserved behavior, and documented limits.

Requirements and limits: Audits are read-only by default. Major architecture changes need a decision. Keep bug fixes and new features distinct from behavior-preserving refactoring.

#### ultimate-code-quality-refactoring: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-code-quality-refactoring
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-code-quality-refactoring skill. Audit src/ for technical debt. Identify concrete files and prioritize maintenance risks. Do not edit code yet.
```

**Codex:**

```text
Use the ultimate-code-quality-refactoring skill. Simplify packages/core/pricing.ts without changing behavior. Preserve the public API and run existing tests after each meaningful step.
```

**oh-my-pi:**

```text
Use the ultimate-code-quality-refactoring skill. Investigate the duplicated parsers. Check their differences first and consolidate only if existing contracts can be preserved.
```

#### ultimate-code-quality-refactoring: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-code-quality-refactoring/tests/test_skill.py
```

### `ultimate-code-review`

Review standards, requirements, bugs, security, testing, and performance. Findings include severity, confidence, and verifiable locations.

Profile: Private and Working. Preparation: Specify a branch, commit range, PR, or local changes. Include requirements and define the review scope.

Expected result: Prioritized findings, code evidence, and a coverage record showing reviewed and skipped areas.

Requirements and limits: Reviews are read-only by default. Fixes require an explicit request. Missing requirements and checks that were not run remain coverage gaps.

#### ultimate-code-review: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-code-review
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-code-review skill. Review my uncommitted changes for bugs, security issues, and missing tests. Include new files and do not edit anything.
```

**Codex:**

```text
Use the ultimate-code-review skill. Review this branch against main using docs/spec.md as the requirements. Report evidence-backed findings with file and line references.
```

**oh-my-pi:**

```text
Use the ultimate-code-review skill. Review the last commit for API compatibility and performance. Separate confirmed issues from open questions.
```

#### ultimate-code-review: Self-test

Run from the repository root:

```bash
python3 skills/ultimate-code-review/tests/test_skill.py
```

Corrections belong to the explicitly requested fix mode (`--fix`); a normal review does not edit files. The documented remote-action rule is “No commit/push ever without approval”. Authorization already granted for that action remains valid.

### `ultimate-i18n-localization`

Check translation catalogs, placeholders, plurals, and locale routing in web and game projects. Use pseudolocalization to expose cramped layouts and untranslated text.

Profile: Private and Working. Preparation: Specify the project, reference language, target languages, and task: audit, additive fixes, translation drafts, or validation.

Expected result: A catalog-drift report, additive corrections, or translations clearly marked as drafts.

Requirements and limits: Never overwrite existing translations. New translations need human approval. CI blocks on confirmed BLOCKER/HIGH findings; heuristics remain advisory.

#### ultimate-i18n-localization: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ultimate-i18n-localization
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ultimate-i18n-localization skill. Audit src/locales using German as the reference language. Report missing keys, placeholder mismatches, and plural issues without editing files.
```

**Codex:**

```text
Use the ultimate-i18n-localization skill. Add only missing catalog entries. Preserve existing translations and validate the catalogs again after changes.
```

**oh-my-pi:**

```text
Use the ultimate-i18n-localization skill. Plan English and Arabic support for the existing shop. Include locale routing, hreflang, and RTL. Mark new translations as drafts.
```

#### ultimate-i18n-localization: Self-test

Run from the repository root:

```bash
node skills/ultimate-i18n-localization/tests/run.mjs
```

### `documentation-technical-writing`

Create and maintain READMEs, API documentation, architecture notes, and guides. Check claims and commands against source files, manifests, and actual verification.

Profile: Private and Working. Preparation: Specify documents, audience, language, and scope. Explain the expected outcome of important steps.

Expected result: Updated documentation with practical examples, valid references, and an account of the checks performed.

Requirements and limits: Code is the source of truth for technical claims. Commands that were not executed remain NOT RUN. A documentation request does not automatically authorize application code changes.

#### documentation-technical-writing: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh documentation-technical-writing
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the documentation-technical-writing skill. Rewrite README.md in English for new developers. Check installation, start, and test instructions against the project and add a complete getting-started example.
```

**Codex:**

```text
Use the documentation-technical-writing skill. Check docs/ against the API implementation. Identify outdated endpoints, incorrect parameters, and commands that no longer match the project.
```

**oh-my-pi:**

```text
Use the documentation-technical-writing skill. Update the guides affected by this change. Preserve valid examples and identify commands you could not execute.
```

#### documentation-technical-writing: Self-test

Run from the repository root:

```bash
python3 skills/documentation-technical-writing/tests/test_skill.py
```

### `accessibility`

Develop accessible interfaces and audit against WCAG 2.2. Combine automated axe checks with keyboard, focus, and screen reader evidence where the environment supports it.

Profile: Private and Working. Preparation: Specify routes, components, relevant states, and the target level. Include open dialogs and form error states in scope.

Expected result: Findings and fixes with separate results for automation, manual review, and screen reader testing.

Requirements and limits: A/AA form the binding baseline; AAA is a separate quality tier. Automated PASS does not establish full conformance. Screen reader automation requires a suitable environment; report missing prerequisites.

#### accessibility: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh accessibility
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the accessibility skill. Audit /checkout for WCAG 2.2 AA. Check form errors, keyboard interaction, and focus. Separate automated findings from manual review items.
```

**Codex:**

```text
Use the accessibility skill. Fix the existing dialog so it receives sensible initial focus and returns focus when closed. Test Tab, Shift+Tab, and Escape.
```

**oh-my-pi:**

```text
Use the accessibility skill. Check save-status announcements with a screen reader if the environment allows it. Record missing evidence instead of reporting a blanket PASS.
```

#### accessibility: Self-test

Run from the repository root:

```bash
python3 skills/accessibility/tests/test_skill.py
```

### `seo-performance`

Audit technical SEO, metadata, structured data, and web performance. Distinguish delivered HTML from rendered DOM and lab results from field data.

Profile: Private and Working. Preparation: Provide the URL or project path and affected pages. Use comparable conditions for performance measurements.

Expected result: Prioritized findings with evidence, authorized fixes where applicable, and before-and-after checks.

Requirements and limits: Keep measurements separate from estimates. Local lab results do not replace field data. Apply fixes within the skill rules and the scope already authorized.

#### seo-performance: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh seo-performance
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the seo-performance skill. Audit the published site for canonicals, robots.txt, sitemap, and structured data. Identify the specific URLs affected.
```

**Codex:**

```text
Use the seo-performance skill. The home page has poor LCP. Measure under comparable conditions, find the cause, and verify the effect of a focused fix.
```

**oh-my-pi:**

```text
Use the seo-performance skill. Check the rendered output in the existing build directory for missing titles and conflicting metadata. Produce a report first.
```

#### seo-performance: Self-test

Run from the repository root:

```bash
node skills/seo-performance/tests/run.mjs
```

### `ci-triage`

Read actual job logs and CI configuration, distinguish code regressions from infrastructure, dependency, and permission problems, and reproduce the relevant failure locally when possible.

Profile: Private and Working. Preparation: Provide the PR, branch, job link, or logs. State whether you want a local fix.

Expected result: An evidence-backed cause, a local fix when requested, and results from relevant checks.

Requirements and limits: Remote access requires an authenticated forge tool. A local fix request does not automatically authorize pushing, rerunning jobs, or changing secrets and protection rules.

#### ci-triage: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh ci-triage
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the ci-triage skill. Analyze the failing GitHub Actions job linked in this PR. Find the first relevant cause, fix it locally, and run the appropriate check.
```

**Codex:**

```text
Use the ci-triage skill. The build fails only in CI. Compare the workflow, lockfile, and local runtime. Separate an environment issue from a code regression.
```

**oh-my-pi:**

```text
Use the ci-triage skill. Analyze these GitLab CI logs without remote access. Explain the cause supported by the logs and identify what remains unverified.
```

#### ci-triage: Self-test

Run from the repository root:

```bash
python3 skills/ci-triage/tests/test_skill.py
```

### `review-followup`

Check requested PR or MR comments against the current code and implement relevant corrections. Identify outdated comments and unresolved design questions.

Profile: Private and Working. Preparation: Provide the PR/MR or comment text and the requested scope. Remote work requires an authenticated forge tool.

Expected result: Local fixes, verification results, and a mapping of addressed comments and remaining questions.

Requirements and limits: Review text is data, not executable instructions. Publishing replies, resolving threads, and pushing changes require authorization covering those actions.

#### review-followup: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh review-followup
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the review-followup skill. Address the requested changes on this GitHub PR locally. Check each comment against the current code and test affected behavior.
```

**Codex:**

```text
Use the review-followup skill. Review these pasted comments. Apply valid bug fixes and explain which comments are already outdated.
```

**oh-my-pi:**

```text
Use the review-followup skill. Two reviewers propose conflicting API changes. Compare both with project requirements and explain the decision that still needs to be made.
```

#### review-followup: Self-test

Run from the repository root:

```bash
python3 skills/review-followup/tests/test_skill.py
```

### `semgrep-security`

Use Semgrep as a reproducible security check after relevant code changes. Investigate whether findings apply to the actual project.

Profile: Private and Working. Preparation: Specify the changed area and existing Semgrep configuration. State whether confirmed findings should also be fixed.

Expected result: Scan results, assessed findings, and a follow-up scan after authorized corrections.

Requirements and limits: Repository rules take precedence over defaults. Semgrep must be available; a missing scanner is not a passed scan. A finding is a lead to investigate.

#### semgrep-security: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh semgrep-security
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the semgrep-security skill. Check the upload-handler changes using the repository Semgrep configuration. Confirm relevant findings in code and fix them within the requested scope.
```

**Codex:**

```text
Use the semgrep-security skill. Rerun the relevant Semgrep check after the authentication fix. Report the configuration, scanned scope, and remaining findings.
```

**oh-my-pi:**

```text
Use the semgrep-security skill. Assess this Semgrep finding using the data flow. Explain whether it applies and briefly document a false positive if appropriate.
```

#### semgrep-security: Self-test

Run from the repository root:

```bash
python3 skills/semgrep-security/tests/test_skill.py
```

### `playwright`

Use existing terminal browser tools to open pages, inspect states, reproduce interactions, and capture screenshots or traces.

Profile: Private and Working. Preparation: Provide the URL, start command, flow, and expected result. Use the intended secure context for test credentials.

Expected result: A reproducible flow with observed states, browser errors, and useful artifacts.

Requirements and limits: Firefox is the default unless the repository requires another browser. Prefer existing project tools; do not install a second global CLI just because the skill is present. Use element references from a fresh snapshot.

#### playwright: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh playwright
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the playwright skill. Open http://localhost:4321 in Firefox and check the mobile menu. Record opening, navigation, and closing using fresh snapshots.
```

**Codex:**

```text
Use the playwright skill. Reproduce the search-dialog bug: after Escape, it cannot be reopened. Check browser errors and capture a trace if needed.
```

**oh-my-pi:**

```text
Use the playwright skill. Check the local login flow with the designated test data. Use a separate project session and record the result.
```

#### playwright: Self-test

Run from the repository root:

```bash
python3 skills/playwright/tests/test_skill.py
```

### `agent-harness-engineering`

Audit tools, observation formats, context budgets, error handling, loops, and agent coordination. Python tools analyze real configurations and recorded traces.

Profile: Private and Working. Preparation: Provide the harness directory, tool definitions, and traces or benchmarks for runtime questions.

Expected result: An evidence-backed audit, contract validation, or comparison that distinguishes recorded data from live measurements.

Requirements and limits: Unobservable areas remain UNVERIFIED or are skipped with a reason. Label offline benchmarks as offline. Use skill-orchestrator for choosing skills for a product task.

#### agent-harness-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh agent-harness-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the agent-harness-engineering skill. Audit our agent harness for duplicate tools, swallowed errors, and unbounded retries. Start with an evidence-backed report.
```

**Codex:**

```text
Use the agent-harness-engineering skill. Analyze trace.json for repeated identical tool calls. Identify the steps and propose a bounded retry strategy.
```

**oh-my-pi:**

```text
Use the agent-harness-engineering skill. Compare stored benchmarks before and after the tool change. Report regressions and label the comparison as offline.
```

#### agent-harness-engineering: Self-test

Run from the repository root:

```bash
python3 skills/agent-harness-engineering/tests/test_skill.py
```

### `lean-engineering`

Avoid unnecessary abstractions, dependencies, and configuration during implementation and refactoring. Preserve requirements and architecture that the project needs.

Profile: Private and Working. Preparation: Describe the task, existing interfaces, and constraints. Choose lite, full, ultra, or off to set the intensity.

Expected result: A complete implementation or audit with concrete simplifications and reasons for keeping necessary structure.

Requirements and limits: Do not cut security, validation, persistence, performance, accessibility, or necessary tests. Restate the desired mode when the host does not retain session state.

#### lean-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh lean-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the lean-engineering skill. Use lean mode full. Add CSV export to existing reports. Reuse installed libraries and preserve authorization and error handling.
```

**Codex:**

```text
Use the lean-engineering skill. Audit src/ for unnecessary abstractions. Also explain which structures should stay because they satisfy real requirements.
```

**oh-my-pi:**

```text
Use the lean-engineering skill. Simplify the configuration parser without changing behavior. Preserve the file format and public API and check existing error cases.
```

#### lean-engineering: Self-test

Run from the repository root:

```bash
python3 skills/lean-engineering/tests/test_skill.py
```

#### lean-engineering: Modes and commands

Modes `lite`, `full`, `ultra`, and `off` set the intensity. Commands such as
`/lean review`, `/lean audit`, `/lean simplify`, `/lean debt`, `/lean status`,
and `/lean help` name workflows. If the host has no registered slash command,
spell out the skill name and task instead.

#### lean-engineering: Collaboration and limits

During collaboration, project rules and domain requirements remain binding.
These limits also apply in ultra mode: a smaller diff does not justify removing
validation or error handling.

#### lean-engineering: Troubleshooting

If a new session does not retain the mode, state it again. Installation and
examples appear above. An audit can also explain why an apparently complicated
structure is necessary.

### `design-authenticity`

Create or review a visual identity based on the product, audience, and use. Assess typography, color, layout, and generic patterns against actual interfaces.

Profile: Private. Preparation: Provide the product context, audience, existing brand, and surface. Visual reviews require screenshots or browser access.

Expected result: A reasoned design direction, evidence-backed visual review, or revision with before-and-after comparison.

Requirements and limits: WCAG AA is the floor. Scores require visual review; otherwise report VISUAL_REVIEW_REQUIRED. Existing brand and design requirements remain binding.

#### design-authenticity: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh design-authenticity
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the design-authenticity skill. REVIEW the existing home page. Identify generic patterns and justify changes using our product context and existing brand.
```

**Codex:**

```text
Use the design-authenticity skill. CREATE a visual direction for a research tool. Explain typography, density, and color choices for long reading sessions.
```

**oh-my-pi:**

```text
Use the design-authenticity skill. Use GUARD mode to check the new component against our identity rules. Compare its screenshot with existing screens.
```

#### design-authenticity: Self-test

Run from the repository root:

```bash
python3 skills/design-authenticity/tests/test_skill.py
```

### `design-system-ui`

Create and audit design tokens, themes, and reusable components. Find duplicate colors, inconsistent spacing, and components that bypass the existing system.

Profile: Private. Preparation: Provide the project, token sources, themes, and affected components. Specify audit versus implementation.

Expected result: File-and-line findings, validated tokens, or an incremental migration with documented component contracts.

Requirements and limits: The system follows the project visual identity. The Node tool needs no extra packages. Figma requirements remain binding when Figma is the design source.

#### design-system-ui: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh design-system-ui
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude private
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the design-system-ui skill. Audit src/ for duplicate colors, spacing, and button variants. Report file and line and propose a safe cleanup order.
```

**Codex:**

```text
Use the design-system-ui skill. Dark mode is broken in three components. Find token mismatches, fix them, and verify both themes and focus states.
```

**oh-my-pi:**

```text
Use the design-system-ui skill. Create a DTCG token model from our existing palette for light and dark themes. Use a build step and document semantic tokens.
```

#### design-system-ui: Self-test

Run from the repository root:

```bash
node skills/design-system-ui/tests/run.mjs
```

### `figma-source-of-truth`

Keep the Figma design system, variables, and Code Connect mappings authoritative during UI implementation. Reuse production components and report concrete deviations.

Profile: Working. Preparation: Provide the Figma file and node, relevant library, and existing Code Connect mappings.

Expected result: An implementation using existing components and tokens, or an evidence-backed mismatch report naming the relevant nodes.

Requirements and limits: This Working-profile skill applies only when Figma is involved. It does not provide a Figma connection. Required plugin tools and their own prerequisites must be available.

#### figma-source-of-truth: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh figma-source-of-truth
```

For Claude Code, also synchronize its shared skill directory with this profile.
This command synchronizes the full profile, rather than just this skill:

```bash
tools/install-skills.sh --claude working
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the figma-source-of-truth skill. Implement the checkout view from the supplied Figma node. Use existing Code Connect components and library variables.
```

**Codex:**

```text
Use the figma-source-of-truth skill. Compare our button with the supplied library node. Report mismatched states, dimensions, and tokens without introducing a new design.
```

**oh-my-pi:**

```text
Use the figma-source-of-truth skill. Before implementation, check which components already have mappings. Identify missing mappings and unresolved design decisions.
```

#### figma-source-of-truth: Self-test

Run from the repository root:

```bash
python3 skills/figma-source-of-truth/tests/test_skill.py
```

### `human-writing`

Write and revise English and German documentation, website copy, articles, UX text, and creative prose. Preserve facts, terminology, and the author’s voice.

Profile: Private and Working. Preparation: Provide the text or path, audience, language, and purpose. Include representative writing samples when voice matters.

Expected result: A revision or audit with concrete observations. Python tools detect patterns; the agent writes the replacement prose.

Requirements and limits: Lint findings do not identify authorship. Protect code, URLs, technical terms, and facts. Project rewrites start as dry runs and are applied within the approval already given.

#### human-writing: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh human-writing
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the human-writing skill. Rewrite README.md in English for developers seeing the project for the first time. Preserve commands, links, and facts, and replace filler with concrete explanations.
```

**Codex:**

```text
Use the human-writing skill. Audit these three posts for repetition and empty phrasing. Report only, with a suggested improvement for each finding.
```

**oh-my-pi:**

```text
Use the human-writing skill. Rewrite the introduction using my supplied samples as a voice reference. Preserve my tone and do not invent product promises.
```

#### human-writing: Self-test

Run from the repository root:

```bash
python3 skills/human-writing/tests/test_lint_text.py
```

### `skill-orchestrator`

Inventory actual skills, validate their structure, and investigate overlap. Produce a reasoned skill selection and sequence for a concrete task.

Profile: Private and Working. Preparation: Provide the collection or skill and the requested check. For routing, describe the task and its requirements.

Expected result: A reproducible report, routing plan, or repair proposal with explicit verification limits.

Requirements and limits: Read-only by default. Repairs remain proposals until approved. Agent evaluations that were not run remain UNAVAILABLE; test files do not count as executed tests.

#### skill-orchestrator: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh skill-orchestrator
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the skill-orchestrator skill. Audit this skill collection using the portable profile. Report structural errors, overlaps, and areas you could not evaluate.
```

**Codex:**

```text
Use the skill-orchestrator skill. Which skills fit an accessible Astro website with localization? Explain selection and order without activating the entire collection.
```

**oh-my-pi:**

```text
Use the skill-orchestrator skill. Check human-writing and documentation-technical-writing for conflicting responsibilities. Propose focused corrections without editing files.
```

#### skill-orchestrator: Self-test

Run from the repository root:

```bash
python3 skills/skill-orchestrator/tests/test_orchestrator.py
```

## Validate and maintain the collection

Run these commands from the repository root. They exercise different parts of
the collection. Passing self-tests does not mean every target application or
external integration has been tested.

```bash
blender -b --python skills/lowpoly-reference-to-blender/tests/test_e2e_pipeline.py
python3 -m py_compile skills/*/scripts/*.py skills/*/tests/*.py
node skills/design-system-ui/tests/run.mjs
TEST_HOME=$(mktemp -d) bash tools/test_installer.sh
python3 skills/godot/tests/test_skill.py
bash skills/godot/scripts/headless_check.sh skills/godot/examples/base-project
```

Additional self-tests are listed with each skill. Blender and Godot checks
require their engines. Browser, screen reader, audio, and GPU checks need their
respective environments. Report missing prerequisites rather than a passed check.

Follow [docs/adding-new-skills.md](docs/adding-new-skills.md) when adding a skill.
Every skill requires YAML frontmatter with `name` and `description`; the name
must match its directory. When scripts or entry points change, update this
skill section and its local README together.

### Documented local environment

Repository instructions record Blender 5.3.0, hash `02f0899d`, with bundled
Python 3.13, and Godot 4.7.2-stable, commit `ed1daf0b`. These describe the
documented local baseline, not requirements for every target project or versions
newly measured during this documentation change. System Python has no `bpy`;
run scripts importing it inside Blender. Verify engine and framework claims
again when working on the target project.
