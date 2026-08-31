## translator-pk-inspector

**Whenever an ARS primary key or a Translator UI results URL comes up — in an issue, a report, or
straight from the dev — reach for `/translator-pk-inspector` first.** That's the entry point for
turning a PK into the TRAPI responses each ARA actually returned. Same when the question is about
what a specific ARA returned (ARAGORN / BTE / ARAX comparison, missing results, scoring).

**On `feedback` triage** (NCATSTranslator/Feedback is the default issue source): reports there
usually arrive as a PK plus a complaint, so pulling the PK is the **default first move** — do it
before theorizing about the cause.

**Tool choice vs. `tt`:** for **PK / ARA-response inspection**, prefer pk-inspector over `tt pk`.
`tt` remains the instrument for *firing* queries and regression-testing a component. Inspect with
pk-inspector, then reproduce with `tt`.

**Context hygiene (matters here — payloads are big):** always write to the investigation's
`artifacts/` via `--output`, then summarize with a script in the investigation's `scripts/`.
Never read an ARA payload into context — they run to tens of MB. **`--metadata-only` does not
make them smaller** (see the bundle definition); assume every fetch is full-size.

**Don't guess at failures.** The skill deliberately surfaces retrieval failures (HTTP / JSON /
missing field) rather than inferring a cause. Preserve that — report the gap, don't explain it away.
Scrub payloads before they go into a handoff or an upstream issue.
