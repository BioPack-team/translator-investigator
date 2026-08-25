---
name: <repo-name>
org: <github-org>
repo: <repo>
kind: <platform|ara|kp|aggregator|backend|sri-utility|ars|ui|tooling|infra>
status: active         # active | deprecated | defunct  (liveness)
curation: inferred     # inferred | curated | canonical  (lifecycle — see BUNDLES.md)
infores: <infores:...> # if it has one; omit otherwise
trapi_version: <"1.6" | "2.0">   # TRAPI services only; omit otherwise. Notes may clarify if it varies by branch.
owner: <maintainer handle / team>
parts: []              # sub-operations as tags — the repo stays the unit
related: []            # cross-repo links (e.g. a backend it depends on)
# default_enabled: true # optional — onboard pre-selects this bundle to enable by default
---

# <name>

## What it is

<Its role in the Translator ecosystem (its `kind`) and what it does, in a line or two.>

## Running it locally

<`/run-target` fills the `###` subsections below. Keep them as `###` under this heading. Delete a
subsection that genuinely doesn't apply.>

### Prerequisites

<Runtimes, package manager, Docker, etc.>

### Setup

<Install / sync commands.>

### Run

<The primary run command (and the debug variant if there is one), plus the port it serves on.>

### Verify

<How to confirm it's up — e.g. a health endpoint / expected port.>

### Common tasks

<Test, lint/format, tracing, etc.>

### External deps

<Each external service + a reachability check; note which need special network access.>

### Config & secrets

<Config mechanism (env vars, files). For secrets, describe WHAT is needed and WHERE, never the
value — placeholder skeletons in code blocks; real values stay in the dev's local env/`.env`.
Secrets rule: BUNDLES.md.>

## Gotchas & notes

<Accumulated dev notes, quirks, and secondary info a future agent will find useful.>
