#!/usr/bin/env python3
"""Disable a bundle: remove its skill symlinks + .git/info/exclude entries, re-index concepts,
remove its AGENTS.local.md snippet block, and best-effort remove its settings.local.json hooks.
Stdlib only; idempotent. Reverse of enable-bundle.py.

Usage: disable-bundle.py <kind> <name>     # kind = components | tools | extensions

Does NOT edit scope.yaml (the agent removes it from `enabled:` first). Hook removal is
**content-based and best-effort** — the agent should verify settings.local.json afterward and clean
up any leftover (e.g. if the dev hand-edited a merged hook).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
KINDS = ("components", "tools", "extensions")
AGENTS_LOCAL = ROOT / "AGENTS.local.md"
SETTINGS_LOCAL = ROOT / ".claude" / "settings.local.json"


def drop_excludes(lines: set[str]) -> None:
    exclude = ROOT / ".git" / "info" / "exclude"
    if not exclude.exists():
        return
    kept = [ln for ln in exclude.read_text().splitlines() if ln not in lines]
    exclude.write_text("\n".join(kept) + ("\n" if kept else ""))


def remove_md_snippet(tag: str) -> bool:
    if not AGENTS_LOCAL.exists():
        return False
    start, end = f"<!-- BUNDLE-SNIPPET:{tag}:START -->", f"<!-- BUNDLE-SNIPPET:{tag}:END -->"
    text = AGENTS_LOCAL.read_text(encoding="utf-8")
    s, e = text.find(start), text.find(end)
    if s == -1 or e == -1 or e < s:
        return False
    new = (text[:s].rstrip() + "\n" + text[e + len(end) :].lstrip("\n")).strip() + "\n"
    AGENTS_LOCAL.write_text(new, encoding="utf-8")
    return True


def remove_hooks(frag: dict) -> int:
    if not SETTINGS_LOCAL.exists():
        return 0
    settings = json.loads(SETTINGS_LOCAL.read_text())
    hooks = settings.get("hooks", {})
    removed = 0
    for event, entries in frag.get("hooks", {}).items():
        arr = hooks.get(event, [])
        for entry in entries:
            while entry in arr:  # deep-equality via ==
                arr.remove(entry)
                removed += 1
        if event in hooks and not hooks[event]:
            del hooks[event]
    if hooks == {}:
        settings.pop("hooks", None)
    SETTINGS_LOCAL.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return removed


def main() -> int:
    p = argparse.ArgumentParser(prog="disable-bundle.py")
    p.add_argument("kind", choices=KINDS)
    p.add_argument("name")
    a = p.parse_args()

    bundle = ROOT / a.kind / a.name
    dest_root = ROOT / ".claude" / "skills"

    # skill sources mirror enable-bundle: the bundle's own skills + any the cloned repo ships.
    skill_sources = [
        bundle / "skills",
        ROOT / "repos" / a.name / ".agents" / "skills",
        ROOT / "repos" / a.name / ".claude" / "skills",
    ]
    removed: set[str] = set()
    for src_dir in skill_sources:
        if not src_dir.is_dir():
            continue
        for sk in src_dir.iterdir():
            dest = dest_root / sk.name
            if dest.is_symlink() and os.path.realpath(dest) == str(sk.resolve()):
                dest.unlink()
                removed.add(f".claude/skills/{sk.name}")
    drop_excludes(removed)

    reindex = ROOT / ".claude" / "hooks" / "reindex-concepts.py"
    if reindex.exists():  # via `uv run` — reindex needs PyYAML, which the bare interpreter lacks
        subprocess.run(["uv", "run", "--project", str(ROOT), "python", str(reindex), "--all"], check=False)

    md_removed = remove_md_snippet(f"{a.kind}/{a.name}")
    hooks_frag = bundle / "snippets" / "settings.hooks.json"
    hooks_removed = remove_hooks(json.loads(hooks_frag.read_text())) if hooks_frag.exists() else 0

    print(
        f"disabled {a.kind}/{a.name}: {len(removed)} skill symlink(s)"
        + (", AGENTS.local.md snippet removed" if md_removed else "")
        + (
            f", {hooks_removed} hook entr{'y' if hooks_removed == 1 else 'ies'} removed"
            if hooks_removed
            else ""
        )
    )
    if hooks_frag.exists():
        print("  NOTE: hook removal is best-effort — verify .claude/settings.local.json; clean up leftovers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
