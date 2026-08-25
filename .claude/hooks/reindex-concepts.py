#!/usr/bin/env python3
"""Regenerate the concept keyword index in CLAUDE.md.

Runs as a PostToolUse (Write|Edit) hook — regenerating only when a concept file changed — and at
SessionStart / on demand (`--all`). Rebuilds the block between the CONCEPT-INDEX:START / END
markers from each concept's `aka`, across global `concepts/` plus the `concepts/` of every bundle
listed in `scope.yaml` `enabled:`. Stdlib only, so it needs no venv and never touches the network.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
CLAUDE_MD = ROOT / "CLAUDE.md"
CLAUDE_LOCAL_MD = ROOT / "CLAUDE.local.md"
START = "<!-- CONCEPT-INDEX:START"
END = "<!-- CONCEPT-INDEX:END -->"
LOCAL_START = "<!-- CONCEPT-INDEX-LOCAL:START"
LOCAL_END = "<!-- CONCEPT-INDEX-LOCAL:END -->"
LOCAL_START_LINE = (
    "<!-- CONCEPT-INDEX-LOCAL:START (your per-dev concepts: local + enabled-bundle"
    " — generated; do not edit) -->"
)
LOCAL_HEADER = "# CLAUDE.local.md — your local, per-dev instructions & index (gitignored)."
KIND_DIRS = ("tools", "components", "extensions")


def should_run() -> bool:
    """Regen unless the hook fired for a non-concept file edit."""
    if "--all" in sys.argv:
        return True
    if sys.stdin.isatty():
        return True
    raw = sys.stdin.read()
    if not raw.strip():
        return True
    try:
        path = json.loads(raw).get("tool_input", {}).get("file_path", "")
    except (ValueError, AttributeError, TypeError):
        return True
    return (not path) or ("concepts" in Path(path).parts)


def frontmatter(md: Path) -> dict[str, object]:
    """Parse YAML frontmatter enough for our needs: scalars and lists (inline or block)."""
    text = md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict[str, object] = {}
    cur_key: str | None = None
    for line in text[3:end].splitlines():
        item = re.match(r"\s+-\s+(.*)", line)
        current = fm.get(cur_key) if cur_key is not None else None
        if item and isinstance(current, list):
            current.append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"([A-Za-z0-9_-]+):\s*(.*)", line)
        if kv and not line[:1].isspace():
            cur_key, val = kv.group(1), kv.group(2).strip()
            fm[cur_key] = val if val else []  # empty value ⇒ expect a block list
        else:
            cur_key = None
    return fm


def as_list(raw: object) -> list[str]:
    if isinstance(raw, list):
        return [str(x) for x in raw]
    raw = str(raw).strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [item.strip().strip("'\"") for item in raw.split(",") if item.strip()]


def enabled_concept_dirs() -> list[Path]:
    scope = ROOT / "scope.yaml"
    if not scope.exists():
        return []
    dirs: list[Path] = []
    in_enabled = False
    for line in scope.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^enabled:\s*$", line):
            in_enabled = True
            continue
        if in_enabled:
            if line[:1] not in ("", " ", "\t"):  # dedent → block ended
                break
            m = re.match(r"\s*([\w-]+):\s*\[(.*)\]", line)
            if m and m.group(1) in KIND_DIRS:
                for name in as_list(m.group(2)):
                    dirs.append(ROOT / m.group(1) / name / "concepts")
    return dirs


def collect() -> list[tuple[str, str, list[str], bool]]:
    """(display-name, repo-relative-path, aka, main_index). main_index=True → the TRACKED CLAUDE.md
    index, which holds ONLY global canonical concepts (global `concepts/*.md`, non-underscore).
    Everything per-dev — global underscore-local concepts AND all enabled-bundle concepts (which
    depend on what this dev enabled) — is main_index=False → the gitignored CLAUDE.local.md, so
    the tracked CLAUDE.md never varies per-dev."""

    def row(f: Path, main: bool):
        fm = frontmatter(f)
        return (
            fm.get("name") or f.stem.lstrip("_"),
            str(f.relative_to(ROOT)),
            as_list(fm.get("aka", "")),
            main,
        )

    rows = [row(f, not f.name.startswith("_")) for f in sorted((ROOT / "concepts").glob("*.md"))]
    for d in enabled_concept_dirs():
        rows += [row(f, False) for f in sorted(d.glob("*.md"))]  # bundle concepts are per-dev
    return sorted(rows, key=lambda r: r[0].lower())


def render(rows) -> str:
    if not rows:
        return "_(none yet)_"
    return "\n".join(f"- **{name}** — {', '.join(aka) or '—'} → `{rel}`" for name, rel, aka, _ in rows)


def set_block(path: Path, start: str, end: str, start_line: str | None, body: str, header: str) -> bool:
    """Replace the start..end marker block in `path` with `body`; append/create if the block is
    absent. `start_line` (if given) is the full START line to use when creating. Returns True if
    the file must exist (CLAUDE.md) and the block wasn't found."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    s, e = text.find(start), text.find(end)
    if s != -1 and e != -1 and e >= s:
        eol = text.find("\n", s)
        new = text[: eol + 1] + "\n" + body + "\n\n" + text[e:]  # blank line before END → mdformat-clean
    elif start_line is not None:  # create the block (append, or new file with header)
        block = f"{start_line}\n\n{body}\n\n{end}\n"
        new = (text.rstrip() + "\n\n" + block) if text.strip() else (f"{header}\n\n{block}")
    else:
        return True  # required existing block missing
    if new != text:
        path.write_text(new, encoding="utf-8")
    return False


def main() -> int:
    if not should_run():
        return 0
    rows = collect()
    main_rows = [r for r in rows if r[3]]  # global canonical → tracked CLAUDE.md
    local_rows = [r for r in rows if not r[3]]  # per-dev (local + enabled-bundle) → CLAUDE.local.md

    if not CLAUDE_MD.exists():
        print("reindex-concepts: CLAUDE.md not found", file=sys.stderr)
    elif set_block(CLAUDE_MD, START, END, None, render(main_rows), ""):
        print("reindex-concepts: CONCEPT-INDEX markers not found in CLAUDE.md", file=sys.stderr)

    # Per-dev concepts → CLAUDE.local.md (gitignored, also always-loaded).
    # Only touch it when there are per-dev concepts, or when a stale block needs clearing.
    has_block = CLAUDE_LOCAL_MD.exists() and LOCAL_START in CLAUDE_LOCAL_MD.read_text(encoding="utf-8")
    if local_rows or has_block:
        set_block(CLAUDE_LOCAL_MD, LOCAL_START, LOCAL_END, LOCAL_START_LINE, render(local_rows), LOCAL_HEADER)

    print(f"reindex-concepts: {len(main_rows)} global + {len(local_rows)} per-dev concept(s) indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
