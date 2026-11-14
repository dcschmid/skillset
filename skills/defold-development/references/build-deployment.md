# Build & Deployment — Defold 1.14.1 baseline

Load for bundling, CI, store uploads. All flags below verified against
`/manuals/bob` (bob requires OpenJDK 25; download bob.jar from the GitHub
releases). Never report "build successful" without exit 0 **and** an artifact
check — `scripts/check_build.sh` exists for that.

## bob.jar command shape

```sh
java -jar bob.jar --root . --archive --platform <platform> \
  resolve build bundle --variant release -o build/default
```

- `resolve` → external libs; `build` → dependency graph from `game.project`
  (add `--archive` for the game archive; unreferenced files are NOT built —
  raw runtime loads need Custom Resources). `bundle` → platform app; needs
  archive + `--platform`. `clean`/`distclean` for teardown. `resolve` alone
  checks libraries.
- `--variant debug|release|headless` replaces deprecated `--d`; debug =
  unstripped/symbols. `headless` for CI test bundles
  (`debugging-testing.md`).
- `-o/--output` (build dir, default `build/default`), `--bundle-output`
  (bundle dir), `--settings a.settings` (overlay game.project files, CI),
  `--defoldsdk <sha>` pin the engine — pin it to 1.14.1 `ee283d4…` for this
  baseline (`version-compatibility.md`).
- Reports: `--build-report-html f.html` / `--build-report-json f.json`
  (size ranking — `performance.md`). `--texture-compression` switch enables
  profile-driven compression. `--with-sha1` (web), `--strip-executable`
  (iOS/Android), `--max-cpu-threads`.

## Platform targets (`--platform`, `--architectures`)

| Target | Platform id | Notes |
|---|---|---|
| Linux | `x86_64-linux` / `arm64-linux` | ARM = Pi/handhelds |
| macOS | `x86_64-macos` / `arm64-macos` | |
| Windows | `x86_64-win32` | 64-bit |
| iOS | `arm64-ios` (+ `arm64_sim-ios`, no signing needed for sim) | `--identity`, `--mobileprovisioning` |
| Android | `armv7-android`, `arm64-android`; `x86_64-android` opt-in | `--bundle-format apk|aab`, `--keystore*` |
| Web | `wasm-web` / `wasm_pthread-web` | pthread needs cross-origin-isolated host |

Build server (native extensions): default follows bob's channel —
stable → `build.defold.com`, else `build-stage.defold.com`; override
`--build-server` (self-hosted Extender possible). CI caching:
`--resource-cache-local <dir>` + `--resource-cache-remote <url>` +
`--ne-build-dir`; cache keyed on `--defoldsdk` sha. `java -jar bob.jar
--version` prints channel+version — log it in CI runs.

## Gate: what "built" means

```
bob exit 0 → artifact exists → unpacked check → run smoke
```
`scripts/check_build.sh` performs exit-code + unpacked-artifact inspection
(bundle dir/zip contents, engine binary present, archive present). A green
`BUILD` without `RUNTIME` (engine booted, logs clean) is partial — report
levels separately (SKILL.md ladder).

## Distribution routes (desktop/web stores)

- **Steam (desktop)**: bundle `x86_64-win32`/`x86_64-macos`/`x86_64-linux`
  (variant release), zip per Steamworks UploadTool layout — engine doesn't
  ship a Steam pipeline; `extension-steam` exists for runtime API, upload is
  your Steamworks workflow. 32-bit Windows: not in the bob platform list —
  verify before promising it.
- **itch.io**: desktop zips as above; **HTML5**: `--platform wasm-web`
  bundle, zip *contents at root*, upload, "This file will be played in the
  browser" — serve-side wasm MIME (`application/wasm`) required
  (`/manuals/html5`); itch's pages qualify, raw `file://` never does.
- **HTML5 hosting generally**: `webgl_version_hint` (default 2) + since
  1.14.1 GLES2/WebGL1 shaders excluded by default → WebGL1 targets need
  `exclude_gles_sm100 = 0` too (both settings in game.project — pair is
  documented, verify against `version-compatibility.md` gate).
  `wasm_pthread-web` demands COOP/COEP headers; ship `wasm-web` fallback when
  host can't isolate. Heap `html5.heap_size`; download retry knobs
  `html5.retry_count/time`.
- **Mobile stores**: apk/aab via keystore flags; iOS needs identity +
  provisioning (`--identity`, `--mobileprovisioning`).
- **Consoles (Switch / PlayStation / Xbox)**: documented platform manuals
  exist (`/manuals/nintendo-switch`, `/manuals/sony-playstation`,
  `/manuals/microsoft-xbox`) — toolchain/devkit access runs through the
  console-maker programs; verify current steps on those pages, bundling
  specifics beyond the docs: UNVERIFIED, don't invent flags.

## CI skeleton (boring, cacheable)

```yaml
# JDK 25 + pinned bob; caches keyed on engine sha
java -jar bob.jar --root . --defoldsdk ee283d4... \
  --resource-cache-local .cache/rcc --archive \
  --build-report-json reports/report.json \
  resolve build bundle --platform x86_64-linux --variant release
bash scripts/check_build.sh build/default   # exit 0 + artifacts, else fail
```

Artifacts retained on failure: report json/html, bob log, engine logs
(`debugging-testing.md`). Matrix builds share the resource cache; run
`distclean` only on cache-bust.
