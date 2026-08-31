---
name: xcrg
org: Translator-CATRAX
repo: xCRG
kind: backend
status: active
curation: canonical
# no infores — not a registered TRAPI service (SmartAPI: 0 hits). It emits edges attributed to
# its caller's infores, defaulting to infores:arax.
trapi_version: "1.6"   # emits TRAPI 1.6.0 responses (XCRGConfig.trapi_schema_version default)
owner: Jonathan Pettinger, David Koslicki (dkoslicki)   # no CODEOWNERS; venkataseshtej authored v1 and has left
parts: [runner, queries, retriever, ranking, ngd, pmid, trapi, biolink, reporting, debugging, context]
related: [rtx, retriever, pathfinder, shepherd, translator-tom, tier0-graph]
---

# xcrg (xCRG — chemical→gene regulation, MVP2)

## What it is

A **library, not a service** — a reusable Python package (`catrax-xcrg`, import name `xcrg`) that
answers **MVP2 gene activity/abundance inferred TRAPI queries**: given a chemical and a gene, does
the chemical increase or decrease that gene's activity or abundance, and what evidence supports it.

It is **deliberately deployment-agnostic**: it starts no HTTP server, chooses no maturity, and
manages no database files. The caller — **ARAX today, Shepherd by design** — supplies every runtime
input through a single frozen `XCRGConfig` dataclass. The README states this boundary explicitly and
the package enforces it (no ARAX Flask imports, no `shepherd_utils` imports).

No SmartAPI registration (0 hits) — it is not a TRAPI endpoint. It *produces* TRAPI, and the edges
it creates are attributed to `XCRGConfig.resource_id`, which **defaults to `infores:arax`**. So in
an ARS payload, xCRG-derived edges look like ARAX's own.

