# Example 7 — analyze a slow endpoint (latency, raw SQL, no ORM)

Fixture: `tests/fixtures/healthy_api/app.py` `handle_orders` — audit
finds the query-per-row loop (scenario D).
Detection: request log/ORM echo shows 1+N statements; fix to single
`IN`-join; compare under identical seeded DB + same limit.

Report form: `GET /orders p95 210→46ms; stmts 51→2 (sqlite3 echo)` —
delta only where measured; if no runner, the claim stops at `NOT TESTED
(manual payload recorded)`. Cache added after, not before: cache hides the
N+1, it doesn't remove it (performance.md ladder step order).
