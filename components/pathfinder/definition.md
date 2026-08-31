---
name: pathfinder
org: Translator-CATRAX
repo: pathfinder
kind: backend
status: active
curation: canonical
# no infores — not a registered TRAPI service. (A SmartAPI search for "pathfinder" hits
# infores:biothings-explorer on the word alone; that is not this.)
# no trapi_version — not a TRAPI endpoint; it returns TRAPI-shaped objects, see body.
owner: Mohsen Taheri (mohsenht)   # sole author; no CODEOWNERS
parts: [bidirectional_search, three_hops, breadth_first, path_ranker, ml_repo, retriever_repo, ngd_repo, node_degree_repo, converters, xgboost_model]
related: [rtx, retriever, xcrg, tier0-graph, gandalf, translator-tom]
---

# pathfinder (catrax-pathfinder)

## What it is

A **library, not a service** — a Python package (`catrax-pathfinder`, import name `pathfinder`)
that finds **semantic paths between two CURIE nodes** in a Translator knowledge graph. It backs
ARAX's **Pathfinder query** capability (ARAX's SmartAPI registration advertises
`pathfinderquery: true`).

Given a source and destination CURIE it does a **bidirectional, pruned graph expansion** through
**Retriever**, ranks candidate neighbors at each step with a **bundled XGBoost learning-to-rank
model**, applies degree/blocklist filters, and returns TRAPI-shaped results.

`get_paths(...)` returns a **3-tuple** — `(result, aux_graphs, knowledge_graph)` — of
TRAPI-compliant objects. It is not itself a TRAPI endpoint and declares no TRAPI version; the
caller (ARAX, at TRAPI 1.6) owns the envelope.

**Independently released on PyPI**, unlike its sibling [`xcrg`](../xcrg/definition.md): **18
releases**, latest **2.4.3**, MIT licensed, `requires-python >=3.9`. ARAX pins
`catrax-pathfinder==2.4.3` — i.e. **ARAX is current with pathfinder's latest release**. Contrast
with xCRG, which is git-SHA-pinned because it has no PyPI release. Both are pins, but only xCRG's
gap is a work-in-progress iteration.

## Public API

```python
from pathfinder.Pathfinder import Pathfinder

pathfinder = Pathfinder(repo_uri, ngd_url, degree_url,
                        blocked_curies, blocked_synonyms, logger)
result, aux_graphs, knowledge_graph = pathfinder.get_paths(...)
```

### Constructor inputs

| Parameter          | What it is                                                          |
| ------------------ | ------------------------------------------------------------------- |
| `repo_uri`         | The KG source. **Only `retriever:<URL>` is accepted** (see Gotchas) |
| `ngd_url`          | CURIE-NGD repository — `sqlite:<path>` or `mysql:<config>`          |
| `degree_url`       | Node-degree repository — `sqlite:<path>` or `mysql:<config>`        |
| `blocked_curies`   | Set of CURIEs; any path passing through one is dropped              |
| `blocked_synonyms` | Set of name strings; paths through matching nodes are dropped       |
| `logger`           | Any logger-like object                                              |

Backend selection is by **URL prefix** (`repo_factory.py`) — `sqlite:` / `mysql:` for the two
databases, `retriever:` for the graph. An unrecognized prefix raises `ValueError`.

### `get_paths(...)` tuning knobs

| Parameter              | Package default | ARAX passes                       |
| ---------------------- | --------------- | --------------------------------- |
| `hops_numbers`         | `4`             | `parameters['max_path_length']`   |
| `max_hops_to_explore`  | `6`             | `parameters['max_path_length']`   |
| `limit`                | `500`           | `max_pathfinder_paths` (dflt 500) |
| `prune_top_k`          | `30`            | **`75`**                          |
| `degree_threshold`     | `30000`         | **`10000`**                       |
| `category_constraints` | `None`          | Biolink `descendants`             |

`max_hops_to_explore` is the exploration depth; `hops_numbers` is the post-filter cap on returned
path length. `prune_top_k` keeps only the top-ranked *k* neighbors per expansion step;
`degree_threshold` refuses to expand nodes above that degree.

## How ARAX drives it

`ARAX_connect.py:468` constructs it as:

```python
Pathfinder(f"retriever:{retriever_url}",
           get_curie_ngd_path(),      # -> "sqlite:.../curie_ngd_v1.0_tier0-YYYYMMDD.sqlite"
           get_kg2c_db_path(),        # -> "sqlite:.../tier0-info-for-overlay_v1.0_tier0-YYYYMMDD.sqlite"
           blocked_curies, blocked_synonyms, self.response)
```

