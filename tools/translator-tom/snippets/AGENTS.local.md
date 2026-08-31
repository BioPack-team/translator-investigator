## translator-tom (TOM)

For anything TRAPI in a script — constructing, validating, manipulating, comparing, or
version-converting — **prefer translator-tom over bespoke TRAPI code** where a model, utility method,
or CLI covers it. **Before writing TRAPI code, check `tools/translator-tom/definition.md`** — it
catalogs the CLIs (`tom-parse` / `tom-validate` / `tom-up-version` / `tom-diff`), version pinning
(1.6 / 2.0), and the model/model_dict utilities — so you reach for what already exists.

**Match the component's TRAPI version.** TOM's default import is 2.0, but **most components are
still TRAPI 1.6** — and a component's version isn't obvious from its repo. Before using TOM against a
specific component, establish *its* TRAPI version: check the component's **`trapi_version`**
frontmatter (in its `definition.md`); if unset, **ask the dev and record it** (notes may clarify if
it varies by branch). Then pin the matching models (`from translator_tom.v1_6 import …` / `.v2_0`).

When you need to understand a **TRAPI structure or field conceptually**, read TOM's
**self-documenting models** (their docstrings mirror the spec) — e.g.
`… python -c "import translator_tom as t; help(t.QueryGraph)"` — rather than guessing.

Use it as a **structural** reference only — never to "fix" a reporter's CURIEs / categories / values
(coercion can mask their error; a rejection is a signal to note, not correct). Normalization is out
of scope.
