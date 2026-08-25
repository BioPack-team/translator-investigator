#!/usr/bin/env python3
"""Informal secret check: scan files for things that *could* be secrets and print a PRIORITIZED
list for the dev to review. Stdlib only. This is advisory — it never edits or blocks; the dev
decides what (if anything) to redact/placeholder. Always exits 0.

Usage: secret-scan.py <path> [<path> ...]   # files or dirs (dirs walked; .git/.venv/etc. skipped)

Shared artifacts should carry secret *descriptions + placeholder skeletons* only, so real-looking
values where a placeholder belongs are what this flags. Values that look like placeholders
(<...>, ${VAR}, your-…, example, changeme) are downgraded to LOW.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "repos", "investigations"}
PLACEHOLDER = re.compile(
    r"<[^>]*>|\$\{?\w+\}?|your[-_]|example|changeme|placeholder|dummy|redacted|xxx+|\.\.\.|_here\b", re.I
)

# (name, severity, compiled pattern). Group 'v' (if present) is the candidate value to placeholder-check.
PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("private key block", "HIGH", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("AWS access key id", "HIGH", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", "HIGH", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", "HIGH", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("credentials in URL", "HIGH", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s:/@]+:(?P<v>[^\s@/]+)@")),
    ("Sentry DSN", "HIGH", re.compile(r"https://(?P<v>[0-9a-f]{16,})@[\w.-]*sentry\.io/\d+", re.I)),
    ("bearer token", "MEDIUM", re.compile(r"(?i)\bbearer\s+(?P<v>[A-Za-z0-9._\-]{20,})")),
    (
        "secret-like assignment",
        "MEDIUM",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|pwd|access[_-]?key|auth[_-]?token|client[_-]?secret|dsn|credential)\b\s*[:=]\s*['\"]?(?P<v>[^\s'\"#]{6,})"
        ),
    ),
    (
        "long high-entropy string",
        "LOW",
        re.compile(
            r"(?<![A-Za-z0-9+/=])(?P<v>(?=[A-Za-z0-9+/]*[0-9])(?=[A-Za-z0-9+/]*[A-Za-z])[A-Za-z0-9+/]{32,}={0,2})(?![A-Za-z0-9+/=])"
        ),
    ),
]
RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def redact(s: str) -> str:
    s = s.strip()
    return s if len(s) <= 8 else f"{s[:4]}…{s[-2:]} ({len(s)} chars)"


def iter_files(paths: list[str]):
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            for f in pp.rglob("*"):
                if f.is_file() and not (set(f.parts) & SKIP_DIRS):
                    yield f
        elif pp.is_file():
            yield pp


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: secret-scan.py <path> [<path> ...]", file=sys.stderr)
        return 0
    findings = []
    for f in iter_files(sys.argv[1:]):
        try:
            text = f.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue  # skip binary/unreadable
        for i, line in enumerate(text.splitlines(), 1):
            for name, sev, pat in PATTERNS:
                m = pat.search(line)
                if not m:
                    continue
                val = m.groupdict().get("v")
                s = "LOW" if (val and PLACEHOLDER.search(val)) else sev  # placeholder ⇒ downgrade
                snippet = redact(val) if val else name
                findings.append((RANK[s], s, str(f), i, name, snippet))

    findings.sort(key=lambda r: (r[0], r[2], r[3]))
    if not findings:
        print("secret-scan: 0 potential-risk items — nothing to review.")
        return 0
    print(f"secret-scan: {len(findings)} potential-risk item(s) — REVIEW (advisory; nothing removed):\n")
    for _, sev, path, ln, name, snippet in findings:
        print(f"  [{sev:6}] {path}:{ln}  {name} — {snippet}")
    print(
        "\nThese may be false positives. Descriptions + placeholder skeletons are fine; real values are not."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
