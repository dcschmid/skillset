# Example 2 — audit an existing API (Astro endpoints)

Task: "check my endpoints for problems." Mode AUDIT.
`scripts/detect-project.sh .` → `api: http-routes`, `orm:drizzle`,
`class-guess active-project`. Read `src/pages/api/**` + db schema.

Findings (templates/finding.json each, score via scorecard.md):
- HIGH `GET /api/items/[id]` — no owner filter (IDOR) → fix now
  (workflows/fix.md): scope `where(eq(items.ownerId, session.userId))`.
- MEDIUM list route unbounded — add `limit` zod cap + cursor.
- MEDIUM errors: two shapes (throw text vs json 500) → single
  `apiError()` RFC 9457 helper.
- LOW no ETag on expensive GET → `Cache-Control: private,max-age=5` note.
Re-run tests + detect; fixes carry vitest regressions. Deep vuln sweep →
ultimate-security-hardening (handoff noted in finding.handoff).
