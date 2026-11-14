// forms-validation — useActionState + hardened Server Function
// (react-modern-apis.md + nextjs-server-actions.md). Hand-rolled validator:
// no schema lib dependency (rule 7); swap for zod if the project chose one.

// app/settings/actions.ts
"use server";

export type RenameResult =
  | { ok: true }
  | { ok: false; errors: Record<string, string> };

async function rename(input: unknown): Promise<RenameResult> {
  // 1. unknown → validated (typescript.md boundary rule)
  if (typeof input !== "object" || input === null) return fail("bad payload");
  const raw = input as { id?: unknown; name?: unknown };
  if (typeof raw.id !== "string" || !/^[0-9a-f-]{36}$/.test(raw.id)) return fail("bad id");
  if (typeof raw.name !== "string" || raw.name.trim().length === 0 || raw.name.length > 80)
    return fail("name 1..80");

  // 2/3. authn + authz INSIDE the action; ownership in the query (IDOR guard)
  const session = await readSession();
  if (!session) return fail("unauthorized");

  await updateOwned("project", raw.id, session.userId, { name: raw.name.trim() });
  return { ok: true };
}
function fail(m: string): RenameResult {
  return { ok: false, errors: { form: m } };
}
// readSession/updateOwned: project data layer (fullstack-integration.md)
declare async function readSession(): Promise<{ userId: string } | null>;
declare async function updateOwned(table: string, id: string, ownerId: string, data: unknown): Promise<void>;
export { rename };

// settings-form.tsx — client island, minimal surface (rendering.md split)
"use client";
import { useActionState, useOptimistic } from "react";
import { rename, type RenameResult } from "./actions";

export function SettingsForm({ projectId, initialName }: { projectId: string; initialName: string }) {
  const [optimistic, setOptimistic] = useOptimistic(initialName);
  const [state, formAction, isPending] = useActionState(
    async (_prev: RenameResult | null, fd: FormData) => {
      setOptimistic(String(fd.get("name") ?? "")); // provisional UI (react-modern-apis)
      return rename({ id: projectId, name: fd.get("name") });
    },
    null,
  );

  return (
    <form action={formAction}>
      <label htmlFor="name">Project name</label>
      <input id="name" name="name" defaultValue={optimistic} aria-describedby="name-err" />
      {state && !state.ok && <p id="name-err" role="alert">{state.errors.form}</p>}
      <button disabled={isPending}>
        {isPending ? "Saving…" : "Save"}
      </button>
    </form>
  );
}
