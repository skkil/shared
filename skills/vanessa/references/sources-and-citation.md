# Sources: gathering, judging, citing

Your content comes only from sources. This file says where they come from, how you judge them, how you cite them, and what you do when they disagree or run out.

Contents: 1. Where sources come from · 2. Judging credibility (SIFT) · 3. The source record · 4. Citing precisely · 5. Conflicts · 6. Gaps · 7. Code and commands · 8. Copyright and private excerpts

## 1. Where sources come from

**What the user provides:** files, links, repositories, books, papers, transcripts, notes, and answers in a co-writing interview (cite as "Interview with <name>, <date>").

**What you find:** search the web broadly, then fetch and read pages in full; snippets are not sources. Use the browser tool for pages that need a real browser or a login the user has. In Claude Code, the codebase and its history (commit messages, ADRs, issues) are primary sources for how the system works. If a link fails, search for the source by name; if a fetch returns binary or blocks, try a mirror that hosts the original document, and record which copy you used.

Keep searching until every section of the outline has support. Then stop: more sources than the reader needs is its own failure.

**Prefer primary sources:** official documentation, the codebase itself, standards, peer-reviewed papers, original data, first-hand transcripts, the people who created a method. **Use secondary sources** (reputable textbooks, established publications) to explain or confirm primary ones, not to replace them. **Avoid** content farms, unattributed posts, SEO listicles and AI-generated summaries. A vendor blog is a primary source for what the vendor claims and a weak source for anything else.

## 2. Judging credibility (SIFT)

Use Mike Caulfield's SIFT moves on every source you didn't get from the user. They take about a minute each and work better than reading a page in isolation, because they check the source from the outside.

1. **Stop.** Do you know this site or author? Is it what you assumed? Note your purpose: what claim do you need it for?
2. **Investigate the source.** Read laterally: open other tabs to see who publishes it, their expertise, and their stake in the claim.
3. **Find better coverage.** If the source is weak or you can't tell, trade up to a better source for the same claim instead of propping up the first one.
4. **Trace claims to the original context.** Follow quotes, numbers and figures upstream to where they first appeared, and check they were presented accurately.

Record the result in the source record with the CRAAP fields (Currency, Relevance, Authority, Accuracy, Purpose; Blakeslee, Meriam Library, CSU Chico). CRAAP alone judges a page in isolation, which is why SIFT comes first.

## 3. The source record

One row per source in `sources.jsonl` (`chunk_source.py inventory` creates rows for files; add web sources by hand). Fields: `id` (S01…), `title`, `author`, `date` (publication or last update; mark "file modified" when that's all you have), `url` or `path`, `kind`, `tier` (primary / secondary), `credibility` (one line of SIFT findings), and for long sources the structure.

**Dates matter.** On fast-moving topics (APIs, prices, regulations, AI products, store policies), prefer the newest credible source and show its date in the document: "Apple's product page limits the subtitle to 30 characters (checked 2026-10-06)". A stale source that was right once is the most convincing kind of wrong.

## 4. Citing precisely

Every claim links to its source at a location a reader can open: page, section heading, timestamp, or file and line.

| Source type | Locator form | Example |
|---|---|---|
| Book or PDF | printed page, plus physical page for the script | "p. 9" (`pages=19`) |
| Paper | section, then page | "§3.2, p. 5" |
| Web page | section heading or anchor, and the date checked | "Rate limits, checked 2026-10-06" |
| Transcript | timestamp range and speaker | "00:41:12–00:43:05, Minji" |
| Code | file and line range at a commit | `src/billing/retry.py:40-88 @ 1a2b3c4` |
| Slides | slide number | "slide 14" |
| Interview | person and date | "Interview with the user, 2026-10-06" |

In the draft, put the ledger ID next to the claim (`[S01-C003-07]` or a `data-ledger` attribute on HTML elements). The published form depends on the format: footnote-style links in Markdown, superscript links to a sources list on web pages, a dropdown excerpt in knowledge guides (`web-artifacts.md`). Cite at the claim, not in a pile at the end of a section.

## 5. Conflicts

When sources disagree:

1. Show both claims, each with its citation.
2. Say which is more credible and why: primary over secondary, newer over older on fast-moving topics, the code over the docs about what the code does, a measurement over an assertion.
3. If the difference changes what the reader should do, ask the user to decide and mark the passage `[CONFLICT: S02 vs S05, awaiting decision]` until they do.
4. Record it in the ledger (`status: conflict`, `conflicts_with`). `coverage_check.py` warns when a conflicting entry is cited without its counterpart.

Never resolve a conflict by quietly picking one side; that is a decision, and decisions belong to the user or the source's owner.

## 6. Gaps

If no source covers something the reader needs: search again with different terms, check primary sources the user might have (docs, code, people), then mark `[SOURCE NEEDED: what's missing and why the reader needs it]` and list it in the delivery note with a question. A gap stated plainly is useful; a gap papered over is a defect that ships.

## 7. Code and commands

In Claude Code, read the source before documenting it, and run every code sample and command in a clean shell before shipping it. Record what you ran and the output in the ledger (cite as `ran: <command> @ <commit>, <date>`). If you can't run something (needs credentials, hardware, production), say so next to the sample and in the delivery note. Never present an untested command as tested.

## 8. Copyright and private excerpts

Source dropdowns (`extract_excerpts.py`) copy original passages into the user's document. That's for private study and team use; the user asked for it and their own tooling performs the copy. If a document will be published, replace long excerpts from copyrighted works with links and short quotations, and tell the user. Don't type out long passages of copyrighted text yourself; let the script pull them.
