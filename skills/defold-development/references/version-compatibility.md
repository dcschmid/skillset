# Version Compatibility — Defold 1.14.1 Stable

## Central version config

```
ENGINE_VERSION   = 1.14.1
ENGINE_CHANNEL   = stable
ENGINE_SHA       = ee283d4dad9fa451dd6399d83602e1dc25133681
RELEASE_DATE     = 2026-11-10
RELEASE_URL      = https://github.com/defold/defold/releases/tag/1.14.1
STABLE_ANNOUNCE  = https://defold.com/2026-11-10/Defold-1-14-1/
```

Previous stable: 1.14.0 (2026-10-12, `d295ed4`); before that 1.13.2
(2026-09-29, `8620195`). Verified via the GitHub releases API
(`api.github.com/repos/defold/defold/releases`) on 2026-11-13: newest stable
tag is still 1.14.1; 1.14.2 exists only on the alpha channel. Re-verify with
`scripts/check_version.py` before pinning anything else.

## Channel discipline

- Alpha and beta releases are **never** silently treated as stable.
- A project pinned to an older channel than the current stable gets a written
  compatibility note, not an automatic upgrade.
- Never auto-update the engine. Engine updates are an explicit user decision.
- Existing projects are NEVER migrated to a newer engine without asking.

## How to read a project's version

1. Editor: bottom-left status / `Help > About`.
2. Build: `bob.jar --version` (or the SDK's `engines/` directory name).
3. CI caches: the pinned engine URL/sha in the workflow file.
4. `game.project` itself does not store the engine version — do not guess it
   from file format quirks; ask or read the SDK.

## What 1.14.1 changed (verified, release notes + announcement)

Verified from the official release announcement
(https://defold.com/2026-11-10/Defold-1-14-1/, forum thread
https://forum.defold.com/t/defold-1-14-1-has-been-released/83487):

| Change | Kind | Impact |
|---|---|---|
| GLES2/WebGL1 shaders **excluded by default** (`[shader] exclude_gles_sm100`, editor "Exclude GLES 2.0") | BREAKING | Opt-in again if you target WebGL1/GLES2; HTML5 `webgl_version_hint = 1` needs `exclude_gles_sm100 = 0` too |
| Runtime vector fonts (Slug2): sharp scaled text, less texture memory; emoji via COLRv1 | NEW | Vector mode needs `RGBA16F`/`R32UI` — **not** GLES2/WebGL1; no auto-fallback to SDF |
| Draco/Meshopt compressed glTF reading | NEW | **import-time only** — engine runtime does not decompress at runtime |
| `.ktx2` textures for `.gltf`/`.glb` | NEW | Texture profiles decide recompression; may be lossy |
| GLFW2 removed from Android/iOS/HTML5 (engine-native platform layer); desktop keeps GLFW3 | NEW | input layer differences per platform |
| HTTP response buffer doubles on resize | FIX | fewer temp allocations |
| Resource loader scheduling on job system | FIX | faster async loading |

New `.font` resources default to **Vector + Dynamic**; existing fonts keep
their Bitmap/SDF mode.

## Update routine (future Defold releases)

When a new Defold release appears:

1. Read the successor of the 1.14.1 announcement — release blog + forum
   thread — and the GitHub release body.
2. Classify each item: engine API / resource format / shader / build flags /
   editor behavior. Copy exact wording of breaking changes.
3. Check `https://defold.com/manuals/` pages touched (bob, project-settings,
   html5, font, gltf are the hot ones).
4. Update this file's config block + change table; grep this skill's
   references for `1.14.1`-gated claims and re-verify.
5. Run `scripts/check_version.py` against the official releases and
   `tests/test_skill.py`.
6. Bump nothing in any game project without an explicit user go-ahead.

## Feature-vs-version quick gates

| Feature | Min version | Gate |
|---|---|---|
| Vector fonts (runtime) | 1.14.1 | not GLES2/WebGL1; `RGBA16F`+`R32UI` required |
| Draco/Meshopt glTF read | 1.14.1 | import-time only |
| KTX2 in glTF | 1.14.1 | recompress policy per texture profile |
| GLES2 opt-out default | 1.14.1 | set `exclude_gles_sm100=0` for WebGL1 |
| Video recording (`recorder`) | 1.14.1 ref | verify per project before use |
| Compute shaders | 1.9+ era, verify | desktop GL contexts; check platform page |
| Lua 5.4 script mode | project-configured | check `[script]` before newer syntax |

Anything not in this table: check `/ref/` for the pinned version, cite the URL
in the answer, else mark UNVERIFIED.

## Stable vs beta vs experimental reporting

When answering, tag every engine claim:
- **Stable-in-baseline** — documented for 1.14.1 stable, cite URL.
- **Newer-channel** — exists only in alpha/beta; present as "available on the
  X channel, not stable", never as a project default.
- **Engine extension required** — not engine built-in; name the extension or
  the extra implementation work (e.g. full voxel editing, online multiplayer
  frameworks, advanced audio mixing).
