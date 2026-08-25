## trapi-testing-tools (`tt`)

For firing TRAPI queries, asserting on responses, or analyzing them, use **ttt** (`tt`) — the main
repro / regression instrument. It **ships its own agent interface**, so reach for the
**`/trapi-testing` skill** and **`repos/trapi-testing-tools/AGENTS.md`** for current usage (authoring
query files, running non-interactively, analyses, ARS PKs). The repo's docs are the source of
truth — don't rely on the bundle definition for `tt` usage.

**Keep the clone synced.** ttt is fast-moving — when you interact with it, first pull latest `main`
(`git -C repos/trapi-testing-tools pull`), unless the dev says otherwise. (This also refreshes the
adopted `/trapi-testing` skill + `AGENTS.md`.)
