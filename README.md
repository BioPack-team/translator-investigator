# Translator Investigator

A shareable framework for investigating
[NCATS Translator](https://ncats.nih.gov/translator) components (TRAPI services and
their neighbors) with an [AGENTS.md](https://agents.md)-compatible coding agent —
[Claude Code](https://claude.com/claude-code), Codex, Cursor, Gemini CLI, and others.
Clone it, set up your scope, and start investigating.

## Quick start

1. Install the prerequisites: the
   [GitHub CLI](https://github.com/cli/cli#installation) (`gh`, then `gh auth login` to
   authenticate) and
   [uv](https://docs.astral.sh/uv/getting-started/installation/#installing-uv) — install uv
   from your system package manager (Homebrew, apt, etc.) or with `pip install uv`. (See
   [Requirements](#requirements) for the full list.)
2. Clone the repo and open it in your coding agent (e.g. Claude Code).
3. Run **`/onboard`** — sets up your scope (identity, purview, target repos, issue
   sources, preferences), wires contribution remotes, and enables the tools you want. It
   also sets up the **activation layer** for your agent (skills + concept-reindex hooks)
   — on a non-Claude agent it attempts to port those hooks (see `AGENTS.md`). Purview is
   optional: PIs, PMs, and other triage-only roles can register the repos they watch as
   issue sources — purview (which marks components you maintain) is not required.
4. Start an investigation — give the agent a GitHub issue (`investigate #123`) or a
   topic (`look into <X>`); it scaffolds a workdir and works it with you.

## Workflow

A loop: **onboard**, **investigate**, **resolve** — and, throughout, **make it yours** and
**contribute back**. Each step is a skill you invoke by name.

### Investigate — issues & topics

**`/begin-investigation`** scaffolds a throwaway workdir under `investigations/`:

- **Issue mode** — `investigate #123` fetches the issue and scaffolds
  `investigations/<repo>/i<num>/`. Nicknames resolve through `issue-sources.yaml`
  (`look at feedback #45`), so you **triage** across every repo you watch, in or out of
  purview.
- **Topic mode** — `look into <X>` scaffolds `investigations/topics/<slug>/` for a
  free-form or cross-cutting question.

The posture, either way: **reproduce before theorizing**, **record as you go** in
`worknotes.md` (findings plus what they _mean_), and capture big outputs to `artifacts/`,
not into context. Run a component locally with **`/run-target <name>`**.

### Resolve — hand off or fix

- **Handoff** — `handoff.md`, a standalone writeup for the owning team; the default when
  the component isn't yours or the fix belongs elsewhere.
- **Fix** — the agent works in a investigation-local **worktree** (`worktree/`). It
  commits / pushes / PRs only on your explicit request, only within purview, and only to
  the **component's own repo** — never unprompted.

### Make it yours — extend the framework

Teach the framework your world:

- **Discover components & tools** — **`/discover <repo>`** characterizes one repo into a
  **bundle**: a **component** (a target you investigate) or a **tool** (an instrument you
  use, e.g. a TRAPI query runner). _Enabling_ it wires in the bundle's skills, concepts,
  and snippets; inert until then. See `BUNDLES.md`.
- **Register issue sources** — map a `nickname → repo` in `issue-sources.yaml` (via
  `/onboard`) so `look at <num>` resolves — how a triage-only role watches many repos
  without "owning" any.
- **Capture concepts** — **`/concept-capture`** records a Translator/TRAPI mechanism or
  term as a single-file **concept**: shared, keyword-triggered understanding the agent
  auto-reads when the keyword resurfaces, so it reasons from a checked account, not a guess.
- **Write extensions** — the third bundle kind: an **extension**, an opt-in standing
  behavior (a workflow or posture the agent adopts once enabled) for a specific use-case.
- **Modify the framework itself** — edit the core (`AGENTS.md`), a skill, or the activation
  scripts/hooks, and **add uv dependencies freely** (`pyproject.toml` + the committed `uv.lock`),
  to generalize better or fix a bug.

### Contribute back

Any of the above — concept, bundle, skill, or framework change — goes upstream via
**`/contribute`**: it audits, stages the exact files, previews the commit and PR, then (per
your `contribution` preference) opens it or hands you the git. Or just open an issue on the
framework repo. This is the **one sanctioned remote action** — outside an explicit
`/contribute`, the agent never pushes, comments, or mutates remote state.

## Yours vs. shared

- **Shared & versioned** (the framework): `concepts/`, `components/`, `tools/`,
  `extensions/`, skills, `AGENTS.md` (the agent-agnostic core). Improvements flow back
  upstream via **`/contribute`**.
- **Yours & local** (gitignored, never leaves your machine): `scope.yaml`,
  `issue-sources.yaml`, `investigations/`, `repos/`, `AGENTS.local.md` (+ per-agent
  adapters like `CLAUDE.local.md`). Per-dev memory lives in your agent's memory store
  (or a gitignored `MEMORY.md`), not the repo.

## Requirements

- An [AGENTS.md](https://agents.md)-compatible coding agent (e.g. Claude Code) · `gh`
  (authenticated) · `git` · `uv` (runs the tooling and the reindex hook — `uv sync` / `uv run`) ·
  `python3` (stdlib, for the enable / new-artifact / resolve-remotes / secret-scan helpers).

## Docs

- `AGENTS.md` — the agent's always-on core (safety, preferences, routing, activation
  layer). Claude Code loads it through the thin `CLAUDE.md` adapter.
- `BUNDLES.md` — bundle anatomy + the enable / contribute model.
- `CONTRIBUTING.md` — how to share improvements back.

## License

MIT — see [`LICENSE`](LICENSE).
