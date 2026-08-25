#!/usr/bin/env python3
"""Enable a bundle: symlink its skills into .claude/skills/, ignore those symlinks via
.git/info/exclude, re-index concepts, and merge its snippets. Stdlib only; idempotent.

Usage: enable-bundle.py <kind> <name> [--hooks]     # kind = components | tools | extensions

- CLAUDE.local.md snippet → **auto-merged** (enabling is the dev's opt-in), wrapped in per-bundle
  markers so disable can remove it.
- settings.local.json hooks → **offered by default**; merged only with `--hooks` (content-based).

Does NOT edit scope.yaml (the agent records `enabled:` first). The agent records enabling; this
does the deterministic filesystem/merge work.
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
CLAUDE_LOCAL = ROOT / "CLAUDE.local.md"
SETTINGS_LOCAL = ROOT / ".claude" / "settings.local.json"
LOCAL_HEADER = "# CLAUDE.local.md — your local, per-dev instructions & index (gitignored)."


def add_excludes(lines: list[str]) -> None:
    exclude = ROOT / ".git" / "info" / "exclude"
    if not exclude.parent.exists():
        return
    existing = exclude.read_text().splitlines() if exclude.exists() else []
    new = [ln for ln in lines if ln not in existing]
    if new:
        with exclude.open("a") as f:
            if existing and existing[-1].strip():
                f.write("\n")
            f.write("\n".join(new) + "\n")


def merge_md_snippet(tag: str, content: str) -> None:
    start, end = f"<!-- BUNDLE-SNIPPET:{tag}:START -->", f"<!-- BUNDLE-SNIPPET:{tag}:END -->"
    block = f"{start}\n\n{content.strip()}\n{end}"
    text = CLAUDE_LOCAL.read_text(encoding="utf-8") if CLAUDE_LOCAL.exists() else ""
    s, e = text.find(start), text.find(end)
    if s != -1 and e != -1 and e >= s:
        new = text[:s] + block + text[e + len(end) :]
    elif text.strip():
        new = text.rstrip() + "\n\n" + block + "\n"
    else:
        new = f"{LOCAL_HEADER}\n\n{block}\n"
    if new != text:
        CLAUDE_LOCAL.write_text(new, encoding="utf-8")


def merge_hooks(frag: dict) -> int:
    settings = json.loads(SETTINGS_LOCAL.read_text()) if SETTINGS_LOCAL.exists() else {}
    hooks = settings.setdefault("hooks", {})
    added = 0
    for event, entries in frag.get("hooks", {}).items():
        arr = hooks.setdefault(event, [])
        for entry in entries:
            if entry not in arr:  # deep-equality via ==
                arr.append(entry)
                added += 1
    SETTINGS_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_LOCAL.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return added


def main() -> int:
    p = argparse.ArgumentParser(prog="enable-bundle.py")
    p.add_argument("kind", choices=KINDS)
    p.add_argument("name")
    p.add_argument(
        "--hooks", action="store_true", help="also merge the bundle's settings hooks (offered by default)"
    )
    a = p.parse_args()

    bundle = ROOT / a.kind / a.name
    if not (bundle / "definition.md").exists():
        print(f"enable-bundle: no bundle at {a.kind}/{a.name}", file=sys.stderr)
        return 1

    # 1. symlink skills + gitignore them locally. Sources: skills the bundle itself ships, PLUS any
    #    the cloned repo ships (adopt-from-repo — auto-tracks upstream on `git pull` of the clone).
    dest_root = ROOT / ".claude" / "skills"
    dest_root.mkdir(parents=True, exist_ok=True)
    skill_sources = [
        bundle / "skills",
        ROOT / "repos" / a.name / ".agents" / "skills",
        ROOT / "repos" / a.name / ".claude" / "skills",
    ]
    linked: list[str] = []
    for src_dir in skill_sources:
        if not src_dir.is_dir():
            continue
        for sk in sorted(p for p in src_dir.iterdir() if (p / "SKILL.md").exists()):
            dest = dest_root / sk.name
            target = os.path.relpath(sk, dest_root)
            if dest.is_symlink():
                if os.readlink(dest) != target:
                    print(f"enable-bundle: {dest.name} is a different symlink — skipping", file=sys.stderr)
                    continue
            elif dest.exists():
                print(f"enable-bundle: {dest.name} exists and isn't our symlink — skipping", file=sys.stderr)
                continue
            else:
                dest.symlink_to(target)
            linked.append(f".claude/skills/{sk.name}")
    add_excludes(linked)

    # 2. re-index concepts (folds this bundle's concepts/ if scope.enabled lists it)
    reindex = ROOT / ".claude" / "hooks" / "reindex-concepts.py"
    if reindex.exists():
        subprocess.run([sys.executable, str(reindex), "--all"], check=False)

    # 3. CLAUDE.local.md snippet — auto-merge
    md = bundle / "snippets" / "CLAUDE.local.md"
    if md.exists():
        merge_md_snippet(f"{a.kind}/{a.name}", md.read_text(encoding="utf-8"))

    # 4. hooks — offered by default, merged only with --hooks
    hooks_frag = bundle / "snippets" / "settings.hooks.json"
    hooks_note = ""
    if hooks_frag.exists():
        if a.hooks:
            n = merge_hooks(json.loads(hooks_frag.read_text(encoding="utf-8")))
            hooks_note = f"; merged {n} hook entr{'y' if n == 1 else 'ies'} into settings.local.json"
        else:
            hooks_note = "; a HOOK is available — offer it to the dev, then re-run with --hooks to merge"

    print(
        f"enabled {a.kind}/{a.name}: {len(linked)} skill(s)"
        + (", CLAUDE.local.md snippet merged" if md.exists() else "")
        + hooks_note
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
