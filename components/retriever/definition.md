---
name: retriever
org: BioPack-team
repo: retriever
kind: kp
status: active
curation: canonical
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

## Deployed instances (maturity levels)

Quick URL access per maturity (see the `component-maturity-levels` concept for the
level model). **Source: trapi-testing-tools `DEFAULT_ENVS`** (`trapi_testing_tools/config.py`)
— the maintained enumeration; target with `tt … -e <level>` (e.g. `-e ci`).

| Level (`tt -e`) | Formal (`x-maturity`) | URL                                  |
| --------------- | --------------------- | ------------------------------------ |
| `local`         | —                     | `http://localhost:8080`              |
| `dev`           | `development`         | `https://dev.retriever.biothings.io` |
| `ci`            | `staging`             | `https://retriever.ci.transltr.io`   |

- **Dev is on owner (BioThings) infra**, not `transltr.io` — matches "Dev = owner-maintained."
- **`test` / `prod` are not in tt's defaults.** By the shared-infra convention they'd be
  `retriever.test.transltr.io` / `retriever.transltr.io`, but that's **unverified** — confirm
  against SmartAPI `servers[]` `x-maturity` before using, don't assume.

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
(`config/config.default.yaml`, `docker-compose.yaml`). `task start` is the
non-debug variant; `task dev:otel` also launches Jaeger (`:16686`, `task jaeger:open`).

**`task dev` is a long-running foreground server** — start it in the background (Bash
`run_in_background: true`; never a bare `&`), then **wait for startup** (DB containers come up
first, then Uvicorn), then **poll the Verify `curl /` until it returns 200** — that probe is
the readiness signal — before proceeding.

> ⚠️ **Destructive:** `task dbs` (invoked by `dev`/`start`) runs
> `dbs:stop && dbs:start`, which `docker rm --force` the `test-dragonfly` /
> `test-mongodb` containers. **Every `task dev` wipes local DB state** — expected, but
> don't rely on data persisting across restarts.

### Verify

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:8080/    # 200 (server.py)
curl -sS http://localhost:8080/meta_knowledge_graph | head          # metakg (server.py)
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
  subclassing is orchestrated by retriever's own **QGX** (Query Graph eXecution — see this
  bundle's `qgx` concept). (Retriever-specific OBI mechanics → this bundle's `concepts/`.)
- **Retriever registers as a KP but functions as an aggregator** — `kind: kp` reflects
  the SmartAPI `component`; the aggregating role is the substance.
- **`instance_env` = internal maturity signal (vs `x-maturity` = advertised).** `instance_env`
  (config, default `dev`; `src/retriever/config/general.py`) is how the **deployer tells the
  running app which maturity level it is**, so the app can apply maturity-appropriate behavior if
  warranted; it also feeds the Sentry environment and the outbound sub-query User-Agent. Distinct
  from **`x-maturity`** in the OpenAPI `servers[]` (`src/retriever/config/openapi.py`), which
  *advertises* the level to clients/SmartAPI. See the `component-maturity-levels` concept.
- Gandalf config: `CONFIG.tier0.gandalf` (`src/retriever/config/general.py`); Tier 1
  alongside in `config/` + `general.py`.
- **`/status/*` operational dashboard API** (`src/retriever/status.py`, `include_router`;
  plus the `/monitor` static UI). Reachable on a **live/deployed instance over plain HTTP —
  no VPN, no auth** (like the TRAPI endpoints; e.g. `curl -sS https://retriever.ci.transltr.io/status`),
  so it's the first stop for triaging a running instance without local setup. Purpose-built:
  `/status` (snapshot — per-tier `up`/`last_outage`/`last_recovery`, Mongo/Redis
  health, version), `/status/tiers`, `/status/timeline`, `/status/failed` · `/completed` ·
  `/failure_breakdown` (windowed job records), `/status/durations`, `/status/jobs/{id}`,
  `/status/server_logs` (non-job lifecycle/driver logs — e.g. `GandalfDriver down: ReadTimeout`).
  Job history is **MongoDB-backed** (durable across redeploys); the `/status` root `tiers`
  block is the driver's **in-process** health tracker (resets on redeploy, so it won't show a
  past outage after a CI auto-deploy).
  - **⚠️ Gotcha — `lookback` shadows `since`.** On `/status/tiers`, `/status/timeline`, and
    `/status/durations`, the `lookback` query param **defaults to `24.0` (hours) and overrides
    `since`** (`status.py:_resolve_time_window`) — so passing `since`/`until` silently returns
    the last 24h, *not* your window. `/status/failed`, `/status/completed`,
    `/status/failure_breakdown`, `/status/submitters` default `lookback=None` and **do** honor
    `since`/`until`. To bound a window on the lookback-defaulting endpoints, pass an explicit
    `lookback` sized to the window, or use the paged endpoints.
