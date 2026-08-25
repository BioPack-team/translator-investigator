---
name: reasoner-api
org: NCATSTranslator
repo: ReasonerAPI
status: active
curation: canonical
provides: secondary reference — how a TRAPI API should behave (concept + implementation guidance), complementing TOM
---

# reasoner-api (ReasonerAPI — the TRAPI standard)

## What it provides

The TRAPI standard repo. As a **tool it's secondary reference material** — it explains **how a TRAPI
API should behave** (semantics + implementation guidance), which the schema alone doesn't convey.
Pair it with **`translator-tom`**: TOM for structure / validation / manipulation; ReasonerAPI for
**intended behavior and semantics**. It ships **no meaningful scripts** — it's read, not run.

## TRAPI version → branch (important)

ReasonerAPI's guidance is **per-branch by TRAPI version** — branches `1.4` / `1.5` / `1.6` / `2.0`
(and `master` = latest/working). The specs and docs differ meaningfully across versions, so **check
out the branch matching the component you're investigating** before reading:

```bash
# clone if absent (normally done on enable): gh repo clone NCATSTranslator/ReasonerAPI repos/ReasonerAPI
git -C repos/ReasonerAPI checkout 1.6   # match the component's `trapi_version` (most are 1.6)
```

Reading `master` (or the wrong version) gives guidance that may not match the component's actual
behavior. **Note:** `checkout` switches the **whole clone's** branch (stateful) — if you're juggling
components on different TRAPI versions, switch back when done rather than leaving the tree on a stale
branch.

## Where the useful content is (cloned into `repos/ReasonerAPI/`)

- **`ImplementationGuidance/Specifications/`** — the core: behavioral/semantic specs —
  `knowledge_level_agent_type`, `retrieval_provenance`, `binding_structure`,
  `supporting_publications`, `qualifier_rules_and_examples`, `qedge_constraints`, `query`,
  `pathfinder_query`.
- **`ImplementationGuidance/MigrationGuides/`** — 1.4 / 2.0 migration + implementation guides.
- **`ImplementationGuidance/DataExamples/`** — annotated example TRAPI responses.
- **`docs/reference.md`** — human-readable request/response structure. README — overview + a worked
  example.

**Ignore `TranslatorReasonerAPI.yaml`** (the OpenAPI schema) — use TOM for structure/validation.
(Default branch is `master`.)

## Using it

Read it as **secondary reference** when you need to understand *intended TRAPI behavior/semantics* —
e.g. what `knowledge_level` / `agent_type` mean, how provenance / retrieval sources should be
structured, qualifier rules, binding structure. Not for schema/validation (→ TOM).
