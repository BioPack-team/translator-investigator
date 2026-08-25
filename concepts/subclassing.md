---
name: subclassing
aka:
  - OBI
  - Ontology-Based Inference
  - OBIE
  - Ontology-Based Inference Engine
  - infores:obie
  - ISR
  - implicit subclass reasoning
  - implicit subclassing
  - subclass reasoning
  - subclass expansion
  - subclass rollup
  - subclass_of
  - logical_entailment construct edge
  - implicit_subclassing
domain: [TRAPI, lookup, reasoning]
see_also: [query-resolution-modes]
curation: canonical
---

# Subclassing / OBI — Ontology-Based Inference

> **Terminology.** Prefer **OBI** ("Ontology-Based Inference") over **ISR** ("implicit subclass
> reasoning") — semantically equivalent, but OBI also points at **OBIE**, the Ontology-Based
> Inference *Engine* whose infores (`infores:obie`) tags these edges. **One concept, not two:**
> there is no "explicit" subclassing to contrast against — "implicit" survives only because some
> components' code/config/logs use `implicit_subclassing`.

## What it is

A query pinned to a **general** term should also be satisfied by knowledge about its **ontological
subclasses (descendants)**, rolled up to the parent. E.g. "what treats diabetes mellitus
(`MONDO:0005015`)?" should surface a drug that treats *type 2 diabetes* (a subclass), presented as
an answer about the parent. It turns a single-term lookup into a lookup over the term *and its
descendants*.

## How it appears in TRAPI

OBI is expressed as a small, recognizable structure — the same shape regardless of which component
produced it:

- a **subclass edge**: `descendant --biolink:subclass_of--> parent` (primary knowledge source
  typically `infores:ubergraph`);
- a **support / auxiliary graph** justifying the parent-level answer = { the base edge on the
  *descendant*, the subclass edge };
- a **construct edge** bound at the *parent* term, carrying `knowledge_level: logical_entailment`
  and `agent_type: automated_agent`, with a `biolink:support_graphs` attribute pointing at that
  support graph.

**`infores:obie` on a construct edge is the marker that it came from OBI** (rather than a plain
lookup). The base premise edge keeps its own KP provenance; only the parent-level inference is
attributed to the engine.

## Where it happens

OBI can be performed **natively by a backend** (an engine that reasons over ontology subclasses as
part of answering) or **orchestrated by an aggregator** on behalf of backends that can't multi-hop
(build a parent→descendants map, expand pinned terms, then synthesize the subclass + construct
edges). The **TRAPI shape above is identical either way**; what differs is provenance and where the
logs live. OBI is **not** a resolution *mode* — it's a type of logical entailment a lookup must
handle: more involved than a bare subgraph match, but nothing "creative," living **entirely within
lookup**. See the `query-resolution-modes` concept. (A given aggregator's tier/backend split — e.g. retriever's data
tiers — is a component-specific detail; it lives in that component's bundle concepts.)

> Component-specific mechanics (e.g. a given aggregator's subclass-map / expansion / reformat
> pipeline, its config flags and code paths) belong in that component's bundle concepts, not here —
> this concept stays implementation-agnostic.

## Why it matters

`infores:obie` provenance on an edge is the tell that it's an OBI construct edge, not a plain
lookup. So a difference in subclass-derived aux graphs **across backends** points at that backend's
native reasoning (or its underlying data) — not at an aggregator's orchestration. Getting this
straight is what lets an investigation localize a subclass-rollup discrepancy to the right
component.
