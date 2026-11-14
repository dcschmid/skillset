#!/usr/bin/env python3
"""docs_sync — find docs that drifted from code after changes.

Maps changed files (git diff --name-only RANGE, else working tree) to the
docs that must be re-checked. Read-only: emits a plan, never edits docs.
Auto-edit is only allowed by the agent for VERIFIED facts it re-reads itself.

Usage: docs_sync.py [--range BASE..HEAD] [--json] [--out FILE] [ROOT]
exit: 0 no drift, 1 findings need review
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_lib as L  # noqa: E402

# changed-source pattern -> what must be re-checked in docs
RULES = [
    (r"(package\.json|pyproject\.toml|Cargo\.toml|go\.mod|composer\.json|Pipfile|requirements[.\w]*\.txt)",
     "dependencies/commands changed: verify README install+run+test sections and versions"),
    (r"(\.env\.|config\.(example|sample)|settings\.(py|toml|json)$|\.ini$)",
     "configuration changed: verify every documented env key, default and type"),
    (r"(routes?/|controllers?/|handlers?/|api/|resolvers?/|\.proto$|schema\.graphql|openapi\.(ya?ml|json)|swagger\.)",
     "API surface changed: verify endpoints, methods, params, status codes, examples against code"),
    (r"(migrations?/|models?/|entities/|schema\.sql|\.sql$)",
     "data model changed: verify schema docs, ER diagrams, field lists"),
    (r"(Dockerfile|docker-compose|\.dockerignore|compose\.ya?ml)",
     "container setup changed: verify setup/run instructions and ports"),
    (r"(\.github/workflows/|\.gitlab-ci\.yml|Jenkinsfile|Makefile|justfile)",
     "build/CI changed: verify build/test instructions and required checks"),
    (r"(cli/|cmd/|commands/|__main__\.py|argparse|click\.|commander|yargs|clap)",
     "CLI changed: verify flags, subcommands, help text in the CLI reference"),
    (r"(README|docs/|\.md$|\.mdx$)",
     "docs changed themselves: re-run link + structure checks on the touched files"),
]


def git(root: Path, *cmd: str) -> str:
    r = subprocess.run(["git", *cmd], cwd=root, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed(root: Path, rng: str | None) -> tuple[list[str], str]:
    if not git(root, "rev-parse", "--is-inside-work-tree").strip():
        return [], "not a git worktree"
    if rng:
        out = git(root, "diff", "--name-only", rng.replace("..", " "))
        how = f"git diff {rng}"
    else:
        out = git(root, "diff", "--name-only", "HEAD") + git(root, "diff", "--name-only", "--cached")
        how = "git diff working-tree/HEAD"
    return sorted({f for f in out.splitlines() if f.strip()}), how


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".", type=Path)
    ap.add_argument("--range", help="git range, e.g. main..HEAD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        L.die(f"not a directory: {root}")

    files, how = changed(root, args.range)
    if not files:
        print(f"{how}: no changed files — nothing to sync (NOT RUN for edits)")
        return 0

    docs = {str(d.relative_to(root)) for d in L.walk_docs(root, 1000)}
    tasks: list[dict] = []
    for f in files:
        for pat, instruction in RULES:
            if re.search(pat, f):
                subtree = str(Path(f).parent)
                hits = sorted({d for d in docs if d.startswith(subtree)} |
                              ({p for p in docs if p.lower().startswith("readme")} if docs else set()))
                tasks.append({"changed": f, "instruction": instruction,
                              "candidate_docs": hits[:10] or ["(none found — decide placement)"],
                              "mode": "inspect-then-edit-verified-only"})
                break

    verdict = "REVIEW_REQUIRED" if tasks else "PASS"
    checks = [{"id": "docs-sync", "verdict": verdict,
               "detail": f"{len(files)} changed files, {len(tasks)} sync tasks via {how}",
               "findings": tasks}]
    L.emit({"title": f"docs_sync {root.name}", "checks": checks}, args.out, args.json or bool(args.out))
    return 1 if tasks else 0


if __name__ == "__main__":
    sys.exit(main())
