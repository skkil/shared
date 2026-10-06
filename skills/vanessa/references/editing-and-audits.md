# Editing, rewriting, auditing and co-writing

## Levels of edit

Name the level you're doing so the user knows what will change:

| Level | Changes | Leaves alone |
|---|---|---|
| Structural | Order, sections, what's in and out, the point-first opening | Meaning |
| Line | Sentences: clarity, length, voice, terms | Structure and meaning |
| Copy | Mechanics: spelling, spacing, punctuation, glossary terms, style guide | Wording beyond mechanics |
| Check | Facts against sources, links, commands, numbers | Wording |

## Rewriting hard-to-read content

The original is the source. Extract every claim into the ledger first, so the rewrite can be checked against it: nothing dropped, nothing added. Then rewrite to the standard. After rewriting:

- Run `coverage_check.py`; every original claim is in the rewrite or excluded with a reason the user can approve ("repeated in §2").
- **Change-rate guard:** if a sentence's meaning changed, or the rewrite adds a fact the original didn't have, stop and either cite a source for it or remove it. A rewrite that "improves" by adding plausible detail is a defect.
- Report what you cut, merged and reordered, briefly.

## Auditing existing content

Return a score and a prioritized fix list (`assets/templates/audit-report.md`).

1. Run `readability_check.py` and, if the content was built from sources, a spot check of five claims against them.
2. Score each dimension 0–3 with one line of evidence:

| Dimension | 3 means |
|---|---|
| Point first | The first lines give the answer or action |
| Structure and headings | Headings state the content; skimming them gives the argument |
| Sentence clarity | Sentences read once; length within targets |
| Terminology | One name per concept; terms and acronyms defined |
| Accuracy and sources | Claims sourced and current; no gaps hidden |
| Reader fit | Register, depth and format match the reader and where they read |
| Mechanics | Style guide followed; no FAIL findings |

3. **Fix list**, ordered by reader impact first and effort second. Each item: where, what's wrong, the fix (rewritten text where short), and why it matters to the reader. Group repeated issues ("acronyms undefined in 11 places") into one item with locations.
4. **Before and after** for the top three fixes, so the user can see the difference.

## Editing Jennifer's documents

Only when the user asks. Clarity edits only: structure, wording, readability. Never change a decision, number, priority or scope. Ambiguities, contradictions and missing information become clarification requests for Jennifer (`team-handoffs.md`), delivered with the draft.

## Co-writing

When the knowledge is in the user's head:

1. Reader brief, then ask the user to dump everything they know in any order; shorthand is fine.
2. Ask follow-up questions in numbered batches of up to five, each answerable in a line ("1: yes, 2: see #infra channel"). Ask about edge cases, decisions and their reasons, and what goes wrong.
3. Treat each answer as a source: record it in the ledger as "Interview with <name>, <date>", with the question it answers.
4. Draft section by section, starting with the part that has the most unknowns; show the outline first.
5. Reader-test the draft (workflow step 7) before calling it done.
