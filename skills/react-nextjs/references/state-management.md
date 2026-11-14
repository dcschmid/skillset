# State Management — right tool, lowest owner

## Placement ladder (walk top-down, stop at the first fit)

1. **Derivable?** Compute in render. Zero state.
2. **Local UI state** (open/tab/input) → `useState`/`useReducer` at the
   lowest component that renders all readers.
3. **URL-shareable** (filters, page, selected tab worth linking) → search
   params/path (`useRouter`/`useSearchParams` Next; `URLSearchParams`+history
   in plain React). URL is free persistent global state.
4. **Server data** (lists, records) → server cache (Next data layer; plain
   React: TanStack Query *opt-in* when client-side caching/dedup is a proven
   need — named need or no dep).
5. **Read-mostly tree context** (theme, locale, session) → Context split by
   update frequency (react-core.md).
6. **Cross-cutting fast-changing client state** → `useReducer`+Context module
   before a store; Zustand when middleware/selector ergonomics are asked for
   with a reason; Redux Toolkit only where team/devtools/time-travel demands
   it. Never auto-installed.
7. **Persistent** (survive reload) → URL/localStorage/IndexedDB behind a tiny
   hook with versioning + JSON validation (`unknown` first).
8. **Optimistic** → `useOptimistic` (19) or write-target + rollback; pairs
   with actions (server-actions.md).

## Rules

- One source per fact; duplicates need a sync mechanism or get deleted.
- Store shape = behavior need, not API mirror. Selectors beat deep reads.
- Forms: framework-native (useActionState/Form state of the lib in use)
  before a form library.
- Auth/session: server session or tokens; client holds display copy only.
- Test the placement with: "which components re-render and must they?"

## Signals to add a library (all must hold)

Named need above ladder + ladder exhausted + dep justified in report.
Otherwise: no new dependency (SKILL rule 7).
