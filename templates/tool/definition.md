---
name: <tool-name>
org: <github-org>
repo: <repo>
status: active         # active | deprecated | defunct  (liveness)
curation: inferred     # inferred | curated | canonical  (lifecycle — see BUNDLES.md)
provides: <one line — the capability this tool gives, e.g. "fire TRAPI queries and assert on responses">
# default_enabled: true   # optional — onboard pre-selects this bundle to enable by default
---

# <name>

## What it provides

<The capability, and when to reach for it (this drives `tool_choice`). If it overlaps another
tool, note how they differ.>

## Install & run

<How to obtain and invoke it — prefer a pinned `uv run …` invocation. Note any flags/gotchas an
agent needs to run it cleanly (e.g. non-interactive flags in a non-TTY shell).>

## Using it

<Usage patterns for investigation work. If this tool ships a skill (in `./skills/`, symlinked into
`.claude/skills/` on enable), point to it as the detailed playbook. Secrets: descriptions +
placeholder skeletons only — see BUNDLES.md.>
