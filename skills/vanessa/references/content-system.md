# The content system: voice guide, glossary, style guide

Rebecca has a design system; Vanessa's equivalent is a content system of three files per product, saved in the project under `.vanessa/`. Read them before every task. They are why ten writers (or ten sessions) sound like one.

## The three files

1. **Voice and tone guide** (`voice.md`, template `assets/templates/voice-guide.md`). Voice is the product's constant personality; tone shifts with the reader's situation. Mailchimp's framing: you have the same voice all the time, but your tone changes with who you're talking to and how they feel. An error message is calmer than a launch announcement; a payment failure is plainer than an empty state. The guide holds 3–5 named voice traits, each with a do and a don't example; a tone map by situation; reading-level targets and limits in a `vanessa-config` block that `readability_check.py` reads; and copy strategies the product never uses.
2. **Terminology glossary** (`glossary.md`). One approved name per concept in each language: the English form, the Korean form, when to use which (English only, Korean only, Korean with English on first use), terms to avoid, and capitalization. `readability_check.py` flags the Avoid column. Acronyms listed here count as defined.
3. **Content style guide** (`style.md`). Mechanics: capitalization of headings and buttons, numbers, dates and times, punctuation, lists, links, code and UI formatting, Korean spacing choices where the rules allow two forms.

## Building them

Build from evidence, then confirm:

1. **Read existing content:** the UI strings in the codebase, the website, the README and docs, Jennifer's PRODUCT.md and PRDs, Rebecca's DESIGN.md voice section, support replies. Note the words the product already uses for each concept, the register, and the habits worth keeping.
2. **Find inconsistencies:** one concept with two names, mixed registers, mixed capitalization. Each becomes a glossary or style decision.
3. **Interview the user briefly** (three questions maximum, with defaults): who the main readers are, three words they'd use for the product's personality, and anything they never want to sound like.
4. **Draft all three files**, citing where each rule came from ("from 14 UI strings in `app/strings.json`").
5. **Show the user the decisions that were real choices** (two names for one concept, a register switch) and let them pick.

If no content system exists, don't block the task: draft one with defaults from this skill, use it, and offer it at delivery.

## Keeping them current

When the user's feedback teaches a new rule ("we never say 'customer', it's 'member'"), add it to the right file immediately, tell them which file changed, and apply it from then on. Give rules short names, the way Toss calls its brevity rule "weed cutting" (잡초 뽑기): reviewers can then say "that's a weed" instead of explaining. Date every change in the file's change log.

## Vale (Claude Code, optional)

To enforce the content system in the repository, generate Vale rules from it:

```
.vale.ini
styles/<Product>/Avoid.yml        existence rule from the glossary Avoid column and banned-en.md FAIL rows
styles/<Product>/Terms.yml        substitution rule: avoid term → approved term
styles/config/vocabularies/<Product>/accept.txt   approved terms and known acronyms
styles/config/vocabularies/<Product>/reject.txt   terms to avoid
```
`.vale.ini` sets `StylesPath = styles`, `MinAlertLevel = suggestion`, `Vocab = <Product>` and `[*.{md,mdx}] BasedOnStyles = Vale, <Product>`. Vale's tokenizer handles Korean poorly, so keep Korean checks in `readability_check.py` and use Vale for English and glossary terms. Offer to add a CI step; don't add one without asking.
