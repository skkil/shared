# Ideation: what to fix, add, or remove

Contents: 1. Why ideation needs a protocol · 2. Three living lists · 3. The idea session protocol · 4. Far-domain analogies · 5. Lenses and techniques · 6. One-card pitch · 7. Portfolio balance and honest killing · 8. Brainstorming as a thinking partner

## 1. Why ideation needs a protocol

Language models generate ideas that are individually decent but collectively repetitive. The research is consistent on this:

- Pools of ideas from GPT-4 were measurably less diverse than ideas from groups of people, and the idea space got exhausted faster. Multi-step (chain-of-thought) prompting raised diversity close to the human level, and ideas from different prompting strategies overlapped little, so pooling strategies helps (Meincke, Mollick & Terwiesch, Wharton, 2024).
- In a study with 100+ researchers, LLM ideas were rated more novel than experts' ideas but slightly less feasible; the model's diversity fell off as it generated more, and it was unreliable at judging its own ideas (Si, Yang & Hashimoto, Stanford, 2024).
- Alignment training causes "mode collapse" toward typical answers, partly because human raters prefer familiar text. Asking for several responses with their probabilities, and sampling from the low-probability tail, raised diversity 1.6-2.1x in creative tasks without hurting accuracy (Verbalized Sampling, Zhang et al., 2025).
- Writers using AI ideas produced better individual work but more similar work as a group (Doshi & Hauser, Science Advances, 2024). Left alone, an AI teammate pulls a team's ideas toward the middle.
- Problem solvers from distant, analogous fields produced substantially more novel solutions than experts from the target market, though less immediately usable ones; the farther the field, the stronger the effect, and it was strongest among the most novel ideas (Franke, Poetz & Schreier, Management Science, 2014).

So Jennifer never brainstorms with a single "give me 10 ideas" pass. She injects randomness from outside the model (the lens roll and a randomly drawn far domain), borrows mechanisms from fields that have nothing to do with the product, generates in stages, deliberately samples the tail, pools across strategies, deduplicates, and leaves feasibility and final judgment to evidence, Emil, and the human.

## 2. Three living lists

Keep three lists per product in `PRODUCT.md` and propose a balanced mix from them, not just new features.

- **Fix:** friction, bugs, confusing flows, drop-off points. Sources: issues, reviews, support, analytics funnels, and Jennifer's own walkthrough of the product (read the routes and screens, try the main flow, note every hesitation).
- **Add:** capabilities, segments, integrations, ways to make money.
- **Remove:** features few people use, complexity that slows everyone down, anything whose maintenance cost exceeds its value. Subtraction is the most underused move in product work; propose at least one removal per opportunity review.

## 3. The idea session protocol

**Step 1: Load context.** Ideas from thin context come out generic; this is the main failure mode, and more sampling does not fix it. Before generating, write down: the outcome being pursued, the target segment, current numbers, constraints (team size, stack, budget, timeline), what has been tried and rejected (from `PRODUCT.md`), and what competitors do. If any of these is unknown and would change the ideas, ask.

**Step 2: Roll lenses.** Draw lenses from the deck with external randomness so sessions don't repeat:

```bash
python scripts/lens_roll.py --n 4 --product sync           # 4 lenses, avoids recently used ones
python scripts/lens_roll.py --n 3 --category business      # restrict to a category
python scripts/lens_roll.py --list                          # see the deck
```

Every session also draws at least one **far domain** (section 4), a field with nothing obvious in common with the product:

```bash
python scripts/lens_roll.py --n 4 --far 2 --product sync    # 4 lenses + 2 far domains
python scripts/lens_roll.py --far 3 --only-far             # far domains only
```

The script records what was drawn in `lens_history.json`. Report the seed so a session can be reproduced. If the human names a lens or a domain ("what would an art museum do?"), use it in addition to the rolled ones.

**Step 3: Generate in stages, per lens and per far domain.** Run the far-domain transfer in section 4 for each drawn domain. For each lens, separately:
1. Restate the lens as a question about this product ("Constraint flip: what if sync had to work fully offline?").
2. Generate 4-6 short raw ideas (one line each). No evaluation yet.
3. For one or two lenses, do a tail pass: generate five more ideas with an estimated probability for each (how likely a typical PM would propose it), and keep only those below roughly 0.10. Typical ideas will also come from other lenses; the tail pass is where surprises come from.

**Step 4: Pool and deduplicate.** Merge all lenses' ideas. Collapse near-duplicates (same mechanism, different wording) and note how many unique ideas remain. If one mechanism dominates the pool, the session collapsed; roll two more lenses from different categories and repeat Step 3 for those.

**Step 5: Critique and improve.** For each idea, check: Is it obvious (would it appear in a top-10 listicle)? Does it rely on magic (a step that "just works" with no mechanism)? Does it ignore base rates (an approach that usually fails)? Is it actionable (could work start this week)? Rework the weak ones or drop them. Steelman before dropping anything unusual.

**Step 6: Converge.** Quick-screen the survivors with the market-value test (one line per question). Write one-card pitches for the top 3-5. Score with `score.py` if the human wants a ranking. Feasibility questions go to Emil, not to Jennifer's guess.

**Step 7: Log.** Append every idea to `ideas/journal.md` with its lens, date, and fate (proposed / parked / rejected + reason). Rejected ideas go to the tried-and-rejected log in `PRODUCT.md`, so they don't resurface without new evidence.

Show the human the final shortlist, not the whole pool. Mention the pool size and offer the parked ideas if they want to dig.

## 4. Far-domain analogies

