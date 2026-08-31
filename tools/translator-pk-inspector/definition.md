---
name: translator-pk-inspector
org: cbizon
repo: translator-pk-inspector
status: active
curation: canonical
owner: cbizon
provides: retrieve an ARS parent PK's ARA child messages and their stored TRAPI responses, for inspecting what each ARA actually returned
---

# translator-pk-inspector

## What it provides

Turns an **ARS primary key** (or a Translator UI results URL) into the **TRAPI responses each ARA
actually returned** for that query. It fetches the parent ARS message, selects the children whose
`actor.agent` starts with `ara` (e.g. `ara-shepherd-aragorn`, `ara-shepherd-bte`,
`ara-shepherd-arax`), then fetches each child's own stored message — so you can compare ARAs
side-by-side on one submitted query.

This is the **entry point for PK-shaped reports**: a Translator user's complaint almost always
arrives as a PK or a UI link plus "this result is wrong/missing", and this tool converts that into
the actual per-ARA payloads to reason over.

**vs. `trapi-testing-tools`** — they overlap on ARS retrieval (`tt pk`) but differ in direction:

- **pk-inspector** — *inspect an existing submission*: fan out from one parent PK to per-ARA
  responses. Reach for it whenever a PK is the starting point.
- **`tt`** — *fire new queries and assert on them*: authoring query files, regression checks,
  hitting a component directly. Reach for it once you're reproducing rather than inspecting.

A typical investigation uses both: pk-inspector to see what happened, `tt` to reproduce it against
a specific component.

**Design principle worth preserving:** the skill deliberately **does not infer failure causes it
can't verify** — retrieval failures (HTTP, JSON, missing fields) are surfaced as-is rather than
guessed at. Keep that posture; an unexplained gap is a finding, not something to paper over.

## Install & run

**Not a package** — no manifest, no console script, **Python 3 stdlib only** (`argparse`, `json`,
`urllib`; no third-party deps, no `uv`).
It's used as a **cloned agent skill**; this framework clones it to `repos/translator-pk-inspector/`
and enabling the bundle adopts its skill as **`/translator-pk-inspector`**.

The underlying script can also be called directly:

```bash
# from the framework root; <investigation> is the workdir /begin-investigation scaffolds,
# e.g. investigations/feedback/i1370/ (issue mode) or investigations/topics/<slug>/
python3 repos/translator-pk-inspector/scripts/fetch_ars_children.py <PK-or-UI-URL> --env ci \
  --output investigations/<repo>/i<num>/artifacts/pk.json
```

Arguments: `input` (parent PK or UI results URL) · `--env {dev,ci,test,prod}` (**required for a raw
PK**; inferred from the host for a UI URL) · `--output` (default stdout) · `--timeout` (default 60s)
· `--no-trace` · `--include-all-children` (also emit the raw parent + non-ARA children) ·
`--metadata-only` (**does not work as named — see the warning below**).

**Environments** map to the standard maturity levels (see the `component-maturity-levels` concept):
`dev` → `ars.dev.transltr.io`, `ci` → `ars.ci.transltr.io`, `test` → `ars.test.transltr.io`,
`prod` → `ars.transltr.io`. Note the **`dev` UI host is `transltr-bma-ui-dev.ncats.io`**, not a
`*.transltr.io` name — a UI link from dev looks unlike the others.

**Credentials: none.** The ARS endpoints are public unauthenticated GETs.

## Using it

The detailed playbook is the repo's own **`SKILL.md`** (adopted as `/translator-pk-inspector` on
enable, so it tracks upstream on `git pull`) plus **`references/trapi-response-guide.md`** in the
clone, which the skill loads for downstream TRAPI analysis (result counts, edge bindings, support
graphs, ARA differences, log/timeout interpretation). Prefer those over this file for usage.

**Context hygiene — important.** Full ARA payloads are large (**~38M per environment** on a
real query) and there can be several per PK. Always `--output` to the investigation's `artifacts/`
and summarize with a script; never read a payload into context.

> **`--metadata-only` does not trim the payload** (verified 2026-08-31 on Feedback#1370): the
> "metadata" output still carried the full 1260-edge knowledge graph and was the same ~38M as the
> full fetch. Don't rely on it to keep responses small — treat every fetch as full-size.

**Sharing caution:** the repo's README warns that fetched ARS/TRAPI payloads may carry internal
service detail — scrub before putting them in a handoff or an upstream issue.

## Notes

- **Young repo** (single commit as of 2026-05-13, authored by this dev) — no tests, no CI, no
  license file. Expect it to evolve; re-check `SKILL.md` rather than trusting a cached
  understanding.
- **Skill layout quirk:** `SKILL.md` lives at the **repo root** (the repo is designed to be cloned
  *into* `~/.claude/skills/`), not under `.agents/skills/` or `.claude/skills/` where
  `enable-bundle.py` looks. This bundle bridges that with a `skills/<name>` symlink pointing at the
  clone; see that symlink before assuming adoption is broken.
