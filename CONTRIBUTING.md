# Contributing

`translator-investigator` grows by contribution: devs improve the shared framework — concepts,
component / tool / extension bundles, skills, and the core — and share them back so everyone
benefits.

## The model

Your **scope, clones, investigations, and memory are local** (gitignored) and never leave your
machine. The **framework** is the shared, versioned part: `concepts/`, `components/`, `tools/`,
`extensions/`, skills, `CLAUDE.md`, `BUNDLES.md`, templates, and the helper scripts.

## How to contribute

Let the agent do it: **`/contribute <thing>`** — a concept, a bundle, a skill, or a framework
change. It runs the pre-PR hygiene, promotes the artifact's `curation` to `canonical`, and
**previews the branch + commit + PR before opening it** — you stay in control, and nothing is pushed
without your explicit go.

Pre-PR hygiene includes:

- **mdformat** the staged markdown (`uv run mdformat .`; config in `.mdformat.toml`).
- an **advisory secret check** — bundles carry secret *descriptions + placeholder skeletons* only,
  **never real values**.
- a **cold-read agent-fitness review** for a component/tool bundle (could a fresh agent use/run it
  from the definition alone?), or a **coherence check** for a concept.

Conventions:

- **One artifact per PR** by default; combine a related family if it makes sense.
- Bundle/concept lifecycle is `inferred → curated → canonical`; only `/contribute` sets `canonical`.

## Boundary

The agent **never pushes or mutates remote state without your explicit request**. `/contribute` is
the one sanctioned path to upstream.
