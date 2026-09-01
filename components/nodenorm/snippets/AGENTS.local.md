## nodenorm (biothings/NodeNormalizationAPI)

**There are two different NodeNorms. Establish which one before reasoning about a report.**

- **`biothings/NodeNormalizationAPI`** — this bundle. BioThings SDK / Tornado, **Elasticsearch**-backed.
  A from-scratch *reimplementation* ("mirror") of the API contract. Hosts carry an **`-es` infix**:
  `nodenorm-es.ci.transltr.io` and `nodenorm-es.test.transltr.io` — **CI and Test appear to be the
  only levels**; no Prod or Dev host resolved as of 2026-09-01 (checked the bare, `.prod`, `-prod`,
  `.dev`, `-dev` patterns). Clone: `repos/NodeNormalizationAPI/`.
- **`NCATSTranslator/NodeNormalization`** (formerly `TranslatorSRI/…`) — the original SRI service,
  **Redis**-backed. Hosts: `nodenormalization-sri.renci.org`, `nodenorm{,.test}.transltr.io`.

With **no Prod deployment found**, a *user-facing* NodeNorm complaint is most likely about the RENCI
original — confirm which service the report came from before opening an investigation here.

They share an API contract, so **a behavioral difference between them is a real bug class** — never
assume a finding about one transfers to the other, and never assume `nodenorm.transltr.io` runs this
repo's code.

**`infores:sri-node-normalizer` does not disambiguate them.** It denotes this deployment *and* names
the node-normalization function generally (SmartAPI still maps it to the RENCI hosts). So a TRAPI
`resource_id` of `infores:sri-node-normalizer` tells you **nothing** about which implementation
answered — pin it by **host** (`-es` ⇒ this one) or `GET /version`.

**The repo's own docs are wrong — read the code.** `README.md` is byte-identical to
`biothings/pending.api`'s (a different project; it calls its subject a **KP** — NodeNorm is an
`sri-utility`), and `openapi.json`'s `info` block is RENCI's, including a bogus `x-trapi` claim —
**this is not a TRAPI endpoint**. Both are known-and-unfixed; the correction of record is
`components/nodenorm/definition.md` → "Documentation discrepancies".

The **only** authority on what routes exist is `src/nodenorm/handlers/__init__.py`
(`build_handlers()`) — e.g. `/get_curie_prefixes` is documented and has a handler file, but is never
wired, so it 404s.

**`conflate` defaults to `true`** on `/get_normalized_nodes` — omit it and you get GeneProtein
conflation anyway, which is the usual answer to "why were these two nodes merged?".

**`GET /status` is the cheapest triage call** — it returns the **Babel release** the ES index was
loaded from, the biolink-model-toolkit version, and ES cluster health in one hit. A normalization
discrepancy between two environments is very often a **Babel release difference**, not a code
difference, so compare `/status` across levels before diffing code. (`GET /version` gives the
deployed git SHA.) **Don't trust SmartAPI for this component's URLs** — it has no `-es` entry at all.

**Reproducing locally requires Elasticsearch loaded with a Babel compendia release** — there's no
bundled ES and the committed tests point at an internal Scripps host (`su10:9200`). Factor that in
before proposing a local repro; see `components/nodenorm/definition.md` → "Running it locally".
