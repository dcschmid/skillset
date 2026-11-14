# Authorization

Load for modes AUTH / AUDIT / FIX. Rule: **authenticated ≠ authorized.**

## Model selection (simplest sufficient)

1. **Ownership check** — resource has `owner_id`; every read/mutate filters
   by it. This covers most apps; start here.
2. **RBAC** — stable role set (admin/editor/member); roles→permissions map
   in code/config, enforced in one layer (middleware/service), not
   copy-pasted per handler.
3. **ABAC/policies** — rules over attributes (tenant, status, time);
   introduce when role explosion proven, via a maintained engine or a
   central `can(user, action, resource)`.
4. **DB-level backstop** — PostgreSQL RLS / tenant views when defense in
   depth is required and the team can maintain policies; document per-table
   policy set.

Enforcement in ONE place (service layer or policy module). Controllers call
`authorize()`; they don't re-implement it. Shared helper for every resource
route — duplicated ad-hoc checks are an audit finding.

## Mandatory checks (audit these first — IDOR/BOLA)

For every route taking an `{id}`:
1. Does the query filter by the caller (owner/tenant), or is access
   intentionally public? Both fine; undeclared is not.
2. Cross-tenant reads: `WHERE tenant_id = current_tenant()` present or
   guaranteed by schema/RLS?
3. Mass assignment: DTO/allowlist selects writable fields; no
   `**request.body` into model constructors.
4. Collection endpoints paginate AND scope before filtering — unbounded
   cross-tenant list is HIGH.
5. Nested resources re-validate the parent chain (`/users/{a}/docs/{b}`:
   doc b belongs to user a).
6. Batch endpoints: element-level authz, not just endpoint-level.
7. Side channels: exports, CSV, search indexes, cache keys, logs carry the
   same tenancy filter.

## Tenant isolation (multi-tenant)

- One strategy: shared-schema+`tenant_id`, schema-per-tenant, or
  db-per-tenant; follow the project's. Never mix ad-hoc.
- Tenant id from session/token, never from client body/query.
- Unique constraints include tenant column; indexes lead with `tenant_id`
  where scans happen.
- Cross-tenant joins only through explicit shared tables.

## Tests (acceptance for AUTH mode)

user A reads/edits/deletes user B's resource → 403/404 · A lists → only
own rows · role endpoints return only permitted actions · anonymous → 401
not 500 · tenant switch isolation · RLS policies exercised by non-owner DB
role · permission change takes effect without re-login where required.
These are the regression tests FIX mode must add when authz was missing.
