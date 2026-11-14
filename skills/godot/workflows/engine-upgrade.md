# Workflow: Engine upgrade (explicit user decision only)

NEVER run this on a project without the user asking. `godot-versions.md` owns
the version facts.

## Steps

1. **Confirm scope** — which project(s), from→to (e.g. 4.7.2 → 4.8.x stable
   when stable exists; betas/dev snapshots only on explicit opt-in).
2. **Research** — release article + GitHub release body + interactive
   changelog for the to-version; classify: API renames, resource format,
   renderer, exporters, editor behavior. Copy breaking-change wording verbatim
   into the migration note.
3. **Checkpoint** — clean VCS branch; backup `user://` saves if test-run.
4. **Dry run** — open in new editor, `--headless --import`; collect every
   error/warning; `--validate-conversion-3to4` pattern does NOT apply within
   4.x — diff `.godot` import artifacts, not authored files.
5. **Migrate authored files** — only what the changelog names; run
   `scripts/headless_check.sh` before/after; style settings (filter/stretch)
   re-checked against refs (defaults can shift between minors).
6. **Addons** — each addon: version-supports-engine check (README/issues),
   update pin; no blind auto-update.
7. **Gates** — full ladder green on the new engine + VISUAL spot checks on
   style-critical scenes; export one platform build.
8. **Land** — engine pin in README/CI + changelog summary; existing saves
   forward-compatible or migration shipped.

Older-project rule: a project on 4.x stays until the user asks; document
migration problems, never silently patch around them.
