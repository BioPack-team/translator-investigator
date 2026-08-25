---
name: translator-tom
org: NCATSTranslator
repo: TRAPIObjectModeling
status: active
curation: canonical
default_enabled: true   # core TRAPI tooling — onboard pre-selects it (dev can opt out)
provides: TRAPI object models (1.6 + 2.0) for structural validation, manipulation, and a self-documenting spec reference
---

# translator-tom (TOM — TRAPI Object Modeling)

## What it provides

A performant Python data model + centralized utilities for the Translator Reasoner API (TRAPI).
Ships **both TRAPI 1.6 and TRAPI 2.0** models, each in **two representations**:

- **Pydantic models** — deserialize with validation, serialize, statically-typed construction, plus
  utility methods for **standard TRAPI manipulation** (message/result/KG merging, `.new()` with
  sensible defaults, `.<field>_list` / `.<field>_dict` accessors that avoid None-guarding). Finer
  validation + cleaner ergonomics.
- **model_dicts** (`TypedDict`) — the same shapes without class-instantiation overhead (higher
  performance, lower memory), at the cost of some verbosity. **Don't validate by default.**

Reach for TOM whenever constructing, validating, reconstructing, comparing, or manipulating TRAPI
bodies — **prefer TOM over bespoke TRAPI scripting** where a model, utility method, or CLI covers it
(merging, up-versioning, diffing, field access are already solved).

**Understanding TRAPI itself:** the models are **self-documenting** — every model carries docstrings
**equivalent to the descriptions in the TRAPI spec**. So when you need to understand a TRAPI
structure/field conceptually, **read the model** (or introspect it) rather than guessing — TOM is
the framework's structural + conceptual TRAPI reference.

**Scope caveat:** structural only — it enforces formatting/shape but does **not** call
node-normalizer / name-resolver. Bad CURIEs, wrong categories, unnormalized entities are out of
scope.

## Install & run

PyPI **`translator-tom`** (**package** v2.0.0 — *not* the same as TRAPI 2.0; the package ships
**both** TRAPI 1.6 and 2.0 models; author `tokebe`; source
[`NCATSTranslator/TRAPIObjectModeling`](https://github.com/NCATSTranslator/TRAPIObjectModeling)). As
an ad-hoc dependency, no project setup needed:

```bash
uv run --no-project --python 3.13 --with translator-tom python <script>.py
```

**Versions:** top-level import is the **latest (2.0)**; pin a version explicitly when needed.
Version-agnostic pieces (Biolink, CURIEs, `TOMBase`, `translator_tom.utils`) are shared.

```python
from translator_tom import Response                 # TRAPI 2.0 (latest)
from translator_tom.model_dicts import ResponseDict  # TRAPI 2.0, dict representation
from translator_tom.v1_6 import Response             # pin TRAPI 1.6
from translator_tom import up_version                # 1.6 model → 2.0 model
```

## CLIs (console scripts)

Invoke in the ad-hoc context (they're console scripts, not otherwise on PATH):
`uv run --no-project --python 3.13 --with translator-tom <cli> …` — e.g.
`… tom-parse <Model> path/to.json`.

- **`tom-parse <Model> <file.json>`** — parse a JSON file into a named TRAPI model.
- **`tom-validate <Model> <file.json>`** — parse + run semantic validation (WIP; returns
  warnings/errors with descriptions + locations).
- **`tom-up-version <file.json>`** — up-convert a TRAPI 1.6 JSON to 2.0.
- **`tom-diff <Model> a.json b.json`** — TRAPI-aware diff of two files parsed as the same model,
  emitting the deltas as JSON (handy for comparing two responses).

## Viewing a model's structure / spec description

The descriptions live in the model **docstrings**, so read the source or introspect — no schema dump
needed:

```bash
# introspect the installed package (no clone required):
uv run --no-project --with translator-tom python -c "import translator_tom as t; help(t.QueryGraph)"
```

Or read `src/translator_tom/v2_0/models/<model>.py` (resp. `v1_6/`) if TOM is cloned for reference.

## Using it — cautions

- **Structural reference/diagnostic** when reconstructing a partial request — check where a fragment
  deviates from a valid envelope. (Serialization drops defaults/None to save space.)
- **Do NOT use it to alter an issue's input.** `from_dict`/parsing validates + coerces (and may
  *reject* a malformed fragment). A rejection is a **signal to note** — reconstruction means adding
  boilerplate *around* the reporter's content, **not** correcting their IDs/values. Preserve their
  errors verbatim; they're often informative.