The most novel ideas come from fields that solved a structurally similar problem in a completely different world. A sync tool can learn from an art museum's conservation records; a team dashboard from a physics lab's run logbook; onboarding from a theme park queue. Distance is the point: the far domain hasn't inherited the target market's assumptions. The cost is that raw transfers are less immediately usable, so the protocol ends with a translation step.

**Transfer protocol** (for each drawn domain):

1. **Abstract the product's problem** into domain-free language. "Users lose track of which file version is current" becomes "many people change a shared artifact over time, and anyone must be able to tell which state is authoritative and how it got there." Abstraction is what lets the far domain connect; a problem stated in the product's jargon only finds the product's usual answers.
2. **Immerse briefly in the far domain.** List its roles, rituals, artifacts, spaces, rules, and failure modes. What does a physics lab actually do every day? Logbooks, calibration runs, shift handovers, sign-off before a beam run, a control room with alarms ranked by severity. Use what you know; if the domain matters and your knowledge is thin, do a quick search (a professional's day-in-the-life, a training manual, a glossary).
3. **Find the mechanism, not the surface.** For each practice, ask what problem it solves there and why it works. A museum's provenance record works because ownership disputes are settled by an unbroken chain of custody. A kitchen brigade's mise en place works because preparation is separated from execution under time pressure. The mechanism is what transfers; the costume (velvet ropes, chef hats) doesn't.
4. **Map the mechanism onto the product's job.** "Provenance chain" → every file shows an unbroken history of who changed what and from which device, and conflicts are resolved by the chain, not by timestamps. Generate 2-4 ideas per domain.
5. **Translate for usability.** Far-domain ideas arrive less practical. For each, write the most practical version a small team could ship and test, without losing the mechanism. Keep both versions in the journal; sometimes the wild version is right two years later.
6. **Check the user's seat.** Would the actual user recognize this as solving their problem, in their words? If the idea only makes sense to someone who knows the analogy, rework or drop it. Users don't need to know the idea came from a museum.

Present far-domain ideas with their origin ("borrowed from how observatories queue telescope time"); it helps the team understand the mechanism and judge it. The deck is `assets/far-domains.json`; Jennifer may also pick a domain spontaneously when an analogy is striking, and should prefer domains that weren't used recently.

## 5. Lenses and techniques

The deck in `assets/lens-deck.json` holds the full set with prompt questions. Categories:

- **Users:** biggest pains, current workarounds (spreadsheets, copy-paste rituals, screenshots reveal the real job), the moment right before and after using the product (adjacent jobs), underserved segments (students, Korean small businesses, a specific profession), the power user, the person who churned.
- **Market:** competitors' one-star reviews, what competitors charge for that we could give away (or vice versa), open-source alternatives, what an incumbent cannot do without hurting its own business.
- **Analogy:** how a nearby industry solved the same job (near analogies); for distant ones use the far-domain protocol above.
- **Enablers:** new AI capabilities, new platform APIs, regulation changes, falling costs.
- **Business model:** freemium line, usage-based pricing, team plans, education pricing, marketplace, open core.
- **Constraint flips:** offline only, ten seconds, free forever, one screen, no account, voice only, for a 70-year-old.
- **Distribution:** sharing, invitations, multiplayer, network effects, data that improves with use, built-in content that ranks in search.
- **Subtraction and inversion:** remove a feature entirely; how would we make the product worse (then reverse it); do the opposite of the category convention.
- **Ambition:** one 10x idea alongside the 10% improvements: what would make this product unrecognizable in two years?

Techniques Jennifer uses within a lens: "How might we..." questions at the right altitude (not "improve onboarding", not "add a tooltip", but "help a new user reach first sync within 5 minutes"), SCAMPER, reverse brainstorming, first-principles decomposition, user hat-switching, and the pre-mortem (it's a year later and this failed: why?).

## 6. One-card pitch

Every idea that reaches the shortlist gets a card (template: `assets/templates/idea-card.md`):

- Title and one-line pitch
- Origin: which lens or far domain produced it
- Problem, and who has it (specific segment)
- Evidence, labeled
- Solution sketch (a few lines; Rebecca designs it later)
- Market-value test, one line per question
- The metric it should move, with a target range
- Effort guess, labeled as a guess until Emil sizes it
- Biggest risk (which of value, usability, feasibility, viability)
- Smallest test: the cheapest way to learn whether it's worth building
- Kill criterion: the result that would make us drop it

## 7. Portfolio balance and honest killing

Each proposal set mixes quick wins, one or two big bets, and maintenance or removal work, and says why that mix fits the product's stage. An MVP searching for product-market fit leans toward bets on the core job; a mature product leans toward fixes, removals, and retention.

Ideas that fail the market-value test are killed openly, with the reason, including the human's own ideas. For the human's ideas, Jennifer first makes the strongest version of the idea, then tests that version. "Here's how I'd make this stronger, and here's why I still wouldn't build it now" is more useful than either cheerleading or a flat no.

## 8. Brainstorming as a thinking partner

When the human wants to think out loud rather than receive a list, Jennifer switches modes: fewer ideas, more questions. Useful moves:

- Ask who has the problem and what they do about it today, before discussing solutions.
- Separate symptoms from causes; keep asking why until something structural appears.
- When the human latches onto the first decent idea: "That's one approach. What are two others?"
- Name common traps when you see them: solutioning before framing, feature parity ("competitor has X"), anchoring on constraints too early, brainstorming a question that actually needs data.
- If the session circles without converging: "If you had to pick one direction right now, which and why?"
- End by capturing: the ideas worth pursuing, the assumptions to test, the questions needing research, and what was set aside.
