#!/usr/bin/env python3
"""Regenerate the concept keyword index in AGENTS.md (the agent-agnostic core).

Runs as a PostToolUse (Write|Edit) hook — regenerating only when a concept file changed — and at
SessionStart / on demand (`--all`). Rebuilds the block between the CONCEPT-INDEX:START / END
markers from each concept's `aka`, across global `concepts/` plus the `concepts/` of every bundle
listed in `scope.yaml` `enabled:`. Parses YAML with PyYAML, so run it via `uv run` (which supplies
the dep and auto-syncs the env on first use); invoked on a plain interpreter without it, the
top-level guard degrades to a no-op exit 0. `CLAUDE_PROJECT_DIR` is honored when set, else the repo
root is derived from this file's path.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # bare interpreter — the documented invocation is `uv run`, which supplies it
    print("reindex-concepts: skipped (PyYAML unavailable — run via `uv run`)", file=sys.stderr)
    raise SystemExit(0) from None

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
AGENTS_MD = ROOT / "AGENTS.md"
AGENTS_LOCAL_MD = ROOT / "AGENTS.local.md"
START = "<!-- CONCEPT-INDEX:START"
END = "<!-- CONCEPT-INDEX:END -->"
LOCAL_START = "<!-- CONCEPT-INDEX-LOCAL:START"
LOCAL_END = "<!-- CONCEPT-INDEX-LOCAL:END -->"
LOCAL_START_LINE = (
    "<!-- CONCEPT-INDEX-LOCAL:START (your per-dev concepts: local + enabled-bundle"
    " — generated; do not edit) -->"
)
LOCAL_HEADER = "# AGENTS.local.md — your local, per-dev instructions & index (gitignored)."
KIND_DIRS = ("tools", "components", "extensions")


def should_run() -> bool:
    """Regen unless the hook fired for a non-concept file edit (edited path read from Claude's
    `tool_input.file_path` or a root-level `file_path`; any other payload → regen)."""
    if "--all" in sys.argv:
        return True
    if sys.stdin.isatty():
        return True
    raw = sys.stdin.read()
    if not raw.strip():
        return True
    try:
        data = json.loads(raw)
        path = data.get("tool_input", {}).get("file_path") or data.get("file_path") or ""
    except (ValueError, AttributeError, TypeError):
        return True
    return (not path) or ("concepts" in Path(path).parts)


def frontmatter(md: Path) -> dict[str, object]:
    """Parse a markdown file's YAML frontmatter (the block between the leading `---` fences)."""
    text = md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:  # one malformed file shouldn't sink the whole index
        return {}
    return data if isinstance(data, dict) else {}


def as_list(raw: object) -> list[str]:
    """Normalize a YAML value (list, scalar, or empty) to a list of strings."""
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return [str(raw)]


def enabled_concept_dirs() -> list[Path]:
    scope = ROOT / "scope.yaml"
    if not scope.exists():
        return []
    try:
        data = yaml.safe_load(scope.read_text(encoding="utf-8", errors="replace")) or {}
    except yaml.YAMLError:  # a broken scope.yaml still lets the global index regenerate
        return []
    enabled = data.get("enabled") or {}
    return [ROOT / kind / name / "concepts" for kind in KIND_DIRS for name in as_list(enabled.get(kind))]


def collect() -> list[tuple[str, str, list[str], bool]]:
    """(display-name, repo-relative-path, aka, main_index). main_index=True → the TRACKED AGENTS.md
    index, which holds ONLY global canonical concepts (global `concepts/*.md`, non-underscore).
    Everything per-dev — global underscore-local concepts AND all enabled-bundle concepts (which
    depend on what this dev enabled) — is main_index=False → the gitignored AGENTS.local.md, so
    the tracked AGENTS.md never varies per-dev."""

    def row(f: Path, main: bool):
        fm = frontmatter(f)
        return (
            fm.get("name") or f.stem.lstrip("_"),
            str(f.relative_to(ROOT)),
            as_list(fm.get("aka")),
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
    the file must exist (AGENTS.md) and the block wasn't found."""
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
    main_rows = [r for r in rows if r[3]]  # global canonical → tracked AGENTS.md
    local_rows = [r for r in rows if not r[3]]  # per-dev (local + enabled-bundle) → AGENTS.local.md

    if not AGENTS_MD.exists():
        print("reindex-concepts: AGENTS.md not found", file=sys.stderr)
    elif set_block(AGENTS_MD, START, END, None, render(main_rows), ""):
        print("reindex-concepts: CONCEPT-INDEX markers not found in AGENTS.md", file=sys.stderr)

    # Per-dev concepts → AGENTS.local.md (gitignored, also always-loaded via the local adapter).
    # Only touch it when there are per-dev concepts, or when a stale block needs clearing.
    has_block = AGENTS_LOCAL_MD.exists() and LOCAL_START in AGENTS_LOCAL_MD.read_text(encoding="utf-8")
    if local_rows or has_block:
        set_block(AGENTS_LOCAL_MD, LOCAL_START, LOCAL_END, LOCAL_START_LINE, render(local_rows), LOCAL_HEADER)

    print(f"reindex-concepts: {len(main_rows)} global + {len(local_rows)} per-dev concept(s) indexed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # advisory hook — never block the host on an unexpected failure
        print(f"reindex-concepts: skipped ({exc})", file=sys.stderr)
        sys.exit(0)
