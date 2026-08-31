---
name: concept-capture
description: >-
  Capture a Translator/TRAPI concept into the shared concept library so the agent (and other
  devs) reason from a checked understanding. Use when the dev explicitly asks to capture/record
  a concept; offer it when a keyword-like term or a non-obvious interaction mechanism recurs and
  is involved enough to persist (e.g. subclassing / OBI); or author one as `inferred` when you've
  derived a concept from code + prior dev responses. Triggers on: "capture this as a concept",
  "add a concept", "record how X works", repeated mention of an unfamiliar term with interaction
  implications.
---

# Concept capture

Bring a **new** concept into the library. Two lifecycles:

- **Curated** — dev-requested or offered; interview the dev, author at `curation: curated`.
- **Inferred** — you derived it from evidence; author at `curation: inferred`, **skip the
  interview**, notify the dev (non-blocking), and carry on.

(Reconciling a concept toward `canonical` for sharing is the audit half — that lives in
`/contribute`, not here.)

## When to use

- **On request** — the dev asks to capture something as a concept. → curated path.
- **On offer** — a term keeps recurring like a keyword, or the dev describes a mechanism with
  non-obvious interaction implications. Offer; don't auto-capture. → curated path.
- **On inference** — you've formed a solid working understanding from code / prior dev responses
  and it's worth persisting, but interrupting to interview isn't warranted (e.g. mid-task, or a
  more autonomous `autonomy` preference). → inferred path.

## 1. Triage — is it concept-worthy, and where does it live? (both paths)

- **Not worth persisting** — a simple, obvious mechanism. Drop it.
- **Small but non-obvious** — a useful fact, not an involved mechanism. **Not a concept**; note it
  in the relevant component's `definition.md` "Gotchas & notes" instead.
- **Involved + component-specific** — meaningful only inside one component → a **bundle concept**:
  `components/<name>/concepts/<slug>.md`.
- **Involved + ecosystem-wide or cross-cutting** (e.g. subclassing / OBI) → a **global concept**:
  `concepts/<slug>.md`.

## 2. Gather (both paths)

- **Cursory code scan** — **delegate to a background subagent** (read-only, e.g. Explore) at **low
  or medium effort** — a lighter model, chosen by what the concept calls for. Do **not** run the
  scan at the main agent's effort or higher unless the nuance clearly demands it. It greps/reads
  related code (`repos/<target>/`, the component's `definition.md`) to orient and surface targeted
  questions — orienting, not exhaustive tracing. (Curated path: await its result, then interview.)
- **Check the concept index** — AGENTS.md's auto-trigger index + `concepts/` (global and enabled
  bundles') for related/overlapping concepts. Note `see_also` candidates. **On overlap, don't
  proliferate:** if it substantially duplicates an existing concept, **augment that file** instead
  of creating a new one; if it's merely another name for one, add it to that concept's `aka` and
  stop.

## 3. Authoring quality (both paths)

Instantiate the file — `python3 .claude/scripts/new-artifact.py concept <slug>` (from the repo root; for a bundle concept add `--bundle components/<name>` — **plural** kind, must be an existing
bundle). This creates `concepts/_<slug>.md` — **underscore-prefixed = local/unaudited** (gitignored)
until `/contribute` promotes it (drops the underscore → canonical). Then **fill it in** (don't
compose from scratch). Exemplar to match for shape and depth: the shipped `concepts/subclassing.md`.

- **`aka` is load-bearing** — it drives the auto-trigger index, so list *everything a dev would
  actually say*: synonyms, abbreviations, the `infores:` tag, informal names. Weak `aka` = the
  agent silently fails to recall the concept.
- **Reason from evidence, and cite it** — ground claims in `repos/<target>/path:LINE` or the dev's
  own words; don't assert from thin air. Say what the mechanism *means*, not just what it is.
- **Conventions** — `<slug>` is kebab-case and the filename matches frontmatter `name`; set
  `see_also` to the few tightly-related concepts (not all of `domain`); reuse existing `domain`
  tags rather than coining near-synonyms.
- **Terseness** — a concept file is durable shared knowledge: keep it **clear and complete
  regardless of the dev's `terseness`**. Terseness governs your *narration to the dev*, not the
  artifact.

## 4a. Curated path — interview → summarize → author → review

- Ask for a **general description** in the dev's words, then **targeted questions** from the scan
  (ambiguities, edge cases, interactions). Confirm the term, `aka`, and `see_also`.
- Give a **brief summary** of your understanding (note the chosen placement so the dev can
  redirect); **offer** to author it.
- On yes, write the file (§3) with `curation: curated`.
- **Review loop:** show it, take corrections/edits, repeat until the dev is satisfied.

## 4b. Inferred path — delegate → author → notify → move on

- **Run the whole inferred path in a background agent** so the main task never blocks. It must be
  **write-capable** (general-purpose or a fork) — **not** the read-only Explore used for §2's scan,
  since it authors files and re-indexes. Spawn it (low/medium effort — it does its own cursory scan
  inline, no further sub-spawn) and **continue the main task immediately.** The background agent
  triages and writes the file (§3) with `curation: inferred`.
- **Re-index explicitly** — a background/subagent write may not trigger the after-edit re-index
  hook (and non-Claude agents may be on the manual reindex fallback), so after authoring run
  `uv run python .claude/hooks/reindex-concepts.py --all` (from the repo root) and **confirm it prints
  `N concept(s) indexed`** (a missing line means it didn't run — check you're at the repo root) to fold the new
  keywords into the index.
- **On completion, notify the dev — terse and non-blocking:** relay that you authored an inferred
  concept and they may review at their convenience. (The main task has continued in the meantime.)
- Later, the dev may:
  - **offer review** → resume at **4a** (interview + review loop); on satisfaction bump
    `curation: curated`.
  - **ask to re-capture** → restart the skill in explicit (curated) mode from triage.

## Notes

- Curation reflects guidance: **`inferred`** (agent-only) → **`curated`** (human-reviewed). Neither
  path produces `canonical` — that's `/contribute`.
- Don't hand-edit the AGENTS.md concept index; the re-index hook regenerates it on concept edits
  (global or an enabled bundle's `concepts/`). A bundle concept must be enabled for its keywords to
  join the index.
- No secrets in concept files (they're shared/contributable) — see `BUNDLES.md`.
