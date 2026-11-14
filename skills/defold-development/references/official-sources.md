# Official Sources & Citation Discipline

Primary references are **official English Defold docs**. Cite them; do not
paraphrase from memory when precision matters.

| Source | URL | Use for |
|---|---|---|
| Homepage | https://defold.com/ | product truth |
| Manuals | https://defold.com/manuals/ | workflows, settings, platform pages |
| API reference | https://defold.com/ref/ | exact function signatures per version |
| Releases | https://github.com/defold/defold/releases | version/channel/date/sha, change lists |
| Release blog | https://defold.com/2026-11-10/Defold-1-14-1/ | 1.14.1 narrative |
| Forum | https://forum.defold.com/ | release threads, staff answers |

Key manual pages for this skill (verify paths resolve at use time):

- `/manuals/bob/` — build tool usage, targets, flags
- `/manuals/project-settings/` — every `game.project` key
- `/manuals/gltf/` — glTF/GLB import surface
- `/manuals/font/` — bitmap/SDF/vector modes, static/dynamic generation
- `/manuals/html5/` — wasm targets, WebGL hints, limitations
- `/manuals/collections/`, `/manuals/game-object/`, `/manuals/components/`
- `/manuals/physics*` — engine choice, groups, events
- `/manuals/render/` — render scripts, constants
- `/ref/gui`, `/ref/go`, `/ref/msg`, `/ref/vmath` — runtime APIs

## Rules

1. **API existence**: before calling `foo.bar()`, it must appear in
   `/ref/` output or a manual example. Otherwise: UNVERIFIED → verify or
   pick a documented alternative.
2. **Version claims**: engine claims carry the version they were checked
   against. Feature tables in this skill state min-version or cite 1.14.1.
3. **Import vs runtime**: a format being readable at import (e.g. Draco)
   does not imply runtime support — manuals state both sides separately.
4. **Platform claims** (HTML5, mobile, console): the platform manual page
   wins over general pages.
5. **Conflicts**: newer manual > release notes > forum > memory. Record the
   discrepancy in the task report instead of picking silently.
6. **Fetching**: docs may 404 via simple scrapers when paths redirect; try
   the in-site search or the manuals index before concluding "absent".

## Citation format in answers

`claim — https://defold.com/ref/<module> (checked against 1.14.1, YYYY-MM-DD)`
