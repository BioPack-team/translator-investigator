## retriever

When investigating **retriever**, three standing cautions (full run/verify: this bundle's
`definition.md`):

- **Reachability-first triage (local runs).** A **locally-run** Retriever reaches the tier backends
  **directly**, so on timeouts / connection errors / empty-or-partial results **check the backend
  before blaming retriever** — Tier 0 Gandalf (`https://gandalf.renci.org`, no VPN — a good control)
  and Tier 1 Elasticsearch (`tier1.transltr.biothings.io`, **direct access needs VPN**). `000`/timeout
  on Tier 1 usually means the VPN is down, not a retriever bug. This VPN caveat is **only** for
  reaching a backend directly — a **live Retriever instance** fronts the backends over TRAPI (plain
  HTTP, **no VPN, Tier 1 included**), so it doesn't apply there.
- **Destructive DB tasks.** `task dev` / `task dbs` **force-recreate (wipe) the local Dragonfly +
  MongoDB containers on every run** — don't rely on local DB state persisting across restarts.
- **`/status/*` `lookback` shadows `since`.** On a live instance's status dashboard,
  `/status/tiers`, `/status/timeline`, and `/status/durations` default `lookback=24h`, which
  **silently overrides `since`** — a `since`/`until` window quietly returns the last 24h instead.
  Use the paged endpoints (`/status/failed` · `/completed` · `/failure_breakdown`, which honor
  `since`/`until`) or pass an explicit `lookback` sized to the window.
