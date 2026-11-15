# Backend examples

These ten scenarios show how to request backend work and what evidence to
expect. They describe the task, workflow, and verification; they are not
deployable services. Related fixtures live in `../tests/fixtures/`.

| Example | Use it for |
|---|---|
| [Build a REST API](01-new-rest-api.md) | New endpoints with explicit contracts |
| [Audit an existing API](02-audit-existing-api.md) | Systematic service inspection |
| [Verify OIDC](03-verify-oidc.md) | Check authentication against actual configuration |
| [Fix authorization](04-fix-authorization.md) | Prevent access to another user's data |
| [Optimize PostgreSQL](05-optimize-postgres.md) | Improve queries and indexes using evidence |
| [Plan a safe migration](06-safe-migration.md) | Evolve the schema compatibly |
| [Investigate a slow endpoint](07-slow-endpoint.md) | Measure, change, and measure again |
| [Modernize a legacy service](08-legacy-modernization.md) | Preserve existing behavior |
| [Prepare for production](09-production-ready.md) | Identify operational and verification gaps |
| [Add contract tests](10-contract-tests.md) | Protect interface compatibility |

Open your project in Claude Code, Codex, or oh-my-pi and ask:

```text
Use backend-api-engineering. Follow the safe-migration example to plan a new
tenant ID in our existing database. Check compatibility and rollout steps
without running a production migration.
```

See the [skill README](../README.md) for installation, limits, and tool commands.
