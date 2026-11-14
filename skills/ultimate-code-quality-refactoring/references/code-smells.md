# Code Smell Catalog

Detection signals reference `collect_metrics.py` / `detect_duplicates.py`
fields or a grep pattern. **A smell is a finding only with evidence +
impact.** No smell inventory changes code by itself.

## Structure

| Smell | Signal (measurable) | Fix only when |
|---|---|---|
| God function | `long_functions_over_50 ≥ 1`, `complexity_proxy > 20` | function does >1 job AND callers/test surface allow extraction |
| God class / large module | file lines > 500 AND > 4 responsibilities in public surface | responsibilities diverge in change history |
| Long parameter list | `signatures_over_6_params` hit | params are a data clump (travel together) |
| Deep nesting | `max_nesting_depth > 4` | guard clauses preserve ordering semantics |
| Dead code | 0 references repo-wide, exported symbol, verified via LSP/grep incl. dynamic refs | removal survives full-suite run |
| Duplicate code | clone group + sites change together | abstraction couples only cooperating modules |
| Shotgun surgery | 1 concept change touches > 5 files | consolidation preserves public APIs |
| Circular imports | import cycle in dependency graph | split point exists without API churn |
| Primitive obsession | stringly-typed domain value passed through > 3 layers | type is behavior-bearing, not logging sugar |

## Non-smells (do not report as debt)

- Intentional duplication in independent deployables / language adapters.
- Long switch/match over a closed enum (often correct dispatch).
- Boilerplate mandated by framework version (verified against lockfile).
- Generated code, vendored code, snapshot baselines.
- Simple small projects that "look under-engineered" — size earns ceremony.

## Prioritization (P0–P3)

- **P0** provable correctness/stability risk (evidence: failing or flaky
  path, silent data loss).
- **P1** architecture/maintainability damage with change-frequency evidence.
- **P2** worthwhile, not urgent.
- **P3** cosmetic. Default: leave alone unless batched with a P0–P2 pass.

Score inputs: blast radius, test coverage of affected code, edit frequency,
fix cost. Arbitrary severities without these inputs are forbidden.
