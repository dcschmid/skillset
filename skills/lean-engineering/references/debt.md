# /lean debt — the tracked shortcut & complexity ledger

Debt tracking without infrastructure: the ledger is text in the repo the
project already owns. No new tool, no database, no service.

## Two sources

1. **Inline markers** — `shortcut: <the limit>, <when to upgrade>` comments
   placed by the floor rule (engineering-ladder.md). Greppable, live next
   to the code, die with it.
2. **Ledger file** — `LEAN-DEBT.md` at the project root (or the project's
   existing TODO/debt doc if it has one; reuse beats creation). Created on
   first `/lean debt` write, only if the project has none.

## /lean debt (read)

Harvest both sources, report as a table:

| where | shortcut/complexity | limit accepted | upgrade trigger | age | verdict |

`verdict`: KEEP (still earning its place) / RIPENED (upgrade trigger hit) /
STALE (limit no longer real — candidate for the simplify pass). Verdicts
cite evidence (call count, versions, current sizes), not sentiment.

## /lean debt add (write)

Append one row to the ledger. Format is one line per entry so it diffs
cleanly and survives merges:

```
- YYYY-MM-DD  path/to/file.ts:42  reason: <limit>  upgrade: <trigger>
```

## Lifecycle

- An entry's upgrade trigger fires → the entry is work, not debt; it moves
  to the normal task flow (and the inline marker is removed in the same
  change).
- STALE entries batch into `/lean simplify`.
- The ledger is pruned when empty of live entries; a doc nobody reads is
  itself complexity.

## Anti-goals

No tooling beyond grep + one markdown file. No scores. No ceremony that
makes logging debt more expensive than paying it — that inverts the point.
