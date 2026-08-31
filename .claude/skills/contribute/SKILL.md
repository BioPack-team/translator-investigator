---
name: contribute
description: >-
  Share a local framework improvement upstream via a PR — a concept, a bundle (component / tool /
  extension), a skill, or a framework change. The one sanctioned remote action, and ONLY
  on the dev's explicit request. Runs hygiene + audit, stages the exact files, previews the commit
  and PR, then (per the dev's `contribution` preference) offers to open the PR or hands off so the
  dev drives it. Triggers on: "contribute X", "share X upstream", "PR this concept/component/skill",
  "upstream my changes to Y".
---

# Contribute

The one **sanctioned remote action** — and **only ever on the dev's explicit request** (boundary: no
unprompted `gh`-writes). It moves a local improvement upstream so other devs get it. **The dev stays
in control:** you stage + preview, and never commit/push without their go (except under
`contribution: automatic`).

## Scope — what can be contributed

- **concept** — `concepts/*.md` or a bundle's `concepts/*.md`
- **bundle** — a component / tool / extension dir
- **skill** — a `.claude/skills/<name>/` (new or improved)
- **framework change** — AGENTS.md (+ per-agent adapters), BUNDLES.md, templates, hooks,
  dependencies (`pyproject.toml` + `uv.lock`), etc.

## 0. Pre-flight

- **Curated-required.** A curation-carrying artifact (concept/bundle) must be **`curated`**
  (human-vetted). **Refuse an `inferred` one** — route it to review first (concept-capture review /
  dev review). `canonical` is reachable **only** through this skill.
- **Target = the framework repo.** Contribution always PRs to the **framework repo** (this clone) —
  *never* a component's own repo (that would be a `fix`, not a contribution).
- **Resolve remotes** (deterministic — don't guess remote names):
  `python3 .claude/scripts/resolve-remotes.py` (from the repo root) → JSON
  `{upstream, fork, default_branch, mode, fork_exists, error}`. If `error` is set (gh not authed,
  not a git clone) → surface it, route to `/onboard`, and stop. `mode` from the resolver wins over
  a stale `scope.remotes.mode`; fork mode with `fork_exists: false` → have the dev create the fork
  (`gh repo fork --clone=false <upstream>`) first.
- **Sync + branch off latest:** `git fetch <upstream-remote> && git switch -c contribute/<type>-<name> <upstream>/<default_branch>` (clean PR base).

## 1. Resolve X → its file set

Map the request to an explicit path list (a concept file; a whole bundle dir; a skill dir; specific
framework files). **One artifact per PR** by default; the dev may combine a related **family**.
**Stage exactly those paths** (`git add <paths>` — never `-A`; gitignored local dirs can't leak, but
this also keeps unrelated tracked edits out of the PR).

## 2. Hygiene — the audit gate

- **mdformat** the staged markdown:
  `uv run mdformat <staged paths>` (`wrap="keep"`, frontmatter-safe — reads `.mdformat.toml`).
- **Secret check (informal, advisory)** — run
  `python3 .claude/scripts/secret-scan.py <staged paths>`. It returns a
  **prioritized list of potential-risk items** (HIGH→LOW); **surface that list to the dev to review**
  — it never removes anything and isn't a hard block. Shared artifacts should carry secret
  *descriptions + placeholder skeletons* only, so flag real-looking values where a placeholder
  belongs. The dev decides what to redact before proceeding.
- **Type-specific audit:**
  - **concept** → coherence vs the canonical set (drift / duplication / confusion).
  - **component / tool** → **agent-fitness review** (below); the secret check above covers run
    procedures.
  - **extension / skill / framework change** → none; **PR review is the audit**.

### Agent-fitness review (component / tool)

These bundles exist to let the agent *act*, so audit how well the docs actually **inform and guide
an agent** — not just that they're secret-free:

- **Sufficiency** — could an agent use/run this from the `definition.md` (+ `snippets/`) **alone**?
  Tool: is the capability + install + invocation clear enough to actually use it? Component: is the
  run procedure complete (prereqs → setup → run → verify)?
- **Implied-but-missing snippets** — does it describe standing behavior ("always pass X in
  non-interactive use", "prefer this for that") that *should* be a `snippets/` entry
  (`AGENTS.local.md` / settings hook) but isn't? Offer to add it.
- **Gaps** — unfilled placeholders, TODOs, vague steps, missing prereqs/verify.
- **Agent-facing quality** — imperative + concrete + clickable refs, not just description.

**Technique:** run it as a **cold read by a fresh subagent** — given only the definition + snippets,
*not* this conversation — asking "could you use/run this from this alone? what's missing?" That
surfaces curse-of-knowledge gaps the author can't see. Low/medium effort. Feed findings back (fill
gaps, add implied snippets) before the curation flip.

## 3. Curation — promote to canonical

For a **new** artifact currently at `curated`, set the exact field in the exact file:

- **concept** → set `curation: canonical` in the concept file's frontmatter, **rename `_<slug>.md`
  → `<slug>.md`** (local → tracked), then re-index (its row moves `AGENTS.local.md` → `AGENTS.md`).
- **bundle** (component / tool / extension) → set `curation: canonical` in
  `<kind>/<name>/definition.md` frontmatter.
- **skill / framework change** → no `curation` field; the PR itself is the promotion.

An **update** to an already-`canonical` artifact → **no flip**, just the diff.

## 4. Preview + offer — the dev gate

Stage the files, then **STOP and preview** for the dev:

- the **commit message(s)** — convention `Add|Update <type>: <name>`;
- the **PR title** (same) and **description** — what changed + why + the curation transition + the
  artifact type, following the repo's PR conventions.

Then **offer** to commit + push + open the PR for them — **or** let the dev commit + PR themselves to
control how the change is presented. **Do not commit or push without the dev's explicit go.**

## 5. Execute — on the dev's go, using the resolved remotes (§0)

Address repos by **identity**, not guessed local remote names. Commit the staged paths, then:

- **fork mode:** `git push -u <fork-remote> contribute/<type>-<name>` then
  `gh pr create --repo <upstream> --base <default_branch> --head <fork-owner>:contribute/<type>-<name> --title "…" --body "…"`. (If the fork has no local remote, add it:
  `git remote add fork https://github.com/<fork>.git`.)
- **branch mode** (push access): `git push -u origin contribute/<type>-<name>` then
  `gh pr create --repo <upstream> --base <default_branch> --head contribute/<type>-<name> …`.
- The **`contribution` preference** sets how far you go: **`ask`** (default — preview + offer, §4,
  proceed on the dev's go) · **`automatic`** (carry through `gh pr create`) · **`manual`** (preview
  only; the dev does all git/`gh`).

## Notes

- **Never self-initiate** — the dev's explicit "contribute X" is what authorizes the remote action.
- `canonical` = shipped or being-PR'd; **only this skill sets it**.
- Secrets are dev-local and never enter a PR (`BUNDLES.md`; boundary).
- **Re-contribution** (updating an existing PR after feedback) isn't handled yet — open a fresh PR,
  or have the dev manage the branch.
