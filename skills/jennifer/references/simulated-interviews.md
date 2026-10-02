# Simulated user interviews

Contents: 1. Why a separate agent · 2. When to use them, and the evidence ceiling · 3. Grounding: personas built from evidence · 4. Persona variety · 5. The blind interviewee · 6. Conducting the interview · 7. Bias audit · 8. Synthesis · 9. Reporting and transcript sharing · 10. Running it in each environment

## 1. Why a separate agent

When one model plays both interviewer and interviewee, the answers inherit the interviewer's hypothesis: the "user" knows what the PM hopes to hear. Jennifer removes that channel by running each interviewee as a **separate agent with its own context**, which sees only its persona card and the questions asked, never the product idea, the hypothesis, the interview guide, or other interviews. Jennifer writes the persona from domain knowledge and evidence, then interviews it as she would a real person.

This fixes interviewer-to-interviewee leakage. It doesn't fix the simulation's own tendencies: published comparisons (Nielsen Norman Group reran three real studies with AI participants) found simulated users shallower, more positive, and more agreeable with each other than real people, and less able to produce genuine surprises. The protocol below counters those tendencies (grounded personas, deliberate skeptics, anti-agreeableness instructions, past-behavior questions, audits) and is honest about what remains.

## 2. When to use them, and the evidence ceiling

Good uses:
- Early discovery in a new domain, after a domain primer exists, to map likely jobs, pains, and vocabulary.
- Sharpening an interview guide or survey before real research (find confusing, leading, or useless questions).
- Exploring segments the team can't reach quickly, to decide which to recruit for real.
- Stress-testing assumptions: which ones would a grounded skeptic attack?

The ceiling: findings are labeled `[simulated]` and can shape hypotheses, guides, and what to test first. They cannot alone justify a large commitment (major engineering time, money, a public launch, pricing). For those, every report names the real-user check that would confirm the key findings: a handful of real interviews, a fake-door test, a survey. Concept reactions ("would you use this?") from simulated users are the weakest evidence of all; skip them or report them separately as near-worthless.

## 3. Grounding: personas built from evidence

A persona invented from imagination produces the model's average person. Each persona card (template `assets/templates/persona-card.md`) is built from the domain primer and real material: reviews, forum posts, job postings, support tickets, past real interviews. Fields:

- ID and a fictional name; language and speech style (register, verbosity, dialect if relevant).
- Role, organization, and context (team size, budget authority, tools available).
- A typical week, with the job in question placed in it.
- Two or three **specific recent incidents** involving the job, grounded in real accounts ("based on 4 similar reviews of tool X, Sept 2026").
- Current tools and workarounds, and what they cost the person (time, money, risk).
- Constraints: time, money, permissions, skills.
- Attitudes: toward change, technology, vendors, the problem itself. What they'd never do.
- Knowledge limits: what this person wouldn't know (persona agents should say "I don't know").
- Grounding sources, listed at the bottom (stripped before the card goes to the interviewee).

Never put the product idea, the hypothesis, or "this person needs a tool like ours" into a card.

## 4. Persona variety

