# Strategy, business model, and prioritization

Contents: 1. Strategy · 2. Positioning · 3. Defensibility · 4. Business model and pricing · 5. Prioritization · 6. Roadmaps and OKRs · 7. Making decisions · 8. Red-team and pre-mortem

Jennifer turns research and ideas into a small number of clear bets, and shows her working so people can disagree with the inputs rather than the conclusion.

## 1. Strategy

When a published test pitted AI-written product strategies against human ones, the consistent criticism of the AI version was that it read as a list of features or tactics rather than a strategy. Jennifer guards against exactly that.

**Write strategy as a kernel** (Richard Rumelt, *Good Strategy/Bad Strategy*):
- **Diagnosis:** what is really going on. The critical obstacle or opportunity, stated plainly. "Students try sync during exam season and abandon it after, because setup costs more than one season of benefit" is a diagnosis; "we need to grow" is not.
- **Guiding policy:** the overall approach to the obstacle, including what we will not do. A guiding policy makes some options clearly wrong.
- **Coherent actions:** a few actions that reinforce each other and follow from the policy.

**The tactics test.** Read the draft and ask: Does it name the obstacle? Does it make choices, so a reasonable person could disagree? Does it rule things out? Do the actions reinforce each other, or are they independent wishes? Could you swap in another product's name and keep the text? If it fails, it's a list of tactics; rewrite from the diagnosis.

**Other strategy work:**
- **Vision:** a picture of the world for the user in 3-5 years if we succeed, short enough to remember. In fast-moving AI markets, pair it with a 3-6 month directional horizon and revisit often; long plans go stale faster than they used to.
- **Portfolio decisions:** across the team's products, which to invest in, maintain, merge, or sunset, with reasons (shared users, shared technology, competition for team time, market momentum).
- **Quarterly strategy review:** are the current bets working? Recommend doubling down, changing course, or stopping, with the evidence.

## 2. Positioning

From April Dunford's *Obviously Awesome*, built in this order, because each step depends on the last:

1. **Competitive alternatives:** what customers would use if we didn't exist (often a spreadsheet or nothing).
2. **Unique attributes:** what we have that those alternatives don't.
3. **Value:** what those attributes enable for customers, with proof.
4. **Best-fit customers:** who cares most about that value, by characteristics we can find and target.
5. **Market category:** the frame that makes our value obvious to those customers. Choosing an existing category, a subsegment of one, or (rarely, expensively) a new one.
6. **Relevant trends** that make it matter now, used sparingly.

Output a positioning statement plus a messaging hierarchy (core claim, three supporting value points, proof for each) for Rebecca and Wren. Positioning is hypothesis until the target customers respond to it; test headlines on a landing page or in outreach before committing.

## 3. Defensibility

For a small team, realistic moats are: switching costs (data and workflows that live in the product), network effects (each user makes it better for others), data advantages (usage data that improves the product), community, brand and trust in a niche, and speed. Name which one the product is building, the evidence it is working, and what would erode it. "We'll execute better" is not a moat. In AI products, a feature built on a model capability is copied quickly; defensibility comes from workflow, data, distribution, and trust around the model.

## 4. Business model and pricing

- **Canvas:** a Lean Canvas (problem, segments, unique value proposition, solution, channels, revenue, costs, key metrics, unfair advantage) per product, kept in `PRODUCT.md`.
- **Revenue models compared:** subscription, usage-based, freemium, one-time license, open core, marketplace take, education and academic pricing, grants and sponsorship for open-source or research tools.
- **Pricing:** the value metric, tiers, and where the free-to-paid line sits (generous enough to deliver the core value, firm enough that serious users upgrade). See `market-research.md` for willingness-to-pay methods.
- **Unit economics:** customer acquisition cost, lifetime value, payback period, gross margin, infrastructure cost per user, and AI cost per call times calls per user. Present as a spreadsheet with every assumption visible and labeled (use the xlsx skill when building one).
- **Go-to-market:** the beachhead segment (one segment you can win and that talks to the next segment), channels, partnerships, launch tiers, and the messaging hierarchy from positioning.

## 5. Prioritization

Pick the framework that fits the decision, and say why in one line:

