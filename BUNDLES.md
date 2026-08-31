# Bundles

A **bundle** is a self-contained, contributable unit the framework can _enable_. Three
kinds share this shape:

- **`components/<name>/`** — a repo under investigation (a target). Template:
  `templates/component/`.
- **`tools/<name>/`** — an instrument of investigation. Often a repo (a CLI/library), but
  a tool need **not** be a repo — it can be a non-repo bundle of info + infra: instructions
  for using a public endpoint, a set of scripts for a specific task, etc. Template:
  `templates/tool/`.
- **`extensions/<name>/`** — an optional standing behavior. Template:
  `templates/extension/`.

(Concepts are _not_ bundles — they're single files, `concepts/<name>.md`.)

## Anatomy

```
<kind>/<name>/
  definition.md      # frontmatter (metadata) + body (notes / usage / run info)
  skills/            # optional — skill dirs symlinked into .claude/skills/ when enabled
  concepts/          # optional — bundle-specific concepts; folded into the auto-trigger index on enable
  snippets/          # optional — opt-in snippets for the dev's local surfaces
    AGENTS.local.md      # standing-instruction snippet (per-dev local core)
    settings.hooks.json  # hook snippet for .claude/settings.local.json
```

Only `definition.md` is required. Each kind's template (`templates/<kind>/`) carries the
kind-specific frontmatter and body prompts; the fields below are common to every kind.
**Instantiate a new bundle from its template** with
`python3 .claude/scripts/new-artifact.py <kind> <name>` (a deterministic copy — don't compose from
a sibling bundle), then fill it in.

## Common frontmatter

- **`name`** — the bundle's name (matches its dir name).
- **`curation`** — lifecycle, shared by every contributable artifact:
  - `inferred` — agent-derived, not yet meaningfully human-guided.
  - `curated` — a human has guided it, so it carries real nuance.
  - `canonical` — audited for coherence and shipped, or being committed for PR.

Kind-specific keys (e.g. `org` / `repo` / `kind` / `status` / `owner` for components)
live in each kind's template.

## Enabling

A bundle is inert until **enabled**. Enabling records it in `scope.yaml` `enabled:`,
symlinks its `skills/` — **plus any skills the cloned repo ships** (`repos/<name>/.agents/skills/`
· `.claude/skills/`; adopt-from-repo, tracks upstream) — into `.claude/skills/` (clean names) and adds them to
`.git/info/exclude`, folds any `concepts/` into the auto-trigger index, **auto-merges any
`snippets/AGENTS.local.md`** into `AGENTS.local.md` (legacy `snippets/CLAUDE.local.md` still
accepted), and **offers** any `snippets/settings.hooks.json` hook (merged only on the dev's yes, via
`--hooks`). Scaffold snippets with `new-artifact.py snippet --bundle <kind>/<name>`. Full procedure:
see **AGENTS.md → "Enabling & disabling bundles."**

A bundle can set **`default_enabled: true`** in its `definition.md` frontmatter — `onboard`
pre-selects such bundles on first setup (the dev can opt out). The default-ness is a self-describing
property of the bundle; the durable per-dev record is still `scope.yaml` `enabled:`.

## Contributing

A bundle moves upstream (`curated → canonical`) via `/contribute`: pre-PR hygiene
(mdformat + any kind-specific audit + an informal secret check that flags potential values for
review), one PR per bundle by default.
**Secrets never enter a bundle** — `definition.md` and templates carry secret
_descriptions + placeholder skeletons_ only.
