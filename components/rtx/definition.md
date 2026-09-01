---
name: rtx
org: RTXteam
repo: RTX
kind: ara
status: active
curation: canonical
infores: infores:arax
trapi_version: "1.6"
owner: dkoslicki, saramsey, edeutsch   # PIs (README); no CODEOWNERS file in the repo
parts: [araxi, expand, overlay, filter, infer, rank, resultify, connect, path_finder, node_synonymizer, response_cache, background_tasker, autocomplete, ui]
related: [xcrg, pathfinder, retriever, gandalf, rtx-kg2, plover, tier0-graph, babel, node-normalizer, name-resolver]
---

# rtx (ARAX — Team Expander Agent / CATRAX)

Sources: repo scan + the **[RTX wiki](https://github.com/RTXteam/RTX/wiki/)** (all 15 pages read
2026-08-31). The wiki is the authoritative developer documentation; see
[Wiki map & what's stale](#wiki-map--whats-stale) at the bottom before trusting any single page.

## What it is

The **ARA** for Team Expander Agent (Oregon State U. + Institute for Systems Biology +
Penn State U.), now also referred to as **CATRAX**. The repo is named `RTX` for historical
reasons — RTX was the 2017–2019 feasibility-phase prototype; **ARAX is the current system
built on that code-base**. Treat "RTX" as the repo and "ARAX" as the service.

SmartAPI registers it as `x-translator.component: **ARA**`, `infores:arax`, team
`Expander Agent`, TRAPI **1.6.0**, Biolink 4.2.5. `asyncquery: true`,
**`pathfinderquery: true`**, `multicuriequery: false`.

What makes ARAX distinctive is **ARAXi** — its domain-specific language. An incoming TRAPI
query is turned into a sequence of ARAXi commands (or interpreted from the query graph via
`ARAX_query_graph_interpreter.py`), then executed as a pipeline: choose upstream KPs →
expand → overlay/filter/infer → rank → resultify. That's why its SmartAPI `operations` list
is unusually long (21 entries: `lookup`, `lookup_and_score`, the `overlay_*` family, the
`filter_kgraph_*` / `filter_results_*` family, `sort_results_*`, `bind`, `fill`, `score`,
`annotate_nodes`, `complete_results`) — those are ARAXi operations exposed as TRAPI workflow
operations, not separate endpoints.

The ARAXi reference is `code/ARAX/Documentation/DSL_Documentation.md`. The six core modules
are `ARAX_expander`, `ARAX_overlay`, `ARAX_filter_kg`, `ARAX_infer`, `ARAX_resultify`,
`ARAX_ranker` (described in [Bioinformatics 39(3) btad082](https://academic.oup.com/bioinformatics/article/39/3/btad082/7031241)).

## Deployed instances

### ITRB (the maturity ladder)

See the `component-maturity-levels` concept — and note ARAX's maturity naming is **derived at
runtime and does not match the domains**, see Gotchas.

| Maturity     | URL                                           |
| ------------ | --------------------------------------------- |
| `production` | `https://arax.transltr.io/api/arax/v1.4`      |
| `testing`    | `https://arax.test.transltr.io/api/arax/v1.4` |
| `staging`    | `https://arax.ci.transltr.io/api/arax/v1.4`   |

### Team-run "devareas" on `arax.ncats.io`

The team's own EC2 host runs **multiple independent ARAX endpoints out of one container**, each
a separate checkout under `/mnt/data/orangeboard/<devarea>/RTX` on its own branch, served by its
own `RTX_OpenAPI_<devarea>` service and its own `.elog`. Known devareas: `production`, `test`,
`beta`, `devED`, `devLM`, `legacy`, `shepherd`, plus retired ones (`dili`, `mvp`, `NewFmt`).
A Google Sheet linked from the wiki's *Dev-info* page tracks which endpoint runs which branch.

- `/beta` is the **shared human-testing devarea** — claim it on Slack `#deployment` first, and
  check `git status` shows clean-on-`master` before taking it (a dirty tree or a non-`master`
  branch means someone else is mid-test).
- `/legacy` runs **Legacy-ARAX at TRAPI 1.5.0**.

Jenkins dashboard for ITRB builds: `https://deploy.transltr.io/`.

## Data foundation — Tier0 now, KG2 historically

**This is the single most important thing to get right about current ARAX.** The team has moved
from RTX-KG2-versioned artifacts (`KG2.X.Y`) to the **Tier0 graph** (the Translator KG, KGX
format, distributed as `nodes.jsonl` / `edges.jsonl`), stamped `tier0-YYYYMMDD`. See the
`data-tiers` concept (via the `retriever` bundle) for the tier model itself.

Per-rollout artifacts, named `*_v1.0_tier0-MMDDYYYY.*` and listed under `database_downloads`
in `code/config_dbs.json`. Current build at time of writing: **`tier0-20260621`**
(`LATEST_TIER0_VER` in `code/generate-db-symlinks.sh`).

| `config_dbs.json` key          | Artifact                 | Purpose                                                    | Built by         |
| ------------------------------ | ------------------------ | ---------------------------------------------------------- | ---------------- |
| `curie_to_pmids`               | `curie_to_pmids`         | CURIE → PMIDs, feeds the NGD overlay                       | OSU              |
| `autocomplete`                 | `autocomplete`           | Term/CURIE list for UI autocomplete                        | OSU              |
| `tier0_sqlite` / `kg2c_sqlite` | `tier0-info-for-overlay` | Edge publications, neighbor counts, category counts        | OSU              |
| `curie_ngd`                    | `curie_ngd`              | Pre-computed NGD for CURIE pairs                           | **PSU** (Mohsen) |
| `explainable_dtd_db`           | `ExplainableDTD` (xDTD)  | Pre-computed drug-treats-disease probabilities + MOA paths | **PSU** (Chunyu) |
| `fda_approved_drugs`           | `fda_approved_drugs`     | Version-invariant; regenerate only on a new DrugBank       | —                |
| `cohd_database`                | `COHD_v1.0_KG2.8.0.db`   | Version-invariant; the KG2.8.0 stamp is historical         | —                |

**`tier0_sqlite` and `kg2c_sqlite` are two keys pointing at the same file** — a leftover of the
KG2→Tier0 rename, not two databases.

**Two of the artifacts are your lab's** (PSU): `curie_ngd` and xDTD. `curie_ngd`'s build docs live
in `Translator-CATRAX/pathfinder` (`build_model/db_build/README.md`) — so pathfinder is a
*build-tooling* dependency of ARAX as well as a runtime one. xDTD's pipeline is
`RTXteam/xDTD_training_pipeline`.

> **`gandalf_mmap` is gone.** It was historically a required PSU-built artifact (a memory-mapped
> tarball backing Gandalf lookups for Pathfinder), built via
> `Translator-CATRAX/pathfinder`'s `build_model/gandalf/README.md`. **It is no longer required at
> all** and has been fully removed: there is no `gandalf_mmap` key in `config_dbs.json`, no symlink
> in `generate-db-symlinks.sh`, and `get_gandalf_mmap_path()` no longer exists in
> `code/ARAX/ARAXQuery/Path_Finder/utility.py` (which now exposes only `get_kg2c_db_path`,
> `get_curie_ngd_path`, `get_curie_to_pmids_path`). **The wiki's Rollout Procedure still lists it
> as a build step and a Phase-2 checklist item — that page is stale on this point.** Drop it from
> any rollout checklist copied from the wiki, and treat a `gandalf_mmap` reference in older code,
> notes, or issues as historical.

Gandalf itself is still very much in play — just as a *service*, not an artifact: it backs the
Tier0 graph, `Overlay/fisher_exact_test.py` attributes to `infores:gandalf`, and `plover_url_override`
currently points ARAX at it (see below).

RTX-KG2 has **not** disappeared: it is separately registered (`infores:rtx-kg2`, KP, TRAPI 1.5,
`kg2cploverdb{,.test,.ci}.transltr.io`) and `RTXConfiguration` still selects a Plover URL by
matching KG2's SmartAPI `servers` on `x-maturity`, overridable via `plover_url_override` in
`config_dbs.json`. Expect **both vocabularies in the codebase at once** during the transition.

**Note `plover_url_override` is currently *set*, not null**, pointing at
`https://automat.renci.org/translatorkg-gandalf` — so master is deliberately bypassing the
SmartAPI-derived KG2 Plover URL and querying the Tier0/Gandalf graph via Automat. The wiki
instructs setting this slot back to `null` when done with a rollout; that guidance describes the
KG2-era temporary-override use, and does not mean the current value is a leftover. Confirm intent
before changing it.

Build inputs worth knowing: **Babel** (a ~233 GB local SQLite) has replaced external
name-resolution API calls in the NGD build, and a local **PubMed mirror** (~54 GB) feeds it.

## Running it locally

The wiki's **ARAX Maintenance SOP** (Ramsey, 2026-03-23) documents this properly; the procedure
below is condensed from it. `/run-target rtx` should still verify it end-to-end before anyone
leans on it.

### Prerequisites

- **python3.12** (production runs CPython 3.12 — avoid newer language features).
- **200 GiB free disk**, **32 GiB RAM** on the dev machine.
- `x86_64` and `ARM64` both work. **Not Windows** except under WSL/WSL2.
- `bash`, `curl`, OpenSSH, `git`, `jq`, `yq`; a mainstream browser.
- ssh access to `arax-databases.rtx.ai` (as `rtxconfig`) and `araxconfig.rtx.ai` (as `araxconfig`).
- VPN + IP-allowlist access for anything touching `arax.ncats.io` (it sits behind a bastion).

### Setup (once per database release, not per issue)

1. **Download the ARAX databases** to a persistent `DB_DIR` with `tier0-YYYYMMDD/` and `KG2.8.0/`
   subdirectories (the latter only holds the long-frozen COHD db). The authoritative list is
   whatever `code/generate-db-symlinks.sh` references — check it rather than trusting a snapshot.

2. **Install `generate-db-symlinks.sh`** into your dev dir and **edit its hardcoded
   `DB_DIR="/mnt/data/orangeboard/databases"`** to your local path.

3. **Write a `flask_config.json`** — this is what makes a local run feasible:

   ```json
   {
       "port": 5001,
       "check_databases": false,
       "run_background_tasker": false,
       "force_disable_telemetry": true,
       "query_fork_mode": false
   }
   ```

   Full schema in the wiki's *Config, databases, and SFTP* page. Defaults if the file is absent:
   port 5000, and `check_databases` / `run_background_tasker` / `query_fork_mode` all **true** —
   i.e. a default local start will try to download databases, fork a background tasker, and fork
   per query. Turn all three off for dev. A malformed `flask_config.json` raises at startup; an
   absent one is handled gracefully.

### Per-issue setup

```bash
cd ARAX_DEV_DIR
mkdir issue-XXX && cd issue-XXX
git clone -b issue-XXX git@github.com:RTXteam/RTX.git
python3.12 -m venv venv
venv/bin/pip install -r RTX/requirements.txt
venv/bin/pip install -r RTX/dev-requirements.txt
../generate-db-symlinks.sh          # run from inside issue-XXX
cp ../flask_config.json RTX/code/UI/OpenAPI/python-flask-server/openapi_server/
cd RTX/code && ../../venv/bin/python -u -m ARAX.ARAXQuery.Expand.kp_info_cacher
```

The last command builds the KP info cache and should end with
`The process with process ID NNNNN has FINISHED refreshing the KP info caches`.

### Run

```bash
cd ARAX_DEV_DIR/issue-XXX/RTX/code/UI/OpenAPI/python-flask-server
../../../../../venv/bin/python -u -m openapi_server
```

Serves on the `flask_config.json` port (5001 by convention; 5000 default; various `arax.ncats.io`
devareas use others, e.g. 5003 for `/beta`). If 5001 is taken (`netstat -an | grep tcp | grep ':5001'`),
pick another.

### Verify

Open `code/UI/interactive/index.html` as a **file** in the browser, dismiss the expected
"Call to /meta_knowledge_graph failed" banner, then in *Settings* set **ARAX QUERY URL** to
`http://localhost:5001/api/arax/v1.4/query`. Run **Example 1, 2, 3, and Pathfinder** and compare
against `arax.ncats.io/test` or `arax.ci.transltr.io`. Results needn't match exactly; *major*
differences mean you aren't starting from a known-good baseline.

One TRAPI warning is expected locally and harmless:
`Not saving response to S3 because I don't know the S3BucketMigrationDatetime`. Any *other*
warning/error is worth diffing against a `master` run.

Working over port-forwarding may need
`sed -i 's/window\.location\.hostname/window.location.host/g' RTX/code/UI/interactive/rtx.js`.

### Common tasks

- **Tests:** `pytest.ini` sets `testpaths = code/ARAX/test`. Run from the **repo root**
  (`../../../venv/bin/pytest -v`), *not* from `code/` — pytest will otherwise pick up
  `UI/OpenAPI/python-flask-server/openapi_server/test`. Takes ~15 minutes.
  Flags: `--runslow`, `--runexternal`; `pytest -v --runslow --runexternal` runs everything.
  Running pytest **auto-updates databases and the KP info cache**, so you don't do that by hand.
  Avoid `pytest --lf`.
- **Static checks — required before committing**, per module you touched:
  `ruff check foo.py`, `mypy --ignore-missing-imports foo.py`, `pylint foo.py`.
  No `ruff`/`mypy` errors; **pylint ≥ 9.50**. Run them *before* you start editing too, to get a
  baseline. Syntax-check edited JSON/YAML with `jq`/`yq`.
- **Behave tests:** `tests/run-rtx-behave-tests.sh`.
- **OpenAPI model regeneration:** `openapi-generator-cli generate -i …/openapi.yaml -g python-flask -o python-flask-server --global-property models,apis` from `code/UI/OpenAPI`.

### External deps

Resolved through `code/RTXConfiguration.py` + `code/config_dbs.json` (override keys
`plover_url_override`, `node_normalizer_url_override`, `name_resolver_url_override`, `neo4j`):

- **Plover / RTX-KG2** — primary KP; URL picked by `x-maturity` match against KG2's SmartAPI reg.
- **Node Normalizer** / **Name Resolver** (SRI utilities); **Babel** in the build path.
- **Retriever** — reached by the xCRG path, keyed by maturity.
- **Neo4j**, **MySQL**, and local SQLite caches. In production Neo4j inside the container is
  described as a *legacy* dependency; most Neo4j use is a separately hosted server.
- **Jaeger / OpenTelemetry** — mandatory Translator telemetry. ITRB instances report to
  `jaeger-otel-agent.sri`; team instances to `jaeger.rtx.ai`. Locally, set
  `"force_disable_telemetry": true`.

### Config & secrets

- **`config_secrets.json`** — never in the repo. Auto-downloaded (~every 24 h) from the master copy
  at `araxconfig@araxconfig.rtx.ai:/home/araxconfig/config_secrets.json`; your public RSA key must
  be in that host's `authorized_keys`. Override locally with
  `RTX/code/config_secrets_local.json`, which always wins if present. **Never commit or share it.**

- **`config_dbs.json`** — in-repo; database versions/paths + Plover/KG2 endpoints.

- **`flask_config.json`** — local server behavior (above).

- **`maturity_override.txt`** — one line, in `RTX/code/`, forces a maturity. Delete when done.

- Deployment secrets live under `deploy/arax/secrets/` (Helm). Never copy values into this bundle.

- Env vars read by the xCRG path:

  ```bash
  ARAX_XCRG_RETRIEVER_URL=<override the maturity-derived Retriever /query URL>
  ARAX_XCRG_TIMEOUT=<seconds; default 210>
  ARAX_XCRG_TF_BATCH_SIZE=<batch size>
  ```

## Dev workflow & conventions

Condensed from the wiki's **ARAX Maintenance SOP** and **Coding guidelines** — follow those pages
for the authoritative version.

- **Branch per issue: `issue-XXX`, off `master`.** Commit messages tag the issue (`#XXX`) and stay
  under ~70 chars. Never commit to `master` directly during issue work.
- **`production` and `itrb-test` are never committed to** (save ITRB-specific changes); `master`
  merges *into* them, never the reverse.
- **Bring a stale branch up to date with `git rebase origin/master`**, not a merge, to avoid
  dragging `master`'s commit messages in.
- **Never use GitHub's web merge-conflict tool to merge `master` into an issue branch** — it only
  modifies the parent branch, which silently does the wrong thing in that direction.
- **`/deploy` on a PR** builds an isolated preview on `cicd.rtx.ai` and reports smoke checks,
  pytest results, and the four example queries against the live endpoint. `/redeploy` after a
  code-only push (~1 min), `/undeploy` to tear down. Dashboard: `https://cicd.rtx.ai/previews/`.
  Repo members only, no forks, branch must be reasonably current with `master` or it refuses.
  **This is the modern alternative to claiming the shared `/beta` devarea.**
- Assign **Copilot** as a PR reviewer; the guidelines also ask for an LLM review of diffs in the
  context of the full code-base before committing.
- **Merging to `master` auto-deploys to `arax.ci.transltr.io` in ~10 minutes** (ITRB). Verify there
  after merge; if it's not back in 15 min, ask on `#deployment`. If a database changed, allow up
  to ~an hour for the rebuild to pull it.
- Mark temporary debugging lines with `# :DEBUG:` so they can't leak into a commit.
- Modern type hints (3.10+): lowercase `dict`/`list`, `| None` not `Optional`. PEP8; 4 spaces, no
  hard tabs, LF only; ≤120 chars (79 is the standard but treated as unreasonably short).
- **New PyPI dep → pin it in `requirements.txt`** (or `dev-requirements.txt` for tooling) and test
  the install. **No secrets in the repo, ever.**
- **Avoid lazy imports** (ARAX is multithreaded; lazy import + circular imports = race conditions —
  see issue #2788) and minimize `sys.path` surgery.
- **Performance rules — nothing slow at query time:** no YAML/large-JSON parsing, no config reads,
  no `scp`, no un-slept polling loops, no cross-AWS-region DB queries, no database manager, no
  `kp_info_cacher.refresh_kp_info_caches` (Background Tasker only).
- **Closing an issue** also means: note it in the ARAX ChangeLog issue (#2515), add an agenda item
  for the ARAX all-hands, log it against a milestone in `Translator-CATRAX/Y2-CATRAX-Milestones-Repo`,
  and comment on the parent issue (see below).

### Cross-linking `NCATSTranslator/Feedback` → `RTXteam/RTX`

Roughly a third of ARAX issues have a **parent issue** in another tracker — usually
`NCATSTranslator/Feedback`, from something seen in the Translator UI. The SOP requires the two
issues to **reciprocally hyperlink**: the RTX issue points at the parent ("cross-post status
updates in the parent issue here:"), and the parent points at the RTX issue ("ARAX team is working
on this; for the latest status, check here:"). When the fix merges, comment on the parent so its
stakeholders (e.g. the TAQA team) can re-run their reproducible example.

*Directly relevant to triage from `feedback`, which is the default issue source.*

### What a good ARAX bug report contains

The SOP's stated expectations — useful both when filing and when judging whether a report is
actionable:

- The **query graph JSON or ARAXi/DSL verbatim** (pasted into the issue — this is called "vital",
  because without it the maintainer can't confirm they reproduced the bug).
- The **ARAX host** the query ran against.
- The **date/time with timezone**.
- The relevant excerpt from `/tmp/RTX_OpenAPI_<devarea>.elog`, if available.
- Screenshots from the UI and excerpts of the TRAPI message log.

## Rollout (Tier0)

A full Tier0 rollout is an 8-phase procedure documented on the wiki's **Rollout Procedure** page,
driven from a kickoff issue ("Attempt to build ARAX Tier0-MMDDYYYY") with a copy-pasteable
checklist. Shape:

1. Kickoff issue + `issue-XXXX` branch → 2. build the per-rollout artifacts → 3. integrate
   (`config_dbs.json`, `ARAX_database_manager.py`, `LATEST_TIER0_VER` in `generate-db-symlinks.sh`,
   OpenAPI version bumps) → 4. test on dev + CI → 5. stage artifacts to four servers → 6. **tag
   `master` with the previous Tier0 stamp** (the rollback anchor) then merge → 7. progressive
   production rollout → 8. cleanup after a one-week stability window.

Merge concurrence is sought from **@hodgesf, @bazarkua, @saramsey, @dkoslicki, @edeutsch** — you
are on that list.

Staging targets: `arax-databases.rtx.ai` (`/home/rtxconfig/tier0-MMDDYYYY/`), `arax.ncats.io`,
ITRB SFTP (`sftp.transltr.io`, **file + its `.md5`**), and `cicd.rtx.ai`. Require ≥100 GB free on
the first two before starting, and **always leave at least one legacy endpoint on the previous
build** for a week.

**Ordering trap:** a `config_dbs.json` change in `master` that points at a database not yet present
on *both* `arax-databases.rtx.ai` and the ITRB SFTP server **will break things**. Upload first,
point second.

**The wiki's checklist is one item out of date:** it still includes "gandalf_mmap tarball refresh
work. Work with PSU team on this." and a corresponding Phase-2 build section. **That artifact has
been removed and is no longer required** — skip it when copying the checklist into a kickoff issue
(see the Tier0 artifact table above).

## Operations & triage aids

Quick things worth reaching for during an investigation:

- **Pull an ITRB instance's log** — there's an API endpoint for it, no ssh needed:
  ```bash
  wget -O log.txt https://arax.ci.transltr.io/api/arax/v1.4/status/logs
  ```
- **Ask a running ARAX which KG version it loaded** — post this query graph and read the single
  result's title (e.g. "RTX-KG2.10.0c"):
  ```json
  {"nodes": {"n00": {"ids": ["RTX:KG2c"]}}, "edges": {}}
  ```
- **Per-devarea logs** live at `/tmp/RTX_OpenAPI_<devarea>.elog` inside the container. Startup is
  complete when you see `ARAXBackgroundTasker: Completed meta KG refresh successfully`.
- **Flaky/stubborn local test failures** — delete the TRAPI query cache and re-run:
  ```bash
  rm RTX/code/ARAX/ARAXQuery/Expand/trapi_query_cacher_database.sqlite
  rm -rf RTX/code/ARAX/ARAXQuery/Expand/trapi_query_cacher_responses/
  ```
- **`Unable to store response record in MySQL`** in the ARAX log, recurring and multi-user, points
  at the central response database on `arax-responses.rtx.ai` (EC2, `us-east-1`) being down rather
  than at a query-level bug.
- Service management inside the container uses `service RTX_OpenAPI_<devarea> …` — **never** the
  init script directly (`/etc/init.d/…`), which causes issue #2350.

Key hosts: `arax.ncats.io` (team endpoints, bastion + IP allowlist), `arax-databases.rtx.ai`
(artifacts, user `rtxconfig`), `araxconfig.rtx.ai` (secrets), `cicd.rtx.ai` (CI + PR previews),
`ngdbuild2.rtx.ai` (NGD builds), `arax-responses.rtx.ai` (response DB), `jaeger.rtx.ai`
(telemetry), `buildkg2.rtx.ai` (KG2 builds).

Slack: `#deployment` (announce before touching a shared devarea or merging), `#outages` in the
`NCATSTranslator` workspace for CI-affecting merges, `#devops-teamexpanderagent` for ITRB.

## Gotchas & notes

- **Maturity is auto-detected, not configured** (`code/RTXConfiguration.py:88-113`), and **the
  names don't match the domains**: `arax.ci.transltr.io` → **`staging`**,
  `arax.test.transltr.io` → `testing`, `arax.transltr.io` → `production`, everything else →
  `development` (instance name `ARAX`/`kg2` or branch `production` forces `staging`; branch
  `itrb-test` → `testing`). `maturity_override.txt` short-circuits all of it. **So "CI" in the URL
  means `staging` in ARAX's own vocabulary** — a trap when cross-referencing the
  `component-maturity-levels` concept or targeting with `tt -e`. The wiki itself calls the ITRB CI
  instance "ITRB CI/staging", confirming the two names are the same thing.

- **Two of the dev's other purview repos are compiled into ARAX as pinned dependencies** —
  `code/ARAX/ARAXQuery/ARAX_connect.py:6-7` does
  `from pathfinder.Pathfinder import Pathfinder` and `from xcrg import XCRGConfig, run_xcrg`.
  In `requirements.txt`:

  - `catrax-pathfinder==2.4.3` — PyPI, pinned version. (Also constrains `bmt==1.4.8`.)
  - `catrax-xcrg @ git+https://github.com/Translator-CATRAX/xCRG.git@c97da53…` — pinned to a
    **git SHA**, not a release.

  **Consequence:** the pinned revision — not upstream `main` — is what ARAX executes. When an ARAX
  bug traces into either package, read the pinned revision before reasoning about the code.

  **For xCRG this gap is large and expected.** xCRG is never deployed on its own; shipping inside
  ARAX *is* its release mechanism, so the SHA pin is by design. As of 2026-08-31 `main` carries a
  **second iteration of xCRG still in progress** (a typing refactor, a module split, a new ranking
  method, and the whole test harness — `49 files changed, +7170/-2849` past the pin), not yet ready
  for deployment. So `repos/xCRG` on `main` shows the *next* xCRG, not the deployed one — read
  `c97da53` for production behavior. This is a work-in-progress branch, **not a stale pin to bump**.
  See `components/xcrg/definition.md`.

- **xCRG has two paths, and the legacy one is dead weight.** `RTXConfiguration.py:181-193` still
  computes model/embedding paths for the old `creativeCRG` code, but the comment states the
  current `connect(action=xcrg)` path is **model-free**. The new path calls **Retriever** at
  `retriever.{ci,test,}.transltr.io/query` selected by maturity (`ARAX_connect.py:41-46`; note
  `development` also points at the **ci** host). The ML training story in
  `code/ARAX/ARAXQuery/Infer/README.md` (GraphSage embeddings + Random Forest on KG2.8.0c)
  describes the **legacy** models — don't read it as current behavior.

- **Pathfinder is both internal and external.** There's an in-repo
  `code/ARAX/ARAXQuery/Path_Finder/` (utility resolving the kg2c / curie_ngd / curie_to_pmids db
  paths) *and* the external `catrax-pathfinder` package. They're distinct; `ARAX_connect.py` uses
  both. The in-repo utility previously also resolved a `gandalf_mmap` path; that function is gone.

- **`kind: ara` is clean here** — ARAX registers as ARA and behaves as one. But a **separate**
  SmartAPI registration exists: `infores:shepherd-arax` ("Shepherd-arax", ARA, TRAPI **1.5.0**) —
  ARAX fronted by the Shepherd platform. Different infores, different TRAPI version; don't
  conflate it with `infores:arax` when reading ARS child messages (pk-inspector shows children
  like `ara-shepherd-arax`). Note the team also runs a `shepherd` devarea and a `/legacy` devarea
  at TRAPI 1.5.0 — **there is more than one 1.5.0-era ARAX in play**, so pin down *which* endpoint
  a report came from before reasoning about version-specific behavior.

- **Legacy-ARAX needs a source edit, not a config flag.** To work on `/legacy` (TRAPI 1.5.0) you
  change `self.forced_kp_version = '1.6.0'` → `'1.5.0'` in
  `code/ARAX/ARAXQuery/Expand/kp_info_cacher.py`. The SOP warns explicitly not to commit that
  change — so **treat a `forced_kp_version` diff in any branch as an accidental leak**, not a fix.

- **The `config_dbs.json` paths are deliberately wrong.** Its root
  (`/translator/data/orangeboard/databases/`) is a legacy location; the real root on
  `arax-databases.rtx.ai` is `/home/rtxconfig/`. `RTXConfiguration` maps between them because ITRB
  couldn't adjust their scripts. The wiki's own words: "It's silly, but it works." Don't "fix" it.

- **The README's branch guidance is stale.** It says the most up-to-date branch is `demo` —
  **no `demo` branch exists** on the remote. Actual long-lived branches: `master` (default, and
  where recent work lands), `production`, `dev`. The wiki's *ARAX-Home* page links to
  `blob/demo/README.md`, which is likewise dead.

- **URLs say `/v1.4` on every instance despite TRAPI 1.6** — a frozen path prefix, not a version
  signal. Don't infer TRAPI version from the URL. (Some in-repo spec paths still say `1.5.0` too.)

- **Container name is inconsistent across the wiki** — older pages say `rtx1`, newer ones `rtx2`,
  and the Rollout page mixes both. Run `sudo docker ps -a` rather than trusting either.

- **CI database downloads are semi-manual.** The self-hosted runner on `cicd.rtx.ai` is documented
  as *not* reliably auto-downloading databases (issue #1914); after `config_dbs.json` changes in
  `master` someone runs
  `python3 code/ARAX/ARAXQuery/ARAX_database_manager.py --mnt --skip-if-exists --remove_unused`
  there by hand. A red "Test Build" badge may mean this, not a code regression.

- **Team/naming drift:** the team is "Expander Agent" in SmartAPI and the README, "CATRAX" in the
  newer wiki pages, org `Translator-CATRAX` on GitHub. The wiki names both an `ARAXTeam` Slack
  workspace and a `CATRAX` Slack workspace as the home of `#deployment` — verify which is current
  before posting. Similarly the SFTP host appears as both `sftp.transltr.io` (usual) and
  `sftp.ncats.io` (once, in the Rollout prerequisites) — `sftp.transltr.io` is the one used in
  every actual command.

- **Generic-term blocklist** for filtering overly general concepts lives in
  `code/ARAX/KnowledgeSources/general_concepts.json` — three mechanisms: `curie` (lowercase;
  equivalent CURIEs filtered automatically), `synonyms` (case-insensitive strings), and `patterns`
  (Python regexes). Relevant when a report says "why is this generic node in my results".

- **Response logging paradigm:** every major method takes or creates an `ARAXResponse`, logs via
  `.debug/.info/.warning/.error`, puts data in `response.data`, and returns it; callers merge and
  check `.status`. Severity contract: DEBUG = team-only, INFO = innocuous assumptions users might
  want, WARNING = assumptions with impact, ERROR = request-preventing failure (which does **not**
  necessarily halt processing — several can accumulate).

- No `CODEOWNERS` file. `owner` above is the PI list from the README. Most active committers over
  the last two years: Stephen Ramsey, Eric Deutsch, Adilbek Bazarkulov, Mohsen Taheri, Amy Glen,
  Chunyu Ma. Access notes from the wiki: `arax.ncats.io` access is limited (named: Amy, Steve,
  Eric); `arax-databases.rtx.ai` needs a key added by a team member.

- MIT licensed. Zenodo DOI badge in the README. RTX-KG2 public build artifacts:
  `https://rtx-kg2-public.s3.us-west-2.amazonaws.com/index.html`.

## Wiki map & what's stale

`https://github.com/RTXteam/RTX/wiki/` — 15 pages. Current and worth reading:

| Page                               | What it covers                                                                                                                                |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **ARAX Maintenance SOP**           | The per-issue procedure end to end. Dated 2026-03-23 (Ramsey). Most current page.                                                             |
| **Rollout Procedure**              | Tier0 rollout, 8 phases + rollback + copy-pasteable checklist. **Stale on one point: it still requires the removed `gandalf_mmap` artifact.** |
| **Config, databases, and SFTP**    | `flask_config.json` schema, the three config files, DB update + SFTP steps.                                                                   |
| **Dev-info**                       | Branching/merging, PR handling, testing, instance list, config files.                                                                         |
| **Coding guidelines**              | Style, typing, performance rules, dependency policy.                                                                                          |
| **Operations & deployment info**   | Restart/recovery runbooks, `/status/logs`, telemetry, response DB. Self-described as "a draft… not complete".                                 |
| **CI system (via GitHub actions)** | The `cicd.rtx.ai` self-hosted runner.                                                                                                         |
| **Docker Deployment, ARAX**        | Image build + container layout + nginx config.                                                                                                |

**Treat as stale — do not follow:**

- **`xx-Deployment-info---OLD`** — self-marked out of date at the top. Ubuntu 18.04/16.04, Flask
  1.1.2, python 3.7, `KG2.3.4` paths. Superseded by *Docker Deployment* and *Operations*.
- **`Things-to-Be-Updated-for-A-New-Release-of-ARAX`** — authored 2023-12-20 (Chunyu Ma) and
  entirely **KG2-era**: `KG###` artifact naming, the `kg2rollout.md` template, xDTD via
  `config.yaml`. **Superseded by the Tier0 *Rollout Procedure*.** Still useful for *who owns what*
  and for xDTD build background (~3 weeks: 1 week training, 2 weeks pre-computation, needs GPUs).
- **`Updating TRAPI Workflow Operations`** — references `RTX_OA3_TRAPI1.2_ARAX.yaml` and a
  `devED`-specific `replaceall.pl` step. TRAPI 1.2-era mechanics; the intent still applies but the
  filenames don't.
- **`Dev-info` → "Old or infrequently used info"** — explicitly flagged in-page.
- **`Error messages and what they mean`** — a single COHD entry; effectively a stub.
- **`ARAX-Home`** — links to `blob/demo/README.md` (branch no longer exists) and describes ARAX as
  "an early alpha version".
- `Home` / `RTX-Home` are navigation stubs.