The `Path_Finder/utility.py` helpers **already prepend `sqlite:`**, so the prefix contract is
satisfied — ARAX always uses the SQLite backend, never the MySQL one, reading the symlinked local
artifacts. Note `get_kg2c_db_path()` resolves `RTXConfiguration().kg2c_sqlite_path`, which under
Tier0 points at **`tier0-info-for-overlay`** (its `neighbors` table supplies node degree) — the
`kg2c` name is a leftover of the KG2→Tier0 rename, not a separate database.

`self.response` (an `ARAXResponse`) is passed as the logger, so pathfinder's diagnostics land in
the TRAPI message log.

**Both of ARAX's CATRAX-built capabilities route through Retriever** — pathfinder via
`repo_uri`, xCRG via `XCRGConfig.retriever_url` — so a Retriever outage or Tier0 regression
degrades Pathfinder queries and xCRG inferred queries together.

## Running it locally

*Run-hints from the repo scan — `/run-target pathfinder` should confirm before anyone leans on it.*
There is no service to start.

### Prerequisites

Python **≥3.9**. Runtime deps are heavier than xCRG's: `numpy==1.26.4`, `xgboost==2.1.4`,
`pandas==2.3.1`, `mysql-connector-python`. The numpy/pandas pins **match ARAX's own**, which is
what keeps the two installable together.

### Setup

```bash
pip install catrax-pathfinder          # or: pip install -e .  from repos/pathfinder
```

### Databases

You need a **`curie_ngd`** and a **`tier0-info-for-overlay`** database matching your KG version.
The README's guidance: ask a team member for **MySQL URLs** (recommended) or local SQLite copies.
The MySQL form points at a shared read-only server, e.g.

```text
mysql:arax-databases-mysql.rtx.ai:public_ro:curie_ngd_v1_0_kg2_10_2
mysql:arax-databases-mysql.rtx.ai:public_ro:kg2c_v1_0_kg2_10_2
```

**This is the cheap path for local investigation** — it avoids downloading multi-GB SQLite files,
and it's an option ARAX itself does not use.

### Run

No server to start — "running" pathfinder means calling it:

```python
from pathfinder.Pathfinder import Pathfinder

pf = Pathfinder(
    repo_uri="retriever:https://retriever.ci.transltr.io/query",
    ngd_url="sqlite:curie_ngd_v1.0_tier0-20260621.sqlite",
    degree_url="sqlite:tier0-info-for-overlay_v1.0_tier0-20260621.sqlite",
    blocked_curies=set(), blocked_synonyms=set(), logger=logger,
)
result, aux_graphs, knowledge_graph = pf.get_paths(
    src_node_id="MONDO:0005148", dst_node_id="CHEBI:15365",
    src_pinned_node="node_1", dst_pinned_node="node_2",
    hops_numbers=4, max_hops_to_explore=4, limit=500,
    prune_top_k=75, degree_threshold=10000, category_constraints=[],
)
```

**The `sqlite:` / `mysql:` / `retriever:` prefixes are mandatory** — `repo_factory` raises
`ValueError` without them. To reproduce ARAX's behavior rather than the package defaults, pass
`prune_top_k=75`, `degree_threshold=10000`, and `max_hops_to_explore == hops_numbers` as above.

### Verify

Run `pytest src/tests/` — prefer the `test_*_using_retriever.py` variants, since the plain ones
were the Gandalf-backed path. A successful `get_paths` returns a 3-tuple whose `knowledge_graph` is
non-empty; an empty result for the MONDO:0005148 / CHEBI:15365 pair above usually means the NGD or
degree database doesn't match the KG version the Retriever endpoint is serving.

### Common tasks

Tests live in `src/tests/` and split by backend: `test_*_using_retriever.py` exercise the
Retriever-backed path; the plain `test_*.py` counterparts were the Gandalf-backed ones. No task
runner, no CI config, and no dev dependency group in `pyproject.toml` — run `pytest` directly.

### Model training (`build_model/`)

Not needed to *use* the package, but this is where ARAX's Tier0 artifacts partly come from:

- **`build_model/training/`** — trains the XGBoost learning-to-rank model
  (`objective=rank:pairwise`) that ranks 1-hop neighbors. Output is
  `pathfinder_xgboost_model_kg_<KG_VERSION>` written into `src/pathfinder/resources/`.
  `nohup env PYTHONPATH=src python build_model/training/training.py --kg-version "20260621" &`.
  **Hyperparameters are hard-coded in `train()`**, taken from the last tuning log
  (`hyperparameter-tuning.log` is committed).
