# React Core — Components, Composition, Hooks Discipline

## Component model

Function components + JSX/TSX only. Class components = legacy; touch only in
existing codebases. One component file exports one component; file name ==
component name (PascalCase).

```tsx
type BadgeProps = { label: string; tone?: "neutral" | "accent" };

export function Badge({ label, tone = "neutral" }: BadgeProps) {
  return <span data-tone={tone}>{label}</span>;
}
```

Props: typed with an explicit `type XProps` (not `interface` inheritance
games). `children?: ReactNode` when it accepts children. Destructure in the
signature. No `React.FC` (adds implicit children, hides generics).

## Composition over configuration

- Small components composed via `children`/slots beat one component with 12
  boolean props. If a component grows a prop per variant-per-context, split
  it or accept render-prop/slot children.
- **State colocation:** state lives in the lowest component that owns all its
  readers. Lift only on demand. Deep prop-drilling past 2 levels ⇒ Context or
  restructure, not a store.
- **Component boundaries:** a component ends where its reason to change ends.
  Presentation (props→markup) separated from logic (hooks, data shaping) —
  logic in custom hooks, not in the JSX tree.
- Avoid premature abstraction: a second consumer is the trigger for a generic
  component, not a "maybe we'll need it". Three similar blocks < wrong
  abstraction.

## Hooks discipline

- Hooks order is stable per component; no conditional hook calls.
- `useState` for values that render; `useRef` for values that must not
  re-render (timers, DOM nodes, previous values).
- `useReducer` once state transitions are multiple/interdependent or the
  updater needs the previous state under events you don't control.
- **Effects:** an Effect synchronizes with an external system (subscription,
  browser API, imperative child). NOT for: deriving state (compute during
  render), transforming fetched data (do it at the fetch site), event logic
  (put it in the handler). If deleting the Effect breaks nothing, delete it.
  Cleanup is mandatory for anything that outlives the render (listeners,
  observers, async): return it and honor re-runs.
- **Custom hooks** = named logic extraction with a `use` prefix; they are
  the reuse primitive, preferred over component inheritance and HOCs.
- `useContext` for read-mostly trees (theme, locale, auth session). Writer
  churn through Context re-renders consumers — split contexts by update
  frequency before adding one.

## Controlled vs uncontrolled

Controlled (`value`+`onChange`) when the parent needs the value to render or
validate live. Uncontrolled (`defaultValue` + ref/FormData) for simple forms,
file inputs, high-frequency inputs where per-keystroke renders cost more than
they return. Both allowed; mixing mid-lifetime is a bug source.

## Error boundaries & Suspense

- Error boundaries are class components (only surviving class use) or a
  library component; wrap at data-load and route segments, show recovery UI.
- `Suspense` boundary: place where the *fallback* should appear, not at the
  root. `startTransition` + Suspense for navigations so stale UI survives.
- `lazy`+`Suspense` for route-level and heavy-below-the-fold splits; not for
  tiny components (network waterfall > saved bytes).
- Portals for overlay surfaces (modals, tooltips, toast layers) so CSS
  stacking/overflow stops fighting you — events still bubble through the
  React tree.
- Refs: forward via props (`ref` as a normal prop on React 19+, no
  `forwardRef` needed); `useImperativeHandle` only to expose a narrow
  imperative API (focus, scrollTo) on a composite.

## Server/client note (Next.js)

This file governs React in any stack. In Next.js, a component that renders
without browser APIs/state stays a Server Component — see
`nextjs-rendering.md`. Never port `"use client"` habits into Astro/Vite
projects; never port Next idioms into React-only apps.

## Typical mistakes

| Mistake | Fix |
|---|---|
| `useEffect` to copy props into state | derive during render |
| Derived state duplicated in two `useState` | compute from one source |
| `useEffect` fetching with manual abort/loading | framework data layer or a query library (opt-in) |
| Context holding fast-changing values used by all | split context / move state down |
| 15-prop god component | compose with children/slots |
| `forwardRef` on React 19 new code | `ref` prop directly |
