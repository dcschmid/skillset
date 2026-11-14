# Workflow: New Defold Project

Use when no project exists yet (or only stub files). Output: a bootable,
version-pinned project skeleton with honest scope notes.

## Steps

1. **Capture inputs** — genre?, art style?, platforms?, team size?, is a
   project profile named? Any unknown → one question, else pick the smallest
   safe default and record it.
2. **Version pin** — decide engine version WITH the user (default: current
   stable per `references/version-compatibility.md`). Record
   version+sha+channel in the project README. Never silently pick a
   beta/alpha.
3. **Pick the engine feature set from needs only** — yes/no per system:
   physics engine? GUI vs labels? render script? extensions? Systems not
   requested are NOT scaffolded.
4. **Layout decision** — propose ONE tree (see architecture.md module
   layout); small projects: `main/` + `modules/` + `assets/` is enough. No
   framework dirs "for later".
5. **Create minimal boot** — `game.project` (input bindings, bootstrap
   collection, physics config IF physics used), `main.collection`, boot
   script, one GUI/script only if UI was requested.
6. **Version gate for style-sensitive settings**:
   - Pixel art → nearest filtering, texture profiles, integer-scale plan
     (`references/2d-pixel-art.md`).
   - HTML5/WebGL1 target → `exclude_gles_sm100 = 0` decision.
   - Vector fonts on GLES2/WebGL1 targets → unavailable, choose SDF/bitmap.
7. **Verify** — STATIC: structure audit
   `scripts/audit_defold_project.py .` → BUILT:
   `scripts/bob_build.sh --profile debug --output-dir build/dev` (dry-run
   first) → RUNTIME: engine opens, boot log clean → VISUAL: window renders
   boot scene.
8. **Document** — project README: version pin, chosen systems, deferred
   systems, how to run/build/test.

## Anti-rules

- No parallel `framework/` layer; no genre system (inventory, race manager)
  unless the genre asked for it; no engine upgrade "while setting up".