Build a small matrix of the dimensions that matter for the decision (segment, experience level, context, attitude, stakes) and pick personas that cover its corners rather than its center. For 5-8 interviews, include at minimum:
- one **skeptic** (has been burned by tools like this, or thinks the problem isn't worth solving),
- one **non-user or churned user** (tried something similar and stopped, or uses pen and paper on purpose),
- one **edge case** relevant to the product (low bandwidth, accessibility needs, older user, non-native speaker, a very small or very large organization),
- and the core target segment, with variation in experience.

Vary the personas' moods and verbosity too; real interview pools include terse and distracted people.

## 5. The blind interviewee

The interviewee agent receives only:
1. The interviewee instructions built into `sim_interview.py` (stay in character; answer from the persona's own life; say "I don't know" when the persona wouldn't know; it's fine to be bored, skeptical, uncertain, or contradictory; don't volunteer enthusiasm for products; answer hypotheticals vaguely, as people do; give spoken-length answers; never mention being an AI; don't invent statistics or outside facts).
2. The persona card, with grounding sources removed.
3. The conversation so far.

It never sees the guide, the hypothesis, Jennifer's notes, or other transcripts. Run each persona in a fresh session.

## 6. Conducting the interview

Jennifer interviews exactly as with a real person (`discovery.md`, section 4):
- Ask about specific past events ("Tell me about the last time you...") rather than opinions or futures.
- One question at a time; adapt follow-ups to the answers; follow emotion and specifics.
- Don't pitch. If a concept reaction is needed, put it at the very end, label that section, and treat its answers as the weakest evidence.
- Every question is recorded verbatim in the transcript, including follow-ups. The script does this automatically.
- Typical length: 12-25 exchanges.

## 7. Bias audit

After each interview, before synthesis, review the transcript and write audit notes into the report:
- **Leading questions:** list any question that suggested an answer, assumed a fact, or revealed the hypothesis. Down-weight the answers they produced.
- **Persona drift:** answers inconsistent with the card (the skeptic suddenly enthusiastic, the novice using expert jargon).
- **Agreeableness:** praise without specifics, agreement with every premise, no complaints at all. Flag the interview as low-confidence if pervasive.
- **Hallucinated specifics:** concrete claims (prices, statistics, product names) the persona couldn't know or the card doesn't support. Exclude them from findings.

For high-stakes studies, a second, separate agent can audit the transcripts blind to the hypothesis.

## 8. Synthesis

Same method as real research (`discovery.md`, section 7), with three differences:
- Counts are reported as "3 of 6 simulated participants" and never merged with real participants' counts.
- Findings that merely restate a persona card ("the skeptic was skeptical") aren't findings. Look for what emerged from the interaction: the workflow details, the language, the objections, the trade-offs the persona revealed under specific questions.
- Every theme carries a confidence level, capped at medium for simulated evidence, and the real-user check that would confirm it.

## 9. Reporting and transcript sharing

When interviews are conducted, simulated or real, the report shares the interviews themselves, not just conclusions. The human needs to see what was asked and answered to judge the findings and spot bias. The report contains:

1. Bottom line and the decision it informs; source type (`[simulated]` or `[primary]`) stated in the first lines.
2. Method: the guide (as written beforehand), number of interviews, persona matrix or recruitment criteria, and the backend used for simulated runs.
3. **Per interview:** the persona card summary (or anonymized participant profile), then the **major parts of the transcript, verbatim**: every question asked and every substantive answer. Trim only greetings, small talk, and repetition, marking each cut with `[...]`. Then the audit notes for that interview.
4. Themes with counts, representative quotes (linked to the transcript lines above), and confidence.
5. Surprises and contradictions.
6. What this can't tell us, and the real-user validation plan for the key findings.

Full, untrimmed transcripts are saved to `interviews/` in memory (`sim_interview.py show --session ID > interviews/<id>.md`) and linked from the report. For long studies (more than ~6 interviews), put the per-interview transcript sections in an appendix, but keep them in the document.

## 10. Running it in each environment

`scripts/sim_interview.py` keeps each interviewee in its own model context and stores the transcript in `.jennifer/interviews/`. Jennifer calls it once per question so she can adapt follow-ups:

```bash
python scripts/sim_interview.py start --persona .jennifer/interviews/P3-card.md --id P3
python scripts/sim_interview.py ask --session P3 "Tell me about the last time you had to share files with your advisor."
python scripts/sim_interview.py ask --session P3 "What did you do when that happened?"
python scripts/sim_interview.py show --session P3 > .jennifer/interviews/P3-transcript.md
```

Backends (`--backend`, default `auto`):
- **claude-cli:** uses the `claude` command (available in Claude Code and Cowork setups), run from an empty temporary directory so the interviewee can't read the project, its CLAUDE.md, or Jennifer's files. A user-level `~/.claude/CLAUDE.md` would still load; mention this if one exists.
- **api:** calls the Anthropic Messages API when `ANTHROPIC_API_KEY` is set. Model from `--model` or `$JENNIFER_SIM_MODEL`. This bills the human's account: a batch of interviews goes through the spending gate with an estimate first.
- **manual:** prints the exact prompt for the human to paste into a fresh, separate chat, then records the answer they paste back (`sim_interview.py answer --session P3 "..."`). Useful in Claude chat, where Jennifer can't start a separate agent herself.
- **Claude Code subagents** are another way to get a separate context; if using one, pass only the persona card and a single question per call, and record the exchange with `sim_interview.py answer`.

If no separate context is available at all, Jennifer may simulate in her own context only if the human explicitly accepts the weaker isolation, and must label the report "same-context simulation: interviewer and interviewee share a context, so hypothesis leakage is possible."
