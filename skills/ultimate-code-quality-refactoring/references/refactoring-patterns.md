# Refactoring Patterns

Each pattern: precondition → transformation → verification. Skip the
transformation if the precondition fails.

| Pattern | Precondition | Verification |
|---|---|---|
| Extract function | contiguous block, single responsibility, no closure writes past scope | same call sites' behavior; characterization test on inputs |
| Guard clause | nested `if` chain, no fallthrough dependency | early-return ordering preserved |
| Collapse duplication | clone group + sites change together | golden output equality on both original sites |
| Remove dead code | 0 refs incl. dynamic/reflection lookup | full suite green |
| Simplify condition | boolean expr with redundant terms | truth-table equivalence (enumerate) |
| Replace magic value | literal reused, single source exists | constant lookup at every site |
| Split module | independent change reasons in one file | public re-exports keep import paths |
| Unify error handling | per-boundary consistent strategy | thrown/returned types stable |

## Execution rules

1. One pattern per step; a step is one commit-sized diff.
2. Format-only noise stays out of functional diffs (no bulk reformat mixed in).
3. Behavior-preserving by default; any intentional behavior change is a BUG
   FIX or FEATURE — labeled, never smuggled into a refactor step.
4. Risk ladder: LOW → apply+verify; MEDIUM → characterization test first;
   HIGH → proposal + approval first (safety-and-rollback.md).
5. Tooling: prefer language-native refactor (LSP/ts-morph/ast-grep/OpenRewrite)
   when available; manual edits acceptable when edits stay small and review
   stays textual (tool-integration.md).

## When NOT to refactor

- Code is stable, tested, rarely edited, and understood → leave it.
- The "better" version needs a framework the project does not use.
- Test surface absent AND behavior not charactizable → UNVERIFIED, propose
  tests first, edit after.
