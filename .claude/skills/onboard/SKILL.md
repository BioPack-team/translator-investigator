---
name: onboard
description: >-
  Set up (or amend) the dev's scope — the config every other skill reads: identity, purview,
  targets, remotes, preferences, and enabled bundles. Writes scope.yaml + issue-sources.yaml, seeds
  memory, scaffolds investigation dirs, wires git remotes, and clones + enables targets/tools.
  Re-runnable. Use on first run after cloning the framework, or to change setup. Triggers on:
  "onboard", "set up my scope", "change my purview / targets / preferences", or a first run with no
  scope.yaml.
---

# Onboard

Set up or amend the dev's **scope** — the per-dev config every other skill reads. Interactive and
**re-runnable**.

## First run (no `scope.yaml`) — interview → scaffold

00. **Precondition & tooling** — verify `gh` auth (`gh api user`; not authed → ask the dev to run
    `! gh auth login`). Set up dev tooling **once**: `uv sync` (installs the format/lint/type
    tools), then `uv run task hook` (arms the pre-commit checks that run on every `git commit` —
    skips gracefully if this isn't a git repo yet). **Never ask about pronouns** (they/them is a
    framework invariant).
    - **Activation layer (per-agent) — see `AGENTS.md` → "Activation layer".** The skill library
      (`.claude/skills/`) and the two concept-reindex hooks (`.claude/settings.json`) are wired for
      Claude Code. **If the running agent is not Claude Code, attempt to port those hooks now** to
      its native hook system (session-start + after-edit → `reindex-concepts.py`), or set up the
      manual reindex fallback, and point it at the `.claude/skills/` library. Record what you wired
      (or that you're on the manual fallback) in per-dev memory. **Claude Code: already wired —
      nothing to port.**
01. **Identity** — auto-detect the handle from `gh api user`, confirm it; ask `name` (worknotes
    attribution); `email` optional.
02. **Repos you'll work on (targets)** — the components/repos the dev will investigate, run, or
    contribute to. Contributor or maintainer — **no ownership required**, just the repos they'll
    actually touch. Offer a pick-list from the registry (`components/*/definition.md`); a repo that
    isn't there → `/discover` it inline. This is the primary scope question; it may be empty for a
    triage-only dev (PI/PM) who works across repos from **issue sources** (step 09) instead.
03. **Purview (optional)** — of the targets (or beyond), the components the dev **maintains / is the
    point-person for**. A scope marker, **not ownership**: purview = the resolution + handoff
    boundary (where the dev drives fixes vs. hands off to the owning team). **Optional — empty is
    completely fine** (pure contributors and triage-only devs have none), and it does **not** gate
    targets. Pick from the targets or the registry.
04. **Remotes** — contribution topology. Record `scope.remotes.mode` (default `auto` —
    `resolve-remotes.py` derives fork-vs-branch from the dev's push access at contribution time;
    override to force). Upstream (the framework repo) + the dev's fork are **derived**, not wired
    here. For fork mode, ensure the dev has a fork (offer `gh repo fork --clone=false`).
05. **Preferences** — show the defaults (`checkpointed` / `standard` / `ask`) and the level menus
    (AGENTS.md); let the dev adjust `autonomy` / `terseness` / `contribution`.
06. **Tools & extensions menu** — list the available bundles (`tools/*/`, `extensions/*/`, each with
    its `provides` / `does`). **Pre-select the ones marked `default_enabled: true`** — find them with
    `grep -rl 'default_enabled: true' tools components extensions --include=definition.md 2>/dev/null`
    (the `2>/dev/null` tolerates a kind-dir that doesn't exist yet; currently matches `translator-tom`). **Ask which to enable — the dev can opt out of a default or add others;
    selection only, the actual enabling happens in step 10.** (A kind with no bundles yet — e.g.
    `extensions/` in a fresh clone — just yields nothing; that's expected, not an error.)
07. **Create `scope.yaml`** — `python3 .claude/scripts/new-artifact.py scope` (copies
    `templates/scope.yaml`), then fill identity / purview / targets / remotes / preferences and the
    **`enabled:` list from the step-6 selection** (this is the record the re-index reads).
08. **Seed memory** — record the dev's identity + their targets/purview (or, for a triage-only dev, their role
    and the repos they watch) in **per-dev memory** so they persist across sessions: the agent's
    native store (Claude Code: memory notes + a `MEMORY.md` pointer) or the gitignored root
    `MEMORY.md` fallback (see `AGENTS.md`). Per-dev, never committed — not a shared in-repo file.
09. **Issue sources** — the repos the dev triages, **independent of purview**. `python3 .claude/scripts/new-artifact.py issue-sources` (copies `templates/issue-sources.yaml`), then add
    an alias per repo of interest and set `default` to whichever they reach for most. **A
    triage-only dev registers repos here without any purview** — `default` can be any repo (e.g. a
    shared tracker like `feedback`), not necessarily one of their targets or purview. For PIs/PMs this is the
    primary setup step, so gather the repos they want to watch here even if steps 02–03 were empty.
10. **Scaffold + clone + enable:**
    - `mkdir` `investigations/<repo>/` for purview + targets + the issue-source repos (by their
      `dir:` segment), and `investigations/topics/`. A triage-only dev still gets dirs for the repos
      they registered in step 09.
    - **Clone targets** into `repos/` (offer now, allow defer).
    - For each bundle in **`scope.enabled`** (already recorded in step 7), run
      `python3 .claude/scripts/enable-bundle.py <kind> <name>` (symlinks skills, folds concepts,
      re-indexes, **auto-merges the `AGENTS.local.md` snippet**). If it reports a **hook** is
      available, ask the dev — on yes, re-run with `--hooks`.
    - **Ensure the per-dev local adapter** so the agent loads `AGENTS.local.md`. Claude Code: a
      `CLAUDE.local.md` containing `@AGENTS.local.md` (create it if absent). Other agents: per their
      own memory-file convention.
11. **Hand off** — "give me an issue number or a topic."

## Re-run (`scope.yaml` exists) — amend

Detect `scope.yaml` and offer an amend menu:

- change **identity**;
- **modify or wholesale-replace purview** (including clearing it — pure contributors and
  triage-only devs may have none);
- **add / remove issue-source repos** — edit `issue-sources.yaml` (the usual amend for a
  triage-only dev, who may never touch purview or targets);
- **add / remove targets** (clone + enable, or `disable-bundle.py` accordingly);
- adjust **preferences**;
- re-wire **remotes**;
- **re-materialize enabled bundles** — re-run `enable-bundle.py <kind> <name>` for everything in
  `scope.enabled` to rebuild missing `.claude/skills/` symlinks + `.git/info/exclude` entries +
  re-index. Use this to restore a dev's setup on a fresh clone or after the symlinks were dropped.

Apply the requested change and keep `scope.yaml` and the derived state (symlinks, dirs, remotes,
index) consistent.

## Notes

- **Enable/disable mechanics** live in `.claude/scripts/enable-bundle.py` /
  `disable-bundle.py` + AGENTS.md "Enabling & disabling bundles". Always **update `scope.enabled`
  before** calling the helper, so the concept re-index reflects the change.
- Never set `canonical` curation (that's `/contribute`); never ask about pronouns.
- Clone + enable are **offer-now-allow-defer**.
