# Technical Debt Management

Debt is inventory, not shame. Every entry is actionable or it is noise.

## Finding record (schema: templates/technical-debt-entry.md)

id · title · category (smell|architecture|duplication|complexity|dead-code|
tests|docs|deps) · location `file:line` · evidence (measured output or diff
excerpt) · cause · impact · risk (LOW/MED/HIGH) · effort (S/M/L) · action ·
verification strategy · status (open|approved|in-progress|done|wontfix).

## Priority = evidence, not vibes

- **P0** provable correctness/stability risk, failing or flaky path.
- **P1** architecture/maintainability damage + change-frequency or blast
  radius evidence.
- **P2** measured, not urgent (clone groups, hotspot files rarely edited).
- **P3** cosmetic — batch or drop.

Inputs: blast radius, coverage of affected code, edit frequency (git churn),
fix cost, dependency fan-out. Without these inputs a finding ships as P3 or
unranked with "insufficient ranking basis".

## Roadmap rules

- Packages are small, independent, each ends green against baseline.
- Order: high benefit × controlled risk first; P0 correctness always first.
- `wontfix` is a valid terminal state with a one-line reason (intentional
  duplication, frozen legacy module, size does not earn ceremony).
- The backlog lives in the project (docs/ or issue tracker), not in the
  skill; the skill seeds it from `templates/technical-debt-backlog.md`.
