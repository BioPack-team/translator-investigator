---
name: <extension-name>
curation: inferred     # inferred | curated | canonical  (lifecycle — see BUNDLES.md)
does: <one line — the standing behavior this adds, e.g. "log every analysis script for later upstreaming">
# default_enabled: true # optional — onboard pre-selects this bundle to enable by default
---

# <name>

## What it does

<The standing behavior and why a dev might want it. It is opt-in and off by default.>

## Opt in

<Enabling offers the snippets in `./snippets/` for the dev to accept into their `CLAUDE.local.md`
(standing instruction) and/or `.claude/settings.local.json` (a hook that makes it automatic).
Describe what each snippet does. If it ships a skill (`./skills/`), note it.>

## Notes

<Caveats, what it produces (e.g. an artifact file), and anything a future agent should know.
Remember: no secrets in snippets — descriptions + placeholder skeletons only (BUNDLES.md).>
