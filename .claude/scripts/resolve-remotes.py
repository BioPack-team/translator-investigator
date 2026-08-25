#!/usr/bin/env python3
"""Resolve the git remotes for a contribution / fix PR — deterministically, so the git/gh commands
that follow don't guess. Prints JSON: {upstream, fork, default_branch, mode, fork_exists, error}.

Usage:
  resolve-remotes.py                    # framework repo (from the current clone) — for /contribute
  resolve-remotes.py --repo <org/repo>  # a specific repo — for `fix` mode (the component's repo)
  [--handle <login>]                    # dev GitHub login (default: `gh api user`)

  upstream       = where the PR lands (the canonical repo)
  fork           = <handle>/<repo-name> (the dev's fork)
  default_branch = upstream's default branch (don't hardcode `main`)
  mode           = "branch" if the dev has push access to upstream, else "fork"

Needs `gh` (network). Best-effort: on gh failure it prints what it can plus an `error` note; the
agent should surface that rather than proceed blindly. Never edits anything.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def gh(*args: str) -> str | None:
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def gh_json(*args: str):
    s = gh(*args)
    if s is None:
        return None
    try:
        return json.loads(s)
    except ValueError:
        return None


def main() -> int:
    p = argparse.ArgumentParser(prog="resolve-remotes.py")
    p.add_argument("--repo", help="target repo <org/repo> (fix mode); omit for the framework repo")
    p.add_argument("--handle", help="dev GitHub login (default: gh api user)")
    a = p.parse_args()

    out = {
        "upstream": None,
        "fork": None,
        "default_branch": None,
        "mode": None,
        "fork_exists": None,
        "error": None,
    }

    handle = a.handle or gh("api", "user", "--jq", ".login")
    if not handle:
        out["error"] = "no GitHub handle (gh api user failed — check `gh auth status`)"

    if a.repo:
        upstream = a.repo
    else:
        info = gh_json("repo", "view", "--json", "nameWithOwner,parent")
        if not info:
            out["error"] = "could not read the current repo (run inside the clone; gh required)"
            print(json.dumps(out, indent=2))
            return 0
        upstream = (info.get("parent") or {}).get("nameWithOwner") or info.get("nameWithOwner")
    out["upstream"] = upstream

    up = gh_json("repo", "view", upstream, "--json", "defaultBranchRef,viewerPermission")
    if up:
        out["default_branch"] = (up.get("defaultBranchRef") or {}).get("name")
        out["mode"] = "branch" if up.get("viewerPermission") in ("ADMIN", "MAINTAIN", "WRITE") else "fork"

    if handle and upstream:
        out["fork"] = f"{handle}/{upstream.split('/')[-1]}"
        out["fork_exists"] = gh("repo", "view", out["fork"]) is not None

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
