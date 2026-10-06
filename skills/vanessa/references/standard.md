# The standard: understood the first time

Every deliverable passes this before it leaves you. The rules below are English defaults; `language-ko.md` adapts them for Korean. Each rule names its source so you can defend it, and the measurable ones are enforced by `scripts/readability_check.py`.

Contents: 1. Writing rules · 2. Measurable checks and targets · 3. Writing so it doesn't read as generated · 4. Final read

## 1. Writing rules

**Point first.** The conclusion, decision, or answer goes in the first lines; background follows. Readers on screens read a fraction of the page and lean on its first lines (NN/g eye-tracking, 2006 and 2017), and Microsoft's guide says to lead with what matters most and front-load keywords. A reader who stops after two lines should still act correctly.

**Headings that inform.** A heading states the content ("Deploys fail without this key"), not a label ("Configuration"). When headings say something, readers scan them in a "layer-cake" pattern and dip in where it's relevant; when they don't, readers fall back to the F-pattern and miss most of the page (NN/g). Avoid starting sibling headings with the same word: readers skip repeated openers ("bypassing" pattern). Sentence case, no end punctuation (Google, Microsoft).

**One idea per paragraph,** about three sentences. Flag at more than four. GOV.UK caps paragraphs at five sentences; the tighter default suits screens and Korean readers alike.

**Plain sentences.** Short, active voice, "you" for the reader, present tense, conditions before instructions ("To deploy, run…"), (Google). Use the passive when the outcome matters more than who acted, or when it keeps the focus on the user (GOV.UK's stated exceptions).

**Define every term on first use.** Assume the reader knows no acronym. English: "single sign-on (SSO)". Korean: see `language-ko.md`. Define specialist terms in plain words where they first appear (GOV.UK).

**One name per concept.** If it's a "workspace", it's always a "workspace". Synonyms for variety make readers wonder whether two things exist, and they break translation (Mailchimp, Microsoft). The glossary holds the one name.

**Clear steps.** Numbered, one action per step, the expected result when it helps the reader confirm they're on track.

**The right shape.** Tables for comparisons, numbered lists for sequences, diagrams for relationships, prose for reasoning. Don't restate a diagram in words beside it: the duplicate adds load without adding understanding (Sweller's redundancy effect).

**Cut what doesn't serve the reader.** No intro that restates the title, no recap of what was just said, no "In this guide, we will…". For every paragraph ask: if it disappeared, would the reader decide or do anything differently?

**Use the reader's words.** Name things the way users name them, not the way the system is built ("notifications", not "webhook config"); check search terms or support tickets when you can (GOV.UK).

**Requirement words mean one thing each:** *must* for a hard rule, *need to* for a step in a process, *can* for an option (GOV.UK). In Korean: ~해야 합니다 / ~해야 해요 for must, ~할 수 있습니다 for can.

## 2. Measurable checks and targets

These make the standard testable. Targets live in the product's voice guide (`vanessa-config` block), so the user can change them per product; the values below are the defaults the script uses.

| Check | English default | Korean default | Source of the number |
|---|---|---|---|
| Sentence length (WARN above) | 25 words | 17 어절 | GOV.UK's 25 words. Korean: measured. On parallel Kubernetes concept pages, Korean averages 10.9 어절 per sentence against 16.0 English words (ratio 0.68); 25 × 0.68 ≈ 17, which is about the 90th percentile of 1,060 sentences of well-regarded Korean technical docs. |
| Paragraph length (WARN above) | 4 sentences | 4 sentences | GOV.UK caps at 5; one idea per paragraph |
| Reading grade | 8 for end users and marketing, 10 for internal readers, not scored for developer docs | no grade formula | Flesch-Kincaid. Developer docs score high because of necessary terms, so sentence length and plain words matter more there. No validated Korean grade formula exists (`language-ko.md`), so Korean uses length and structure proxies. |
| Comma density (WARN above) | not checked | 0.8 per sentence | LLM-generated Korean uses more commas than human writing (KatFishNet, ACL 2025) |
| Em-dash density (WARN above) | 0.7 per 100 words | n/a | Microsoft uses em dashes itself; only heavy use is a tell (Wikipedia: Signs of AI writing) |
| Banned phrases | `banned-en.md` | `banned-ko.md` | Each row cites its reason |
| Acronyms | Defined at first use | Defined at first use | Microsoft, Google, GOV.UK |
| Glossary conflicts | Avoid-column terms | Avoid-column terms | The product glossary |
| UI and store limits | per field | per field | `ux-writing.md`, `marketing-copy.md`; `readability_check.py limits` |

Run it:

```bash
python scripts/readability_check.py check draft.md --audience end-user --profile doc
python scripts/readability_check.py check strings.md --lang ko --profile ui
python scripts/readability_check.py limits store-listing.json
```

The scores are signals. A passing report on a document whose structure confuses still fails; a deliberate long sentence in an explanation can stay. Mark a deliberate exception on its line with `<!-- vanessa-allow: RULE -->` and mention it in the delivery note.

## 3. Writing so it doesn't read as generated

Readers now discount text that looks machine-written, and detection tools misfire on careful human writers too. So the goal isn't to dodge a detector. It's to remove what makes generated text costly to read: it says less per sentence, sounds certain about things nobody checked, and could be about any product.

What gives generated text away, and what you do instead (from Wikipedia's "Signs of AI writing", the Korean findings in KatFishNet, and the community catalogs reviewed in the research log):

- **Content-level (fix first).** Significance inflation ("plays a pivotal role"), promotional adjectives in explanations, vague attribution ("experts say"), coverage of every angle at equal weight. Replace each with the specific fact, its source, or nothing.
- **Template rhetoric.** "It's not just X, it's Y"; reflexive groups of three; a dramatic one-line closer; a heading repeated in the first sentence; a section that ends by summarizing itself. Use the number of items that exist; state the claim directly.
- **Rhythm by rule.** Every sentence the same length, three sentences in a row starting the same way, a dash in every paragraph. Vary length because the content varies, not to look varied.
- **Formatting by rule.** Bold scattered through sentences, headers on every short section, bullets of three words each, emoji in documents. Format only what a scanner needs.
- **Chat residue.** "Great question", "I hope this helps", "Let's dive in", knowledge-cutoff disclaimers.
- **Korean specifics.** More commas than human Korean, noun-heavy sentences with few verbs, stacked "~적" words, 번역투, closing lines like "결론적으로 ~라고 할 수 있습니다" (`language-ko.md`).

What human professional writing has that generated text lacks: concrete nouns from this product's world, numbers with their source, a clear point of view, the occasional precise example only someone who read the sources would know, and the courage to leave things out. If a sentence could appear unchanged in a document about a different product, rewrite it or cut it.

## 4. Final read

After the scripts are quiet, read the draft once as its reader, in their setting (phone, incident, meeting), and answer:

1. Do the first two lines give the point?
2. Reading only the headings, do I get the argument?
3. Is any term used before it's defined, or named two ways?
4. Is there a sentence I had to read twice?
5. Does every claim have a citation, and does every gap say `[SOURCE NEEDED]`?
6. What could I delete without the reader missing it? Delete it.
