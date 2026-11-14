# Server Functions / Server Actions — security posture & patterns

**A Server Function is a public HTTP endpoint wearing an internal hat.**
Anything callable from a form or client import can be called by a client
developer. Harden like an API.

## Shape (App Router, React 19 / Next 16)

```tsx
// app/dashboard/actions.ts
"use server";
import { z } from "zod";                       // schema lib = opt-in, project choice
import { revalidateTag } from "next/cache";

export async function renameProject(input: unknown) {
  const data = z.object({ id: z.string().uuid(), name: z.string().min(1).max(80) })
    .parse(input);                              // 1. validate — unknown input
  const session = await auth();                 // 2. authorize per call
  if (!session?.user) throw new Error("unauthorized");
  await db.project.update({ where: { id: data.id },
    data: { name: data.name },
    // 3. scope: never trust client id alone
    where: { id: data.id, ownerId: session.user.id } });
  revalidateTag(`projects:${session.user.id}`); // 4. invalidation
  return { ok: true };                          // 5. minimal, no secrets
}
```

## Mandatory per action

1. **Validate input** (`unknown` + schema) — lengths, enums, ids.
2. **AuthN + AuthZ inside the function** — session read, ownership check in
   the query, role check for admin ops. Auth on pages ≠ auth on actions.
3. **IDOR guard** — every client-supplied id filtered by owner/tenant in the
   DB call, not just checked.
4. **Invalidate** what changed (tag/path), same file, visible.
5. **Return minimal DTO** — no full rows, no internal fields, no secrets.
6. **Errors**: actionable messages; stack traces stay server-side.

## Forms & UX

`useActionState` + `useFormStatus` + `useOptimistic` = submit/pending/optimistic
without hand-rolled flags (react-modern-apis.md). Progressive enhancement:
`<form action={fn}>` works without JS where feasible.

## Purity & boundaries

Actions run on the server, may be re-invoked by replay — make them
idempotent or carry a token (payments!). `cookies()`/`headers()` reads fine;
writes via Response API not inside actions.

## When NOT an action

- Needs HTTP semantics (headers/status) → Route Handler.
- External caller/webhook → Route Handler + signature verification.
- Read-heavy listing → Server Component + cache policy, not an action.

## Tests

Unit-test validation + authz branches (pure logic extracted); flow-test the
critical ones in E2E (testing.md). Every action file: input, unauth, other
user's resource — three minimum cases.
