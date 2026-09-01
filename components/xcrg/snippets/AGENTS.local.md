## xcrg

**Check the known-failure ledger first.** `scripts/arax_tests.json` carries graded expectations
(`top_answer` / `acceptable` / `bad_but_forgivable` / `never_show`) and flags cases already known to
fail with `fails_on_arax: true`. Before treating an xCRG result complaint as new, look for the pair
there — it may already be a tracked gap.

**Read the pinned SHA, not `main`.** xCRG is never deployed standalone; it ships inside ARAX pinned
by git SHA, and `main` holds a next iteration that is not deployment-ready. For deployed behavior
read the pinned revision; read `main` only to see where xCRG is going. The gap is expected — do not
report it as a stale pin.

**Bad node metadata is a Retriever finding.** xCRG deliberately passes Retriever's nodes and edges
through without repairing categories or names. Chase metadata problems upstream to Retriever rather
than attributing them to xCRG.
