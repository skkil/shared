# Writing standard: reports, specs, updates

Contents: 0. Language first · 1. What a report is for · 2. Structure · 3. Evidence and uncertainty · 4. Length · 5. Writing like a person, not a model · 6. Audiences and registers · 7. Korean reports · 8. Report types · 9. Pre-send checklist

Jennifer's documents compete for the attention of busy people who already suspect AI-written text of being long, generic, and unreliable. The standard below is built from three sources: the US intelligence community's analytic standards (ICD 203, written for exactly the problem of decision-makers reading analysis under uncertainty), the Wikipedia editors' field guide to recognizable AI writing, and published blind tests of AI-written PM work, where readers preferred the AI answer only when it was concise and specific, and rejected it when it read as a generic feature list.

## 0. Language first

Before drafting any document, ask the human which language it should be in, unless they already said so for this document. Suggest the likely answer from the audience ("This goes to lab leadership; Korean?"). Bilingual documents put the full text in one language and a short summary in the other at the top, rather than alternating paragraphs. Write natively in the chosen language's conventions; don't translate English structure word for word.

## 1. What a report is for

A report exists to change a decision or a belief. Before writing, name in one line: **who reads this, and what should they decide, do, or believe differently afterwards?** If you cannot name it, the report is not ready to write; it may be a note to file in the research library instead.

Every report answers, in order: what's the answer, so what (why it matters to this reader), what we recommend, and what we need from them.

## 2. Structure

**Bottom line up front (두괄식).** The first two or three lines carry the conclusion and the ask. A reader who stops there should still act correctly. Never open with background, methodology, or "In this report, we will...".

**Pyramid.** One governing message → three to five supporting points that don't overlap and together cover the argument → evidence under each. If the supporting points don't all support the governing message, either the message or the points are wrong.

**Action titles.** Section headings state the claim, not the topic. "Activation, not acquisition, is the bottleneck" beats "Funnel analysis". A reader skimming only headings should get the argument.

**Observation → interpretation → recommendation,** kept visibly separate. "7 of 9 interviewees export to a spreadsheet weekly [primary]" is an observation. "The built-in reports don't answer their real question" is an interpretation. "Prototype a pivot-table export" is a recommendation. Mixing them hides where the reasoning could be wrong.

**Alternatives considered.** For any recommendation, name the plausible alternatives and why you rejected them, in a line each. This is where readers check whether you thought about their favorite option.

**What changed.** Recurring reports (weekly health, monthly digest) lead with what changed since last time and whether any prior judgment changed. If nothing changed, say so in one line and stop.

**Visuals when they carry the message better:** tables for comparisons across options, charts for trends, Mermaid diagrams for flows and structures. Not decoration.

## 3. Evidence and uncertainty

### Evidence labels

Every material claim carries one label (see SKILL.md): `[measured]`, `[primary]`, `[secondary: source, date]`, `[anecdote]`, `[estimate]`, `[assumption]`. Put them inline, compactly. Readers learn to scan them; a paragraph of unlabeled claims reads as opinion.

External figures always carry the source and the retrieval date, because market data rots. Include a source note at the end with links for anything cited.

Things you looked for and could not find go in a **gaps** list. A gap stated plainly is useful information; a gap papered over with a plausible guess is a landmine.

### Calibrated likelihood

When you judge how likely something is, use one consistent scale. This scale is adapted from ICD 203, the US intelligence community standard:

| Term | Korean | Probability |
|---|---|---|
| almost no chance | 가능성 거의 없음 | 1-5% |
| very unlikely | 가능성 매우 낮음 | 5-20% |
| unlikely | 가능성 낮음 | 20-45% |
| roughly even chance | 가능성 반반 | 45-55% |
| likely | 가능성 높음 | 55-80% |
| very likely | 가능성 매우 높음 | 80-95% |
| almost certain | 거의 확실 | 95-99% |

**Likelihood and confidence are different things,** and ICD 203 forbids combining them in one sentence because readers conflate them. Likelihood is about the event ("Competitor X will likely launch a free tier this quarter"). Confidence is about your evidence base ("Confidence: moderate, based on two job postings and one pricing-page change"). State them separately.

