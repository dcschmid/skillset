# Workflow: Release build & publish prep

`references/export-and-release.md` carries the command surface and platform
matrix. No publish without the user's go.

## Steps

1. **Version gate** — engine + export templates + addon pins pinned in README
   and CI (no `latest`); version string bumped in project + release notes.
2. **Presets** — named presets per target in `export_presets.cfg` (committed);
   export filters exclude tests/scratch; dedupe verify: pack twice → hash.
3. **Ladder** — STATIC → IMPORTED → RUNTIME (headless, long `--quit-after`)
   → BUILT (`--export-release`/`--export-pack` per preset, exit 0 + output
   exists/non-trivial size) → installed-build smoke.
4. **Platform realities** — web: COOP/COEP host + renderer constraint per
   minor; mobile: device perf + orientation; desktop: bundle layout per
   store (Steam depot / itch zip) from store docs at upload time.
5. **Saves & locales** — old saves load on new build (versioned payloads);
   pseudolocalization pass for text overflow.
6. **Credits & licenses** — asset credits shipped; addon licenses listed.
7. **Artifacts** — builds under `builds/` (dated suffix on collision), logs
   archived with the build.

## Report per target

LEVEL (BUILT/VISUAL…) + command + size/hash + known platform caveats.
Publishing itself stays a user action.
