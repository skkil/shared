# English phrases that cost the reader

Every row here is a pattern that makes English text slower to read or less trustworthy. Most come from Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup) and the style guides in `standard.md`. `scripts/readability_check.py` reads this table directly, so a row you add here is enforced on the next run.

Treat a hit as a question, not a verdict. The real problem is usually a sentence that says little; deleting the word without adding substance only hides that. When a word is the precise technical term (a "robust" estimator, a "landscape" orientation), keep it and add `<!-- vanessa-allow: banned-en -->` on that line.

Levels: **FAIL** blocks delivery. **WARN** needs a fix or a reason. **INFO** is worth a second look.

## Chat residue and filler openers

These never belong in a deliverable.

| Pattern | Level | Why | Instead |
|---|---|---|---|
| `\b(great\|good\|excellent) question\b` | FAIL | Chat residue | Delete |
| `^(certainly\|sure\|absolutely\|of course)[!,.]` | FAIL | Chat residue | Start with the content |
| `\bi hope (this\|that) helps\b` | FAIL | Chat residue | Delete |
| `\bas an ai\b\|\bas a language model\b` | FAIL | Chat residue | Delete |
| `\bas of my (last )?(knowledge\|training)` | FAIL | Model disclaimer in a document | State the source date instead |
| `\bin today'?s (fast-paced\|ever-changing\|digital\|modern) (world\|landscape\|era\|age)` | FAIL | Empty opener | Open with the point |
| `\blet'?s (dive\|delve) (in\|into)\b` | FAIL | Staged run-up | Open with the point |
| `\bclick here\b` | FAIL | Link text must say where it goes | Name the destination |
| `\b(it'?s\|it is) (worth noting\|important to note\|worth mentioning) that\b` | WARN | Throat-clearing | State the fact |
| `\bneedless to say\b` | WARN | Then don't say it | Delete or state it plainly |

## Inflated significance and vague authority

| Pattern | Level | Why | Instead |
|---|---|---|---|
| `\bplays? an? (crucial\|vital\|pivotal\|key\|significant\|important) role\b` | WARN | Significance inflation | Name the concrete effect |
| `\bstands? as an?\b` | WARN | Significance inflation | Say what it is or does |
| `\ba testament to\b` | WARN | Significance inflation | Name the evidence |
| `\bunderscores? the (importance\|need\|significance)\b` | WARN | Significance inflation | Say what follows from it |
| `\b(enduring\|lasting) legacy\b\|\brich (cultural )?heritage\b` | WARN | Wikipedia's named tell | Cut, or give the fact |
| `,\s*(highlighting\|underscoring\|emphasizing\|showcasing\|reflecting\|ensuring\|enabling\|demonstrating) (the\|its\|their\|a\|an\|how)\b` | WARN | Shallow -ing rider | Make it its own concrete sentence or cut it |
| `\b(studies\|research) (show\|shows\|suggest\|suggests)\b` | WARN | Vague attribution | Cite the study |
| `\b(experts\|analysts\|industry experts\|many (users\|people\|developers)) (say\|agree\|believe\|feel)\b` | WARN | Vague attribution | Name who, or cut |
| `\bit is widely (known\|believed\|accepted)\b` | WARN | Vague attribution | Cite or cut |

## Rhetorical templates

| Pattern | Level | Why | Instead |
|---|---|---|---|
| `\b(it'?s\|this is\|that'?s\|it is) not (just\|only\|merely\|simply) [^.]{1,60}[,;—–-]\s*(it'?s\|it is\|but)\b` | WARN | Negative parallelism | State the positive claim directly |
| `\bnot only\b[^.]{1,80}\bbut also\b` | WARN | Negative parallelism | Two plain sentences, or one claim |
| `^(in summary\|to summarize\|in conclusion\|overall\|to sum up)\b` | WARN | Recap of what the reader just read | Delete; end on the next step |
| `\bhere'?s (the thing\|why\|what\|how)\b` | INFO | Staged run-up | Lead with the point |
| `\b(may\|might\|could) (potentially\|possibly)\b\|\bpossibly (suggest\|indicate)` | WARN | Stacked hedges | One calibrated word, or a number |

## Words that cluster in generated text

Fine once, a tell when they gather. Read the sentence: does it name something concrete?

| Pattern | Level | Why | Instead |
|---|---|---|---|
| `\bdelve[sd]?\b\|\bdelving\b` | WARN | AI vocabulary | look at, explain, cover |
| `\btapestry\b\|\brealm\b\|\bmyriad\b\|\bmultifaceted\b` | WARN | AI vocabulary | Say the specific thing |
| `\bseamless(ly)?\b` | WARN | Promotional and unmeasurable | Say what the user no longer has to do |
| `\b(unlock\|elevate\|empower\|supercharge\|revolutioni[sz]e)[sd]?\b` | WARN | Sales verb | Say the concrete result |
| `\bleverag(e\|es\|ed\|ing)\b` | WARN | Jargon verb | use |
| `\butili[sz](e\|es\|ed\|ing)\b` | WARN | Formal for "use" ("CPU utilization" is a metric name and passes) | use |
| `\b(game-?chang(er\|ing)\|cutting-edge\|groundbreaking\|transformative\|next-generation\|state-of-the-art)\b` | WARN | Hype | The measurable difference, with its source |
| `\b(holistic\|synergy\|paradigm\|foster(s\|ing)?\|ever-evolving\|intricate\|boasts?)\b` | WARN | AI vocabulary | Plain word or the specific fact |
| `\b(navigate\|navigating) (the\|this\|these) (complexit\|challeng\|landscape)` | WARN | Figurative filler | Say what the reader has to do |
| `\b(the\|this\|today'?s) [a-z]+ landscape\b` | WARN | Figurative filler | Name the market, field, or set of tools |
| `\b(embark\|journey)\b` | INFO | Figurative filler outside travel | start, process, path |
| `\b(crucial\|vital\|pivotal\|robust\|comprehensive)\b` | INFO | Inflated adjectives; legitimate as technical terms | Keep only if it carries a defined meaning |
| `^(additionally\|moreover\|furthermore),` | INFO | Connector that often hides a list | Merge, or start with the new point |

## Instructions and UI text

| Pattern | Level | Why | Instead |
|---|---|---|---|
| `\b(simply\|just\|easily\|obviously\|of course)\b(?=\s+\w+)` | INFO | Tells a stuck reader the task is trivial | Delete |
| `\b(easy\|effortless\|painless)\b` | WARN | Claim the reader judges, not you | Show the steps or the time it takes |
| `\bplease (note\|be aware)\b` | WARN | Filler before a warning | State the warning |
| `\b(an error has occurred\|something went wrong)\b` | WARN | Error that says nothing | What happened, why, and what to do |

## Marketing claims that need a source

`marketing-copy.md` requires a source for these. Without one, cut them. The fifth column limits a row to some profiles; these rows run only with `--profile marketing`, because "guarantees ordering" is a precise technical claim in a developer doc.

| Pattern | Level | Why | Instead | Profiles |
|---|---|---|---|---|
| `#1\b\|\bnumber one\b\|\bbest-in-class\b\|\bworld-class\b\|\bindustry-leading\b` | WARN | Superlative claim | Cite the ranking, or cut | marketing |
| `\b(the )?(fastest\|most (advanced\|powerful\|accurate\|secure\|trusted))\b` | WARN | Comparative claim | Cite the benchmark and date, or cut | marketing |
| `\b(guarantee[sd]?\|100% (secure\|safe\|accurate))\b` | WARN | Absolute claim, often a legal risk | Flag for legal review | marketing |
