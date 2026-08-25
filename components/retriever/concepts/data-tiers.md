---
name: data-tiers
aka:
  - tier0
  - tier1
  - tier2
  - Tier 0
  - Tier 1
  - Tier 2
  - Gandalf
  - data tier
  - data tiers
  - CSR graph
domain: [retriever, TRAPI]
see_also: [subclassing, query-resolution-modes]
curation: canonical
---

# Data tiers (retriever: Tier 0 / Tier 1 / Tier 2)

Retriever's model for **categories of knowledge source**. A *tier* is the category/level; each tier
is served by one or more **backends** (the concrete store + interface behind it). Retriever consults
the tiers and aggregates/validates the results.

- **Tier 0 — backend: Gandalf.** A bespoke graph DB using a **CSR** (compressed sparse row)
  representation (not Neo4j), accessed over an HTTP driver. Source:
  [`ranking-agent/gandalf`](https://github.com/ranking-agent/gandalf).
- **Tier 1 — backend: Elasticsearch.** Reaching the backend **directly** (a locally-run Retriever)
  needs VPN the other tiers may not — but *using* Tier 1 via a **live Retriever instance** does not
  (it fronts the backend over TRAPI, plain HTTP; see the retriever bundle's "Running it locally →
  External deps").
- **Tier 2 — (future) a multi-backend tier.** A driver/transpiler allowing several backends, each
  speaking a different interface/query language. Not yet in play.

Dispatch maps each tier → a driver + query type (`src/retriever/data_tiers/tier_manager.py`); Tier 0
lives under `src/retriever/data_tiers/tier_0/gandalf/`.

## Query handling differs by tier

Tier 1/2 backends **can't do multi-hop querying**, so retriever's **QGX** orchestrates traversal +
subclassing (OBI) for them. A **Tier 0** query is handed off **wholesale to Gandalf**, which does
multi-hop + subclass reasoning **natively** — and whose internal logs retriever does not surface
(so an absence of expansion/subclass logs at Tier 0 is expected). See `subclassing` and the
retriever `qgx` concept.

## Data-parity expectation

Tiers 0 and 1 are expected to hold the **same underlying data** — if one tier can produce an answer,
the other should too. Minor differences from traversal-logic variation are tolerable but
**anomalous** and worth flagging; a genuine difference in *which answers* a tier returns (not just
formatting) is a bug to chase, not expected behavior.

## Why it matters

Many retriever issues are tier-specific ("Tier 1 vs Tier 0 mismatch", "Tier 1 key error"). Knowing
which tier — and thus which backend — is implicated narrows where to look, and whether the failure
is a backend/network problem vs a retriever bug.