| Framework | Use when | Formula / method |
|---|---|---|
| RICE | Comparing many items for one product with some data | (Reach × Impact × Confidence) ÷ Effort. Reach per period, Impact on a 0.25 / 0.5 / 1 / 2 / 3 scale, Confidence 50 / 80 / 100%, Effort in person-weeks |
| ICE | Fast triage of experiments or growth ideas | Impact × Confidence × Ease, each 1-10 |
| WSJF | Timing matters; some items lose value if delayed | Cost of delay ÷ job size; cost of delay = user/business value + time criticality + risk reduction or opportunity enablement |
| Opportunity scoring | Deciding which user needs are most underserved | Importance + max(Importance − Satisfaction, 0), from a survey of users rating each need |
| Kano | Deciding what's a must-have vs a delighter for a release | Survey with functional / dysfunctional question pairs; classify as must-be, performance, attractive, indifferent, reverse |
| Value vs effort | Quick visual sort with stakeholders | 2×2: quick wins, big bets, fill-ins, money pits |
| MoSCoW | Cutting scope within a fixed deadline | Must / Should / Could / Won't (this time) |

Rules:
- **Show the inputs** with evidence labels and confidence. A score without visible inputs is an opinion with decimals.
- **Compute with the script** so results are reproducible: `python scripts/score.py backlog.csv --method rice --sensitivity`. The sensitivity run shows how the ranking changes if the shakiest input is wrong; mention any item whose rank swings.
- **Effort comes from Emil.** Until then, label it a guess.
- **Scores inform, they don't decide.** Strategic fit, dependencies, and risk reduction can justify overriding a score; say so explicitly when you do.

## 6. Roadmaps and OKRs

- **Roadmaps organized by outcome:** Now (committed, high confidence), Next (planned, scope firming up), Later (directional bets). Each item names the outcome it serves and its confidence. Dates only for Now, and for real external deadlines.
- **Treat the roadmap as rolling bets,** not a promise. Revisit monthly; record what changed and why. Product leaders at fast-moving AI companies openly say quarterly plans rarely survive contact with reality; the planning still matters because it forces the choices.
- **"Not doing" list:** explicit, with reasons. It prevents relitigating and sets expectations.
- **Dependencies** called out, with owners.
- **OKRs:** an objective is qualitative and motivating; key results are measurable outcomes (not tasks), 2-4 per objective, with a baseline and a target. "Ship the export feature" is a task; "Weekly active exporters from 120 to 300" is a key result. Score at quarter end; 70% achievement on a stretch goal is normal.

## 7. Making decisions

- **One-way vs two-way doors.** Reversible decisions (copy, layout, feature flags, most experiments) should be made fast by the closest person with data. Irreversible ones (data model, public API contracts, pricing for existing customers, brand, deleting user data) deserve slower, wider review. Say which kind each decision is.
- **Expected value** for bets: probability of success × value if it works − cost if it fails, with each input labeled. Useful mainly to make assumptions explicit.
- **Decision records** (template `decision-record.md`): context, options considered, decision, rationale, what we give up, who decided, date, and the signal that would make us revisit. File in `decisions/` and link from `PRODUCT.md`.
- **Disagree and commit.** Jennifer states disagreement once, with reasons and the evidence that would change her mind, then commits and records the decision.

## 8. Red-team and pre-mortem

For big bets, strategies, and launch plans, Jennifer attacks her own recommendation before presenting it. These are different exercises.

**Red-team (attack the logic now):**
1. List every claim the plan makes about users, the market, the mechanism, and the timeline. Mark the load-bearing ones: if false, the plan fails.
2. For each load-bearing claim, state the strongest case that it's true, then attack that strongest version. Attacking a weak version is worthless.
3. Write each failure mode as "Fails if ___", concrete and falsifiable.
4. Rank by impact if wrong × likelihood of being wrong × cheapness to test. The top items are what to test this week.
5. For each: the evidence to get this week, the kill criterion, the cheapest test.
6. Say plainly what holds up. Manufacturing doubt is as useless as rubber-stamping.

**Pre-mortem (imagine it already failed):** it's launch day plus three months and the project failed. Why? Sort the reasons into:
- **Tigers:** real risks with evidence; need action. Split into launch-blocking (fix before launch, with owner and date), fast-follow (within 30 days), and track.
- **Paper tigers:** worries that look scary but evidence says are unlikely; say why, to align the team.
- **Elephants:** things nobody is discussing that might matter; recommend how to investigate.
