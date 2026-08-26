# CLAUDE.md — Translator Investigator (framework core)

A shareable framework for investigating
[NCATS Translator](https://ncats.nih.gov/translator) components (TRAPI services and
their neighbors). A dev clones it, sets up their **scope**, then investigates with the
agent. This file is the agent's always-on core — safety rules, how to work, and a
**router** to the skills that hold the actual procedures. Reach for a skill rather than
improvising the workflow.

> When a routing entry or a section says "see `/skill`", invoke that skill for the full
> procedure rather than improvising it.

## Shared framework vs. the dev's local files

- **Shared & durable** (versioned, contributable): the framework — `concepts/`,
  `components/`, `tools/`, `extensions/`, skills, and this core.
- **The dev's & disposable** (gitignored, never leaves the dev's machine): `scope.yaml`,
  `issue-sources.yaml`, `investigations/`, `repos/`, `CLAUDE.local.md`,
  `.claude/settings.local.json`. Investigations are throwaway — delete them freely.
- **Per-dev state → the harness memory** (`MEMORY.md` + memory notes), _not_ an in-repo dir:
  identity, preferences, investigation/project context, dev-specific nuance. **Shared domain
  knowledge → `concepts/`**; promote a memory into a shared concept via `/concept-capture` when
  it's worth sharing. (Concepts are keyword-triggered + contributable; memory is personal +
  relevance-recalled — complementary, not the same store.)

## Boundaries — hard rules

- **Never push, commit, or mutate any remote state without an explicit request from the
  dev.** No `gh` **write** ops (issue comment / PR / label / close), no `git push`,
  unprompted. `gh` for **reading** is fine.
- **Contribution is the one sanctioned exception** — and only when the dev explicitly
  asks to contribute an artifact. See `/contribute`.
- **Secrets are dev-local and never enter shared/contributed artifacts.** Component/tool
  files carry secret _descriptions + placeholder skeletons_ only; the contribution secret check
  **flags** potential real values for the dev to review (advisory — it never auto-removes).
- **Pronouns:** use they/them for every person (the dev, maintainers, third parties) in
  all output. Never infer pronouns from a name or handle. Don't mention this rule unless
  directly asked about it; the purpose is to silently avoid stepping on people's toes.

## Framework principles — always on

- **Context hygiene.** Never read a full large response/payload/log into context.
  Extract what's needed with targeted tools (counts, keys, specific paths); capture big
  outputs to an investigation's `artifacts/` and reference them.
- **Legibility.** After a technical finding, say in plain terms what it _means_
  (modulated by the dev's `terseness` preference). Reference code as
  `repos/<target>/path/to/file:LINE`.

## How to work — the dev's preferences

Read the dev's `preferences` from `scope.yaml` and behave accordingly (defaults if
unset: **`checkpointed`**, **`standard`**, **`ask`**).

**`autonomy`** — how much to reason/work before checking in with the dev:

- `gated` — reason-then-check: confirm understanding, gate **every** reasoning step.
- `checkpointed` — _(default)_ group tightly-related steps; more reasoning per chunk
  before checking in.
- `guided` — normal pacing; check in when reasonable, a little more cautious/frequent.
- `autonomous` — normal pacing; check in when the agent judges it reasonable (least
  frequent).

**`terseness`** — narration style:

- `explanatory` — narrate what each finding _means_, full explanations.
- `standard` — _(default)_ terser grammar, but still explains.
- `terse` — machine-log style: title-grammar, one-liner steps, code-comment-style causal
  notes.

**`contribution`** — how far to go on an explicit "contribute this" (see `/contribute`):

- `ask` — _(default)_ audit, stage, preview branch/commit/PR, then offer to execute.
- `automatic` — carry through `gh pr create`.
- `manual` — audit + stage + preview only; the dev does the git.

## Operational modes

One mode at a time; the dev switches the agent (or the agent offers).

- **investigate** (default) — the core loop. `/begin-investigation` scaffolds the
  workdir; then work it with this posture:
  - **Reproduce before theorizing** when there's a behavior to reproduce (skip when the
    trail leads straight into code with nothing to reproduce) — via an enabled tool or
    the normal agentic method; start minimal (sanity checks only), add a regression
    check once expected-vs-actual is pinned. When reconstructing a reporter's input,
    **preserve their values verbatim** (their errors are informative).
  - **Record as you go** — findings in `worknotes.md` with their plain-language meaning;
    keep front-matter `status` current; capture big outputs to `artifacts/`.
