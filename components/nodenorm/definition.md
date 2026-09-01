---
name: nodenorm
org: biothings
repo: NodeNormalizationAPI
kind: sri-utility
status: active
curation: canonical
infores: infores:sri-node-normalizer   # maintainer-confirmed 2026-09-01; shared with the RENCI original — see "Identity"
owner: biothings                       # org-level; no CODEOWNERS — see "Ownership" below
parts: [conflation, elasticsearch-backend, biolink-toolkit, set-id-generation, health-status, swagger-ui-webapp, opentelemetry]
related: [nodenormalization-sri, babel, biolink-model, biothings-sdk, elasticsearch, bte]
default_enabled: true  # onboard pre-selects this bundle (a dev can opt out)
---

# nodenorm (biothings/NodeNormalizationAPI)

## What it is

**Node normalization** is Translator infrastructure, not a knowledge source: given a CURIE, it
resolves the **preferred/canonical identifier**, returns the **equivalent identifiers** across source
vocabularies, attaches **Biolink categories**, and can apply **conflation** — merging
distinct-but-linked entities (a gene and its protein product; a drug and its chemical form) into one
clique. It's how KPs and ARAs agree on node identity across the ecosystem, so a normalization
difference shows up downstream as duplicate, missing, or unmergeable nodes.

