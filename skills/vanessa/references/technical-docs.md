# Developer documentation

READMEs, API references, tutorials, how-to guides, concept explainers, architecture docs, decision records, docstrings, changelogs and release notes.

## Pick the document type first (Diátaxis)

Most hard-to-read docs mix two jobs. Daniele Procida's Diátaxis compass asks two questions: does the content inform **action** or **cognition**, and does it serve **acquiring** a skill or **applying** one?

| Action or cognition | Acquisition or application | Type | The reader is… | Title shape |
|---|---|---|---|---|
| action | acquisition | **Tutorial** | learning by doing, guided | "Build your first X" |
| action | application | **How-to guide** | at work, with a goal | "How to rotate API keys" |
| cognition | application | **Reference** | looking something up | "Webhooks API" |
| cognition | acquisition | **Explanation** | trying to understand why | "How billing retries work" |

Keep each type in its own page or section. A tutorial that stops to explain theory loses the learner; a reference that teaches buries the fact. Apply the compass at the sentence level too: a sentence explaining design history inside a how-to step belongs in an explanation page, linked.

## README

The first screen answers: what is this, who is it for, and how do I see it work. Order:

1. **One sentence** on what it does and for whom, in the reader's words.
2. **Quick start**: the shortest path to a visible result, with the expected output. Run every command in a clean environment first (`sources-and-citation.md` §7).
3. **Usage**: the two or three things people do most, each with a working example.
4. **Configuration**: a table of settings (name, default, what it changes).
5. **Troubleshooting**: the failures people actually hit, titled by symptom.
6. **Contributing, license, contact**, briefly.

Link out for depth. A README that tries to be the whole manual gets skimmed past.

## API reference

Generate the facts from the source of truth (OpenAPI spec, route definitions, the handler code), never from memory. For each endpoint or function:

- **One sentence** on what it does, starting with a verb: "Creates a refund for a captured payment."
- **Signature**: method and path, or the function signature.
- **Authentication and permissions.**
- **Parameters table**: name, type, required, default, constraints, description. State units and formats ("milliseconds", "ISO 8601").
- **Request example** that runs as written, with placeholders formatted one consistent way (Google: `PROJECT_ID`).
- **Response example** and a fields table for anything non-obvious.
- **Errors table**: code, what it means, what the caller should do.
- **Limits**: rate limits, pagination, size limits, timeouts.
- **Since/deprecated** versions.

Reference verbs are third-person present: "Returns", "Creates" (Google "Verbs in reference documents"). Keep reference free of tutorials; link to them.

## Tutorial

A tutorial must work every time for a beginner, so it carries a promise you test. State what the learner will have built and roughly how long it takes. List prerequisites. Each step: one action, the command or code, the expected result ("You should see `Server started on :8080`"). End with what they built and one next step. Don't branch, don't offer alternatives, don't explain more than the step needs.

## How-to guide

Title by goal ("How to …"). Assume competence. Conditions before instructions. Steps only, with a verification step at the end. Link to the explanation for "why".

## Explanation and concept pages

Answer "why" and "how does it work": context, the mechanism, the trade-offs, the alternatives considered, and the history that explains the current shape. A diagram usually carries the structure; the prose carries the reasoning. Cite the decision records and code.

## Architecture docs

- **Diagrams by level** (C4 model, Simon Brown): system context (the system, its users, the external systems it talks to) and containers (the deployable parts and how they talk) carry most of the value; go to components only for the parts the reader will change. Draw in Mermaid so diagrams live as text next to the code; one diagram, one level.
- **Components table**: name, responsibility in one sentence, owner, where the code lives (`path/`), what it depends on, what depends on it.
- **Data flow**: trace one real request end to end with file and line references.
- **Data model**: the core entities and their relationships, from the schema or migrations.
- **Integrations**: each external system, the protocol, and what happens when it's down.
- **Decisions**: link the decision records.

## Decision records

Michael Nygard's format (2011): **Title** (short, with an ID), **Status** (proposed, accepted, deprecated, superseded by …), **Context** (the forces at play, including conflicting ones), **Decision** (what we do), **Consequences** (all of them: positive, negative and neutral). For decisions reconstructed from meeting notes, cite who decided and when; if the notes don't show a decision was made, it's an open question, not a decision record.

## Docstrings and code comments

Follow the language's convention (Python docstrings, JSDoc, KDoc, Javadoc). Document behavior, inputs, outputs, errors and side effects; don't narrate the code. Respect repository rules: some teams forbid comments and keep explanations in decision records instead. Read `CLAUDE.md`, `AGENTS.md` and contributing guides before adding any.

## Release notes and changelogs

Release notes are for users: lead with what they must do, then what's new, then what changed, then what's fixed. Each item says the effect on the reader, not the implementation ("Exports no longer time out on files over 1 GB", not "Refactored the export worker"). Source every item from merged changes, the PRD, or the issue tracker; mark unreleased items "coming soon" or leave them out. A changelog is for developers and can be terser, grouped by version, newest first. A launch announcement leads with the benefit and goes through `marketing-copy.md`.

## Verifying technical docs

In Claude Code: run the quick start and every sample in a clean shell; compare documented parameters against the code; check links. In Claude Chat: mark samples you couldn't run, and ask the user to run them.
