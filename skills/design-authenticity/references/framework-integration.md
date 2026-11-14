# Framework & Skill Integration

Purpose: keep responsibilities clean where other repo skills or any framework is
in play. This skill is **independent** — it never imports another skill; it rides
on whatever the project already has.

## Responsibility split (conflict order: project requirements > functional/
a11y-operable UX > this skill > taste)

| Layer | Owner |
|---|---|
| Framework architecture, APIs, versions, build | `astro`, `react-nextjs`, `godot`, `defold-development` skills |
| Accessibility engineering, WCAG, audit tools | `accessibility` skill |
| Visual originality, identity, anti-slop, composition | **this skill** |
| Project tokens/brand already committed | the project itself (this skill preserves) |

## Per-stack notes (method, not code)

- **HTML/CSS, CSS Modules, Tailwind, CSS-in-JS**: identity lands in tokens/
  theme files first (custom properties, `theme`, styled-system config), components
  second. Tailwind users: theme extension, not utility soup per component;
  arbitrary values (`[]`) flag unchosen defaults. Detection engine reads classes
  and CSS values directly.
- **React / Next.js** (`react-nextjs` skill authoritative for the stack): design
  decisions live in server-rendered markup + CSS modules/global css or theme
  provider; avoid runtime-styled duplication of tokens. REVIEW reads components +
  style sources; screenshots need the dev/preview server (that skill's tooling).
- **Astro** (`astro` skill authoritative): tokens in `src/styles` / config;
  islands don't change the identity rules. Static render + screenshot is the
  cheapest visual review — prefer it.
- **Component libraries** (shadcn/MUI/…): customize the theme layer; shipping a
  library's untouched defaults as final identity is `A/B/E` slop unless the brand
  genuinely is that theme. Extend, restyle, or state the constraint.
- **Game UI** (`godot`, `defold-development` authoritative for engine code):
  themes/theme resources/StyleBoxes (Godot), GUI/`gui.input_mode`, fonts,
 nine-patch (Defold). The game surface must NOT read as a web dashboard: derive HUD/
  menu language from the game's fiction + engine fonts (`design-directions.md`
  Gaming/Pixel). Engine font pipelines constrain type — plan within them.
- **Docs/magazine/content systems**: typography + measure first; content model
  drives layout (`design-principles.md`).

## Activation guidance (when to load this skill)

Load: new UI, page/landing/dashboard/design-system authoring, redesign/
modernization, component styling, visual-quality review, game menu/HUD identity.
Do NOT load: backend, pure logic, non-visual refactor, build/config with no UI
change. GUARD mode fires inline when UI code is being written and stays silent
otherwise.

## Missing tools policy

No browser → `VISUAL_REVIEW_REQUIRED`, never a fake pass. No config → defaults.
No sibling skills present → all floors here still apply unchanged.
