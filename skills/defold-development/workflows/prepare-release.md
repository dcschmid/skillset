# Workflow: Prepare a Release

Build success = exit 0 + artifact check + runtime smoke. Nothing less.

1. **Freeze the version facts** — engine version+sha (pinned, unchanged:
   releases never ride an engine upgrade), engine channel stable only.
2. **Project gate** — `scripts/audit_defold_project.py .`; resolve every
   gate finding (GLES2 opt-out for WebGL1, physics flags, bootstrap).
3. **Test gate** — full automated suite (AUTOTEST) green; failing tests are
   fixed or the release is postponed, never skipped.
4. **Build** — `scripts/bob_build.sh --run --profile release --platform <p>`
   then `scripts/check_build.sh <output>`. Per platform: desktop zip ·
   HTML5/WASM (`/manuals/html5/`, webgl_version_hint) · ios/android per
   their manual pages. Flags come from `java -jar bob.jar help` of the
   pinned engine — no remembered flags.
5. **Runtime smoke on real targets** — boot, core loop 60 s, save/load,
   input devices, audio; logs clean. HTML5: run in a real browser, not just
   served files.
6. **Perf snapshot** — one profiler capture vs budget
   (`templates/performance-report.md`).
7. **Distribution packaging** — Steam: desktop build into Steamworks app
   build pipeline; itch.io: html5 zip or desktop zips; other platforms per
   their official pages. Version numbers + changelog updated.
8. **Report** — platforms shipped at which truth level; deferred platforms
   and why. "Built" claims only for artifacts checked in step 4–5.
