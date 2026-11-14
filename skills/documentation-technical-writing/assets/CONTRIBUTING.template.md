# Contributing — <project-name>

## Environment setup

Same as README install steps; additionally: <editor config, hooks, verified commands>.

## Workflow

1. Branch from `<default branch>` (verified: `git symbolic-ref refs/remotes/origin/HEAD`).
2. <test command> before committing; <lint/build command> where present.
3. Docs affected by your change: update them in the same commit.

## Conventions

- <naming/format rule sourced from lint config or existing code — not invented>
- Commit style: <observed from git log, or state "no established convention">.

## Review

- <CI checks that must pass, copied from the project's real CI config>
- Docs gate: <markdown lint / link check command, or "not configured">.
