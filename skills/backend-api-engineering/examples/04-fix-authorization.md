# Example 4 — fix authorization bugs (IDOR + tenant leak)

Fixture: `tests/fixtures/legacy_app/app.py` — `GET /orders/<id>` lacks
owner check, list unscoped, create mass-assigns. Mode FIX via AUDIT.

fix: reproduce with pytest (403 for foreign owner fails before fix —
proven) → root cause: route predates tenancy; no shared scope helper →
add `scoped_get(order_id, user_id, tenant)` in repository (one place,
authorization.md), call from all order routes → regression tests:
cross-user read 404, cross-tenant list only own rows, create ignores
client `owner_id` → full suite green → status FIXED with test refs.
Not done: RLS rollout (REVIEW REQUIRED — schema change, approval gate).
