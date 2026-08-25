---
name: run-target
description: >-
  Run or debug a Translator component locally, and record how in its component bundle. Use when the
  dev wants to start / launch / run / debug a target, or bring it up locally. If the component's run
  procedure is missing or incomplete, scan the repo + interview the dev to author it into
  `definition.md` first (augmenting discover), then run it. Triggers on: "run <component>", "start
  <component> locally", "launch/debug <component>", "bring up <component>", "run the app".
---

# Run target

Run a characterized component locally. If its run procedure isn't recorded yet, author it (scan +
interview) — figuring out *how to run* a component is this skill's job, not discover's. **If you
have a sufficient procedure (pre-existing or freshly authored), run it.**

## Prerequisites

- **Characterized** — `components/<name>/` exists. If not, run `/discover <name>` first.
- **Cloned** — the repo is in `repos/<name>/`. If cloning was deferred, clone it with the **`gh`
  CLI** (handles private repos): `gh repo clone <org>/<repo> repos/<name>` (`org`/`repo` from
  `definition.md`).
- **De-facto enabled** — running a component means it's in use, so **enable it** if it isn't already
  (`enable-bundle.py components <name>`, recording it in `scope.enabled` first), even if it's only a
  peripheral component, not a nominal purview/target.

## 1. Ensure a run procedure exists

- **Fast path** — if `definition.md`'s "Running it locally" is complete, use it as-is.

- **Otherwise author it.** Delegate a **low/medium-effort background subagent** (read-only) to scan
  the cloned repo for run knowledge, in priority order:

  1. **task runner / scripts** — taskipy `[tool.taskipy.tasks]`, `package.json` scripts, Makefile,
     justfile, Taskfile (usually the canonical run/test commands);
  2. **containers** — Dockerfile, docker-compose, devcontainer (services + ports);
  3. **docs** — README, `docs/INSTALLATION*`, CONTRIBUTING;
  4. **agent-facing** — AGENTS.md, `.claude/skills` / `.agents/skills` (some repos ship a run
     playbook — opportunistic, not guaranteed);
  5. **config/env** — `.env.example`/`.env.sample`, config defaults, CI workflows.

  Then **interview the dev** for what the docs don't cover — machine prerequisites, **external
  service dependencies** (often live in config/tribal knowledge, not the repo files), and **which
  secrets the dev holds**. Fill the `###` subsections the component template pre-seeds under
  `## Running it locally` (see "Authoring the procedure" below). A freshly authored procedure is
  human-guided → set `curation: curated`.

## 2. Run it — when the dev wants a launch (not just the procedure authored)

- **Check it's not already up first** — run the Verify step; if it's already running (port in use /
  health OK), say so and **don't relaunch**.
- Execute the **primary run command**. Start **long-running processes (servers) in the background
  via the Bash tool's `run_in_background: true`** — never a bare `&` (dies with the call) or a
  foreground server (hangs the turn). Then **verify it's up** (health endpoint / port) and report.
- **Destructive tasks** — confirm before running anything that wipes/resets state; **warn when the
  normal run is transitively destructive** (e.g. a `dev` task that force-recreates its DB containers
  on every start).
- **External-dependency reachability** — a component may depend on external services. On a run
  failure (or empty/partial results where a dependency should have contributed), **check that
  dependency's reachability first** and surface an unreachable dependency as the **likely cause**,
  not a component bug. Canonical check:
  `curl -sS -o /dev/null -w "%{http_code}\n" -m 6 <dep-url>` (`000`/timeout ⇒ unreachable). Record
  each dep's check in the procedure so it's repeatable.
- **Fold discoveries back.** If the run surfaces something the procedure got wrong or omitted (a
  missing prereq, a wrong port, a destructive surprise), treat it as a **signal to consult the dev**
  for corrective information, then update the `definition.md` body (a `curated`/`canonical` bundle
  edit).

## Authoring the procedure (definition.md body)

Fill the `###` subsections the component template pre-seeds under `## Running it locally` — keep
them as `###`, delete one that genuinely doesn't apply: **Prerequisites · Setup · Run · Verify ·
Common tasks · External deps** (each dep + its reachability check, per §2) **· Config & secrets**
(descriptions + placeholder skeletons only — real values stay in the dev's local env/`.env`,
`BUNDLES.md`).

## Notes

- **Delegation & effort:** the run-knowledge scan runs on a lighter model at low/medium effort,
  never inheriting the main agent's effort unless the nuance demands it. Executing/verifying the run
  is the main agent's job (it needs to see and iterate on output).
- **Secrets never enter the bundle** — placeholders + descriptions only; the dev supplies real
  values locally.
