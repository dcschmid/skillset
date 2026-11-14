# UI/UX — Defold 1.14.1 baseline

Load for menus, HUDs, fonts, localization, or cross-device layout. GUI facts:
`/manuals/gui` + node pages (`gui-box`, `gui-text`, `gui-pie`,
`gui-template`, `gui-script`, `gui-clipping`, `gui-layouts`), API `/ref/gui/`.
Label component: `/manuals/label`. Engine does not ship a widget toolkit —
GUI is a retained node tree you script.

## System choice

| Surface | Use |
|---|---|
| In-world text (signs, damage numbers) | `label` component (lightweight, 3D-placed) |
| Menus, HUD, anything scripted/animated | `gui` component + `.gui` scene |
| Complex animated UI | GUI ParticleFX / Spine / Rive nodes (extensions for Spine/Rive) |

GUI scene = boxes (rects), text, pie, templates (reusable node groups),
scripts in `.script` files with `gui` callbacks. Boxes nest; templates
instance; clipping masks scroll lists. Verify node creation signatures on
`/ref/gui/` — do not recall.

## Layouts & responsiveness

`/manuals/gui-layouts`: anchored positioning (parent/anchor/pivot) +
fit policy. Pixel-art UI: integer scaling, no fractional anchors
(`2d-pixel-art.md`); non-pixel: adaptive anchors. Cover every shipped
resolution/aspect: desktop 16:9/21:9, phone portrait/landscape, HTML5 canvas
size (`html5.md` scale modes). Pattern: compute one scale factor from
window size, apply to a root box; children inherit. Safe areas on mobile:
`extension-safearea` (extension, not engine).

```lua
function on_input(self, action_id, action)      -- nav below needs raw events
    if action_id == hash("up") and action.pressed then self.fsm:fire("focus_up") end
    if action_id == hash("tap")  and action.pressed then self.fsm:fire("activate") end
end
```

## Controller / keyboard navigation

No focus system ships. Own it as an FSM (`gameplay-systems.md`): ordered node
list per screen, `focus` index, up/down/left/right move it, confirm fires the
node's action. Gamepad input identical to kb apart from `action.gamepad`
(`multiplayer.md`). Mouse/touch: `on_input` with `action_id` from input
actions; touch = mouse on HTML5/mobile — test both event shapes
(`action.touch`, pressed/repeated/released per `/manuals/input-mouse-and-touch/`).

## Fonts (decision table)

| Kind | Use | Cost / limits |
|---|---|---|
| Bitmap (TrueType baked at sizes, `/manuals/font`) | fixed-size UI, pixel art | crisp at baked size; blur when scaled |
| **SDF fonts** (`/manuals/font` SDF section) | scaled text, zooming | soft edges at small sizes; shader needs float textures? verify per platform |
| **Vector fonts** (since 1.14.1) | crisp at any size, CJK/large sets | need `RGBA16F`/`R32UI` render targets → **no GLES2/WebGL1 builds**; keep bitmap fallback if targeting WebGL1 |
| `font.prewarm_text()` (`/ref/font/`) | CJK first-use hitch | prewarm visible strings at boot |

Rich text markup on Label/GUI text is 1.13+ (`/manuals/font-richtext`) —
check project version gate (`version-compatibility.md`).

## Localization

1.14.1 manuals index carries **no** dedicated translation-tables manual page
— the classic "text.translation_tables" workflow: UNVERIFIED for this
baseline. Boring shipped path instead:

```lua
-- lang/en.lua returns flat key→string table; lang.t("menu.start")
-- keys are static strings (lua-engineering.md); fallback lang always loaded.
local L = require("lang." .. session.lang)
gui.set_text(node, L.menu_start)
```

`sys.load_resource` + `json.decode` for non-Lua pipelines; version-tag
exports. Subtitles: GUI text node driven by `sound_done`/play_id of voice
lines (`audio.md`) — timing from data, not guessed. RTL/LTR: text node
pivot+position trick per `/examples/gui/localization`; no bidi engine ships.

## Accessibility (cheap wins, genre-agnostic)

- Contrast ≥ 4.5:1 body / 3:1 large on shipped palettes — measure, don't vibe.
- Every pointer target ≥ ~40 px at min supported resolution (48 px touch).
- Text scales: font size derived from the root scale factor, never hardcoded.
- Full gamepad+kb menu paths (above); don't require mouse for anything.
- Subtitles/captions when voice exists; colorblind-safe palettes for
  state-critical color (grouping by hue alone fails grayscale).

## HUD & menu patterns (adopt only if the project asks)

Diegetic (in-world labels) > screen-space overlay > modal walls. One GUI
scene per screen; templates for repeated rows (inventory cell, quest entry).
HUD subscribes to gameplay events (`architecture.md` single-owner rule) — it
never recomputes truth. Screenshots/profilers off in release
(`performance.md`).

## Animation

`/manuals/property-animation` (tweens) for node position/color; engine
animation files for flipbook UI. Tween on enter/exit only — idle loops are
draw-call noise (`performance.md`).
