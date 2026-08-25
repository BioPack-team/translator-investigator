---
name: trapi-testing-tools
org: biothings
repo: trapi-testing-tools
status: active
curation: canonical
default_enabled: true   # core repro/regression instrument — onboard pre-selects it (dev can opt out)
provides: fire TRAPI queries at Translator services and assert/analyze the responses (the `tt` CLI)
---

# trapi-testing-tools (ttt / `tt`)

## What it provides

A CLI (`tt`) for rapidly exercising and analyzing TRAPI resources in the Translator ecosystem —
running query files, asserting on responses, analyzing them, pulling ARS responses by PK, and more.
The framework's main instrument for **reproducing and regression-testing** TRAPI-service bugs.

## Usage — deferred to the repo's own agent docs (deliberately light)

ttt is **fast-moving and ships its own agent interface**, so this bundle stays thin on purpose —
duplicating its usage here would just drift. The current, authoritative guidance lives in the clone:

- **`repos/trapi-testing-tools/AGENTS.md`** — architecture + gotchas.
- **The shipped skill `.agents/skills/trapi-testing/`** — the task playbook. Enabling this bundle
  (after cloning) **adopts it as `/trapi-testing`** (symlinked from the clone, so it tracks upstream
  on `git pull` — nothing here to keep current).

Reach for **`/trapi-testing`** and **AGENTS.md** — not this file — for how to run `tt`, author query
files / analyses / response tests, run non-interactively, etc.

## Setup

Cloned into `repos/trapi-testing-tools/` (Python 3.13, `uv`-managed). Run from the clone so imports
resolve — `uv run --directory repos/trapi-testing-tools tt …`, or activate its `.venv`. Details:
its README / AGENTS.md.