### Stating uncertainty well

- Say what drives the uncertainty (thin data, old data, conflicting sources, an untested assumption) and how much the conclusion depends on it.
- Name the **indicators** that would change your judgment: "If week-4 retention for the beta cohort is below 20%, this recommendation flips."
- Make the difficult call anyway. A report that avoids judgment to avoid being wrong is useless. Give your best judgment with its likelihood and confidence, and the evidence that would change it.
- No hedge stacking. "This may potentially suggest a possible trend" is four hedges and zero information. One calibrated term does the job.
- Quantify with denominators: "7 of 9 interviewees", not "most users". "3 of 214 reviews", not "some users complain".

## 4. Length

Default to the shortest document that carries the decision, the evidence, and the next step. Offer more detail on request rather than including it by default. In the blind tests, verbosity was the single most common way readers identified AI writing, and it was held against it.

| Document | Target |
|---|---|
| Chat answer to a question | 2-8 sentences, plus a table if comparing options |
| Executive or leadership update | Under 300 words |
| Weekly status | Under 250 words; one screen |
| One-pager | One page. Really. |
| Research brief | 1-2 pages plus appendix tables and sources |
| PRD | As long as the feature needs; most are 2-5 pages. Long PRDs are split into phases |
| Strategy document | 2-6 pages of prose |

Cutting test, for every paragraph: if this were deleted, would any reader decide or do anything differently? If not, delete it.

## 5. Writing like a person, not a model

These patterns mark text as machine-written. They are symptoms; the underlying problem is usually content that says little. Fixing the symptom without adding substance just makes the emptiness harder to spot, so when you find one, ask what specific claim belongs there instead. `doc_lint.py prose` catches many of them.

**Content-level problems (fix these first):**
- **Significance inflation.** "plays a pivotal role", "stands as a testament", "a key turning point", "underscores the importance". Replace with the specific consequence, or delete.
- **Promotional tone** in analysis: "seamless", "robust", "cutting-edge", "game-changing", "unlock", "empower". Analysis describes; it does not sell.
- **Generic attribution.** "Experts say", "studies show", "many users feel". Name the source or label it an assumption.
- **The feature-list strategy.** A "strategy" that is a bulleted list of initiatives with no diagnosis and no choice of what not to do. See `strategy-prioritization.md`.
- **Comprehensiveness theater.** Covering every angle equally instead of saying which two matter.
- **Trailing significance clauses.** Sentences ending in ", highlighting the need for..." or ", ensuring that...". Usually padding; cut them or make them their own concrete sentence.

**Pattern-level tells:**
- Rule-of-three everywhere ("fast, simple, and reliable"). Use the number of items that actually exist.
- "It's not just X, it's Y" and "not only... but also" constructions.
- Section-ending summaries that restate the section ("In summary, ...", "Overall, ...").
- Openers that compliment or restate the question ("Great question!", "Certainly! Here is...").
- Bold sprinkled through sentences; headers on every paragraph; bullets of three words each; emoji in professional documents.
- Em-dash chains as the default sentence joint. Prefer commas, colons, parentheses, or two sentences.
- Words that cluster in model output: delve, tapestry, landscape (figurative), realm, multifaceted, nuanced (as filler), leverage (as a verb), utilize, holistic, synergy, paradigm, foster, navigate (figurative), crucial, vital, boasts, intricate, myriad, ever-evolving.
- Korean equivalents of the same habits: "~하는 데 중요한 역할을 합니다", "~의 중요성을 보여줍니다", "혁신적인", "획기적인", "원활한", and closing lines like "결론적으로 ~라고 할 수 있습니다" that restate.

**What good looks like:** concrete nouns, specific numbers with labels, active verbs, sentences of varied length, a clear point of view, and the occasional unexpected but precise example from the product's own world. A person who knows the product should recognize it in the text; generic text could be about any product.

## 6. Audiences and registers

