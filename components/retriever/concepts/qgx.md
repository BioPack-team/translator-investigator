---
name: qgx
aka:
  - QGX
  - qgx
  - QueryGraphExecutor
  - Query Graph eXecution
  - query graph execution
  - query graph executor
domain: [retriever]
see_also: [data-tiers, subclassing]
curation: canonical
---

# QGX — Query Graph eXecution (retriever lookup)

QGX is retriever's per-tier **lookup execution** algorithm — the class `QueryGraphExecutor`
in `src/retriever/lookup/qgx.py`. Given a query graph + a target tier, it traverses the graph
with an async "branch / superposition" approach, dispatches subqueries to the tier backend,
reconciles partial results, and assembles the KG / results / aux graphs.

## Scope — Tier 1/2 only (Tier 0 bypasses QGX)

QGX exists to drive **Tier 1 / Tier 2**, whose backends **can't do multi-hop querying** — so
QGX performs the multi-hop traversal *and* implicit subclass handling on their behalf. A
**Tier 0** query is instead handed off **wholesale to Gandalf**, which does its own multi-hop +
subclass reasoning natively; **QGX's subclass expansion does not apply to Tier 0**. (See
`data-tiers`, `subclassing`.)

## Subclass handling within QGX (Tier 1/2)

- `expand_initial_subclasses()` / `expand_subclasses()` (`qgx.py`) add each pinned node's
  descendants (from the subclass map) to the query and record `subclass_backmap`
  (descendant → parent).
- `solve_subclass_edges()` (`subclass_format.py`, called from `qgx.py`) rewrites
  subclass-derived matches into construct edges + support/aux graphs. See `subclassing`.

## Why it matters

QGX is the boundary between "retriever did the reasoning" and "the backend did the reasoning."
Because Tier 1/2 go through QGX (retriever's own traversal + subclass expansion) while Tier 0
delegates wholesale to Gandalf, a **Tier 0 vs Tier 1 discrepancy** (e.g. different aux graphs or
subclass edges) usually pins to the *backend that produced it* — Gandalf for Tier 0 — rather
than to a single shared retriever code path. Knowing which tier ran tells you which engine to
suspect.
