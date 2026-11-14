# Version Compatibility — Godot 4.7.2 stable

## Central version config

```
ENGINE_VERSION   = 4.7.2
ENGINE_CHANNEL   = stable
ENGINE_COMMIT    = ed1daf0bf001b61586d9930840f2f1394092c079 (ed1daf0b)
RELEASE_DATE     = 2026-08-18
RELEASE_NOTICE   = https://godotengine.org/article/maintenance-release-godot-4-7-2/
RELEASES_ARCHIVE = https://godotengine.org/download/archive/
DOCS_PIN         = https://docs.godotengine.org/en/4.7/
```

Verified 2026-11-13 against https://godotengine.org/download/archive/:
4.7 line is `stable`; 4.7.2 is the newest 4.7 patch; the official notice
reports **no known incompatibilities with 4.7.1**; 4.8 is `beta3`
(2026-11-09) — pre-release, never a default. Previous stables: 4.7.1, 4.7
(2026-06-18, `5b4e0cb`, feature release, compat-preserving), 4.6.x, 4.5.x.

## Channel discipline

- Beta/dev-snapshot builds (4.8-beta*, *-dev*) are never silently treated as
  stable; they may only be used when the user explicitly opts in and the
  project documents the pin.
- A project pinned to an older 4.x stays there; upgrades are the
  `workflows/engine-upgrade.md` decision, never automatic.
- Patch releases (4.7.x) are safe-upgrade by policy but still get a
  backup/VCS checkpoint first (official guidance).

## How to read a project's version

1. `project.godot` → `[application] config/features` (e.g.
   `PackedStringArray("4.7", "4.x")` — editor-written, may lag the binary).
2. CI: the pinned engine download URL / Docker image tag.
3. Editor: `Help > About`; binary: `godot --version`.
4. `--dump-extension-api` output pins the exact API surface of the binary.

## What 4.7 changed that touches skill guidance

Verified from the 4.7-stable release page and 4.7.2 maintenance notice
(interactive changelog: https://godotengine.github.io/godot-interactive-changelog/):

| Change | Kind | Skill impact |
|---|---|---|
| Feature release "preserve compatibility with previous releases" | NOTE | 4.6-era guidance remains valid on 4.7 |
| 4.7.2: 57 fixes incl. core threading, GDExtension `register_extension_class`, BaseButton long-press input, high-polling-rate mouse perf | FIX | no authored-API rewrites needed for 4.7.1→4.7.2 |
| HDR 3D pipeline work in the 4.7 line | NEW | verify on docs page before enabling in stylized projects |
| Console support surfaced officially | NEW | console targets: verify exporter availability per platform |

Full item list: cite the changelog link; do not restate 57 fixes as claims.

## Feature-vs-version quick gates (4.x line)

| Feature | Min version | Gate / note |
|---|---|---|
| `TileMapLayer` node (replaces TileMap) | 4.3 | prefer per-layer nodes in new projects |
| Jolt physics (built-in) | 4.4 (experimental) / hardened in 4.7-era | project setting `physics/3d/engine = "JoltPhysics3D"`; verify before pinning |
| `ResourceLoader.load_threaded_*` async scene flow | 4.1 | desktop; web/mono caveats per docs |
| AccessKit screen-reader tree | 4.3 | `--accessibility` CLI + Control a11y; verify per target |
| HDR 2D (4.7 line) | 4.7 | verify renderer + platform before use |
| C# export per-platform | version+build | .NET mono builds only; verify platform matrix per release |

Anything not in this table and version-sensitive: check
`https://docs.godotengine.org/en/4.7/` before claiming support.

## Update routine (future Godot releases)

When a new stable appears (4.7.3+, or 4.8 stable):

1. Read the release article + GitHub release body + interactive changelog.
2. Classify each item: API rename / resource format / renderer / exporter /
   editor behavior. Copy exact wording of breaking changes.
3. Re-verify doc pages touched (multiple_resolutions, jolt, exporters,
   shaders) and update this file's config block + gate table.
4. Grep this skill for `4.7`-gated claims, re-verify, run
   `scripts/check_version.py` and `tests/test_skill.py`.
5. Bump nothing in any game project without an explicit user go-ahead.
