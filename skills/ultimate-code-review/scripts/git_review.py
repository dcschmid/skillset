#!/usr/bin/env python3
"""git_review.py — resolve a review scope into a machine-readable bundle.

Read-only toward the repository: runs `git` query commands only (rev-parse,
merge-base, diff, status, ls-files). Never fetches, commits, or writes inside
the project (output goes to -o or stdout).

Modes (positional: repo dir, default "."):
  --base REF        three-dot review: git diff merge-base(REF, HEAD)..HEAD
  --commit REF      single commit review (vs its parent)
  --range A..B      two-dot review: git diff A B
  --staged          staged changes (git diff --cached)
  --uncommitted     staged + unstaged + untracked working changes
  --file PATH       full-file review of one path (must exist)
  --full            whole-repo inventory (tracked files, excludes applied)
  (no mode)         default: dirty tree -> uncommitted; upstream -> base
                    upstream; otherwise NEEDS_BASE_REF (never a guess).

--exclude GLOB      extra exclude pattern (repeatable). --max-files N (default
2000). Exit: 0 scope resolved (incl. NO_CHANGES), 1 bad ref/config/repo.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_EXCLUDES = [
    "node_modules/", ".git/", "dist/", "build/", "__pycache__/", ".venv/",
    "venv/", "*.min.js", "*.min.css", "*.lock", "*-lock.json", "*.snap",
]
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
              ".mp3", ".wav", ".ogg", ".mp4", ".woff", ".woff2", ".ttf",
              ".zip", ".glb", ".gltf", ".fbx", ".blend", ".ogg", ".exr"}


def die(msg):
    print(json.dumps({"error": msg}), file=sys.stdout)
    sys.exit(1)


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                       text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def resolve_ref(repo, ref):
    rc, out, _ = git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    return out.strip() if rc == 0 and out.strip() else None


def excluded(path, patterns):
    parts = path.split("/")
    for p in patterns:
        p = p.rstrip("/")
        if p.startswith("*"):
            if path.endswith(p[1:]):
                return True
        elif any(part == p for part in parts) or path.startswith(p + "/"):
            return True
    return False


def numstat(repo, cmd_args):
    """cmd_args: list forming the diff command; returns file records."""
    rc, out, err = git(repo, *cmd_args)
    if rc != 0:
        die("diff failed: " + err.strip()[:200])
    rc2, ns, _ = git(repo, *[a for a in cmd_args if a != "--numstat"]
                     + ["--name-status"])
    status_map = {}
    for line in ns.splitlines():
        f = line.split("\t")
        if len(f) >= 2:
            status_map[f[-1]] = f[0][0]
    files = []
    for line in out.splitlines():
        f = line.split("\t")
        if len(f) < 3:
            continue
        add, dele, path = f[0], f[1], f[-1]
        files.append({"path": path, "status": status_map.get(path, "M"),
                      "added": add, "removed": dele})
    return files


def tracked_files(repo, patterns, max_files):
    rc, out, err = git(repo, "ls-files")
    if rc != 0:
        die("not a git repository or ls-files failed: " + err.strip()[:120])
    files = [p for p in out.splitlines()
             if p and not excluded(p, patterns)
             and not p.rsplit(".", 1)[-1].lower() in BINARY_EXT
             and ("." not in p or p.rsplit(".", 1)[-1].lower() not in BINARY_EXT)]
    return files[:max_files]


def main():
    ap = argparse.ArgumentParser(prog="git_review.py")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--base"), ap.add_argument("--commit"), ap.add_argument("--range")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--uncommitted", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--max-files", type=int, default=2000)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    repo = a.repo
    patterns = DEFAULT_EXCLUDES + a.exclude

    rc, _, err = git(repo, "rev-parse", "--git-dir")
    if rc != 0:
        die("not a git repository: " + repo)

    scope = {"tool": "git_review.py", "generated_at":
             datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "repo": repo, "status": None, "mode": None, "base": None,
             "base_sha": None, "target": None, "target_sha": None,
             "merge_base_sha": None, "diff_command": None, "files": [],
             "staged_files": [], "unstaged_files": [], "untracked_files": [],
             "excluded_patterns": patterns, "notes": []}

    def untracked():
        rc, out, _ = git(repo, "ls-files", "--others", "--exclude-standard")
        return [p for p in out.splitlines() if p and not excluded(p, patterns)] \
            if rc == 0 else []

    def finalize(files, status=None):
        scope["files"] = [f for f in files if not excluded(f["path"], patterns)]
        if status:
            scope["status"] = status
        elif not scope["files"] and not scope["untracked_files"]:
            scope["status"] = "NO_CHANGES"
        else:
            scope["status"] = "RESOLVED"

    if a.base:
        if not resolve_ref(repo, a.base):
            die(f"invalid ref: {a.base!r} (git rev-parse failed)")
        mb = git(repo, "merge-base", a.base, "HEAD")[1].strip() or None
        scope.update(mode="base", base=a.base, base_sha=resolve_ref(repo, a.base),
                     target="HEAD", target_sha=resolve_ref(repo, "HEAD"),
                     merge_base_sha=mb,
                     diff_command=f"git diff {a.base}...HEAD  "
                                  f"(three-dot = merge-base {mb} to HEAD)")
        if not mb:
            die(f"no merge-base between {a.base} and HEAD")
        finalize(numstat(repo, ["diff", "--numstat", mb, "HEAD"]))
    elif a.commit:
        if not resolve_ref(repo, a.commit):
            die(f"invalid ref: {a.commit!r}")
        parent = git(repo, "rev-parse", "--verify", "--quiet",
                     a.commit + "^")[1].strip() or None
        args = (["diff", "--numstat", parent, a.commit] if parent
                else ["show", "--numstat", "--format=", a.commit])
        scope.update(mode="commit", commit=a.commit,
                     target_sha=resolve_ref(repo, a.commit),
                     base=parent, diff_command=f"git {args[0]} ... {a.commit}")
        files = numstat(repo, args)
        finalize(files)
    elif a.range:
        if ".." not in a.range:
            die("range must be A..B")
        left, right = a.range.split("..", 1)
        ls, rs = resolve_ref(repo, left), resolve_ref(repo, right)
        if not ls or not rs:
            die(f"invalid range endpoint in {a.range!r}")
        scope.update(mode="range", base=left, base_sha=ls, target=right,
                     target_sha=rs, diff_command=f"git diff {left} {right} "
                                                 "(two-dot = direct compare)")
        finalize(numstat(repo, ["diff", "--numstat", ls, rs]))
    elif a.staged:
        scope.update(mode="staged", target="INDEX",
                     diff_command="git diff --cached")
        files = numstat(repo, ["diff", "--cached", "--numstat"])
        scope["staged_files"] = [f["path"] for f in files]
        finalize(files)
    elif a.file:
        rc, out, _ = git(repo, "ls-files", "--error-unmatch", a.file)
        if rc != 0 and not (repo_path := __import__("pathlib").Path(repo, a.file)).exists():
            die(f"unknown file: {a.file!r}")
        scope.update(mode="file", file=a.file, target="WORKTREE",
                     diff_command=f"full-file review of {a.file}")
        finalize([{"path": a.file, "status": "review", "added": "-", "removed": "-"}])
    elif a.full:
        scope.update(mode="full", target="HEAD",
                     target_sha=resolve_ref(repo, "HEAD"),
                     diff_command="git ls-files (inventory; review by priority)")
        files = tracked_files(repo, patterns, a.max_files)
        scope["files"] = [{"path": p, "status": "inventory",
                           "added": "-", "removed": "-"} for p in files]
        scope["file_count"] = len(files)
        scope["truncated"] = len(files) >= a.max_files
        scope["status"] = "RESOLVED"
    elif a.uncommitted or _default_uncommitted(repo):
        scope["mode"] = "uncommitted"
        scope["diff_command"] = ("git diff --cached (staged) + git diff "
                                 "(unstaged) + git ls-files --others (untracked)")
        st = numstat(repo, ["diff", "--cached", "--numstat"])
        us = numstat(repo, ["diff", "--numstat"])
        scope["staged_files"] = sorted({f["path"] for f in st})
        scope["unstaged_files"] = sorted({f["path"] for f in us})
        scope["untracked_files"] = untracked()
        seen, files = set(), []
        for f in st + us:
            if f["path"] not in seen:
                seen.add(f["path"])
                files.append(f)
        files += [{"path": p, "status": "?", "added": "-", "removed": "-"}
                  for p in scope["untracked_files"]]
        finalize(files)
    else:
        cands = [b for b in ("main", "master", "develop", "trunk")
                 if resolve_ref(repo, b)]
        scope.update(mode="needs-base-ref", candidates=cands,
                     status="NEEDS_BASE_REF",
                     notes=["multiple plausible baselines — pass --base REF; "
                            "no arbitrary baseline is used"])
    _emit(a, scope)


def _default_uncommitted(repo):
    rc, out, _ = git(repo, "status", "--porcelain")
    return rc == 0 and bool(out.strip())


def _emit(a, scope):
    text = json.dumps(scope, indent=1, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"scope -> {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
