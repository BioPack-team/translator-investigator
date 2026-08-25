---
name: retriever
org: BioPack-team
repo: retriever
kind: kp
status: active
curation: curated
infores: infores:retriever
trapi_version: "1.6"
owner: tokebe
parts: [tier0, tier1]
related: [gandalf, shepherd]
---

# retriever

## What it is

A Translator TRAPI component that **aggregates knowledge from other KPs** — it sits
between raw Knowledge Providers ("DogPark KPs") and the **Shepherd** ARA platform,
deduplicating subqueries, caching, and centralizing node-normalization. It queries
**data tiers** and aggregates/validates the results (see the `data-tiers` concept):
**Tier 0** = Gandalf (a CSR graph DB, native multi-hop and OBI), **Tier 1** =
Elasticsearch, Tier 2 eventually.

SmartAPI registers it as `x-translator.component: **KP**` (an *aggregating* KP),
`infores:retriever`, team `DOGSURF`. TRAPI **1.6** (x-trapi `1.6.0`), `operations: [lookup]` (lookup
only — see the `query-resolution-modes` concept), `asyncquery` supported,
`batch_size_limit` 300, Biolink 4.3.2.

## Running it locally

### Prerequisites

- **Python 3.13** (`>=3.13,<3.14`) and **`uv`**.
- **Docker** — local Dragonfly (Redis-compatible, `:6379`) + MongoDB (`:7.0`, `:27017`),
  brought up by the DB tasks.

### Setup

```bash
# clone if absent (normally done at enable / run-target): gh repo clone BioPack-team/retriever repos/retriever
cd repos/retriever
uv sync            # create .venv, install deps
```

### Run

```bash
uv run task dev    # PRIMARY debug entrypoint
```

`task dev` = `task dbs && task launch:debug` — brings up the DB containers, then
launches with `DEBUG=true`, `LOG_LEVEL=TRACE`, single worker, and job timeouts disabled
(`JOB__LOOKUP__TIER{0,1,2}_TIMEOUT=-1`). App serves on **`:8080`**
(`config/config.default.yaml:12`, `docker-compose.yaml:25`). `task start` is the
non-debug variant; `task dev:otel` also launches Jaeger (`:16686`, `task jaeger:open`).

**`task dev` is a long-running foreground server** — start it in the background (Bash
`run_in_background: true`; never a bare `&`), then **wait for startup** (DB containers come up
first, then Uvicorn logs it's serving on `:8080`) before running Verify.

> ⚠️ **Destructive:** `task dbs` (invoked by `dev`/`start`) runs
> `dbs:stop && dbs:start`, which `docker rm --force` the `test-dragonfly` /
> `test-mongodb` containers. **Every `task dev` wipes local DB state** — expected, but
> don't rely on data persisting across restarts.

### Verify

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:8080/    # 200 (server.py:212)
curl -sS http://localhost:8080/meta_knowledge_graph | head          # metakg (server.py:230)
```

Main endpoints: `GET /`, `GET /meta_knowledge_graph`, `POST /query`, `POST /asyncquery`
(`src/retriever/server.py`).

### Common tasks

```bash
uv run task test     # pytest + coverage; `live`-marked tests skipped unless `-m live`
uv run task fixup    # ruff lint:fix + format:fix + basedpyright + deptry
uv run task dbs:stop # stop DB containers (WIPES them)
```

### External dependencies (reachability first)

The DB containers are local, but the **knowledge lives in external tier backends**, which
a **locally-run** Retriever reaches **directly**. On an unexpected failure — timeouts,
connection errors, or empty/partial results where a tier should have contributed —
**check the dependency's reachability before concluding it's a retriever bug:**

- **Tier 0 — Gandalf** (`https://gandalf.renci.org`) — reachable **without VPN** (good
  control).
  - `curl -sS -o /dev/null -w "%{http_code}\n" -m 6 https://gandalf.renci.org`
- **Tier 1 — Elasticsearch** (`tier1.transltr.biothings.io`) — reaching this backend
  **directly requires VPN**.
  - `curl -sS -o /dev/null -w "%{http_code}\n" -m 6 https://tier1.transltr.biothings.io`
  - `000`/timeout ⇒ unreachable ⇒ **likely the VPN is disconnected**, not a retriever
    bug. If Gandalf responds but Tier 1 times out, it's almost certainly the VPN.

> **VPN is only for reaching a backend directly** — i.e. a **locally-run** Retriever, or
> `curl`-ing the backend yourself. A **live/deployed Retriever instance** is the
> data-access layer: it fronts the backends over TRAPI and abstracts their net-config
> behind the app, so you hit it over **plain HTTP — no VPN, Tier 1 included**.

### Config & secrets

`pydantic-settings`: YAML under `config/` + env vars; nested keys use `__` (e.g.
`JOB__LOOKUP__TIER0_TIMEOUT`, `OPENAPI__X_TRAPI__BATCH_SIZE_LIMIT`); a root `.env`
works.

**Secrets:** none required for basic local dev — Gandalf is public and Tier 1 is reached
over VPN, not credentials. Optional observability (e.g. a Sentry DSN) is configured via
env if used:

```bash
# .env (dev-local, gitignored — never commit real values)
# SENTRY__DSN=<your-sentry-dsn>   # optional; omit to disable Sentry
```

## Gotchas & notes

- **Tier 0 vs Tier 1 asymmetry.** Tier 0 hands the query wholesale to Gandalf (native
  multi-hop + OBI); Gandalf's internal logs are **not** preserved in the response, so an
  absence of expansion/subclass logs at Tier 0 is expected, not a bug. Tier 1/2
  subclassing is orchestrated by retriever's own QGX. (Retriever-specific OBI mechanics
  → this bundle's `concepts/`.)
- **Retriever registers as a KP but functions as an aggregator** — `kind: kp` reflects
  the SmartAPI `component`; the aggregating role is the substance.
- Gandalf config: `CONFIG.tier0.gandalf` (`src/retriever/config/general.py`); Tier 1
  alongside in `config/` + `general.py`.
