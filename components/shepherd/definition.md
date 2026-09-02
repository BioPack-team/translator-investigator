---
name: shepherd
org: BioPack-team
repo: shepherd
kind: platform         # registers in SmartAPI as ARA (4 fronts); really a multi-ARA platform — see note
status: active
curation: inferred
trapi_version: "1.5"   # SmartAPI x-trapi.version = 1.5.0 — one behind the usual 1.6; pin translator-tom to 1_6 with care
owner: Max Wang        # Covar; SmartAPI team DOGSLED. Confirmed by dev.
parts: [lookup, score, sort, filter, merge, finish, monitor, pathfinder, aragorn, arax, bte, sipr]
related: [ARS, arax.ncats.io, kg2webhost.rtx.ai]
---

# shepherd

## What it is

A shared **platform for implementing Translator ARAs**: a FastAPI intake/status/callback server plus
a Redis-Streams-backed worker fleet, so multiple ARAs share common operations (lookup, score, sort,
filter, merge, finish) while plugging in their own custom logic.

It fronts **four ARAs**, each a separate SmartAPI registration (all `component: ARA`,
`trapi_version: 1.5.0`): `infores:shepherd-aragorn`, `infores:shepherd-arax`, `infores:shepherd-bte`,
`infores:shepherd-sipr`. So its SmartAPI `kind` baseline is **ARA**, but structurally it's a
platform hosting those four — hence `kind: platform` here. Routes are per-target:
`/{ara_target}/query` and `/{ara_target}/asyncquery`.

Top-level packages: `shepherd_server` (FastAPI), `shepherd_db` (Postgres), `shepherd_broker`
(Redis), `shepherd_utils` (shared worker task-loop + DB/broker/data-download helpers), `workers/*`
(one container per operation — 22 total).

## Running it locally

### Prerequisites

Python ≥3.12, Docker + `docker compose`. A root `.env` (mounted into containers).

### Setup

Populate `.env` (see Config & secrets). Large read-only data volumes self-download on first worker
startup — no manual seeding.

### Run

`docker compose up --build` from the repo root (`compose.yml`; `compose.test.yml` for the test
stack). No Taskfile/Makefile. `shepherd_server` serves on **:5439**.

### Verify

Hit a per-target route on :5439 (`/{ara_target}/query`, e.g. `aragorn`/`arax`/`bte`/`sipr`);
`shepherd_monitor` on :5440.

### Common tasks

Tests: `pip install tox && tox` (pytest + coverage). Integration smoke: `scripts/test_shepherd.py`
(needs a running local stack; takes `target` = ARA name). Tracing UI: Jaeger :16686 (OTLP gRPC
:4317). Redis UI: RedisInsight :5540.

### External deps

- **ARS** — sends queries to `/{ara_target}/asyncquery` and `/query`.
- **`arax.ncats.io`** — the `arax` worker proxies to `https://arax.ncats.io/shepherd/api/arax/v1.4/query`
  rather than reimplementing ARAX locally.
- **`kg2webhost.rtx.ai`** — `arax_pathfinder` downloads sqlite DBs (`curie_ngd_*`,
  `tier0-info-for-overlay_*`) from `/tier0` on first startup.
- ARAGORN's `general_concepts.json` blocked-concept list is fetched from GitHub on first run.
- Deployed hostnames: `shepherd.renci.org`, `shepherd.ci.transltr.io`, `shepherd.test.transltr.io`.

### Config & secrets

Root `.env` mounted into containers:

```dotenv
POSTGRES_PASSWORD=<postgres-password>
REDIS_PASSWORD=<redis-password>
# optional dataset URLs
OMNICORP_LMDB_URL=<url>
PATHFINDER_EMBEDDINGS_URL=<url>
ARAX_PATHFINDER_TIER_VERSION=<tier-version>
```

Per-query deadline `QUERY_TIMEOUT_SEC` (default 300s); worker concurrency `TASK_LIMIT`; drain
`WORKER_DRAIN_TIMEOUT_SEC` (default 30s); reaper `MONITOR_ABANDONED_QUERY_SEC` (default 600s).

## Gotchas & notes

- **TRAPI 1.5.0**, not 1.6/2.0 — one release behind the framework default; pin models accordingly.
- **Self-downloading data volumes** (gitignored, first-startup): `aragorn_omnicorp`→`./omnicorp_lmdb/`,
  `score_paths`→`./pathfinder_embeddings/`, `arax_pathfinder`→`./arax_pathfinder_dbs/`. The presence
  check is an exact path + tier-versioned-filename match — a mismatched
  `ARAX_PATHFINDER_DBS_DIR`/`ARAX_PATHFINDER_TIER_VERSION` silently re-downloads to the wrong path
  and can evict the k8s pod on ephemeral-storage limits.
- `general_concepts.json` (ARAX blocklist) shares the `arax_pathfinder` volume and needs it writable
  on first run, else startup fails on a read-only mount.
- **Per-query hard deadline** `QUERY_TIMEOUT_SEC` is stamped at intake and checked by every worker
  (`finish_query`/`merge_message` exempt); a client's TRAPI `parameters.timeout` can extend it
  (larger wins). Monitor's `MONITOR_ABANDONED_QUERY_SEC` reaper is the backstop.
- Graceful shutdown drains up to `WORKER_DRAIN_TIMEOUT_SEC`; unfinished tasks are left for Redis
  stream reclaim — set k8s `terminationGracePeriodSeconds` above it.
- **Tight Postgres connection budget**: every container has its own psycopg pool; the fleet sum must
  stay under `max_connections` (currently 300; `shepherd_server` alone up to 30).
- `TASK_LIMIT` raises in-process concurrency, but CPU-bound pool workers (`merge_message`,
  `score_paths`, `arax_rank`, `aragorn_score`, `aragorn_omnicorp`) size process pools from an in-code
  default — raising it there only deepens the intake queue.
- Architecture is in the terse `Architecture.txt` at repo root plus the README — no `docs/` dir.
