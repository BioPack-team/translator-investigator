## pathfinder

**Reproduce with ARAX's parameters, not the README defaults.** ARAX overrides two of them —
`prune_top_k=75` (package default 30) and `degree_threshold=10000` (default 30000) — and sets
`max_hops_to_explore == hops_numbers`. A local run on package defaults will not match production
paths.

**The URI prefixes are mandatory.** `repo_uri` must start with `retriever:`, and `ngd_url` /
`degree_url` with `sqlite:` or `mysql:`; `repo_factory` raises `ValueError` otherwise. For local
work the `mysql:` backend against the team's read-only server avoids downloading multi-GB SQLite
files — an option ARAX itself does not use.

**Gandalf is deprecated here.** `repo_factory` accepts only `retriever:`; `GandalfRepo` is commented
out and the `gandalf_mmap` artifact is gone. Ignore `build_model/gandalf/` and the corresponding
step in the RTX wiki's Rollout Procedure.
