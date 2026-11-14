# TypeScript — strict by default, boring by design

## Baseline (new projects)

`tsconfig.json`: `"strict": true`, `"target"` per platform floor, module
resolution per framework default (Next bundler/Native-style per installed
version — Next owns its TS config; Vite react-ts template ships sane strict).
TypeScript major per installed project; TS 7 line current-stable at probe —
check `references/version-policy.md` before claiming syntax availability.

## Rules

- No `any` outside typed boundaries; boundary = one function with a comment
  naming the external shape. Prefer `unknown` + narrowing.
- Public shapes: `type`/`interface` with meaning (`Article`, `ArticleDto`),
  not inline object soup. Discriminated unions for finite states:
  `type Load<T> = {status:'loading'} | {status:'ok', data:T} | {status:'err', error:string}`.
- `unknown` from outside (API, FormData, JSON) → validate/narrow at entry,
  typed inside. Never cast-through (`as`) to silence errors; fix the type.
- Generics only where two+ call sites share logic honestly (`List<T>`,
  `useAsync<T>`); no generic-riddle architecture. If a reviewer can't read it
  in one pass, simplify.
- Component/hook typing: props type exported; `children?: ReactNode`;
  events `React.ChangeEvent<HTMLInputElement>` at DOM boundary; generic list
  components take `items: T[]` + `render: (item: T) => ReactNode`.
- Server/client boundary types: DTOs serializable; import types, not impls,
  across the boundary; `satisfies` over `as` where checking shape.
- API responses typed end-to-end (zod schemas if chosen, else hand types
  mirrored once and cross-checked by a test on the sample payload).
- Error types: thrown = `Error` subclasses with codes for expected failures;
  UI gets display-safe messages.

## Verdict

Type-check is a ship gate: `npx tsc --noEmit` green, no `@ts-ignore`
without comment; `@ts-expect-error` preferred (self-clears).