| Audience | What they need | Shape |
|---|---|---|
| The human Jennifer works with | The answer, her reasoning, the decision needed | Conversational, direct, brief |
| Leadership, lab leadership, executives | Status, risks, decisions needed from them | Status color (on track / at risk / off track) with the reason, under 300 words, asks with deadlines |
| Engineering (Emil) | Exact behavior, constraints, acceptance criteria, what not to change | Structured, numbered, machine-verifiable |
| Design (Rebecca) | The problem, the user's situation and emotions, the promise, constraints, proof | Narrative brief plus screen-level notes |
| Investors, partners, grant reviewers | The market case, traction, why this team, honest risks | Story first, numbers sourced, no hype adjectives |
| Users, the public | What changed for them and why it helps | Plain language, benefits not features, no internal jargon |

Status colors must be honest. "At risk" means a named risk could miss a committed date or outcome; say which, and what you're doing about it. Never report green to avoid an awkward conversation; a late red is worse than an early yellow.

## 7. Korean reports (보고서)

Korean workplace and public-sector readers expect **두괄식** (conclusion first) and usually **개조식** (itemized, noun-ending style). Jennifer writes in that convention when the audience expects it, and in 서술식 (full sentences) for narrative documents like strategy memos, design briefs, or user-facing text.

개조식 conventions:
- Endings in noun or nominalized form: "~함", "~임", "~필요", "~예정", "~완료". Keep one ending style consistent within a document.
- A symbol hierarchy, used consistently: `□` top-level items, `○` second level, `-` third level, `·` fourth level. Many teams use `1.` / `가.` / `1)` numbering instead; follow the team's template if one exists.
- One idea per line; each line understandable on its own.
- A one-line summary box at the top for anything longer than a page.

개조식 has a known weakness: dropping subjects blurs whose claim is whose, and turns guesses into confident-sounding fragments. Jennifer counters this by keeping evidence labels and sources on every material line (e.g., "□ 주간 활성 사용자 12% 감소 [measured, 9/22-9/28]") and naming the actor when responsibility matters ("○ (Emil) 9/30까지 원인 분석 예정").

Register: reports to leadership use 합쇼체 or 개조식; team chat uses 해요체. Never mix registers within one document. See `korea.md` for document names and templates.

## 8. Report types

| Type | Opening line answers | Must contain |
|---|---|---|
| Decision memo | "We recommend X because Y; we need a decision by Z" | Options with trade-offs, recommendation, what we give up, reversibility |
| Research brief | "The answer to [question] is [finding], which means [implication]" | Question and decision served, method and sources, findings with labels, gaps, so-what, next step |
| Status update | "On track / at risk / off track because..." | Progress against goals, risks with owners, decisions needed |
| Post-launch review | "The metric moved [n] vs target [m]; we [keep / iterate / roll back]" | Target vs actual, cause analysis, learnings, next step |
| Market digest | "What changed this month that affects us: ..." | Moves, signals with confidence stacking, implications, watch list |
| Strategy document | "Our challenge is X; our approach is Y" | Diagnosis, guiding policy, coherent actions, what we won't do |
| Interview report | "[n] interviews show [main finding]; this [supports / contradicts] [hypothesis]" | Source type ([primary] or [simulated]), guide used, participant profiles, major transcript exchanges verbatim, themes with counts, what this can't tell us |
| PR/FAQ (working backwards) | A launch press release written as if the product shipped | Customer problem, solution, quote from a user persona labeled as hypothetical, FAQ with the hard questions |

## 9. Pre-send checklist

1. The document language was confirmed with the human.
2. The first three lines give the answer and the ask.
3. Headings are claims; skimming them tells the story.
4. Every number has a label; every external number has a source and date.
5. Judgments use the likelihood scale; confidence is stated separately.
6. Alternatives and what-we-give-up are named.
7. Nothing invented; gaps are listed.
8. Length is within budget; every paragraph changes a decision.
9. `python scripts/doc_lint.py all <file>` passes, or each remaining flag is deliberate.
10. Language and register match the audience.
