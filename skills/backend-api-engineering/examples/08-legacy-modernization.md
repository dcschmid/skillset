# Example 8 — modernize a legacy monolith without rewriting

Fixture: `tests/fixtures/legacy_app` (Flask, in-memory store, stack-leak
errors, class-guess legacy). Mode ARCHITECTURE/MIGRATE (migrate.md).

Keep Flask + add seams: extract repository (sqlite, keep in-memory behind
adapter) → error handler one RFC 9457 shape (2 deploys, old keys kept as
aliases) → route handlers call service funcs (imports tested) → next
release: blueprint-per-domain only if ownership needs it. Framework swap
(FastAPI) proposed as REVIEW-REQUIRED note with trigger metric, never
applied. Each phase: tests + detect diff green before next phase.
