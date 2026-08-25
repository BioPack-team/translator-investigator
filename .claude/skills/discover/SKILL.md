---
name: discover
description: >-
  Characterize a single Translator/TRAPI repo into a bundle — a component (a target you
  investigate) or a tool (an instrument you use) — so the agent knows its
  role, provenance, and how to work with it. Use when the dev says to look at / pull in / add a repo
  (to investigate it, for peripheral context, or to use it as a tool), or when an uncharacterized
  component shows up in an investigation. One repo at a time — dev-guided, never a sweep. Triggers
  on: "look at <repo>", "pull in <repo>", "what is <repo>", "add <repo> as a target", "use <repo> as
  a tool", an unknown component in an investigation's components[].
---

# Discover (characterize a repo into a bundle)

Turn one repo into a bundle — a **component** (a target you investigate) or a **tool** (an
instrument you use — a CLI/library that drives or inspects other services). **Characterization
always happens; cloning and enabling are optional.** This skill does **not** work out how to fully run a component —
that's `/run-target`; discover records run-*hints* only if they fall out of the scan.

## 1. Resolve the reference

- `org/repo`, a URL, or a local path → use directly.
- A bare name → search the known orgs (read-only), e.g.
  `gh search repos <name> --owner NCATSTranslator --owner TranslatorSRI --owner BioPack-team --owner ranking-agent --owner biothings`. Confirm the match with the dev if ambiguous. If the name
  **isn't found** in these orgs, ask the dev for the `org/repo` (or a URL) — the five orgs are a
  starting set, not exhaustive. **Never sweep an org to enumerate.**

## 2. Determine the bundle kind

- **component** — a repo you investigate, or a TRAPI service/backend in the ecosystem.
- **tool** — a repo you use as an *instrument* of investigation (a CLI/library that drives or
  inspects other services).
- Read the dev's **intent** from the request: "use X to… / X is my tool for…" ⇒ tool; "look at /
  debug / investigate X" ⇒ component. **Ask if unclear.** This picks the template + output dir.

## 3. Check for an existing bundle

If `components/<name>/` **or** `tools/<name>/` already exists, **update it** — don't recreate.

## 4. Characterize — delegate the scan

Run the scan on a **read-only background subagent at low/medium effort** (lighter model; not the
main agent's effort unless nuance demands). Shared sources:

- **Repo metadata** — `gh repo view <org>/<repo> --json name,description,isArchived,pushedAt,primaryLanguage,url`
  → `status` (a **soft signal**, not a hard fact: **archived ⇒ `defunct`**; else `active` unless the
  dev says a component is deprecated) + a one-line summary.
- **File content — shallow clone to a scratch dir** (`git clone --depth 1` into scratch, *not*
  `repos/` unless adopting); read with native tools: README, package manifest, task runner, docs,
  CODEOWNERS. (Preferred over piecemeal `gh api .../contents`.)

Then, by kind:

- **component** — also query the **SmartAPI registry** (query API, not a download):
  `https://smart-api.info/api/query?q=<name>&fields=info.title,info.x-translator,info.x-trapi,servers.url`.
  **Authoritative** for `infores` (`x-translator.infores`), `kind` baseline
  (`x-translator.component`: KP→`kp`, ARA→`ara`, Utility→`sri-utility`/`tooling`), and TRAPI facts
  (`x-trapi`: operations/version/asyncquery/…). No hit ⇒ probably not a TRAPI service.
- **tool** — usually **no SmartAPI hit** (it's not a service). Focus the scan on the **capability**
  it provides, how to install/invoke it, and usage patterns. **If it ships its own agent interface**
  — a skill under `.agents/skills` / `.claude/skills`, or an `AGENTS.md` — **keep the bundle
  definition light and defer to those**: don't duplicate the repo's usage docs (they drift, esp. for
  fast-moving tools). Enabling **adopts** the repo's skill (symlinked from the clone, tracks
  upstream); point the definition + snippet at the repo's skill/AGENTS.md as the source of truth
  (e.g. ttt → `/trapi-testing`).

**The subagent returns a structured summary** (so step 5 fills deterministically), covering:
`status` + one-line "what it is"; `kind` baseline + `infores` + TRAPI facts (services); `owner`
(CODEOWNERS → git-log hint → none); `parts` (sub-ops/tiers) + `related` (cross-repo deps from
README/manifest); **run-hints** (task-runner commands, ports, docker services — best-effort, for
`/run-target`); and gotchas/notes.

## 5. Draft the bundle definition (`curation: inferred`)

**Instantiate the skeleton first** — `python3 .claude/scripts/new-artifact.py <component|tool> <name>` — then **fill that file in** (never compose it from scratch or from a sibling bundle):

- **component** (`components/<name>/definition.md`): `kind` (registry baseline, refine with a body
  note, flag clear divergence — e.g. retriever registers **KP** but is an aggregating KP), `owner`
  (CODEOWNERS → git-log hint → dev/blank, never fabricated), `infores`/`status`, **`trapi_version`**
  (from SmartAPI `x-trapi.version` — e.g. `"1.6"`; most components are still 1.6, not 2.0), `parts`
  (sub-ops as tags), `related` (cross-repo links). Body: "What it is"; **"Running it locally" =
  best-effort run-hints only** (→ `/run-target`).
- **tool** (`tools/<name>/definition.md`): `provides` (the capability, drives `tool_choice`),
  `status`, `owner`. Body: what it provides + install/invoke + usage; point at its shipped skill if
  it has one. Secrets: descriptions + placeholders only (`BUNDLES.md`).

## 6. Tools: offer to author snippets (from the interview)

For a **tool**, interview the dev on **how and when they'll use it**, then **offer to author its
`snippets/`** capturing that intent: scaffold with `python3 .claude/scripts/new-artifact.py snippet --bundle tools/<name>` (creates `snippets/CLAUDE.local.md` + `settings.hooks.json`), then fill in
the ones that apply (delete an unused one):

- a **`CLAUDE.local.md`** standing-instruction snippet — when to reach for the tool and the dev's
  workflow/preferences for it (this is **auto-merged** on enable);
- optionally a **`settings.hooks.json`** hook (this is **offered**, merged only with `--hooks`).

If the tool ships its own skill, enabling also symlinks that in (so `/its-skill` becomes available).
(Components may carry snippets too, but this is primarily a tool concern.)

## 7. Offer clone + enable (offer-now-defer)

- **Adopt/use it** → record in `scope.yaml` `enabled:`, then `enable-bundle.py` (symlinks skills,
  re-indexes concepts, **auto-merges the CLAUDE.local.md snippet**, offers any hook) — see CLAUDE.md
  "Enabling & disabling bundles". Clone into `repos/`.
- **Peripheral only** → stop at the `inferred` definition; no clone into `repos/`, no enable. (Drop
  the scratch clone.)

## Notes

- Curation: pure characterization is **`inferred`**; if the dev reviews/adds notes, bump to
  **`curated`**. `canonical` only via `/contribute`.
- **Delegation & effort:** the scan runs on a lighter model at low/medium effort, never inheriting
  the main agent's effort unless the nuance demands it.
- No secrets in the bundle (it's shared/contributable) — see `BUNDLES.md`.
