# Copy strategies

Creative options must differ in strategy, not wording. This library is what `scripts/pick_strategies.py` draws from; add rows freely (keep the table format: the script parses rows that start with a backticked id).

Use the strategy as raw material, then ground it in the product's real facts: a "concrete number" option needs a real, sourced number, and a "social proof" option needs real proof. If the product has no proof yet, that strategy is unavailable; say so rather than inventing it.

Formats: `headline`, `tagline`, `cta`, `name` (feature or product names), `hook` (video and social openers), `concept` (campaign), `subject` (email subject lines), `social`, `store` (store subtitle and promo text), `push`, or `all`.

| ID | Strategy | Formats | Skip when | How it works | Risk |
|---|---|---|---|---|---|
| `benefit-led` | Lead with the outcome | all | The benefit is vague or shared by every competitor | State what the reader gets, in their words: "Every receipt filed before you leave the café" | Generic if the benefit isn't specific to this product |
| `problem-led` | Name the pain first | headline, hook, concept, subject, social, store | The reader doesn't feel the problem yet | Open with the moment the reader struggles: "Still typing receipts into a spreadsheet on Sunday night?" | Can sound negative; pair with the fix in the next line |
| `concrete-number` | One sourced number | headline, hook, subject, social, store, push | No credible number exists | A specific figure with its basis: "Reads a receipt in 2 seconds, measured on a mid-range phone" | Unsourced or cherry-picked numbers break trust |
| `curiosity` | Open a question the reader wants closed | headline, hook, subject, social | Reader needs clarity fast (UI, help, transactional email) | Withhold the answer just long enough: "The one expense category auditors always question" | Clickbait if the payoff is weak |
| `social-proof` | Real people already rely on it | headline, store, social, concept | No real customers, reviews, or usage data yet | Real counts, named customers, or quotes with permission | Fake or vague proof is dishonest; never invent |
| `before-after` | Contrast the old way with the new | headline, hook, concept, social | The "before" insults the reader's current choice | Two short beats: "Before: …  Now: …" | Can overclaim the "after" |
| `direct-instruction` | Tell the reader what to do | cta, push, headline, social | The reader isn't ready to act | Imperative verb plus the outcome: "Scan your first receipt" | Pushy without context |
| `playful` | Wit that fits the voice | tagline, name, hook, social, concept | Voice guide is formal, or the moment is stressful (errors, money, health) | A light turn of phrase rooted in the product's world | Jokes travel badly across languages; check the Korean version separately |
| `story-led` | A tiny scene with a person | hook, concept, social | Format has under 15 words | One character, one moment, one change: "Jun snapped the lunch receipt. The report was done before the bill arrived." | Slow; the point must land fast |
| `identity` | Speak to who the reader is | headline, tagline, concept, store | The audience is broad or mixed | Name the group and its value: "For freelancers who bill clients for expenses" | Excludes readers outside the group |
| `objection-first` | Answer the doubt they already have | headline, hook, social, store | You can't truthfully answer the objection | "Yes, it works without a bank login" | Raises a doubt the reader didn't have |
| `demonstration` | Show it working | hook, concept, social | Nothing visual or verifiable to show | Describe a real moment of use that a screen recording can prove | Needs Rebecca's footage; flag it in the visual brief |
| `metaphor` | One fresh comparison | tagline, name, concept | Literal clarity matters more (UI, docs) | Borrow a concrete image from a far domain | Clichés ("a Swiss army knife") read as generated |
| `plain-description` | Say exactly what it is | name, store, cta, headline | Never skip; it's the control option | The literal name or function: "Receipt scanner and expense report" | Can be forgettable; that's the trade |
| `urgency-honest` | A real deadline | subject, push, cta, social | No real deadline exists | Only a true limit: "Beta seats close Friday" | False urgency is a dark pattern |
| `question` | Ask the reader directly | headline, subject, hook, push | Answer is "no" for most readers | A question the reader answers "yes" to | Weak when the answer is obvious |
