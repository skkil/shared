# Long sources: read everything, drop nothing silently

Use this for anything longer than you can read carefully in one pass: books, long papers, hours of transcripts, a repository, a pile of messy notes.

**The rule:** every piece of information in the sources ends up either in the document or in the exclusion log with a reason. Nothing disappears silently. `coverage_check.py` verifies it.

**Why this method:** language models use the beginning and end of a long input much better than the middle (Liu et al., "Lost in the Middle", TACL 2024), and long-form summaries are least faithful about material from the middle of their sources (Wan et al., NAACL 2025). So you never summarize a long source in one pass. You split it, read each piece completely on its own, extract into a ledger with IDs, build the document from the ledger, and then prove coverage by ID. This is slower than a single summary and much harder to get silently wrong.

Contents: 1. Inventory · 2. Chunk · 3. Extract · 4. Clean up messy input · 5. Map · 6. Check coverage · 7. Surfaces

## 1. Inventory

```bash
python scripts/chunk_source.py inventory SOURCES... --work .vanessa/work/<task>
```
This lists every source with its type, length, date and structure (chapters, sections, speakers, files) in `sources.jsonl`. Fill in title, author, date and credibility where the file didn't provide them. Tell the user the size of the job before you start: "2 books (480 pages), 5 hours of transcripts, 1 repository: about 60 chunks."

## 2. Chunk

```bash
python scripts/chunk_source.py chunk SOURCES... --work .vanessa/work/<task> [--max-tokens 6000] [--ocr]
```
Chunks follow the source's natural structure (chapters and sections from the PDF outline, Markdown and Word headings, slides, speaker turns, files) and stay small enough to read in full. Every segment inside a chunk carries its locator (`=== [pages=42] (printed p. 30) | chapter 3: Interest ===`), so each ledger entry gets an exact location. Blank pages are listed so you can exclude them; pages with no text layer are flagged for OCR or a visual read of the rendered page. In a directory source, data files (CSV, JSONL, logs, JSON over 100 KB), files over 2 MB and unsupported formats are set aside and listed by group; exclude each group with a reason, or rerun with `--include-data` when the data itself is the subject.

## 3. Extract

Read every chunk completely; no skimming, no sampling. Pull every fact, definition, claim, number, example, decision, procedure and open question into `ledger.jsonl`, one entry per line:

```json
{"id": "S01-C003-07", "source": "S01", "chunk": "S01-C003", "locator": "pages=42", "cite": "p. 30",
 "kind": "definition", "text": "Compound interest adds each period's interest to the principal before the next period is calculated.",
 "section": "", "status": "ok"}
```

- **IDs** are the chunk ID plus a two-digit counter, so parallel readers never collide.
- **`text`** is a short restatement in the working language, precise enough to write from. Keep numbers, names and conditions exact. Mark anything you inferred rather than read.
- **Kinds:** fact, definition, claim (someone asserts it), number, example, decision, procedure, question (open question in the source), quote (pointer to wording that matters exactly; the excerpt script copies the words later).
- **Duplicates across chunks** still get entries; later you exclude them as "duplicate of <ID>", which proves you saw them.
- **A chunk with nothing usable** (index, copyright page, blank pages) gets one line in `exclusions.md`: `| S01-C001 | front matter: title, copyright, table of contents |`.

**In Claude Code**, process chunks with parallel subagents. Give each subagent: the chunk path, this section, the reader brief, the ledger schema, and an output path `ledger-<chunk>.jsonl`. Ask it to read the whole chunk and return the count of entries. Merge the files into `ledger.jsonl` afterward. Spot-check two or three chunks yourself against their entries.

**In Claude Chat**, work through chunks in order. After each chunk, append its entries to `ledger.jsonl` on disk before reading the next, so a long conversation or a reset loses nothing. `chunk_source.py status` shows what's read; `chunk_source.py next` prints the next unread chunk.

## 4. Clean up messy input

Transcripts and rough notes need cleanup before they're usable, but the original wording must stay checkable.

- **Merge fragments** that belong to one thought, across lines or speaker interruptions.
- **Attribute speakers.** When a transcript has none, infer from context and mark it: "(speaker inferred)".
- **Resolve vague references** ("that thing we discussed", "the old approach") by searching the rest of the sources. If you can't resolve one, keep it as a question entry.
- **Keep the original** available: ledger entries for transcripts carry the timestamp range, so `extract_excerpts.py` can show the exact words.
- **Separate decision from discussion.** In meeting notes, a decision is something someone agreed to; everything else is discussion. Record who agreed and when; if it's unclear whether something was decided, it's a question.

## 5. Map

Assign every ledger entry a `section` from the outline, or an exclusion with a reason. Good exclusion reasons are specific: "duplicate of S02-C004-03", "off-topic for this audience: hiring history", "superseded by S03-C001-02 (2026 docs replace 2023 wiki)", "too detailed for a first read; linked in Further reading". Vague reasons ("not needed") fail the check.

The map is where you find the document's real shape. Sections with many entries may need splitting; entries with no home may reveal a missing section.

## 6. Check coverage

After drafting:

```bash
python scripts/coverage_check.py check --work .vanessa/work/<task> DRAFT.md [MORE_DOCS...]
python scripts/coverage_check.py report --work .vanessa/work/<task> DRAFT.md --out ledger-report.md
```
The check fails when an entry is neither cited nor excluded, a chunk was never read, an exclusion reason is vague, or the draft cites an ID that isn't in the ledger (which usually means an invented fact). Fix every FAIL. Deliver the report with the document so the user can audit what you used and what you left out.

## 7. Surfaces

| | Claude Code | Claude Chat |
|---|---|---|
| Chunk reading | parallel subagents, one per chunk or batch | in order, one chunk at a time |
| Progress | files in `.vanessa/work/` | files in the sandbox; save after every chunk |
| Resume | `chunk_source.py status` | `status`, then `next`; ask the user to re-upload sources if the sandbox reset |
| Scanned pages | `--ocr` with Tesseract installed | `--ocr` if Tesseract is present, otherwise look at the rendered page |
