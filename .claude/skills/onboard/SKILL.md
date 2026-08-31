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
01. **Identity** — auto-detect the handle from `gh api user`, confirm it; ask `name` (worknotes
    attribution); `email` optional.
02. **Purview (optional)** — the components the dev **owns**, if any. Offer a pick-list from the
    registry (`components/*/definition.md`); a component that isn't there → `/discover` it inline.
    Purview = resolution scope + the handoff boundary. **Leave it empty for triage-only roles** (PIs,
    PMs, and others who investigate across repos without owning a component) — they work from **issue
    sources** (step 09) instead. Don't push for a component when the dev doesn't oversee one; offer to
    skip straight to issue sources.
03. **Targets** — the repos the dev will investigate/run locally. Default = purview + any extras (may
    be none for a triage-only dev); from the registry or `/discover`.
04. **Remotes** — contribution topology. Record `scope.remotes.mode` (default `auto` —
    `resolve-remotes.py` derives fork-vs-branch from the dev's push access at contribution time;
    override to force). Upstream (the framework repo) + the dev's fork are **derived**, not wired
    here. For fork mode, ensure the dev has a fork (offer `gh repo fork --clone=false`).
05. **Preferences** — show the defaults (`checkpointed` / `standard` / `ask`) and the level menus
    (CLAUDE.md); let the dev adjust `autonomy` / `terseness` / `contribution`.
06. **Tools & extensions menu** — list the available bundles (`tools/*/`, `extensions/*/`, each with
    its `provides` / `does`). **Pre-select the ones marked `default_enabled: true`** — find them with
    `grep -rl 'default_enabled: true' tools components extensions --include=definition.md 2>/dev/null`
    (the `2>/dev/null` tolerates a kind-dir that doesn't exist yet; currently matches `translator-tom`). **Ask which to enable — the dev can opt out of a default or add others;
    selection only, the actual enabling happens in step 10.** (A kind with no bundles yet — e.g.
    `extensions/` in a fresh clone — just yields nothing; that's expected, not an error.)
07. **Create `scope.yaml`** — `python3 .claude/scripts/new-artifact.py scope` (copies
    `templates/scope.yaml`), then fill identity / purview / targets / remotes / preferences and the
    **`enabled:` list from the step-6 selection** (this is the record the re-index reads).
08. **Seed memory** — record the dev's identity + purview (or, for a triage-only dev, their role
    and the repos they watch) in the **harness memory** (write memory notes + a `MEMORY.md` pointer,
    per the memory system) so they persist across sessions. Not an in-repo file — the harness memory
    is the per-dev store.
09. **Issue sources** — the repos the dev triages, **independent of purview**. `python3 .claude/scripts/new-artifact.py issue-sources` (copies `templates/issue-sources.yaml`), then add
    an alias per repo of interest and set `default` to whichever they reach for most. **A
    triage-only dev registers repos here without any purview** — `default` can be any repo (e.g. a
    shared tracker like `feedback`), not necessarily a component they own. For PIs/PMs this is the
    primary setup step, so gather the repos they want to watch here even if steps 02–03 were empty.
10. **Scaffold + clone + enable:**
    - `mkdir` `investigations/<repo>/` for purview + targets + the issue-source repos (by their
      `dir:` segment), and `investigations/topics/`. A triage-only dev still gets dirs for the repos
      they registered in step 09.
    - **Clone targets** into `repos/` (offer now, allow defer).
    - For each bundle in **`scope.enabled`** (already recorded in step 7), run
      `python3 .claude/scripts/enable-bundle.py <kind> <name>` (symlinks skills, folds concepts,
      re-indexes, **auto-merges the CLAUDE.local.md snippet**). If it reports a **hook** is
      available, ask the dev — on yes, re-run with `--hooks`.
11. **Hand off** — "give me an issue number or a topic."

## Re-run (`scope.yaml` exists) — amend

Detect `scope.yaml` and offer an amend menu:

- change **identity**;
- **modify or wholesale-replace purview** (including clearing it — a former owner or a
  triage-only dev may have none);
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
  `disable-bundle.py` + CLAUDE.md "Enabling & disabling bundles". Always **update `scope.enabled`
  before** calling the helper, so the concept re-index reflects the change.
- Never set `canonical` curation (that's `/contribute`); never ask about pronouns.
- Clone + enable are **offer-now-allow-defer**.
