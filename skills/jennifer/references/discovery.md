# Discovery and user research

Contents: 1. Discovery in one page · 2. Understanding the product first · 3. Jobs to be done · 4. Interviews · 5. Surveys · 6. Usability tests · 7. Synthesis · 8. Personas and journeys · 9. Opportunity solution tree · 10. Assumptions and risks · 11. Cheap experiments · 12. Simulated interviews

Market research tells Jennifer where value is; user research tells her why, in the users' own words. Discovery is how a team avoids spending months building something nobody wanted. Good teams expect most ideas not to work as hoped, and test the riskiest part cheaply first.

## 1. Discovery in one page

- **Problem before solution, outcome over output.** A feature is a bet on an outcome; name the outcome first.
- **The four risks** (Marty Cagan's framing): **value** (will they want it?), **usability** (can they use it?), **feasibility** (can we build it?), **viability** (does it work for the business: cost, legal, support, brand?). For new products add go-to-market (can we reach them?), ethics (should we?), and team (can we sustain it?).
- **Continuous, not one-off.** A small weekly habit (a couple of user conversations, a look at fresh feedback) beats a big study every six months. Jennifer suggests a cadence that fits the team's size.
- **Stage-aware.** Before product-market fit, use fast, cheap, mostly qualitative methods. Heavy analytics and A/B tests come later, when traffic justifies them.

## 2. Understanding the product first

Before forming opinions about a product, Jennifer builds her own picture from its sources:

- **The product itself:** README, routes and screens, data models, settings, permissions, pricing logic, existing docs. Produce a **feature inventory** and a **user-flow map** (Mermaid).
- **Work in flight:** issues, pull requests, discussions, changelogs, milestones: what's broken, requested, in progress.
- **Users:** support messages, reviews, analytics, survey results.
- **Classification:** stage, business model, target segments, the main job it does, and how it relates to the team's other products (shared users, shared technology, competition for team time).
- **Intent vs implementation:** where docs, policies, or past specs say one thing and the code does another (a permission documented but never enforced, a limit in the pricing page that the code doesn't check). Cite both sides: the documented intent and the code location. If you can't cite both, it's a question for Emil, not a finding.

Write the results into `PRODUCT.md`.

## 3. Jobs to be done

Describe what users are trying to get done, independent of any product.

- **Job statement:** "When [situation], I want to [motivation], so I can [expected outcome]." The situation is the trigger; it matters more than demographics.
- **Functional, emotional, and social jobs.** "Keep my notes in sync" is functional; "feel confident I won't lose work" is emotional; "look organized to my advisor" is social. The emotional and social jobs often decide purchases.
- **Forces of progress** acting on a switch: **push** of the current situation's pain, **pull** of the new solution, **anxiety** about the new solution, **habit** of the present way. A product wins when push plus pull beats anxiety plus habit; often the cheapest lever is reducing anxiety (free import, undo, a trial).
- **What did they fire to hire us?** That reveals the real competitive set.

## 4. Interviews

Interviews ask about the past, not the future. People are poor predictors of their own behavior and kind to your ideas. Rules (from Rob Fitzpatrick's *The Mom Test*):

- Talk about their life, not your idea. Don't pitch during discovery.
- Ask about specific past events: "Tell me about the last time you..." not "Would you use...?"
- Listen more than you talk; follow the emotion ("You sighed there. What happened?").
- Compliments and hypothetical promises are noise. Commitment is signal: time, money, introductions, a pilot.

**Interview guide** (template: `assets/templates/interview-guide.md`):
1. Goal and the decision the interviews inform; who we're talking to and why.
2. Screener: the 3-5 questions that qualify a participant (did the job recently, in the target segment), with disqualifying answers marked.
3. Consent and recording note (see privacy below).
4. Warm-up (context about their role and setup).
5. The last time they did the job: walk through it step by step. What tools, what went wrong, what they did about it, what it cost them.
6. Workarounds and alternatives tried; what they paid or would have paid.
7. Probe the riskiest assumption without revealing it.
8. Wrap-up: anything we didn't ask; who else should we talk to.

Five to eight interviews per segment usually reveal the main patterns; stop when new interviews stop adding themes.

**Privacy.** Collect only what the study needs. Get consent for recording and note-taking, state how data will be used and when it will be deleted, and anonymize everything in outputs (P1, P2...). Under Korea's PIPA, collection of personal information needs a stated purpose, items, retention period, and consent; flag anything beyond simple consented interviews for review.

Contacting real people is gated: Jennifer drafts the outreach and the guide; the human approves and sends.

**Report the interviews themselves, not only conclusions.** An interview report includes the guide used, participant profiles (anonymized), the major exchanges from each transcript verbatim (every question asked and the substantive answers; trim greetings and small talk), and then the synthesis. Full transcripts go to `interviews/` in memory.

## 5. Surveys

Surveys quantify what interviews discovered; they're poor at discovering.

- One question per question. Flag **double-barreled** items ("Is it fast and reliable?"), **leading** wording ("How much do you love..."), **loaded** assumptions ("How often do you use our export feature?" to people who may not), and jargon.
- Choose the type deliberately: behavior frequency ("In the last 7 days, how many times..."), rating scales with labeled points, ranking for priorities, and at most one or two open text questions.
- Put sensitive and demographic questions last; keep it under 5 minutes.
- **Sample size:** for a proportion at 95% confidence, roughly 100 responses give about ±10 points, 400 about ±5, 1,000 about ±3. Say the margin of error, and whether respondents differ from the users you care about (who answers surveys is not random).
- **Product-market fit survey (Sean Ellis):** "How would you feel if you could no longer use [product]?" Very disappointed / somewhat / not disappointed. Around 40% "very disappointed" among recent active users is the commonly used threshold. Segment the answers: the "very disappointed" group tells you who the product is really for and what they value.

## 6. Usability tests

Planned with Rebecca. A test plan names: the questions to answer, 3-6 realistic tasks phrased as goals (not instructions: "Share this note with your teammate", not "Click the share button"), success criteria per task, what to observe (hesitations, wrong paths, errors, comments), and 5 participants per round for qualitative findings. Report task success, where people got stuck, severity, and recommended fixes.

## 7. Synthesis

Turn raw notes into decisions:

1. Extract atomic observations, each tagged with participant and context. Keep what people **did** separate from what they **said**.
2. Cluster observations into themes (affinity mapping). Name each theme in the user's words.
3. For each theme: how many participants (denominator), how intense (signals of pain: workarounds, money spent, emotion), which segment.
4. Write insights: an observation plus why it matters ("Researchers export to spreadsheets weekly because the built-in view can't compare two time ranges").
5. Turn insights into opportunities (needs to address, not solutions yet).
6. Rate confidence (high / medium / low) from the strength and consistency of evidence; list contradictions and open questions.

Representative quotes are short and anonymized. Never paraphrase a quote while keeping quotation marks.

## 8. Personas and journeys

- **Personas** grounded in evidence: a segment's job, context, frequency, pains, current tools, and what success looks like, with the evidence count behind it. A persona built without research is labeled a **proto-persona** until validated. Avoid decorative demographics that drive no decision.
- **Customer journey map:** stages, actions, thoughts and emotions, pains, and the moments where the product could matter most. Mark which parts are evidenced and which are assumed.

## 9. Opportunity solution tree

Teresa Torres's structure for connecting work to outcomes:

```
Desired outcome (one measurable product outcome)
├── Opportunity (a need, pain, or desire from research)
│   ├── Solution
│   │   └── Assumption tests
│   └── Solution
└── Opportunity
    └── Solution
```

Opportunities come from research, not imagination; each traces to evidence. Compare several solutions per opportunity. Test assumptions, not whole solutions. Keep the tree in `PRODUCT.md` and update it as you learn; it's the bridge between discovery and the roadmap.

## 10. Assumptions and risks

1. List every assumption the idea depends on, stated and unstated, across value, usability, feasibility, viability (plus go-to-market, ethics, team for new products). Think from three seats: the PM (demand, willingness to pay, competition), the designer (first-time experience, comprehension), the engineer (build vs buy, scale, dependencies).
2. Rate each by **importance** (if wrong, does the idea die?) and **evidence** (how much do we already know?).
3. Test the important assumptions with the least evidence first.
4. Write each as a falsifiable hypothesis with a threshold set in advance: "At least 30% of users who see the team-plan fake door will click it within two weeks."

## 11. Cheap experiments

Choose the cheapest method that could change the decision (with Alberto Savoia's emphasis on "skin in the game": real commitment beats stated interest, and your own data beats others' data):

| Method | Tests | Cost |
|---|---|---|
| Five interviews about the last time | Is the problem real and frequent? | Days |
| Fake door (a button or menu item that leads to "coming soon") | Do people want it enough to click? | Hours of eng |
| Smoke-test landing page with signup or pre-order | Demand and messaging, before a product exists | Days |
| Concierge (deliver the service manually) | Is the value real when delivered? | Weeks of a person's time |
| Wizard of Oz (looks automated, a human behind it) | Will they use it, before building the automation? | Days to weeks |
| Clickable prototype test (with Rebecca) | Usability and comprehension | Days |
| Pre-sale, paid pilot, letter of intent | Willingness to pay | Weeks |

Every experiment states: hypothesis, method, metric, success threshold, sample or duration, and what we'll do if it passes or fails. Fake doors and smoke tests must not mislead users in harmful ways: tell them the feature is coming, don't take payment without delivering, and follow the gates for anything public.

## 12. Simulated interviews

Jennifer can run interviews with simulated users, conducted by a separate, hypothesis-blind agent so her own expectations can't leak into the answers. The full protocol (grounded persona cards, deliberate variety including skeptics, blind interviewee, transcript sharing, bias audit, and the evidence ceiling) is in `simulated-interviews.md`. Two rules carry over to every interview, simulated or real:

- **Share the major parts of the transcript** in the report, not only the synthesis: the questions asked verbatim and the substantive answers, anonymized for real participants. The human must be able to check for leading questions and see the raw material behind each theme.
- **Label the source** of every finding: `[primary]` for real people, `[simulated]` for simulated ones. Never merge the two in one count.
