---
name: begin-investigation
description: >-
  Scaffold a new investigation workdir — pick the mode (issue or topic), fetch issue
  context, and create the dir + worknotes + artifacts/scripts. Use when the dev starts
  looking into a GitHub issue or begins a free-form / cross-cutting investigation.
  Triggers on: "investigate #<n>", "look into <topic>", "start an investigation", "dig
  into <X>", a feedback PK to chase down. This is setup only; how to approach the
  investigation afterward is the ambient investigate posture in CLAUDE.md.
---

# Begin investigation

Scaffold a new investigation workdir. This skill's job is **setup only** — reproducing,
recording, and iterating afterward is the ambient investigate posture in CLAUDE.md
("Operational modes → investigate").

## 1. Pick the mode

- **issue** — a filed GitHub issue. Resolve the nickname via `issue-sources.yaml`
  (longest alias wins; else the issue-sources `default`) → `<org>/<repo>` + number.
- **topic** — free-form / cross-cutting. Choose a short kebab-case slug.

## 2. Gather context + confirm direction

- **Issue mode** — `gh issue view <num> --repo <org>/<repo> --comments` (and
  `--json title,url,state,labels,author,body,comments`). **Read body _and_ comments** — request
  bodies, links, and PKs often live in comments. For a feedback **PK**, pull the request/response
  with the enabled tool if there is one; **save big payloads to `artifacts/`, never inline**.
- **Topic mode** — capture the dev's **framing / initial question** (it becomes the worknotes
  Summary).
- **Both** — per the dev's **`autonomy`** preference, state a short understanding and let them steer
  **before** scaffolding / investigating.

## 3. Scaffold

- issue → `investigations/<repo>/i<num>/` · topic → `investigations/topics/<slug>/`. `<repo>` is the
  **bare** repo name (last segment of `<org>/<repo>`) — e.g. `investigations/retriever/i192/`, not
  `investigations/BioPack-team/retriever/…`.
- Create the worknotes: `python3 .claude/scripts/new-artifact.py worknotes --dest <investigation-dir>`, then fill its front-matter (`title`; `mode` = `issue` or `topic`;
  `status: investigating`; `opened`; `components`; `likely_handoff`). **Issue mode:** uncomment and
  fill the `issue:`/`pk:` block. **Topic mode:** delete that block and seed the Summary with the
  dev's framing (§2).
- Create `artifacts/` (captured payloads/logs) and `scripts/` (analysis scripts) as needed. Repro
  outputs generally land in `artifacts/`, but any **tool-specific repro-file layout** (e.g. the TTT
  tool's `queries/` symlink) is specified by that **tool's bundle**, not here.
- Set `components` to everything it touches; for any **uncharacterized** component, offer
  `/discover`.

## Done → investigate

The workdir is ready. Proceed in the ambient **investigate** mode (CLAUDE.md): reproduce
where applicable, record findings in `worknotes.md`, keep `status` current.