**This repo** is a **from-scratch reimplementation** of that API contract on the **BioThings SDK
stack** (Tornado + **Elasticsearch**), built by the biothings/Scripps team. Handler docstrings across
the codebase call it a *"Mirror implementation to the renci implementation"* — same endpoint names
and semantics, ported logic, **different backend** (Elasticsearch, where the original uses Redis).
It is **not** a proxy or wrapper: it's an independent codebase re-deriving the same contract
(`repos/NodeNormalizationAPI/src/nodenorm/handlers/normalized_nodes.py:305` — *"Ported from the redis
instance"*).

**Not a TRAPI service.** Its wired routes are plain REST utility endpoints — no `/query`, no TRAPI
operation — so there is no `trapi_version`. (The bundled `openapi.json` claims
`x-trapi.version: "1.5.0"` / `operations: ["annotate_nodes"]`, but that's copied metadata and no such
route exists; see "Identity & the copied spec".)

Young repo — first commit 2026-02-25, 28 commits as of HEAD `852eacc` (2026-07-15).

## ⚠️ Two different NodeNorms — don't conflate them

|       | This bundle                                                | The other one                                                     |
| ----- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Repo  | `biothings/NodeNormalizationAPI`                           | `NCATSTranslator/NodeNormalization` (formerly `TranslatorSRI/…`)  |
| Stack | BioThings SDK · Tornado · **Elasticsearch**                | **Redis**                                                         |
| Role  | Reimplementation / "mirror"                                | The original SRI service                                          |
| Hosts | `nodenorm-es.{ci,test}.transltr.io` (**`-es` = this one**) | `nodenormalization-sri.renci.org`, `nodenorm{,.test}.transltr.io` |

When a report says "NodeNorm", **establish which one** before reasoning about it. The two share an
API contract, so a behavioral difference between them is a real and likely class of bug.

## ⚠️ Documentation discrepancies — read the code, not the docs

Three in-repo sources actively **misdescribe** this service. All verified against the code at HEAD
`852eacc` on 2026-09-01, and all **known-and-unfixed as of that date** — the maintainers have chosen
not to correct them for now. Until they are, **this section is the correction of record**: prefer it
and the route table over anything the repo says about itself.

| Source                                      | What it claims                                                                                                          | Reality                                                                                                    | Trust instead                      |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `README.md`                                 | A **set** of BioThings "data plugin" knowledgebase **KP** APIs, hosted at `biothings.ncats.io` / `pending.biothings.io` | **One** service — node normalization, an **`sri-utility`** — hosted at `nodenorm-es.{ci,test}.transltr.io` | this file + `handlers/__init__.py` |
| `src/nodenorm/webapp/openapi.json` → `info` | RENCI's identity, and `x-trapi.version: "1.5.0"` with `operations: ["annotate_nodes"]`                                  | **Not a TRAPI endpoint.** No `annotate_nodes` or `/query` route exists                                     | `handlers/__init__.py`             |
| that spec's description text                | `/get_curie_prefixes` is available                                                                                      | Handler file exists but is **never imported** — not a live route                                           | `handlers/__init__.py`             |

### `README.md` is a different project's README

It is **byte-identical to [`biothings/pending.api`](https://github.com/biothings/pending.api)'s
README** (verified by `diff` against `master`, 2026-09-01) — evidently copied when the repo was
scaffolded and never rewritten. **Nothing in it was written about node normalization.** Concretely:

- *"This repository maintains a **set of** biomedical knowledgebase APIs"* — this repo is **one**
  service, not a collection.
- It explains the BioThings **"data plugin"** authoring model and links a **`/plugins` folder that
  does not exist here** (the top level is `deploy/ docker/ src/ tests/`).
- It frames everything it discusses as a Translator **KP (Knowledge Provider)**. NodeNorm is **not a
  KP** — it's an `sri-utility`. This is the most damaging line in the file: taking it at face value
  puts you in the wrong component class before you start.
- Its hosting claims (`biothings.ncats.io`, `pending.biothings.io`) and its "how to add a new API" /
  "how to update data for an existing API" workflows describe **pending.api's** operations, not this
  service's. For where this actually runs, see "Deployed instances".

The one sentence incidentally true of this repo is that it is built with the BioThings SDK.

### `openapi.json`'s `info` block is RENCI's, never rewritten

The whole block is copied verbatim from the **original RENCI spec**: title "Node Normalization",
a RENCI contact address, `termsOfService` → `toss.apps.renci.org`, `x-translator` (`component: "Utility"`, team "Standards Reference Implementation Team"), `x-translator.infores`, and `x-trapi`.

Consequences, in order of how badly each misleads:

- **The `x-trapi` claim is false.** This service exposes no TRAPI operation — `build_handlers()` wires
  only the REST utility routes in "API surface". Never cite the bundled spec as evidence of TRAPI
  compliance, and don't hand it to a TRAPI validator.
- **The contact/maintainer fields are the wrong team.** The contact address and RENCI terms-of-service
  URL belong to the other implementation. Don't route a question about this service there.
- **`x-translator.component: "Utility"` happens to be right** — this *is* a utility, not a KP or ARA —
  but the provenance is second-hand, so the bundle's `kind: sri-utility` rests on the code and the
  a maintainer's confirmation, not on this field.
- **`infores:sri-node-normalizer` is correct** for this deployment — see "Identity"
  under Gotchas for why it still doesn't disambiguate the two implementations.

### A documented endpoint that isn't wired

`/get_curie_prefixes` appears in the copied description text and has a handler file
(`src/nodenorm/handlers/curie_prefix.py`), but that module is **never imported** by
`handlers/__init__.py` and the path is absent from the spec's own `paths`. Calling it 404s. Treat
`build_handlers()` as the only authority on what routes exist.

## Deployed instances

**Verified live 2026-09-01** (`GET /version` + `GET /status` against each host). Level model:
`concepts/component-maturity-levels.md`.

| Level (short) | Formal (`x-maturity`) | URL                                    | State                                                             |
| ------------- | --------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| CI            | `staging`             | `https://nodenorm-es.ci.transltr.io`   | live                                                              |
| Test          | `testing`             | `https://nodenorm-es.test.transltr.io` | live                                                              |
| Prod          | `production`          | —                                      | **not deployed** (`nodenorm-es.transltr.io` does not resolve)     |
| Dev           | `development`         | —                                      | **not deployed** (`nodenorm-es.dev.transltr.io` does not resolve) |
| local         | —                     | `http://localhost:8000`                | see "Running it locally"                                          |

The **`-es` hosts are this service** (Elasticsearch-backed), confirmed by a repo maintainer (2026-09-01) — distinct from the
plain `nodenorm{,.test}.transltr.io` / `nodenormalization-sri.renci.org` hosts, which are the RENCI
original. **CI and Test appear to be the only levels**: no Prod or Dev host resolved on 2026-09-01 across the
bare, `.prod`, `-prod`, `.dev`, and `-dev` patterns (absence of a guessed hostname isn't proof, but
a maintainer named exactly these two). With no Prod instance of *this* implementation, a user-facing
NodeNorm complaint is most likely about the **other** service.

**SmartAPI is stale for this component** — it has no entry for `nodenorm-es.*` at all (its only
`sri-node-normalizer` record lists the RENCI hosts). Per a repo maintainer, deployment has moved on to the
`-es` hosts ahead of the registry. So for this component, **the registry is not the authority on
where it runs — this table and `/status` are.**

### Current deployment state (2026-09-01)

CI and Test are **identical** — worth re-checking before assuming a level difference explains a
behavioral one:

|                       | CI                                                                                      | Test           |
| --------------------- | --------------------------------------------------------------------------------------- | -------------- |
| `/version` (git SHA)  | `852eacc3`                                                                              | `852eacc3`     |
| `/status` app version | `1.0.0`                                                                                 | `1.0.0`        |
| Babel release         | [`2025sep1`](https://github.com/ncatstranslator/Babel/blob/master/releases/2025sep1.md) | `2025sep1`     |
| biolink-model-toolkit | `v4.2.6-rc5`                                                                            | `v4.2.6-rc5`   |
| Elasticsearch         | 9.3.1, 3 nodes                                                                          | 9.3.1, 3 nodes |

`852eacc3` is also the repo's HEAD, so both deployed levels are **at tip of `main`**.

**`/status` is the cheapest triage call here** — it returns the Babel release the index was loaded
from, the bmt version, and ES cluster health in one hit. A normalization discrepancy between two
environments is very often a **Babel release difference**, not a code difference.

### Build/deploy path

`deploy/Jenkinsfile` + `deploy/values.yaml` commit **no hostname**: image → ECR
`translator-nodenormalization-api`, Helm → EKS `translator-eks-ci-blue-cluster`, k8s namespace
**`bte`**, labels `gov.nih.ncats.appname: bte-node-normalization`. The hostname comes from an
uncommitted `values-ci.yaml` injected by Jenkins. The `bte` namespace suggests this deployment
chiefly serves **BioThings Explorer**.

## API surface

Authoritative route table: `repos/NodeNormalizationAPI/src/nodenorm/handlers/__init__.py`
(`build_handlers()`) — read it, not `openapi.json`.

| Path                       | Method    | Purpose                                                                                                                                                                                     |
| -------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/get_normalized_nodes`    | GET, POST | **The main endpoint.** CURIE(s) → preferred ID, equivalent identifiers, Biolink types, information content. Params: `conflate`, `drug_chemical_conflate`, `description`, `individual_types` |
| `/get_allowed_conflations` | GET, HEAD | Supported conflation kinds — hardcoded `["GeneProtein", "DrugChemical"]`                                                                                                                    |
| `/get_semantic_types`      | GET, POST | All Biolink semantic types (+ ancestors) present in the ES index                                                                                                                            |
| `/get_setid`               | GET, POST | Deterministic UUIDv5 "set ID" for a normalized CURIE set (implements `TranslatorSRI/NodeNormalization#256`)                                                                                 |
| `/status`                  | GET       | Health — ES cluster node stats, Babel version, biolink-model-toolkit version                                                                                                                |
| `/version`                 | GET       | Build version (git commit hash, or baked-in `version.txt`)                                                                                                                                  |
| `/`, `/webapp/(.*)`        | static    | Swagger UI                                                                                                                                                                                  |

### `/get_normalized_nodes` — params and response shape

Parameters, read off `src/nodenorm/handlers/normalized_nodes.py:39-55` (GET) and `:142-145` (POST).
All flags are booleans; **note `conflate` defaults to _true_** — omit it and you get GeneProtein
conflation whether you wanted it or not, which is a common source of "why are these two nodes
merged?" confusion.

| Param                    | Type                   | Default    | Notes                                                                |
| ------------------------ | ---------------------- | ---------- | -------------------------------------------------------------------- |
| `curie`                  | string, **repeatable** | —          | `?curie=A&curie=B` for a batch (`get_arguments`, not `get_argument`) |
| `conflate`               | bool                   | **`true`** | GeneProtein conflation                                               |
| `drug_chemical_conflate` | bool                   | `false`    | DrugChemical conflation                                              |
| `description`            | bool                   | `false`    | include descriptions                                                 |
| `individual_types`       | bool                   | `false`    | per-equivalent-identifier Biolink types                              |

Verified live against CI on 2026-09-01:

```bash
curl 'https://nodenorm-es.ci.transltr.io/get_normalized_nodes?curie=MONDO:0005148'
```

```jsonc
{
  "MONDO:0005148": {                                   // keyed by the CURIE you asked for
    "id": { "identifier": "MONDO:0005148", "label": "type 2 diabetes mellitus" },
    "equivalent_identifiers": [                        // 21 entries for this CURIE
      { "identifier": "DOID:9352", "label": "type 2 diabetes mellitus" },
      { "identifier": "OMIM:125853" },                 // `label` is optional — may be absent
      { "identifier": "UMLS:C0011860", "label": "Diabetes Mellitus, Non-Insulin-Dependent" }
    ],
    "type": ["biolink:Disease", "biolink:DiseaseOrPhenotypicFeature", "biolink:BiologicalEntity"],
    "information_content": 78.3,
    "taxa": []
  }
}
```

**An unresolvable CURIE comes back as `null`, not an error and not an omission:**

```bash
curl '…/get_normalized_nodes?curie=FAKE:12345'   # → {"FAKE:12345": null}
```

So the response is always keyed by every CURIE requested — when triaging "my node disappeared",
check for a `null` value before assuming the request failed.

**`/get_curie_prefixes` does not exist here.** The copied OpenAPI text references it and
`handlers/curie_prefix.py` defines a handler for it, but that file is **never imported** in
`handlers/__init__.py` — dead code, not a callable route.

## Running it locally

> Best-effort run-hints from the characterization scan — **not a verified procedure**. Run
> `/run-target nodenorm` to establish and record one.

### Prerequisites

- Docker (+ Compose) for the containerized path; Python + the `biothings[web_extra]` SDK for a bare run.
- **An Elasticsearch cluster you supply**, pre-loaded with a **Babel compendia release**. Nothing in
  this repo spins one up.
- Network egress on startup (see External deps).

### Setup

`docker-compose.yml` (repo root) builds `docker/Dockerfile`. **Caveat:** the Dockerfile's builder stage
does a **`git clone` from GitHub** (`ARG NODENORM_REPO` / `NODENORM_BRANCH`, default `main`) rather than
using the local build context — **local edits are not picked up** unless you push and point the args at
your branch.

### Run

```bash
docker compose up          # see the port caveat below
```

**Port mismatch (likely a bug).** `docker-compose.yml` maps `9000:9000`, but the container's front door
is **Caddy on 8000** (`docker/configuration/Caddyfile`, Dockerfile `EXPOSE 8000`), reverse-proxying to
Tornado on `localhost:9001` (`docker/configuration/supervisord.conf`, `--port=9001`). **As committed,
`localhost:9000` is unreachable** — remap to `8000:8000`.

Bare run: `python -m nodenorm --conf=<path/to/config.json>` (`src/nodenorm/__main__.py`).

**Pointing it at your own Elasticsearch** is the step the container path doesn't hand you: the image
bakes a k8s-internal ES hostname (see "External deps"), and the app reads **only** the JSON config —
not `ES_HOST` from the environment. So you must supply a config file with your `ES_HOST` and mount or
bake it in; there is no env-var shortcut. `/run-target nodenorm` should nail down the exact
invocation.

### Verify

`GET /status` (ES stats + Babel version) and `GET /version`. Then a real normalization —
`GET /get_normalized_nodes?curie=MONDO:0005148`.

### Common tasks

**No task runner** (no Makefile / tox / nox) and **no `.github/workflows`**. CI/CD is
`deploy/Jenkinsfile` only — build, push to ECR, Helm deploy; **it never runs the test suite**.

**Tests need an internal host.** `tests/test_normalized_nodes.py` and `tests/test_set_identifiers.py`
hardcode `ES_HOST = "http://su10:9200"` and a dated index `nodenorm_20250507_4ibdxry7` — a
Scripps-network host, unreachable from outside and not reproducible without that data load.

### External deps

- **Elasticsearch** — required; default `http://localhost:9200`
  (`src/nodenorm/config/config.default.json`). The image-baked `docker/configuration/config.json`
  points at `http://elasticsearch.es-core-components.svc.cluster.local:9200`, resolvable **only inside
  that k8s cluster**.
- **Babel compendia** (`TranslatorSRI/Babel`) — the data behind the ES index; `/status` reads
  `babel_version` out of the index's `_meta.src.nodenorm.url` (`src/nodenorm/handlers/health.py`).
- **biolink-model** — `src/nodenorm/biolink.py` calls `bmt.Toolkit(...)` against
  `raw.githubusercontent.com/biolink/biolink-model/<version>/biolink-model.yaml` **at import time**.
  Needs egress or a warm `PYSTOW_HOME` cache to start; pin with `BIOLINK_VERSION`.

### Config & secrets

Config is a **JSON file**, passed as `--conf=<path>` (`src/nodenorm/namespace.py`) — **not** env vars.
Note `deploy/templates/deployment.yaml` sets `ES_HOST` / `PORT` as container env vars, but this repo's
own config loading never reads them (whether the upstream `biothings` package does was not verified).

**No application secrets.** No API keys or credentials in source or config. CI uses AWS credentials
from the Jenkins agent environment (`aws ecr get-login-password`, EKS `update-kubeconfig`) — supplied by
Jenkins, never committed.

## Ownership

No `CODEOWNERS`. Git-log **hint** only (commit counts by `%an` at HEAD `852eacc`): Everaldo (14),
shuchenliu (5) and Will (4) — the same contributor under two author names — chevvak2 (3),
ctrl-schaff (2). `pyproject.toml` names a sole package author, Johnathan Schaff.
Treat all of this as a hint, not an authority — commit counts are not
maintainership.

## Gotchas & notes

- **Identity — the infores is right but not discriminating.** `infores:sri-node-normalizer` **does
  denote this deployment** (confirmed with a repo maintainer, 2026-09-01), so the frontmatter value
  is correct. But it also
  names the **node-normalization function** generally, and SmartAPI's only `sri-node-normalizer` record
  still lists the **RENCI** hosts (`nodenormalization-sri.renci.org`, `nodenorm{,.test}.transltr.io`),
  with **0 hits** for `NodeNormalizationAPI`. So **the infores alone does not tell you which
  implementation answered** — both codebases serve the same contract under it. Pin the responder by
  **host** (`-es` ⇒ this one) or `GET /version`, never by `resource_id`.
- **The repo's own docs are unreliable** — README, bundled OpenAPI spec, and a documented-but-unwired
  endpoint. See "Documentation discrepancies" above; that section is the correction of record.
- **`docker-compose.yml` build args are malformed**: entries written as `- ARG NODENORM_REPO=...`
  (Dockerfile `ARG` syntax pasted into a compose `args:` list). Effectively a no-op — harmless only
  because it coincides with the Dockerfile's own defaults. If fixing: make it a proper mapping —
  `args: {NODENORM_REPO: ..., NODENORM_BRANCH: ...}`.
- **`docker/patches/health.py`** — an alternate health handler ("Patched version to handle missing
  metadata gracefully and fix ES API compatibility") **referenced by nothing** in the Dockerfile or any
  build script. Orphaned/staged code.
- `set_identifiers.py` cites upstream `TranslatorSRI/NodeNormalization#256` and `#173` as design
  provenance — useful when a set-ID question comes up.
