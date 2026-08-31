# CLAUDE.md — Claude Code adapter

The framework core is **agent-agnostic** and lives in `AGENTS.md`. Claude Code doesn't
auto-load `AGENTS.md`, so this thin adapter imports it and adds the Claude-Code-specific
bindings of the activation layer. **Read `AGENTS.md` for everything** — safety rules,
preferences, modes, routing, concepts.

@AGENTS.md

## Claude Code bindings

The activation layer (`AGENTS.md` → "Activation layer") is already wired for Claude Code —
no porting needed:

- **Skills** — the skill library in `.claude/skills/<name>/SKILL.md` is invoked via the
  **Skill tool** (or `/name`). Enabled-bundle skills symlink in here.
- **Hooks** — the two concept-reindex automations are configured in
  `.claude/settings.json` (`SessionStart` + `PostToolUse` on `Write|Edit`). They keep the
  auto-trigger index in `AGENTS.md` / `AGENTS.local.md` fresh; don't hand-edit those blocks.
- **Memory** — per-dev state lives in Claude Code's **harness memory** (`MEMORY.md` +
  memory notes), not the repo. (The gitignored root `MEMORY.md` fallback in `AGENTS.md` is
  only for agents without a native memory store.)
- **Per-dev local core** — `CLAUDE.local.md` (gitignored, auto-loaded) imports
  `AGENTS.local.md`; that's where local concepts + enabled-bundle instructions live.
