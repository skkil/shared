# Writing clear English

How clear English expository writing works, for every English deliverable. The defaults come from Google's developer documentation style guide, the Microsoft Writing Style Guide, GOV.UK's content design guidance and Digital.gov's plain-language guidelines; where they disagree, the product's voice guide decides and the conflict is noted below.

## How English carries meaning

**The point goes first, at every level.** First section of the document, first sentence of the paragraph, first words of the heading. Readers sample the start and decide whether to continue.

**Paragraphs** open with a topic sentence that makes a claim; the rest supports it. If the support doesn't fit the claim, the paragraph is two paragraphs.

**Sentences** carry one main idea, with the subject and verb close together and early. Push long qualifications into a second sentence or a list.

**Verbs do the work.** Nominalizations ("perform an installation of", "make a determination") hide the action and lengthen the sentence; GOV.UK singles out -ion and -ment words. Turn them back into verbs: "install", "decide".

**Formality** shows mostly through word choice and contractions. Microsoft encourages contractions ("it's", "you'll") for a friendly voice; GOV.UK avoids negative contractions ("can't", "don't") because some readers misread them. Default: positive contractions yes, negative contractions yes, unless the voice guide sets `"negative_contractions": "avoid"`.

## Do and don't

| Don't | Do | Why |
|---|---|---|
| In order to configure the settings, it is necessary for you to open the dashboard. | To change settings, open the dashboard. | Condition first, verb first, no filler (Google, Microsoft) |
| The configuration of the backup schedule is performed by the operator. | The operator sets the backup schedule. | Active voice names who acts |
| There are three options that you can choose from. | Choose one of three options. | "There are" delays the point (Microsoft) |
| Users can easily export reports. | Export a report from **Reports > Export**. | "Easily" is a claim the reader judges; show the path |
| Leverage the API to facilitate data synchronization. | Use the API to sync data. | Short, common words (GOV.UK) |
| This guide will walk you through the process of setting up… | Set up X in about 10 minutes. | Point first; no meta intro |
| It's not just fast, it's reliable. | It answers in under 200 ms at the 99th percentile [S02-C001-04]. | Specific and sourced beats rhetorical |

## Mechanics (defaults; the style guide overrides)

- **Sentence case** for titles, headings, buttons and labels (Google, Microsoft).
- **Serial comma** in lists of three or more (Google, Microsoft).
- **Numbers:** numerals for 10 and above and for all measurements; spell out zero through nine in running text.
- **Dates:** unambiguous: "October 6, 2026" in prose; ISO `2026-10-06` in tables and logs (Google).
- **Code font** for code, commands, file names, keys and literal values; **bold** for UI element names (Google).
- **Link text** describes the destination; never "click here" (Google, GOV.UK).
- **Em dashes:** closed (no spaces), and rare. One in a page is style; one per paragraph is a tell.

## What makes English read as machine-written

See `standard.md` §3 and `banned-en.md`. The short version: inflated significance, promotional adjectives in explanations, vague attribution, negative parallelism, reflexive triads, -ing riders ("…, highlighting the need for…"), uniform rhythm, and recaps. Fix the content first; a sentence with nothing specific in it can't be saved by swapping words.

## Writing for a global or translated audience

When text will be translated or read by non-native readers (Google "Global audience", Mailchimp "Writing for translation"): keep "that" and articles even where optional, avoid idioms and phrasal-verb stacks, use one term per concept, don't build sentences around wordplay, and keep UI strings whole (no sentences assembled from fragments, which breaks other languages' word order).
