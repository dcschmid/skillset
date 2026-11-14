# API documentation

Contracts first: docs describe the API, never reshape it. Source order:
framework metadata → route/controller code → tests → generated spec → prose.

## Version truth

OpenAPI 3.2.1 is published; toolchains lag. Before writing or linting a spec,
probe what THIS project's generator/validator accepts (redocly, swagger-cli,
openapi-typescript, swashbake… whatever the lockfile pins) and target that.
Document the supported version in the spec header; never claim a version the
project's validator rejects.

## What must be verified per endpoint

path + method (from router), params (name/in/required/type from handler
signatures or serializers), status codes INCLUDING error paths (from code and
tests, not just 200), auth scheme (middleware/decorators), pagination and
rate-limit behavior (only if implemented), examples copied from tests or a
real run.

Anything unconfirmed → open question section, not a guessed schema.

## Formats

- REST: OpenAPI file if the project generates one — regenerate, don't hand-
  edit generated output. Markdown reference (assets/API.template.md) where
  no spec toolchain exists.
- GraphQL: schema files are the reference; prose covers directives, auth
  context, error conventions.
- gRPC: .proto is the reference; document streaming/deadline conventions.
- Events/webhooks: envelope, retry + idempotency semantics, delivery
  guarantees — only what code enforces.

## Checks

`docs_check.py` for links/structure; redocly (when installed) for spec lint;
contract tests when the project has them. FAIL on spec-vs-code mismatch;
NOT RUN when the linter is absent.

## Ownership

backend-api-engineering owns API *design and implementation* questions
(endpoint design, authz model, migrations). This skill owns the *docs*: what
and how they are written, kept true, validated, synced. Route design changes
there; route drift findings back here.
