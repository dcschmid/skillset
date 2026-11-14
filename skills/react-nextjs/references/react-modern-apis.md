# Modern React APIs — selection guide (React 19.x line)

For each: purpose · use when · avoid when · version floor. Verify floor against
installed React (`node -p "require('./node_modules/react/package.json').version"`).

## `use` (React 19.0)
Purpose: read a Promise or Context *without* suspending the whole component
tree the way `use(Context)`/`use()` did; conditional-friendly Context read;
await-in-render of promises passed as props.
Use: conditional Context reads; consuming a promise from a Server Component
(Next) or loader. Avoid: as a general "async state" wrapper — it has no
cancellation/cache; repeated re-renders re-await. TS: `use<T>(promise: Promise<T>): T`.

## `useActionState` (React 19.0; replaces `useFormState`)
Purpose: state for a form action: receives `(prevState, formData)`, returns
`[state, formAction, isPending]`.
Use: form submissions against Server Functions (Next) or any async action.
Avoid for non-form logic (that's `useTransition`). Never call the old
`useFormState` name — beta-only, not stable.

## `useFormStatus` (React 19.0)
Purpose: read submit/pending status of the *parent* `<form>` inside a child
(no prop drilling of `isPending`). Use only in a component rendered as a form
child. Avoid: to gate a sibling — lift state or `useActionState` instead.

## `useOptimistic` (React 19.0)
Purpose: render a provisional value while an async action settles; auto-rolls
back on failure. Use: list add/edit where latency > render cost and failure
is rare/recoverable. Avoid: when correctness demands server truth before
display (payments, inventory counts). Needs an action wrapper; pairs with
`useActionState`/transitions, not raw `onClick` async.

## `useTransition` / `startTransition` (18.0; `addTransitionType` 19.2)
Purpose: mark updates non-urgent; keep UI responsive; lets Suspense show the
old tree. Use: filtering large lists, tab switches with heavy content. Avoid:
input value updates (that's `useState` — typing must feel instant), tiny
updates (pure overhead). TS returns `[isPending, startTransition]`.

## `useDeferredValue` (18.0)
Purpose: render a lagging copy of a prop/state so the expensive list keeps
stale UI while the input stays live. Use: you own the value but not the
expensive consumer (third-party list). Prefer `useTransition` when you own
both sides. Avoid: as a debounce substitute for network calls.

## `useEffectEvent` (19.x compiler-era; verify installed floor)
Purpose: a function that reads latest props/state but never becomes a
dependency — the honest escape hatch for "not reactive" logic inside Effects.
Use: non-reactive callbacks inside Effects (analytics on mount with current
locale). Avoid: as a general useCallback replacement, and for anything that
should retrigger the Effect.

## `<Activity>` (19.2)
Purpose: keep a subtree mounted (state/effects alive) while hidden — tabs,
keep-alive panels — cheaper than unmount/remount, unlike `display:none` hacks
it tells React the tree is inactive. Use: repeated show/hide with live state.
Avoid: one-shot toggles (`hidden` attribute suffices); large hidden trees
still hold memory.

## `<ViewTransition>` (19.2) + CSS `view-transition-name`
Purpose: declarative cross-DOM morph animations via the View Transitions API.
Use: deliberate motion design with `prefers-reduced-motion` honored. Avoid:
as default animation infra; SSR-hydration transitions need care.

## `<Suspense>` · `lazy` · Fragment refs (19: `<Fragment ref>`)
Suspense fallback placement = UX decision, see react-core. Fragment refs:
19 allows `ref` on `<>…</>` wrappers? No — on `<Fragment>` with a real
element child pattern; prefer explicit wrapper element when you need a ref,
mark UNVERIFIED if unsure of the installed version's support.

## Selection ladder (task → API)

| Task | First choice | Not |
|---|---|---|
| local render state | `useState` | store |
| async form + feedback | `useActionState` | manual fetch+spinner state |
| instant-feel list edit | `useOptimistic` + transition | blocking await before update |
| heavy re-render from user input | `useTransition`/`useDeferredValue` | debounce-everything |
| shared read-mostly tree data | `useContext` | global store |
| conditional context read | `use(ctx)` | split into N hooks |
| effect-local "latest value" fn | `useEffectEvent` | dependency-array gymnastics |

No API is "modern by default" — the floor is the installed version, the bar
is a named need.
