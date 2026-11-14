# Framework adapters (detect facts → local idiom; never transplant)

`ds.mjs detect` gives facts. This maps facts to ds-work. Framework best
practice ownership: react-nextjs / astro / (vue,svelte,angular via same
table, extend when a real project needs it). Token/theme/component rules
here stay framework-neutral.

| Stack | tokens in | theming | components | gotchas |
|---|---|---|---|---|
| HTML/CSS/JS | css vars `:root` | data-theme attr + inline head script | web components or plain funcs | no build → generated css committed; content flash w/o JS |
| Tailwind | `@theme`(v4)/config(theme extend) | `dark:` class variant; CSS-var bridge for semantic layer | cn()+cva pattern if project uses | v3 config vs v4 CSS-first — detect version, never mix |
| CSS Modules | imported css vars file | parent scope sets vars | module.s.ts co-located | global vars via `composes`/global scope only |
| CSS-in-JS (sc/emotion) | TS object + css vars for perf | ThemeProvider same keys | co-located | SSR: registered styles/`@emotion/cache`; no runtime randomness |
| React/Next 16 | same as base styling | next-themes if present, else class strategy | forwardRef / React19 ref-as-prop per project React version | server components: no browser APIs; client boundary minimal |
| Astro 5 | `src/styles` + content collection docs | inline script no-flash in Layout.astro | islands minimal props | avoid hydration cost: css-first, island only where interactive |
| Vue 3 | css vars / v-bind css | provide/inject theme ctx | `<script setup>` props typed, defineExpose for refs | scoped-slot state stays in component |
| Svelte 5 | css vars / rune props | class strategy + reactive store | runes ($state/$props), exports = API | snippets over slots where project migrated |
| Web Components | css vars (+`::part` for public hooks) | host attr | customElements define once | styles encapsulation: vars cross, selectors don't |
| Godot 4.7 | Theme resource / ThemeData | default+dark Theme, variations = component tokens | Control + theme_type_variation | no CSS; gamepad focus = engine focus neighbors |
| Defold | .theme GUI files + lua const module | gui theme swap at runtime | gui scripts, builders | engine version 1.14.x truth in its skill |

Extend pattern: new stack = one row, detected by lockfile/deps fact; keep
columns = where tokens live / theming / component shape / top trap.

## Component reuse across stacks
Prefer project-native primitive lib when present (Radix/React Aria for
React; native `<dialog>`/popover elsewhere). Headless libs don't port:
Vue/Svelte = their ecosystem or native elements; don't install React libs
into non-React projects.

## No-dependency rule (binding)
Add a dep only if existing tools can't do the job AND ≥3 components need it.
Icons: project's existing set, imported once, tree-shaken (named imports).
