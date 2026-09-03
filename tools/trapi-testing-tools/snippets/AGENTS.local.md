## trapi-testing-tools (`tt`)

For firing TRAPI queries, asserting on responses, or analyzing them, use **ttt** (`tt`) — the main
repro / regression instrument. It **ships its own agent interface**, so reach for the
**`/trapi-testing` skill** and **`repos/trapi-testing-tools/AGENTS.md`** for current usage (authoring
query files, running non-interactively, analyses, ARS PKs). The repo's docs are the source of
truth — don't rely on the bundle definition for `tt` usage.

**Keep the clone synced.** ttt is fast-moving — when you interact with it, first pull latest `main`
(`git -C repos/trapi-testing-tools pull`), unless the dev says otherwise. (This also refreshes the
adopted `/trapi-testing` skill + `AGENTS.md`.)

**Quick testing → inline `tt query`.** For an ad-hoc single-hop check, prefer `tt query` (alias `q`)
over authoring a file — it builds and runs the query from flags through the same pipeline as `tt test`
(`-e`, `-p`, `--against`, the standard battery; `--no-tests` to skip; `--si "nameres:<name>"` resolves
a name inline). Direct any saved response to a scratch/temp folder, not the repo. **Write an actual
query file only once the query/response is repro- or review/share-worthy** — a regression check to
keep, or a case to hand off. Fall back to a file when inline flags can't express the query (multi-hop,
pathfinder, or an existing query graph — `from_qg`/`load_json`).