- **`build_model/db_build/`** — builds the **`curie_ngd` SQLite that ARAX consumes** (the PSU-owned
  Tier0 rollout artifact). Needs a **running Redis** (localhost:6379 by default) as a working cache
  and SSH access to `arax-databases.rtx.ai` (user `rtxconfig`) to download inputs and upload
  results. NGD normalization constants are CLI-tunable (`--num-pubmed-articles`, default `3.5e7`;
  `--avg-mesh-terms-per-article`, default `20`).
- **`build_model/testing/`**, **`build_model/data/`** — drug-disease matched-DB evaluation and a
  DrugBank NER pipeline.

### Config & secrets

No config files and no env vars in the package itself. `build_model/db_build` accepts an
**`SSH_PASSWORD`** env var as an alternative to key-based auth (keys are the documented
recommendation).

`build_model/data/drugbankner.env` is a committed env-file **template** for the DrugBank NER
pipeline, declaring `DRUGBANK_EMAIL` / `DRUGBANK_PASSWORD` (HTTP basic auth for the DrugBank
download) plus `WORKDIR` / `KG_VERSION`. **Checked: the credential values are placeholders, not
real secrets.** Note `.gitignore` lists `.env`, which does *not* match `drugbankner.env` — so this
file is tracked by design, and anyone filling it in locally must avoid committing it back.

## Gotchas & notes

- **Gandalf is deprecated here too, and the code proves it.** `repo_factory.get_kg_repo()` accepts
  **only** `retriever:` — any other prefix raises. `GandalfRepo.py` is still on disk but was
  wholesale commented out in `d28ca19` / `bbdc43f` ("Comment Gandalf related since it is
  deprecated", 2026-07-22), and `converter/EdgeExtractorFromGandalf.py` was deleted outright. This
  independently corroborates the removal of the `gandalf_mmap` artifact recorded in
  `components/rtx/definition.md` — two repos, same direction of travel.

- **`build_model/gandalf/` is the obsolete `gandalf_mmap` builder.** It still documents building
  and deploying the memory-mapped Gandalf tarball. **That artifact is no longer required at all** —
  ignore this directory, and ignore the corresponding step in the RTX wiki's Rollout Procedure.

- **`build_model/db_build/README.md` still says the curie_ngd builder uses "Gandalf instance for KG
  lookups".** Unresolved from the scan: this may be genuinely current (the *builder* querying the
  graph directly is a different concern from the *runtime* repo abstraction) or may be stale text
  from the same deprecation sweep. **Confirm before following it** — this README is the wiki's
  cited source for a PSU-owned rollout artifact, so a stale instruction here has downstream reach.

- **A 42 MB XGBoost model ships inside the wheel**, stamped with a Tier0 build date:
  `src/pathfinder/resources/pathfinder_xgboost_model_kg_20260408`, alongside four `.pkl` feature
  encoders. Two consequences: (1) `pip install catrax-pathfinder` pulls ~42 MB of model weights;
  (2) **the model is tied to a specific KG build**, so a Tier0 rollout may need a retrained model
  and a new pathfinder release — not just a database swap. The currently shipped model is stamped
  `20260408` while the current Tier0 build is `tier0-20260621`; whether that lag is intentional is
  worth confirming.

- **ARAX overrides two defaults aggressively** — `prune_top_k` 30 → **75** (explore wider) and
  `degree_threshold` 30000 → **10000** (refuse to expand hubs much earlier). If path results look
  different between a local pathfinder experiment and ARAX, check these first; the README's
  defaults are not what production runs.

- **ARAX sets `hops_numbers == max_hops_to_explore`**, both to `max_path_length`. The package
  allows exploring deeper than the returned cap (defaults 6 vs 4); ARAX declines that headroom, so
  a path needing deeper exploration to be found is never found in ARAX even if its final length
  would be acceptable.

- **Single maintainer.** Every commit is Mohsen Taheri (`mohsenht`, 93 + 14 under two author
  names). No CODEOWNERS, no CI workflow, no dev dependency group — bus factor and review surface
  are both thin for a package compiled into production ARAX.

- **No LICENSE file** in the repo, though `pyproject.toml` and PyPI both declare **MIT** (the
  `license` line even carries a `# or use "file" with LICENSE` comment). The metadata is the only
  license statement.

- **Mixed KG vocabulary in the README** — the Quickstart uses `tier0-20260621` names while the
  URL-format section still shows `KG2.10.2`. Both refer to the same slots; see the KG2→Tier0
  transition note in `components/rtx/definition.md`.

- `KG2_graph_predicate_weights.csv` sits at the repo root (predicate weighting for ranking),
  outside `src/` and so **not** shipped in the wheel — a build/analysis input, not a runtime one.