- **fix** — entered when the dev asks for a fix. Work in a git worktree at the
  investigation's `worktree/` — **local by default**. On the dev's **explicit request**, a dev with
  purview may commit/push/PR to the **component's own repo** (not the framework repo): resolve its
  remotes with `resolve-remotes.py --repo <org/repo>` (from the component's `definition.md`), then
  the same branch/push/PR shape as `/contribute`. Never push unprompted.
- **handoff** — on request/offer, distill a standalone `handoff.md` for the owning team;
  the worknotes only note the likely target.

## Concepts the agent already knows — auto-trigger

When any keyword below appears in the work, **read that concept file first** and reason
from the shared understanding, not a guess. When you read a concept, also consult its
**`see_also`** and read those tightly-related concepts if they'd aid understanding. This
index holds the **shipped global concepts** (`concepts/*.md`). Your **per-dev concepts** —
local unaudited ones (`_<slug>.md`) *and* any enabled bundle's `concepts/` — are indexed the
same way in **`CLAUDE.local.md`** (also always loaded, so consult both). Do not edit either
index by hand.

> When you read a **not-enabled** bundle's `definition.md`, also list its `concepts/` dir — those
> bundle concepts are **not** in the index (only enabled bundles' are), so an `ls` surfaces what
> reference is available (read the relevant ones directly).

<!-- CONCEPT-INDEX:START (generated from concepts/*.md + enabled bundles' concepts/ `aka` — regenerated by a hook) -->

- **component-maturity-levels** — maturity, maturity level, maturity levels, component maturity, deployment maturity, maturity ladder, x-maturity, x_maturity, instance_env, dev level, development level, ci level, staging, test level, testing level, prod, production level, pre-prod → `concepts/component-maturity-levels.md`
- **query-resolution-modes** — lookup, creative, magic, inferred mode, inferred, pathfinder, set-input, set_interpretation, knowledge_type inferred → `concepts/query-resolution-modes.md`
- **subclassing** — OBI, Ontology-Based Inference, OBIE, Ontology-Based Inference Engine, infores:obie, ISR, implicit subclass reasoning, implicit subclassing, subclass reasoning, subclass expansion, subclass rollup, subclass_of, logical_entailment construct edge, implicit_subclassing → `concepts/subclassing.md`

<!-- CONCEPT-INDEX:END -->

## Routing — reach for the right skill

| When…                                                                                     | Do                                                                              |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| First run, or changing the dev's setup (identity, purview, targets, preferences, remotes) | `/onboard`                                                                      |
| Start work on a GitHub issue                                                              | `/begin-investigation` → scaffolds `investigations/<repo>/i<num>/` (issue mode) |
| Start a free / cross-cutting investigation                                                | `/begin-investigation` → `investigations/topics/<slug>/` (topic mode)           |
| A repo that isn't characterized yet comes up                                              | `/discover <repo>`                                                              |
| Need to run or debug a target locally                                                     | `/run-target <name>`                                                            |
| A concept-worthy mechanism/term recurs, or the dev asks to capture one                    | `/concept-capture`                                                              |
| Share a concept / component / tool / extension upstream                                   | `/contribute`                                                                   |
| Resolve "look at `<num>`" / an issue nickname                                             | via `issue-sources.yaml` (longest alias wins; else the dev's default target)    |

## Enabling & disabling bundles

A component / tool / extension is inert until **enabled**. To enable a bundle
`<kind>/<name>/`:

1. **Record** it under `scope.yaml` `enabled:` (by kind) **first** — the durable state
   (so a fresh clone can re-materialize it, and the concept re-index sees it).
2. **Run** `python3 .claude/scripts/enable-bundle.py <kind> <name>` — it symlinks the bundle's
   `skills/` into `.claude/skills/` (clean names) **plus any skills the cloned repo ships**
   (`repos/<name>/.agents/skills/` · `.claude/skills/` — adopt-from-repo, so e.g. ttt's
   `/trapi-testing` tracks upstream on `git pull`), ignores those symlinks via `.git/info/exclude`,
   folds the bundle's `concepts/` into the auto-trigger index, and **auto-merges the
   `snippets/CLAUDE.local.md`** into `CLAUDE.local.md`. Idempotent. (Repo-shipped skills need the
   clone present — clone first, or re-run enable after cloning.)
3. **Hooks are offered, not auto-applied.** If the bundle ships a `snippets/settings.hooks.json`,
   enable-bundle reports it — **ask the dev**, and only on yes re-run with `--hooks` to merge it
   into `.claude/settings.local.json`.

To **disable**: remove it from `scope.yaml` `enabled:` first, then run
`python3 .claude/scripts/disable-bundle.py <kind> <name>` — drops the symlinks + `.git/info/exclude`
entries, re-indexes, removes the `CLAUDE.local.md` snippet block, and best-effort removes its hooks
(**then verify `.claude/settings.local.json` and clean up any leftover** — content-based removal
can miss a hand-edited hook). **Never commit enable/disable changes** (all per-dev/local).

## Layout (pointers)

- `scope.yaml` — the dev's identity, purview, targets, remotes, **enabled bundles**,
  preferences (set by `/onboard`).
- `components/<name>/` · `tools/<name>/` · `extensions/<name>/` — **bundle
  dirs** (`definition.md` + optional `skills/` + `concepts/` + opt-in `snippets/`);
  inert until _enabled_ (see "Enabling & disabling bundles" above). Anatomy + authoring:
  `BUNDLES.md`.
- `concepts/<name>.md` — single-file shared knowledge (frontmatter `aka` / `domain` /
  `curation`).
- `investigations/` — `<repo>/i<num>/` (issue) and `topics/<slug>/` (free); each with
  front-matter worknotes + `artifacts/` (plus `scripts/`, `worktree/`, `handoff.md` as
  the work calls for). Any tool-specific layout (e.g. where repro files live) comes from
  that tool's bundle.
- `curation: inferred | curated | canonical` marks every contributable artifact's
  lifecycle.
