# Website Rewrite example — local project, dry-run first

Site: docs/content project `content/blog/post.md` (Markdown, frontmatter,
one code fence).

Phase flow used: audit → proposals (agent-authored) → plan (validates
protected spans) → apply --dry-run → user approves → apply --write →
validate (build+tests).

**Original** (`content/blog/post.md:6-8`)
> In der heutigen schnelllebigen Welt ist es wichtig zu betonen, dass Tempo nicht alles ist.

**Replacement**
> Tempo ist nicht alles; der Rechner braucht Ruhe.

Reason: filler opener, no information. Facts (Docker 24.0.2, code fence,
frontmatter keys) outside editable spans — untouched.

```diff
--- content/blog/post.md
- In der heutigen schnelllebigen Welt ist es wichtig zu betonen, dass Tempo nicht alles ist.
+ Tempo ist nicht alles; der Rechner braucht Ruhe.
```

Apply report printed `applied: 1, mode: dry-run` before any write; second
run wrote. Repeat audit afterwards: 0 new findings → converged (gate: 2
passes max).
