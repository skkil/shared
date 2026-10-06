# Surfaces: Claude Code, Claude Chat, Claude Design

Detect the surface from what's available: a shell and a repository → Claude Code; a sandbox with artifact tools and no subagents → Claude Chat; a design canvas → Claude Design.

## Claude Code

What Vanessa does here: docs in the repository (Markdown, MDX), strings and translation files, docstrings, changelogs and release notes, onboarding docs and guides from the codebase.

- **Accuracy:** read the source before documenting it; run every sample and command; record what you ran.
- **Parallel work:** use subagents for source ingestion (one per chunk or subsystem), research (one per question), and the cold-reader test (a fresh subagent that sees only the draft and the reader questions).
- **Files:** `.vanessa/` at the project root for the content system and work folders. Ask before committing anything.
- **Linting:** offer Vale with rules generated from the content system (`content-system.md`); offer a CI step but don't add one unasked.
- **Dependencies:** `pip install -r <skill>/requirements.txt` for PDF work; Tesseract for scanned pages.

## Claude Chat (claude.ai and the desktop and mobile apps)

What Vanessa does here: documents, web pages, HTML and Markdown decks, reviews and copy.

- **Research:** web search and fetch; the browser tool for pages that need a real browser, when it's connected.
- **No subagents:** read long sources in order, saving the ledger after every chunk (`long-source-ingestion.md` §7); run the cold-reader test by quoting the answering sentence for each reader question.
- **Files reset between sessions:** give the user the content system files and the work folder (ledger, exclusions) to keep, and ask for them next time.
- **Delivery:** HTML pages and decks as files, or published as artifacts when the user wants a shareable link; Markdown as files. When the user asks for Word or PDF, use the docx or pdf skill for the file format and keep Vanessa's standard for the words. When the session offers document or slide artifact types and the user asks for one of those, write the content to this standard and use that type.

## Claude Design

What Vanessa does here: copy inside designs and prototypes, written to fit each element's space and character limit.

- Since September 16, 2026, designs can be created inside regular Claude conversations and Claude Code, where skills load normally. Work there when you can.
- The standalone claude.ai/design takes design systems, project context and prompts as inputs; Anthropic's documentation doesn't say it reads skills. If Vanessa isn't loaded there, paste `references/ux-writing.md`, the product glossary, and the voice guide into the project context, and run `readability_check.py limits` on the copy in a Chat session.
- For each element, ask for (or measure) its space and limit; return copy with character counts and, for Korean, the same check (Hangul is wider, so a 20-character English label may need a shorter Korean form, not a longer one).
