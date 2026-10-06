# Knowledge guides from study material

The scenario: the user hands over lecture notes, research papers, textbooks or whole books, and you build a guide from them. The guide is organized by **concept**, not by source; it connects ideas across sources and shows where they disagree. It covers all the sources, with coverage proven by `coverage_check.py`.

## Shape

Follow `assets/templates/knowledge-guide.md`.

1. **What you'll be able to do** after reading, as 3–6 reader questions.
2. **Concept map**: the concepts and how they depend on each other, as a diagram, with a suggested reading order.
3. **One section per concept**, each in the same order:
   - a plain definition in one or two sentences;
   - the intuition: why it works or why it matters;
   - a worked example, fully worked, from the sources;
   - the precise statement (formula, rule, algorithm) with the source excerpt in a dropdown;
   - how it connects to other concepts;
   - where the sources disagree, if they do;
   - common mistakes, only when a source names them;
   - a short self-check (answers collapsed).
4. **Source concordance**: a table of concepts against sources showing which source covers what, with locations. This proves the cross-source synthesis and lets the reader go deeper.
5. **Ledger report and exclusion log.**

## Synthesizing across sources

Map ledger entries to concepts, not to sources. For each concept, gather entries from every source, then write one explanation that uses the clearest definition, the best example, and the most rigorous statement, each cited to where it came from. When sources use different names or notation for the same thing, pick one (glossary), and note the other at first mention: "what Source A calls *churn* (Source B: *attrition*)".

When sources conflict, show both (`sources-and-citation.md` §5): which source, which claim, which is more credible and why (newer, primary, peer-reviewed, or explicitly corrected by the other).

## Learning science to apply

From cognitive load theory (Sweller) and the retrieval-practice literature summarized by Weinstein, Madan and Sumeracki:

- **Worked examples before problems** for novices; fade the worked steps in later examples (expertise-reversal: guidance that helps novices can slow experts, so offer experts a faster path).
- **Retrieval practice**: short self-checks spaced through the guide, answered from memory before revealing the answer. The evidence is strongest for retaining facts; for complex material, pair retrieval with worked examples.
- **Spacing**: revisit each concept's key point briefly in later sections where it's used.
- **Interleaving** helps when learners must tell similar concepts apart; for complex material the benefit is weaker, so use it for discrimination questions only ("Which of these two policies applies here?").
- **Dual coding without redundancy**: pair a diagram with words that add what the diagram can't show; don't caption a diagram by repeating it.
- **Concrete examples** for every abstract idea, from the sources.

## Equations, tables and figures

When a source passage has math, tables or figures, `extract_excerpts.py` renders the page region as an image in the dropdown so nothing is garbled. In your own prose, write equations in MathML (rendered natively by current browsers, works offline) or as plain inline notation for simple cases. Define every symbol right after the equation that introduces it.

## Long books

A 300-page book is around 60–80 chunks. Tell the user the size before starting; read every chunk (`long-source-ingestion.md`). For a "guideline for our team" from a book, the reader brief decides the shape: a team guideline keeps the book's ideas that change how the team works, with the rest in the exclusion log ("background theory; not needed to apply the practice"), not a chapter-by-chapter summary.
