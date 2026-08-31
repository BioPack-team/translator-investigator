#!/usr/bin/env python3
"""Instantiate a framework artifact from its template — deterministically, so the agent edits a
real copy of the skeleton instead of improvising from a sibling. Stdlib only; refuses to overwrite.

Usage:
  new-artifact.py component|tool|extension <name>
      → <plural>/<name>/definition.md   (from templates/<type>/definition.md)
  new-artifact.py concept <slug> [--bundle <kind>/<name>]
      → concepts/<slug>.md  or  <kind>/<name>/concepts/<slug>.md   (from templates/concept.md)
  new-artifact.py worknotes --dest <dir>
      → <dir>/worknotes.md   (from templates/worknotes.md)

Prints the created path. The agent then edits it to fill the placeholders.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
# bundle kinds — accept singular (natural: "new-artifact.py component foo") or plural (the dir name)
SINGULAR = {"component": "components", "tool": "tools", "extension": "extensions"}
PLURAL = {v: k for k, v in SINGULAR.items()}
BUNDLE_TYPES = tuple(SINGULAR) + tuple(PLURAL)  # both forms allowed


def to_singular(kind: str) -> str | None:
    """Normalize a bundle kind (singular or plural) to its singular form, or None if not a kind."""
    if kind in SINGULAR:
        return kind
    return PLURAL.get(kind)


def create(src: Path, dest: Path) -> int:
    if not src.exists():
        print(f"new-artifact: template not found: {src.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if dest.exists():
        print(f"new-artifact: refusing to overwrite existing {dest.relative_to(ROOT)}", file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    print(str(dest.relative_to(ROOT)))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="new-artifact.py")
    p.add_argument(
        "type", choices=[*BUNDLE_TYPES, "concept", "snippet", "worknotes", "scope", "issue-sources"]
    )
    p.add_argument("name", nargs="?", help="bundle name or concept slug")
    p.add_argument("--bundle", help="for a bundle concept: <kind>/<name> (kind singular or plural)")
    p.add_argument("--dest", help="for worknotes: the investigation dir")
    a = p.parse_args()

    if a.type in ("scope", "issue-sources"):  # per-dev root config, copied from templates/
        return create(ROOT / "templates" / f"{a.type}.yaml", ROOT / f"{a.type}.yaml")

    singular = to_singular(a.type)
    if singular:  # a bundle definition
        if not a.name:
            p.error(f"{a.type} needs a <name>")
        src = ROOT / "templates" / singular / "definition.md"
        dest = ROOT / SINGULAR[singular] / a.name / "definition.md"
    elif a.type == "concept":
        if not a.name:
            p.error("concept needs a <slug>")
        src = ROOT / "templates" / "concept.md"
        if a.bundle:
            kind, _, bname = a.bundle.partition("/")
            plural = SINGULAR.get(to_singular(kind) or "")
            if not plural or not bname:
                p.error(f"--bundle must be <kind>/<name> with a valid kind; got '{a.bundle}'")
            bundle_dir = ROOT / plural / bname
            if not (bundle_dir / "definition.md").exists():
                p.error(f"no bundle at {plural}/{bname} (create it first with new-artifact.py)")
            base = bundle_dir / "concepts"
        else:
            base = ROOT / "concepts"
        # new concepts start LOCAL/unaudited → underscore prefix (gitignored until /contribute
        # promotes them to canonical by dropping the prefix). See BUNDLES.md / plan §8.
        dest = base / f"_{a.name}.md"
    elif a.type == "snippet":  # opt-in snippet skeletons in a bundle's snippets/
        kind, _, bname = (a.bundle or "").partition("/")
        plural = SINGULAR.get(to_singular(kind) or "")
        if not plural or not bname:
            p.error("snippet needs --bundle <kind>/<name> (kind singular or plural)")
        bundle_dir = ROOT / plural / bname
        if not (bundle_dir / "definition.md").exists():
            p.error(f"no bundle at {plural}/{bname}")
        (bundle_dir / "snippets").mkdir(parents=True, exist_ok=True)
        for fn in ("AGENTS.local.md", "settings.hooks.json"):
            dest = bundle_dir / "snippets" / fn
            if dest.exists():
                print(f"kept existing {dest.relative_to(ROOT)}")
            else:
                shutil.copyfile(ROOT / "templates" / "snippet" / fn, dest)
                print(str(dest.relative_to(ROOT)))
        return 0
    else:  # worknotes
        if not a.dest:
            p.error("worknotes needs --dest <dir>")
        src = ROOT / "templates" / "worknotes.md"
        dest = ROOT / a.dest / "worknotes.md"

    return create(src, dest)


if __name__ == "__main__":
    sys.exit(main())
