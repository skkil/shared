# Developer onboarding documents

The scenario: a developer joins a product in a domain they know nothing about (payments, logistics, medical imaging, insurance). After reading your document they should understand the product, its context and its system design well enough to start working like a senior engineer on the team. That goes far beyond setup steps. The document must cover **all** the sources the user provides, with coverage proven by `coverage_check.py`.

## What separates a senior's understanding from a junior's

Practitioners who onboard engineers into unfamiliar codebases describe the same gap: a junior can read the code; a senior knows **why** the system has its shape, **what matters** to the business, **what breaks**, and **where a change belongs**. Without written decision rationale, a newcomer looking at fifty services can't tell whether that was a deliberate choice, a deadline, or an accident (practitioner reports; Nygard's decision records exist for exactly this). So the document is built around those four, not around the folder tree.

## Required sections

Follow `assets/templates/onboarding-doc.md`. Point first: the opening screen says what the product does, for whom, and the one-paragraph mental model of how it works.

1. **The domain, from zero.** Core concepts, vocabulary, rules and regulations, each defined in plain words with an example from this product. Build the glossary first; the rest of the document uses only glossary terms.
2. **The product.** Who uses it, what problem it solves for them, how it makes money (or what "success" means if it doesn't), and the critical user journeys. Cite Jennifer's PRODUCT.md and PRDs when they exist.
3. **The system design.** Context and container diagrams (C4 levels 1 and 2), a components table, the data model, the integrations, and one real request traced end to end with file and line references (`technical-docs.md`).
4. **The why.** The key decisions and trade-offs, and the history that explains the current shape. Extract them from design docs, decision records, commit history and meeting transcripts; each one cites who decided and when.
5. **The codebase.** Where things live, conventions, and how to run, test and deploy. Every command run and verified.
6. **Failure modes.** For each component: what breaks it, how the failure shows up (symptom, log line, alert), the blast radius, and how the team responds (runbook link). Build this from error-handling code, timeouts and retries, incident notes and transcripts. Present it as a table; it's the section seniors reread.
7. **A learning path.** A reading order, checkpoints with self-check questions, and first tasks that build real understanding (a small fix in a core path beats a typo fix).

## Method

1. Reader brief and **senior-level reader questions** first, for example:
   - "Explain to a customer what happens between X and Y."
   - "What breaks if service A goes down, and how would you notice?"
   - "Where would you add a new <domain thing>, and which tests would change?"
   - "Why does the system do Z instead of the obvious W?"
   - "What does <domain term> mean, and where is it in the code?"
2. **Inventory and chunk everything** (`long-source-ingestion.md`): the repository (one source, file locators), design docs, transcripts, wikis, PRDs. Tell the user the size before reading: a research-heavy repository can run to hundreds of chunks and millions of tokens.
3. **Scope with the user, then exclude whole areas with reasons.** Use the reader brief to decide which directories are the product path and which are background (experiment folders, vendored upstream code, archived evaluations). Exclude out-of-scope areas at chunk level in `exclusions.md` ("S01-C210 to S01-C412: research experiments under `core/research/`, not on the request path; summarized in one paragraph from their READMEs"), so coverage still proves nothing was dropped silently. Data files the chunker sets aside (results, datasets, logs) get one exclusion line per group. Very large repositories belong in Claude Code, where subagents can read chunks in parallel.
4. **Read the code, don't infer it.** Entry points, configuration, the main request path, error handling, the data layer, tests. In Claude Code, use subagents for parallel reading of subsystems; each returns ledger entries with `file:line` locators.
5. **Draft the glossary and system map before prose.** If you can't draw the container diagram from the sources, you don't understand the system yet; find out which source is missing.
6. **Write**, citing as you go. Prose for reasoning, tables for comparisons and failure modes, diagrams for structure.
7. **Cold-reader test** with the senior questions. A fresh reader must answer them from the document alone.

## Learning design

From cognitive load research and the retrieval-practice literature:

- **Start with worked examples** for a domain newcomer (the traced request, a walked-through calculation), then fade the guidance: later checkpoints ask the reader to trace a second request themselves. Worked examples help novices most and lose value as expertise grows (expertise-reversal effect), so senior readers get a "skip to the system map" path.
- **Retrieval checkpoints** after each major section: three to five questions answered from memory, with answers in collapsible blocks. Spread them through the document instead of one quiz at the end.
- **Don't duplicate a diagram in prose** (redundancy effect); the prose explains what the diagram can't show: why, and what happens when it fails.
- **Concrete examples** from this product's real data and code, never generic ones.

## Delivery

Usually a self-contained web page (`web-artifacts.md`) with a table of contents, an explorable architecture diagram (click a component to see its responsibility, code location, dependencies and failure modes), collapsible source excerpts, and the checkpoints; or Markdown in the repository when the team keeps docs there. Deliver the ledger report and exclusion log with it.
