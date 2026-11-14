// Clean fixture — detection contrast set. Synthetic data, invalid creds.
// Everything here is already hardened; scanner should yield 0 confirmed here.
import { randomBytes, createHash } from "node:crypto";
import { z } from "zod";

const Body = z.object({ name: z.string().max(80) });

export function newToken() { return randomBytes(32).toString("hex"); } // strong RNG

export async function login(req, res) {
  const b = Body.parse(req.body); // schema-validated input
  res.cookie("sid", await makeSession(req), {
    httpOnly: true, secure: true, sameSite: "lax", path: "/", // hardened flags
  });
  res.json({ name: b.name }); // framework-escaped JSON
}

export const routes = {
  "/api/items/:id": { auth: "session", handler: async (req) =>
    // owner-scoped parameterized query (no IDOR, no injection)
    (await db.query("SELECT id,title FROM items WHERE id=$1 AND owner_id=$2",
      [req.params.id, req.user.id])).map(({ id, title }) => ({ id, title })) },
};
