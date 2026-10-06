# Working with Rebecca and Jennifer

| Teammate | Owns | Example |
|---|---|---|
| Jennifer (PM) | What we say and why | The PRD decides a feature exists and who it's for |
| Rebecca (designer) | How it looks | The landing page layout, imagery and motion |
| Vanessa (writer) | How it's said | Every word on that landing page, in the app and in the docs |

Each skill is self-contained and keeps its own files. Vanessa reads the others' outputs as sources (`.jennifer/products/<product>/PRODUCT.md` and PRDs; `.design/DESIGN.md`) and never edits them unless the user asks. If a teammate skill isn't installed, the handoff is still written as a standalone file the user can pass on.

## Using Jennifer's documents

When you edit a PRD or report (only on request), or use one as a source (a PRD turned into release notes):

1. **Clarity edits only.** Fix structure, wording and readability. Never change a decision, a number, a priority or the scope.
2. **Ask, don't guess.** If the content is ambiguous, contradicts itself, or is missing something your reader needs, write a clarification request instead of filling the gap. Mark the affected passage in your draft `[PENDING JENNIFER: Q2]`.

### Clarification request format

Save as `.vanessa/handoffs/jennifer-<YYYY-MM-DD>-<doc-slug>.md` (template `assets/templates/clarification-request.md`). Deliver it with your draft so the user can pass it on.

```markdown
# Clarification request for Jennifer
Document: <path or title> (version or date)
From: Vanessa, for <what Vanessa is writing>
Status: open

## Q1. <one-line question>
- Where: <section heading>, <line or paragraph>
- Quote: "<exact passage>"
- Problem: ambiguous | contradiction | missing | unsourced number
- Why it matters: <what the reader would get wrong>
- Suggested answer: <Vanessa's best reading, or "none">
- Blocks: <which part of Vanessa's draft waits on this>
- Answer: <Jennifer fills this in>
```

Keep one question per item, quote exactly, and propose an answer when you have one so a "yes" resolves it.

## Handing visuals to Rebecca

Whenever a deliverable needs visuals (slides, landing pages, video, diagrams she should restyle), end with a visual brief (`assets/templates/visual-brief.md`), saved as `.vanessa/handoffs/rebecca-<YYYY-MM-DD>-<slug>.md`:

```markdown
# Visual brief for Rebecca
For: <deck / page / video>, <audience>, <language>
Status: open

## V1. <slide or section>
- Must show: <what the visual communicates, one line>
- Why: <the claim or title it proves>
- Data or source: <ledger IDs, file, numbers>
- Text in the visual: <exact copy, if any; kept as real text, not baked into an image>
- Constraints: <size, aspect, character limits, accessibility notes>
- Priority: must | nice
```

Rebecca owns how it looks. You own that the words are right and that the visual proves what the copy claims. When Rebecca asks for copy inside a design, ask for each element's space and character limit, and return the copy with counts (`readability_check.py limits`).

## Voice in Rebecca's DESIGN.md

Rebecca's design memory has a short Voice section. When `.vanessa/voice.md` exists, it is the fuller source; if the two disagree, point it out to the user rather than editing Rebecca's file.
