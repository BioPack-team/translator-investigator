---
title: <short title>
mode: <issue|topic>      # issue = filed GH issue; topic = free/cross-cutting investigation
status: investigating    # investigating | root-caused | fixing | handoff | resolved
opened: <YYYY-MM-DD>
components: [<target>]   # everything this touches; cross-cutting = list more
likely_handoff: []       # names/teams/repos to hand off to if the cause is outside purview
# --- issue mode only (delete for topic mode) ---
# issue: { repo: <org>/<repo>, number: <n>, url: <issue url> }
# pk: <ARS PK, or a Translator-UI / ARAX-UI link>   # feedback issues
---

# <title>

<!-- Detail and length of every section below follow the dev's `terseness` preference. -->

## Summary

<What's going wrong and why it matters, in plain language.>

## How to reproduce

<The minimal repro and how to run it — via an appropriate enabled tool or the normal agentic
method for the job. Name each repro artifact and what it exercises. If it can't be fully reproduced
locally, note the closest achievable repro.>

## Investigation log

<Chronological findings. After each technical finding, say what it *means*. Reference code as
`repos/<target>/path/to/file:LINE`.>

## Root cause

<The underlying cause, once identified, pinned to specific files/lines.>

## Fix

<Only if fixing. Work lives in `./worktree/` (local only — shipping is an explicit contribution).
Note the regression test/assertion that fails now and passes once fixed, and what's left to
verify.>
