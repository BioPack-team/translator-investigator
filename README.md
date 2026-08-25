# Translator Investigator

A shareable framework for investigating [NCATS Translator](https://ncats.nih.gov/translator)
components (TRAPI services and their neighbors) with [Claude Code](https://claude.com/claude-code).
Clone it, set up your scope, and start investigating.

## Quick start

1. Clone the repo and open it in Claude Code.
2. Run **`/onboard`** — sets up your scope (identity, purview, target repos, preferences), wires
   contribution remotes, and enables the tools you want.
3. Start an investigation — give Claude a GitHub issue (`investigate #123`) or a topic
   (`look into <X>`); it scaffolds a workdir and works it with you.

## Yours vs. shared

- **Shared & versioned** (the framework): `concepts/`, `components/`, `tools/`, `extensions/`,
  skills, `CLAUDE.md`. Improvements flow back upstream via **`/contribute`**.
- **Yours & local** (gitignored, never leaves your machine): `scope.yaml`, `issue-sources.yaml`,
  `investigations/`, `repos/`, `CLAUDE.local.md`. Per-dev memory lives in Claude Code's memory, not
  the repo.

## How it works

- **Skills** carry the procedures: `/onboard`, `/begin-investigation`, `/discover`, `/run-target`,
  `/concept-capture`, `/contribute`.
- **Bundles** — `components/` (repos you investigate), `tools/` (instruments), `extensions/` (opt-in
  standing behaviors). *Enabling* a bundle wires in its skills, concepts, and snippets. See
  `BUNDLES.md`.
- **Concepts** — shared, keyword-triggered understanding of Translator/TRAPI; the agent auto-reads
  the relevant one when a keyword comes up.
- **Boundary** — the agent never pushes or mutates remote state without your explicit request;
  `/contribute` is the one sanctioned path.

## Requirements

- Claude Code · `gh` (authenticated) · `git` · `uv` (markdown/format tooling: `uv sync`).

## Docs

- `CLAUDE.md` — the agent's always-on core (safety, preferences, routing).
- `BUNDLES.md` — bundle anatomy + the enable / contribute model.
- `CONTRIBUTING.md` — how to share improvements back.

## License

MIT — see [`LICENSE`](LICENSE).
