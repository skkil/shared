# Metrics and experimentation

Contents: 1. Metric tree · 2. Frameworks · 3. Activation · 4. Metric dictionary and vanity checks · 5. Analysis hygiene · 6. Experiment design · 7. Low-traffic methods · 8. Product-market fit · 9. AI product evals · 10. Dashboards · 11. Post-launch review

Jennifer decides how success will be measured before anything ships, then checks whether it happened. If nothing is instrumented yet, her first job on a product is an event tracking plan.

## 1. Metric tree

One **North Star metric** per product: it moves when users get more of the core value, predicts long-term success, can be influenced by the team, and is understandable by everyone. Examples by shape: a collaboration tool might use weekly active teams with 3+ members editing; a sync tool, weekly users with a successful cross-device sync; a marketplace, weekly transactions completed.

Under it, 3-5 **input metrics** the team can move directly (e.g., new users activated, active users retained week over week, actions per active user), and under those, diagnostic metrics. Draw it as a tree in `PRODUCT.md`. Every feature names which input metric it should move.

Pair each target metric with **guardrails** that must not get worse (errors, latency, support tickets, unsubscribes, retention of another segment) and **counter-metrics** that catch gaming (time in app rising because people are lost).

## 2. Frameworks

- **AARRR** for growth questions: acquisition, activation, retention, referral, revenue. Find the stage where the biggest drop is relative to benchmarks or to intent; that's usually the priority.
- **HEART** for experience quality: happiness, engagement, adoption, retention, task success. For each chosen dimension, define goals → signals → metrics.
- Don't use both everywhere. Choose per question.

## 3. Activation

Activation is the "aha" moment expressed as a measurable event, plus the time it takes to reach it ("synced a file between two devices within 24 hours of signup"). Find it by comparing retained and churned users' early behavior (what did retained users do in week one that churned users didn't?), then validate that the relationship isn't just "engaged users do everything". Track the share of new users who activate and the time to activate; most early products gain more from improving activation than from acquiring more users.

## 4. Metric dictionary and vanity checks

One written definition per metric, so everyone means the same thing: name, plain-language definition, exact formula (numerator, denominator, time window, filters), data source, owner, known caveats.

**Vanity metric check:** a metric is vanity if it can rise while the product gets worse. Cumulative signups, total downloads, page views, and raw time-in-app are common offenders. Prefer rates, cohorts, and active counts with a meaningful action. Flag vanity metrics when you see them in plans or reports, and propose the better version.

## 5. Analysis hygiene

- State **data quality and sample size** with every result: date range, filters, how many users, known tracking gaps.
- Use **denominators and cohorts.** Retention by signup cohort, not overall averages that mix old and new users.
- Watch for **Simpson's paradox** (a trend that reverses within segments), seasonality (Korean academic calendar, holidays such as Chuseok and Seollal), **novelty effects** (a spike that fades), and survivorship (only looking at users who stayed).
- **Correlation is not a launch decision.** "Users who use feature X retain better" may only mean engaged users do more things.
- Where SQL or exports are available, show the query so it can be checked and rerun.

## 6. Experiment design

Template, written before the experiment starts:

- **Hypothesis:** "Because [evidence], we believe [change] for [segment] will [move metric] by [amount]."
- **Primary metric** (one), **guardrail metrics**, and the **minimum detectable effect** (the smallest change worth detecting, chosen for business relevance, not convenience).
- **Unit of randomization** (user, team, session) and why. Randomize teams when features are shared within a team.
- **Sample size and duration** from the script, rounded up to full weeks to cover weekly cycles:

```bash
python scripts/sample_size.py --baseline 0.12 --mde 0.02 --daily-traffic 800      # absolute lift
python scripts/sample_size.py --baseline 0.12 --mde-rel 0.15 --daily-traffic 800   # relative lift
python scripts/sample_size.py --baseline 0.12 --daily-traffic 800 --weeks 4        # smallest detectable lift in 4 weeks
```

- **Decision rule set in advance:** ship if the primary metric improves significantly and no guardrail degrades beyond its threshold.
- **During the run:** check sample ratio (if a 50/50 split comes out 53/47, something is broken; stop and debug), check that events fire. Do not stop early because results look good; peeking inflates false positives.
- **Readout:** effect size with confidence interval, not just a p-value; guardrails; segment cuts only as hypotheses for next time; the decision.

## 7. Low-traffic methods

The normal case for a small team. If `sample_size.py` says the test needs more than about 4-6 weeks, a classic A/B test is the wrong tool. Use instead:

- **Fake doors and smoke tests** for demand (see `discovery.md`).
- **Concierge and Wizard-of-Oz** trials for value.
- **Before/after comparisons** with their caveats stated: other changes in the same period, seasonality, and a comparison with a similar untouched metric where possible.
- **Qualitative tests:** five usability sessions, follow-up interviews with people who used the new feature.
- **Bigger changes:** small tweaks need huge samples to detect; bold changes produce large effects that small samples can see.

Label results from these as **directional**, never as proven.

## 8. Product-market fit

Signals, strongest first: retention curves that flatten (a stable share of each cohort keeps using the product), organic growth from word of mouth, the Sean Ellis survey (around 40% of recent active users "very disappointed" without the product), and users pulling the product from you (asking for features, paying before it's ready). Measure retention by cohort first; surveys second.

## 9. AI product evals

When the product includes AI features, its quality is a distribution, not a fixed behavior: the same input can produce different outputs, and users do unexpected things. Practitioners now describe writing evals as a core PM skill, because evals are how a team defines what "good" means for a probabilistic feature. The PM is often the right person to judge outputs, because the judgment needs domain taste, not a committee.

The error-analysis loop (as taught by Hamel Husain and Shreya Shankar):

1. **Look at real traces.** Sample 50-100 real interactions (or realistic ones before launch). Read them end to end.
2. **Open coding:** write a free-form note on what went wrong in each failing trace. No predefined categories yet.
3. **Axial coding:** group the notes into a failure taxonomy (e.g., "invents a file that doesn't exist", "ignores the user's language", "too long"). Count each category; the biggest categories are the priorities.
4. **Write evals for the important failures:** code-based checks where possible (format, length, forbidden content, required fields); LLM-as-judge with a binary pass/fail and a written rubric where judgment is needed. Validate any LLM judge against your own labels before trusting it.
5. **Rerun on every change** to prompts, models, or retrieval, and look at fresh traces regularly; new failure modes appear as usage changes.

Generic scores ("helpfulness 4.2/5") rarely drive decisions; specific failure rates do. Add AI-specific requirements to specs: evaluation set and pass threshold, maximum error or hallucination rate on that set, latency, cost per call, and graceful degradation (what the user sees when the model fails or is slow). Earn autonomy incrementally: start with a narrow, supervised capability and expand as evals show reliability.

Products that use generative AI may also carry legal transparency duties (in Korea, the AI Basic Act; see `korea.md`). Flag them in the PRD.

## 10. Dashboards

A dashboard spec lists: who watches it and what decision it supports, the metrics (from the dictionary), segments, time grain, alert thresholds, and the owner. Fewer charts, each answering a question. The weekly product-health ritual reads from it.

## 11. Post-launch review

Two to six weeks after launch (template `post-launch-review.md`): did the primary metric move versus target, by how much, and why (what evidence supports the causal story); what happened to guardrails; what we learned about users; what surprised us; the decision (keep, iterate, roll back, remove); and updates to `PRODUCT.md`, the opportunity tree, and the assumptions log. Write it even when the feature failed; those are the most valuable ones.
