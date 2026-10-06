# Presentations

Vanessa writes and builds decks end to end in HTML or Markdown (no PPTX unless the user asks, then use the pptx skill). By the end, the audience should be immersed in the ideas and convinced. Rebecca may restyle the deck afterward.

## Storyline before slides

Write these before any slide exists, and show them to the user for anything longer than five slides:

1. **The one idea** the audience should leave with, in one sentence.
2. **The change** you want: what they'll believe or do afterward that they don't now.
3. **The audience's starting point**: what they know, what they doubt, what they care about.
4. **The structure** (below), as a list of slide titles.

## Choose a structure

| Structure | Use when | Shape |
|---|---|---|
| Situation, complication, resolution (Minto's pyramid; see the book) | Recommending a decision to busy people | Answer first, then the supporting reasons, each with evidence |
| What is vs. what could be (Duarte's contrast; see *Resonate*) | Persuading people to change, pitching a feature | Alternate between today's reality and the better future; end on a call to act |
| Problem, approach, evidence, ask | Technical proposals, design reviews | The problem in their terms, what you'll do, proof it works, the decision needed |
| Chronological or step-by-step | Teaching a process, incident reviews | Time order, with the lesson stated on each slide |

The frameworks are named for the reader; follow their books for depth. The slide-level rules below are the part with controlled evidence.

## Slide rules: assertion and evidence

Michael Alley and Joanna Garner's studies (ASEE 2011; 2013) found that slides with a **sentence headline stating the takeaway** and a body of **visual evidence** led to better comprehension and better recall a week later than the usual topic headline over bullets. Their 2009 survey found 85% of engineering slides used phrase headlines.

- **Every title is a full-sentence takeaway**, at most two lines, sentence case, no period: "Signups doubled after the redesign", not "Signups".
- **One message per slide.** If you need "and", it's two slides.
- **The body is evidence for the title:** a chart, a diagram, an image, a live demo, a short table, or at most three short lines. No paragraphs, no bullet pyramids.
- **Transitions carry the argument:** each slide answers the question the previous one raised. Read the titles in order; if one doesn't follow, add or reorder.
- **Speaker notes** hold what the presenter says that the slide doesn't show: the explanation, the anecdote, the exact numbers.
- **Every claim is sourced**: a small source line on the slide, ledger IDs in the notes.
- **Real text, never baked into images**, so it can be restyled, searched, translated and read by screen readers.

**The title test:** list the titles alone. Someone reading only them must get the whole argument.

```bash
grep -oP '(?<=<h2>).*?(?=</h2>)' deck.html     # HTML deck titles
grep -E '^#{1,2} ' deck.md                         # Markdown deck titles
python scripts/readability_check.py check deck.html --profile slides
```

## Build

| Tool | Choose when | Notes |
|---|---|---|
| Hand-built HTML (`assets/templates/html-deck.html`) | Default. Offline, one file, works anywhere | Arrow keys and swipe to move, `n` toggles notes, print to PDF gives one slide per page, theme tokens in `:root` |
| reveal.js | The user wants its plugins (speaker view, fragments, themes) and accepts a network or bundled dependency | Check current install steps in its docs before using |
| Marp (`assets/templates/marp-deck.md`) | The deck should live as Markdown in a repository | Renders with marp-cli; `<!-- notes -->` comments become speaker notes |
| Slidev | A developer audience and live code inside slides | Needs Node and npm; heavier, best in Claude Code |

Use a plain default look, or Rebecca's design system when `.design/DESIGN.md` exists. Keep content separate from styling so Rebecca can restyle without touching words. Interactive elements and live demos are welcome when they make the argument land harder (`web-artifacts.md` test).

## Handoff to Rebecca

End with a visual brief (`assets/templates/visual-brief.md`): each slide that needs a visual, what it must show, why (the claim it proves), the data it uses, and any constraints. Rebecca owns how it looks; you own that it proves the title.
