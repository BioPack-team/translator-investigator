## rtx (ARAX)

**Maturity vocabulary is inverted.** ARAX derives its maturity from the domain, so
`arax.ci.transltr.io` is **`staging`** in ARAX's own vocabulary, `.test.` is `testing`, and bare is
`production`. Never read an ARAX maturity straight off the URL — check
`components/rtx/definition.md` before reasoning about `component-maturity-levels` or targeting with
`tt -e`.

**xCRG and pathfinder are pinned dependencies.** When an ARAX behavior traces into either package,
read the **pinned revision** from `RTX/requirements.txt` — not upstream `main`. For xCRG especially,
`main` is a work-in-progress next iteration and is *not* what any deployed ARAX runs.

**Triage crosses two trackers.** Roughly a third of ARAX issues have a parent in
`NCATSTranslator/Feedback`. Before opening an `RTXteam/RTX` issue, check whether one already exists;
when you draft either, **cross-link them reciprocally**, and comment on the parent when a fix merges
so its stakeholders can re-run their example.
