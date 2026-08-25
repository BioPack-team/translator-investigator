---
name: query-resolution-modes
aka:
  - lookup
  - creative
  - magic
  - inferred mode
  - inferred
  - pathfinder
  - set-input
  - set_interpretation
  - knowledge_type inferred
domain: [TRAPI, reasoning]
see_also: [subclassing]
curation: canonical
---

# Query resolution modes

A query resolution mode is an **instruction to the server for _how_ to answer a query** — not just
*what* is asked. TRAPI is the language for both communicating queries/answers **and** signaling the
mode; the mode itself tells the server what kind of answering behavior to apply.

## The lookup → creative axis

Modes sit on an axis from plain **lookup** to increasingly **creative** ("magic") answering:

- **lookup** (the default, non-creative end) — find subgraphs that match the query graph, plus only
  **very simplistic logical entailment** (e.g. **OBI / subclassing — which happens _inside_
  lookup**; see the `subclassing` concept). No "intelligent" inference: just get the matching data
  and return it.
- Toward the **creative** end are several **distinct modes**, each a different creative behavior:
  - **inferred mode** — the specific mode for a **one-hop query whose edge is
    `knowledge_type: inferred`**: the server does inference to answer *that one-hop style* (e.g.
    instead of a direct `thing --treats--> disease` lookup, find multi-hop pathways — mechanism of
    action, etc. — that let it *infer* `treats`). **How** it is creative is up to the server's
    implementation. ("Inferred mode" names **this** mode specifically — it is **not** a synonym for
    "creative" in general.)
  - **pathfinder** — the query uses TRAPI **qpaths** (in place of qedges): two pinned nodes, and the
    server finds valuable arbitrary **multi-hop paths** between them under constraints.
  - **set-input** — uses TRAPI **`set_interpretation`** to ask questions about **sets** of nodes.
    set-interpretation can be handled **naively** (lookup-side) or more **creatively** by servers
    whose nature suits it.

## How a mode is signaled / advertised

- **Signaled per query** by TRAPI structure: lookup = default; inferred = `knowledge_type: inferred`
  on a one-hop edge; pathfinder = qpaths; set-input = `set_interpretation` on qnodes.
- **Advertised per server** via a mix of its **SmartAPI** registration and its
  **`/meta_knowledge_graph`** endpoint (which modes/operations it serves).

## Hierarchy — and why it matters

Modes compose **hierarchically**: a server doing a creative mode typically **farms lookup out** to
another service — e.g. **shepherd / aragorn does inferred mode and gets its lookups from Retriever**.
All modes are in play across Translator, but **a given component serves only some** (e.g.
**Retriever is lookup-only**).

So an investigation must know **which mode a query ran in** and **which modes the component covers**,
or it will **mis-triage**: e.g. don't fault Retriever for missing *inferred*-mode answers — Retriever
only does lookup; the inference lives upstream in the ARA. Matching the observed behavior to the
right layer of the hierarchy is what points the investigation at the right component.
