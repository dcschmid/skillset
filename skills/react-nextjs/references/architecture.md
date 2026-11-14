# Architecture — structure without ceremony

## Selection (new projects) — record the choice + reason

| Shape | Pick | Structure |
|---|---|---|
| content-first, mixed rendering | Next App Router | `app/` routes + `components/ui` + `components/features/<feature>` + `lib/` |
| client-heavy tool behind auth shell | React + Vite | `src/features/<feature>` (component+hook+api+tests co-located), `src/shared/` |
| library/component kit | tsup/pkg lib | `src/<Component>/` with stories/tests, public exports index |
| existing project | mirror it | never dual-structure |

## Invariants

1. **Feature-first beats layer-first** past small size: everything about
   `checkout` lives near `checkout`. Layers (`components/`, `hooks/`) stay
   for truly cross-feature primitives (Button, useLocalStorage).
2. **One direction of dependency**: features → shared; shared never imports
   features; app shell composes features. Circular imports = structure smell.
3. **Server/client is an architecture axis, not a folder** (Next): colocated
   `*.client.tsx`/default-server with boundary at leaves (rendering.md).
4. **Boundaries own their types**: feature exports its public DTOs; internals
   stay internal (index re-exports or explicit imports, project-consistent).
5. **Config & env**: one env module per app that reads+validates (`zod` or
   manual) and exports typed values; no scattered `process.env`.
6. **Ports for external services**: DB/API clients behind an interface the
   feature consumes, so swapping Prisma↔Drizzle↔REST is one file (only where
   a swap is plausible — YAGNI otherwise).
7. Abstraction budget: new layer/interface/context needs a second consumer or
   a named future change it absorbs. Otherwise inline it.

## Review questions (refactor scope)

Where does a new feature go? Where does a bug get fixed? If answers are "it
depends on who wrote it last" — the architecture is the bug; propose the
smallest restructuring that makes both answers unique.
