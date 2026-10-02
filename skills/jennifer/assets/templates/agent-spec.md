# <Feature> · Implementation spec for a coding agent

PRD: <link> · Decision record: <link> · Research done before writing: <docs/files checked, dates>

## Context for the agent
Two or three sentences: what we're building and why. Relevant files and modules. Stack and conventions to follow.

## Global constraints
- DO NOT CHANGE: ___ (schemas, public APIs, auth flow, unrelated modules)
- Non-goals for the whole spec: ___
- Tests: run `___` after each phase; all existing tests must pass.

## Phase 1: <name>
**Objective:** one sentence.
**Requirements:**
1. When ___, the system shall ___.
**Technical notes:** files, schema, endpoints.
**DO NOT CHANGE in this phase:** ___
**Not in this phase:** ___
**Acceptance criteria (runnable):**
- [ ] `___` exits 0 / returns ___
- [ ] All previous functionality still works (`___`)
**Checkpoint:** human verifies, then commit "Phase 1: ___".

## Phase 2: <name>
(same structure)

## AI-feature criteria (if applicable)
Eval set and pass threshold · max error/hallucination rate · latency budget · cost per call · behavior on model failure.