> **Read this before reading the source.** xCRG is **never deployed standalone** — it ships only
> inside ARAX, pinned by git SHA. `main` currently holds a **second iteration in progress** that is
> not yet deployment-ready, so the code in `repos/xCRG` is not the code answering queries in any
> live ARAX. Everything below describes `main` unless noted; for deployed behavior read the pinned
> SHA. Details in [Gotchas](#gotchas--notes).

**Supported query shape** (`is_xcrg_mvp2_query` gates it): one `biolink:ChemicalEntity` node, one
pinned `biolink:Gene` node, one **inferred** `biolink:affects` edge, with
`biolink:object_aspect_qualifier` = `activity_or_abundance` and `biolink:object_direction_qualifier`
∈ {`increased`, `decreased`}. See the `query-resolution-modes` concept for what "inferred" means
here — this is a creative-mode path, not lookup.

**How it answers:** builds **direct** and **TF-mediated** (transcription-factor) queries against
**Retriever**, then filters, merges, ranks, and resultifies. The TF list ships bundled
(`src/xcrg/resources/transcription_factors.json`), overridable via `XCRGConfig.tf_path`. NGD
(normalized Google distance) scoring and PMID publication support are attached from ARAX's own
SQLite databases when the caller passes their paths.

## Public API

```python
from xcrg import XCRGConfig, async_run_xcrg, is_xcrg_mvp2_query, run_xcrg
```

`run_xcrg(query, config=..., logger=...)` / `async_run_xcrg(...)` return a **already-resultified**
TRAPI response dict. `DebugLevel` is also exported.

### `XCRGConfig` — the entire configuration contract

Frozen dataclass; `retriever_url` is the only required field. Actual defaults from
`src/xcrg/config.py` (the README's usage example passes some non-default values, so read the
dataclass, not the example):

| Field                                                                   | Default                             | Notes                                              |
| ----------------------------------------------------------------------- | ----------------------------------- | -------------------------------------------------- |
| `retriever_url`                                                         | **required**                        | Retriever TRAPI `/query` URL — caller selects it   |
| `ngd_db_path`                                                           | `None`                              | ARAX NGD SQLite; enables NGD scoring/support edges |
| `curie_to_pmids_db_path`                                                | `None`                              | CURIE→PMID SQLite; enables publication support     |
| `tf_path`                                                               | `None`                              | Falls back to the bundled TF list                  |
| `timeout`                                                               | `210`                               | Retriever HTTP timeout, seconds                    |
| `tiers`                                                                 | `[0]`                               | Passed as TRAPI `parameters.tiers` — **Tier 0**    |
| `tf_batch_size`                                                         | `50`                                | TF IDs per batched Retriever request               |
| `resource_id`                                                           | `"infores:arax"`                    | Attribution on xCRG-created edges/attributes       |
| `scoring_method`                                                        | `"xcrg-result-filtering-v2"`        | Label on result analyses                           |
| `max_results`                                                           | `500`                               | Cap on final ranked answer pairs                   |
| `trapi_schema_version`                                                  | `"1.6.0"`                           | Response schema version                            |
| `biolink_version`                                                       | `"4.3.2"`                           | Response Biolink version                           |
| `debug_dir` / `debug_run_name` / `debug_level` / `debug_use_http_cache` | `None` / `None` / `BASIC` / `False` | Debug artifact capture                             |

`tiers` defaulting to `[0]` ties this to the `data-tiers` concept — xCRG queries the **Tier 0**
graph through Retriever.

## How ARAX drives it

`ARAX_connect.py` maps `RTXConfiguration().maturity` to a Retriever deployment and passes the URL in:

| ARAX maturity | Retriever URL                              |
| ------------- | ------------------------------------------ |
| `staging`     | `https://retriever.ci.transltr.io/query`   |
| `testing`     | `https://retriever.test.transltr.io/query` |
| `production`  | `https://retriever.transltr.io/query`      |
| `development` | `https://retriever.ci.transltr.io/query`   |

Note **`development` and `staging` both point at the CI host** — and recall ARAX calls
`arax.ci.transltr.io` "staging" (see `components/rtx/definition.md`). Flow:

```text
RTXConfiguration().maturity
  -> ARAX_connect.get_xcrg_retriever_url(...)
  -> XCRGConfig(retriever_url=..., ngd_db_path=get_curie_ngd_path(),
                curie_to_pmids_db_path=get_curie_to_pmids_path())
  -> run_xcrg(...)
```

ARAX env overrides `ARAX_XCRG_RETRIEVER_URL`, `ARAX_XCRG_TIMEOUT`, `ARAX_XCRG_TF_BATCH_SIZE` are
**local/debug only** — not part of normal deployed behavior.

## Running it locally

*Run-hints from the repo scan — `/run-target xcrg` should confirm before anyone leans on this.*
There is no service to start; "running it" means running its tests or calling `run_xcrg` directly.

### Prerequisites

Python **≥3.10** (classifiers list 3.10–3.12; ARAX runs 3.12). Runtime deps are light:
`bmt>=1.4.6`, `httpx~=0.28`, **`translator_tom==1.2.1`**.

### Setup

```bash
python -m pip install -e .          # from repos/xCRG
```

Dev group (`[dependency-groups] dev`): `pytest==9.1.1`, `pytest-xdist==3.8.0`, `ruff==0.15.22`,
`pyright==1.1.411`, `ty==0.0.63`, `optuna==4.9.0`.

### Run

There is no server to start — "running" xCRG means calling it. Minimal invocation:

```python
from xcrg import XCRGConfig, is_xcrg_mvp2_query, run_xcrg

config = XCRGConfig(retriever_url="https://retriever.ci.transltr.io/query")
assert is_xcrg_mvp2_query(query)          # gate first; it only handles the MVP2 shape
response = run_xcrg(query, config=config, logger=logger)
```

Add `ngd_db_path=` / `curie_to_pmids_db_path=` to get NGD scoring and publication support; without
them those are silently absent rather than an error. Use `async_run_xcrg` for the async entry point.
Set `debug_dir=` to capture Retriever request/response artifacts for `scripts/compare_responses`.

### Verify

```bash
scripts/run_tests unit          # fast, offline — confirms the install
scripts/run_tests integration   # confirms Retriever reachability
```

For a functional check, run one `tests/arax/` case and compare against `scripts/arax_tests.json` —
but read the expectation grade first, and check `fails_on_arax` before treating a miss as a
regression.

### Common tasks

```bash
scripts/run_tests unit          # local, fast, no network
scripts/run_tests integration   # slow, requires network
scripts/run_tests all           # unit + integration (NOT arax — see below)
scripts/run_tests arax          # ARAX compliance suite: slow, network, xdist
scripts/run_checks              # ruff check + ty check
```

Markers are `unit`, `integration`, `arax`. **`all` means "unit or integration" — it does *not*
include the `arax` suite**, which must be asked for by name. The `arax` mode runs
`-m arax -n auto --dist=loadgroup --debug_level=basic --use_http_cache`.

Custom pytest options come from `tests/conftest.py` (`--debug_level`, `--use_http_cache`, and
others) — `--use_http_cache` is what makes repeated network-backed runs tolerable.

The README's recommended gate before updating an integration pin:

```bash
scripts/run_tests all
scripts/run_checks
```

### External deps

- **Retriever** — the only network dependency at runtime; URL is caller-supplied.
- **ARAX's NGD SQLites** (`curie_ngd`, `curie_to_pmids`) — optional; without them NGD scoring and
  publication support are simply absent, not an error.

### Config & secrets

None. No secrets, no config files, no env vars of its own — everything arrives via `XCRGConfig`.
(The `ARAX_XCRG_*` env vars belong to ARAX's integration layer, not to this package.)

## The ARAX compliance harness

`scripts/arax_tests.json` is a **curated, graded expectation ledger** — the most investigation-useful
artifact in the repo. `scripts/generate_arax_tests` renders it into the `tests/arax/test_*.py`
modules (marked `DO NOT MODIFY: generated`).

Current contents: **34 test cases** — 17 `find_chemicals_affecting_gene`, 17
`find_genes_affected_by_chemical`; 23 `decreased`, 11 `increased` — carrying **288 answer
expectations** across four grades:

| Expectation          | Count | Meaning                                    |
| -------------------- | ----- | ------------------------------------------ |
| `never_show`         | 179   | Must not appear — the false-positive guard |
| `top_answer`         | 53    | Must rank at the top                       |
| `acceptable`         | 52    | May appear                                 |
| `bad_but_forgivable` | 4     | Tolerated, but undesirable                 |

**61 of the 288 are flagged `fails_on_arax: true`** — an explicit, tracked known-failure ledger
rather than deleted tests. When investigating an xCRG result complaint, **check whether the case is
already in this file** before treating it as new: the answer may be a known gap with an expectation
already recorded. Most expectations are `never_show`, so the harness is weighted toward catching
*spurious* answers, not missing ones.

`scripts/compare_responses` builds a CSV diff between two debug runs (uses `translator_tom` +
`XCRGConfig.debug_dir` artifacts) — the tool to reach for when a ranking change moves results.

## Gotchas & notes

- **`main` is a work in progress; the pinned SHA is the deployed xCRG.** xCRG is **never deployed
  on its own** — it ships only inside ARAX, so `RTX/requirements.txt`'s
  `catrax-xcrg @ git+…@c97da5349a432e29d7a6432ee272a8c1311de9da` (2026-06-11) *is* the release
  mechanism, and pinning it is the intended design, not neglect. Everything on `main` past that SHA
  is a **second iteration of xCRG in progress** — picked up by Jonathan Pettinger after Venkata
  (`venkataseshtej`) left the project — and is **not yet ready for deployment**:

  - `2466628` Refactor entire module to be fully typed + cleanup
  - `b1aa2b9` Module refactor: separate `.py` files, `RunContext`, cleanup
  - `b641f3d` First pass at **new ranking method** + debugging improvements

  Together these are `49 files changed, +7170/-2849`: nearly every module in `src/xcrg/`
  (`biolink`, `constants`, `context`, `debugging`, `ngd`, `pmid`, `queries`, `ranking`, `reporting`,
  `retriever`, `trapi`, `utilities`) plus the whole `tests/` + `scripts/` harness postdate the pin.

  **Practical consequence when investigating:** `repos/xCRG` on `main` shows you the *next* xCRG,
  not the one answering queries in any deployed ARAX. To reason about observed production behavior,
  read the pinned SHA (`git -C repos/xCRG show c97da53:…`) — especially for anything ranking-related,
  since the new ranking method is one of the WIP changes. To reason about where xCRG is *going*,
  read `main`. Don't treat the difference as a bug or a pin that needs bumping.

- **Not on PyPI.** The README anticipates the git-SHA pin becoming `catrax-xcrg==<version>` "once a
  versioned PyPI release is available" — that hasn't happened, which is why ARAX pins a SHA.
  `pyproject.toml` still declares `version = "0.1.0"` across the v2 work, so **the version string
  does not identify which xCRG you're looking at; compare SHAs.**

- **It deliberately does not repair Retriever's metadata.** Stated policy: xCRG "does not infer,
  repair, or enrich Retriever node categories/names"; evidence nodes/edges are deep-copied through
  as returned, and if Retriever returns incomplete metadata xCRG "preserves that behavior rather
  than silently masking it". **So bad categories/names in an xCRG answer are a Retriever finding,
  not an xCRG bug** — chase them upstream. (Same posture as the framework's own
  reproduce-verbatim rule and pk-inspector's design principle.)

- **TP53 is hardcoded out.** `constants.py` excludes `NCBIGene:7157` because, as a master regulator
  of hundreds of genes, it "showed up everywhere (in paths of all lengths)". The comment marks this
  as a ranking workaround that better ranking might remove. **If a user asks why a TP53-mediated
  path is missing, this is the answer** — and it's a deliberate exclusion, not a data gap.

- **Dangling support graphs are dropped, not surfaced.** xCRG preserves Retriever edge-level
  `biolink:support_graphs` references only when the referenced auxiliary graph is available, and
  **removes** dangling references. Valid output, but it means a support graph Retriever intended
  can silently vanish — worth checking if evidence looks thinner than expected.

- **Publications are conditional.** xCRG-created NGD support edges carry `biolink:publications`
  only when the configured CURIE-to-PMID source yields a **non-empty PMID intersection**. Absent
  publications may mean "no configured DB" rather than "no evidence".

- **It pins `translator_tom==1.2.1`** — older than the `translator-tom` bundle's documented package
  v2.0.0. Both here and in `scripts/`. Keep that in mind when using the framework's TOM tool to
  reason about xCRG's own TRAPI construction; the model APIs may differ.

- **Biolink version mismatch with ARAX.** `XCRGConfig.biolink_version` defaults to `"4.3.2"` while
  ARAX registers Biolink `4.2.5` in SmartAPI. The caller supplies the value in practice, so this is
  a default-vs-deployed question rather than a definite conflict — worth confirming which reaches
  production responses.

- **README/code drift on `tf_batch_size`:** the README's usage example shows `200`; the dataclass
  default is `50`. The example is illustrative, not a defaults table — trust `config.py`.

- **No agent interface** — no `AGENTS.md`, no `.agents/skills`, no `.claude/`. The README is
  unusually thorough and serves as the contract; there is nothing for `enable-bundle.py` to adopt.

- **No LICENSE file** in the repo (GitHub reports no license). Public repo, but unlicensed —
  relevant if anything here is ever redistributed.

- `TODO`s left in the source flag known rough edges: `XCRGConfig` → `Config` rename,
  `scoring_method` as a `StrEnum`, and an import-shape problem in `scripts/compare_responses` that
  "breaks type-checking + linting".
