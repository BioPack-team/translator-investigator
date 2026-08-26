---
name: component-maturity-levels
aka:
  - maturity
  - maturity level
  - maturity levels
  - component maturity
  - deployment maturity
  - maturity ladder
  - x-maturity
  - x_maturity
  - instance_env
  - dev level
  - development level
  - ci level
  - staging
  - test level
  - testing level
  - prod
  - production level
  - pre-prod
domain: [Translator, deployment]
see_also: []
curation: canonical
---

# Component maturity levels

A component's **maturity level** is **where an instance of it is deployed** — not a property of the
code, but of a running deployment. The Translator ecosystem runs **several parallel deployments of
each component at once**, one per maturity level, each a **separate live instance at its own URL**.
So any given component is not one thing: a service (BTE, Aragorn, the ARS, a KP, …) exists as a Dev,
CI, Test, and Prod instance simultaneously, and those can differ in code, data, and behavior at any
given moment.

## The four levels

Ascending from least to most stable. Each level has a short name (how people usually refer to it)
and a formal name (the value that appears as `x-maturity`):

| Short | Formal (`x-maturity`) | What it is                                                            |
| ----- | --------------------- | --------------------------------------------------------------------- |
| Dev   | `development`         | Instances **maintained by the component owners** (their own servers). |
| CI    | `staging`             | **Auto-deployed when a component merges PRs** — the freshest code.    |
| Test  | `testing`             | The **stable pre-prod testing environment**.                          |
| Prod  | `production`          | The level that **serves users**.                                      |

> **Naming trap — "CI" = the `staging`/CI *deployment level*, not a CI/CD pipeline.** The short name
> "CI" and the formal name "staging" are the **same rung**. So "a component's CI" (e.g. "the CI
> instance") means *the live instance deployed at the CI maturity level* — **not** GitHub Actions, a
> repo's checks, or its pytest suite. Never conflate a component's *maturity level* with its *CI/CD
> pipeline*; when a report says "X at CI" it almost always means the CI-level running service.
> (Test↔testing and Prod↔production pair the same way, but CI↔staging is the one that trips people up.)

## How a level is signaled

- **A distinct URL per level.** Each maturity is its own instance; the host encodes the level.
  **CI / Test / Prod live on the shared `transltr.io` deployment infra** — `*.ci.transltr.io`,
  `*.test.transltr.io`, and the bare `*.transltr.io` for Prod (e.g. `bte.ci.transltr.io`,
  `bte.test.transltr.io`, `bte.transltr.io`). **Dev usually lives on the *owner's* own
  infrastructure** — often *not* `transltr.io` — consistent with "servers maintained by component
  owners" (e.g. `aragorn.renci.org`, `dev.retriever.biothings.io`). Watch for per-app exceptions:
  **ARS** is on `transltr.io` at *every* level (Dev included) and uses hyphen-suffixed
  `ars-dev.transltr.io` / `ars-prod.transltr.io` rather than the usual `.dev`/`.test`/`.ci` pattern.
- **`x-maturity` in SmartAPI/OpenAPI.** A component advertises its levels through its SmartAPI
  registration: each entry in the OpenAPI `servers[]` array is tagged with an `x-maturity` field
  carrying the formal level name, so clients and the SmartAPI registry can tell which maturity a given
  instance URL is. This is the **authoritative, ecosystem-standard** signal of a URL's level.
- **An internal level signal (component-specific).** A component may *also* be told its own level by
  the deployer at run time, so the running app can apply **maturity-appropriate behavior** where
  warranted — distinct from the client-facing `x-maturity` it advertises. How a given component wires
  this is its own detail (e.g. retriever's `instance_env` — see that bundle's `definition.md`).

## Targeting a level (tooling)

The levels are first-class in the **trapi-testing-tools (`tt`)** instrument, which is the concrete,
maintained enumeration of them: environments are keyed **`app.level`** and the `level` is the
maturity rung. `tt`'s shipped defaults list per-app URLs for `dev` / `ci` / `test` / `prod` — in the
trapi-testing-tools repo, `trapi_testing_tools/config.py`'s `DEFAULT_ENVS` plus `config.yaml`. So
`tt test -e ci` runs against the **CI-level instance** of
the targeted app (e.g. `bte.ci`, `aragorn.ci`). When reproducing a report, run against the **same
level** it came from by selecting that `-e <level>`.

## Why it matters for investigation

- **"Which instance did this come from?" is a first-order triage question.** A behavior observed at
  one maturity may not reproduce at another — CI auto-deploys on merge (so it can be *ahead* of Test
  and Prod), while Prod is the stakes-bearing, user-facing level. Reproduce against the **same level**
  the report came from before concluding anything.
- **It disambiguates the report itself.** A report phrased as *"a component's CI is doing X"* is
  about **the live CI-level instance's behavior**, not a failing GitHub check — a very different
  starting point. Getting the level right points you at the right artifact (a deployed service vs. a
  pipeline).
- **Deployment axis, not an answering axis.** Maturity is about *where a component is deployed*, not
  *how it answers*. Don't conflate it with a component's internal query-behavior axes (e.g. a KP's
  data tiers — which backend sources the knowledge): the same instance at any maturity still carries
  all of those.
