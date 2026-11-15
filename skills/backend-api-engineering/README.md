# backend-api-engineering

Implement APIs, authentication, authorization, databases, migrations, and background jobs using the existing stack and contracts.

Profile: Private and Working. Preparation: Provide the service path, route or job, expected behavior, and relevant database structure.

Expected result: A feature or fix backed by API, database, or migration tests and observable results.

Requirements and limits: Production database operations, deployments, and breaking contracts require authorization covering those actions. Local checks do not prove a migration works on production data.

## backend-api-engineering: Installation and examples

Install from the repository root:

```bash
tools/install-skills.sh backend-api-engineering
```

Try these prompts in your target project:

**Claude Code:**

```text
Use the backend-api-engineering skill. Audit services/api for missing object authorization and N+1 queries. Fix confirmed issues and add tests for access across tenant boundaries.
```

**Codex:**

```text
Use the backend-api-engineering skill. Add pagination to the existing order list. Follow the API contract and test empty results, boundaries, and invalid parameters.
```

**oh-my-pi:**

```text
Use the backend-api-engineering skill. Plan an expand-and-contract migration for a new tenant ID. Check backward compatibility and show deployment steps without changing production data.
```

## backend-api-engineering: Self-test

Run from the repository root:

```bash
python3 skills/backend-api-engineering/tests/test_skill.py
```

## Files and further reading

Start with [SKILL.md](SKILL.md) for the binding agent workflow. This README
contains the usage guide, host examples, and direct tool instructions.

- [references/](references/): Detailed guidance and rules.
- [workflows/](workflows/): Task-specific procedures.
- [templates/](templates/): Templates for the target project.
- [examples/](examples/): Worked examples.
- [tests/](tests/): Self-tests and fixtures.

These files are present in the skill directory. Check the relevant workflow
or command help before running a tool directly. Helper modules are not
standalone CLI entry points.

- [detect-project.sh](scripts/detect-project.sh)
- [migration-review.sh](scripts/migration-review.sh)
- [validate-openapi.py](scripts/validate-openapi.py)

## Run tools directly

Run these examples from this skill directory, for example after
`cd skills/backend-api-engineering` from the repository root. Replace `/path/...` with
existing paths. Set up required programs before running the commands.

```bash
bash scripts/detect-project.sh /path/to/api
python3 scripts/validate-openapi.py /path/to/openapi.json
bash scripts/migration-review.sh /path/to/migrations
```
