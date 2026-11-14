# Architecture Review

Architecture findings need structural evidence, not taste. Evidence sources:
import/dependency graph, change co-occurrence (git history), public API
surface, test seams.

## What to check

1. **Dependency direction** — do low-level modules import high-level policy?
   Cycle in import graph = finding (P1) unless a documented boundary rule
   allows it.
2. **Concern placement** — business logic in UI render paths, SQL in request
   handlers, engine calls in domain code. Finding = cite the file:line where
   the concern leaks.
3. **Boundary integrity** — modules imported by > N unrelated others with a
   wide surface = candidate seam; propose split only if the two halves have
   independent change reasons.
4. **State ownership** — same state stored twice (cache + source of truth)
   without a sync point is a defect vector, not a style issue.
5. **Error strategy** — mixed raise/return-null/Result per call path. One
   strategy per boundary is the finding threshold.

## Migration discipline

Recommend architecture (Hexagonal, DDD, ECS, Clean) only when the current
shape demonstrably blocks a change the project needs. Small projects stay
simple — that is the correct architecture for them.

For any approved structural change: problem evidence → impact → 2+
alternatives compared → risk class → incremental steps, each step verifiable
(green suite per step). Never big-bang rewrites.

## Detection recipes (zero-dep)

- Import graph: grep import/require/use per file → edge list → cycle check
  (language adapters have per-language patterns).
- Layer violation: grep for higher-layer identifiers inside lower-layer dirs
  (e.g. component names in `*/domain/*`).
- Dead seams: exported symbol with 0 importers outside its module.
