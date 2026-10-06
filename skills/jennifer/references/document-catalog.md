# Document catalog: PM documents and how to write each well

Contents: A. Discovery and research · B. Strategy and direction · C. Defining the work · D. Delivery and communication · E. Learning and review · F. Business and funding · G. Choosing the right document

Every document follows `writing-reports.md` (language confirmed first, bottom line up front, evidence labels, length budget). This catalog adds what is specific to each type: who reads it, its shape, and the mistakes that sink it. Where a deeper reference exists, it's named. Templates are in `assets/templates/`.

Format of each entry: **Reader and job** · **Shape** · **Do** · **Avoid**.

## A. Discovery and research

**Domain primer** (`domain-immersion.md`, template `domain-primer.md`)
Reader: the team entering an unfamiliar field. Shape: overview, glossary, actors, workflows, calendar, rules, money, pains, what good looks like, sources. Do: write in practitioners' words; mark confidence per section. Avoid: vendor marketing as the main source.

**Research plan**
Reader: the human approving research. Shape: decision served, questions, hypotheses, method, participants or sources, timeline, budget, how results will be used. Do: one page; state what would change the decision. Avoid: researching without a decision attached.

**Interview guide** (template `interview-guide.md`)
Reader: the interviewer. Shape: goal, screener, consent, warm-up, last-time story, workarounds, assumption probes, wrap-up. Do: past-behavior questions; neutral wording. Avoid: pitching, "would you use", leading questions.

**Interview report** (`simulated-interviews.md` section 9)
Reader: the team deciding what to build. Shape: bottom line with source type, method, per-interview profile and major transcript exchanges verbatim, themes with counts, surprises, limits, validation plan. Do: share the interviews themselves. Avoid: conclusions without the raw exchanges; mixing real and simulated counts.

**Survey**
Reader: respondents, then the team. Shape: purpose line, screener, behavior questions, attitude scales, one or two open questions, demographics last. Do: one idea per question; pilot it; state margin of error in results. Avoid: double-barreled, leading, or loaded questions.

**Persona / proto-persona**
Reader: designers and engineers. Shape: job, context, frequency, pains, current tools, success, evidence count. Do: label proto-personas as unvalidated. Avoid: decorative demographics and stock-photo bios.

**Customer journey map**
Reader: the cross-functional team. Shape: stages × (actions, thoughts, emotions, pains, opportunities). Do: mark evidenced vs assumed cells; highlight moments that matter. Avoid: a map of the ideal journey instead of the real one.

**Competitive analysis** (`market-research.md` section 5)
Reader: strategy and positioning decisions. Shape: competitive set, feature and pricing matrices with retrieval dates, positioning map, messaging analysis, where we can win. Do: include substitutes and doing nothing. Avoid: checkbox wars; unverifiable claims about competitors.

**Market brief and market sizing** (`market-research.md`, template `research-brief.md`)
Reader: the decision-maker. Shape: bottom line, decision served, labeled findings, size range, position, risks and gaps, next step, sources. Do: top-down and bottom-up with ranges. Avoid: a single huge TAM number from an unsourced slide.

**Market digest** (monthly)
Reader: the team. Shape: what changed first, moves with confidence levels, signals, regulation, implications, watch list. Do: keep the section order stable so editions can be compared. Avoid: news summaries with no "so what".

## B. Strategy and direction

**Product vision**
Reader: everyone, including future hires. Shape: the world for the user if we succeed (3-5 years), who it's for, why it matters, a few principles. Do: concrete and memorable; one page. Avoid: slogans that fit any product.

**Strategy document** (`strategy-prioritization.md` section 1)
Reader: leadership and the team. Shape: diagnosis, guiding policy (including what we won't do), coherent actions, metrics, risks. Do: prose; make choices people could disagree with. Avoid: a bulleted list of initiatives presented as strategy.

**Narrative memo (six-pager style)**
Reader: decision-makers reading silently at the start of a meeting. Shape: up to about six pages of prose: context, the question, analysis, options, recommendation; data in appendices. Do: full sentences that force complete reasoning. Avoid: bullet fragments that hide gaps in logic.

**PR/FAQ (working backwards)**
Reader: leadership deciding whether to fund an idea. Shape: a one-page press release dated at launch (headline, customer problem, solution, a clearly hypothetical customer quote, how to get started), then external FAQs (customers' questions) and internal FAQs (cost, risks, dependencies, why now). Do: write the hard questions into the FAQ. Avoid: hype language; skipping the internal FAQ.

**Positioning and messaging document** (`strategy-prioritization.md` section 2)
Reader: Rebecca, Vanessa, anyone writing about the product. Shape: competitive alternatives, unique attributes, value with proof, best-fit customers, category; then a messaging hierarchy (core claim, three value points, proof each). Do: test headlines with real prospects. Avoid: adjectives without proof.

**Business case**
Reader: whoever allocates money or time. Shape: the opportunity, options including doing nothing, costs, benefits as ranges, risks, recommendation, how we'll know. Do: show assumptions in a spreadsheet. Avoid: a single-scenario forecast.

**Pricing proposal**
Reader: leadership. Shape: current state, value metric, tiers and limits, competitor benchmarks with dates, willingness-to-pay evidence, impact on existing users, migration plan, risks. Do: model several scenarios. Avoid: changing prices for existing customers without a grandfathering decision.

**Roadmap** (`strategy-prioritization.md` section 6)
Reader: team, stakeholders, sometimes customers. Shape: Now / Next / Later by outcome, confidence per item, not-doing list, dependencies. Do: date only what's committed; publish a customer version without internal detail. Avoid: a feature list with quarter dates presented as promises.

**OKRs**
Reader: the team. Shape: 1-3 objectives, 2-4 measurable key results each with baseline and target. Do: outcomes, not tasks. Avoid: key results that are a to-do list.

**Decision memo and decision record** (template `decision-record.md`)
Reader: decision-makers now; future team members later. Shape: context, options, recommendation or decision, rationale, what we give up, reversibility, who decided and when, revisit trigger. Do: write it the same day. Avoid: recording only the decision without the rejected options.

## C. Defining the work

**One-pager / 기획 개요서** (template `one-pager.md`)
Reader: anyone deciding whether to pursue an idea. Shape: problem, who, market-value test in short, outcome metric, scope and non-goals, smallest test, open questions. Do: fit on one page. Avoid: solution detail.

**Shape Up pitch** (Basecamp's format, when the team works in fixed cycles)
Reader: the people placing bets for the next cycle. Shape: problem, appetite (how much time it's worth, e.g., two or six weeks), solution sketched at low fidelity, rabbit holes to avoid, explicit no-gos. Do: fix the time, flex the scope. Avoid: estimates in place of an appetite.

**PRD / 서비스 기획서** (`specs-and-deliverables.md` section 3, template `prd.md`)
Reader: design, engineering, QA. Shape: summary, problem, goals and guardrails, non-goals, users, solution overview, requirements with acceptance criteria, policies, analytics and SLIs, risks, rollout, open questions. Do: phase large work; keep P0 small. Avoid: problem statements that contain the solution; everything marked P0.

**Requirements spec / 요구사항 정의서**
Reader: engineering and QA. Shape: table of ID, requirement (EARS), priority, source, acceptance criteria IDs, status. Do: one testable statement per row. Avoid: compound requirements joined by "and".

**User stories with acceptance criteria**
Reader: the developer picking up the work. Shape: story, Given/When/Then criteria, edge cases, notes. Do: vertical slices that deliver visible value. Avoid: splitting by architecture layer; stories with no "so that".

**Developer-ready issue** (`feedback-to-issues.md`, template `issue.md`)
Reader: a developer starting today. Shape: outcome title, context with evidence, expected behavior, acceptance criteria, out of scope, technical pointers, size, priority, links. Do: pass the definition of ready. Avoid: "investigate X" without a time box and an expected output.

**Policy document / 정책서** (`specs-and-deliverables.md` section 7)
Reader: engineering, QA, support, operations. Shape: rules by area with IDs, reasons, and affected screens. Do: one source of truth for business rules. Avoid: rules scattered across screen notes.

**IA and user flows / 정보구조도, 플로우차트**
Reader: design and engineering. Shape: screen hierarchy with IDs and access conditions; Mermaid flows with error paths. Do: draw unhappy paths. Avoid: flows that end at the happy path.

**Screen spec / 화면설계서** (`specs-and-deliverables.md` section 9)
Reader: design and engineering. Shape: per screen, ID, wireframe with numbered markers, description per marker (behavior, states, validation, data, policy IDs). Do: write so no follow-up question is needed. Avoid: pixel-level visual decisions that belong to Rebecca.

**Functional spec / 기능명세서**
Reader: engineering. Shape: per function, inputs, processing rules, outputs, states, validation, errors, data needed. Do: tables for states and errors. Avoid: duplicating the PRD's rationale.

**Event tracking plan / 이벤트 정의서** (`specs-and-deliverables.md` section 10)
Reader: engineering and analytics. Shape: event ID, name, trigger, properties, question answered, owner. Do: name events object_action. Avoid: tracking everything "just in case".

**SLO sheet** (`observability.md` section 4, template `slo-sheet.md`)
Reader: engineering, release, the human. Shape: critical journeys, SLI definitions, SLO targets and windows, error-budget policy, alerts and owners. Do: few, user-centric SLOs. Avoid: 100% targets; CPU-based SLOs.

**Agent-executable spec** (`specs-and-deliverables.md` section 12, template `agent-spec.md`)
Reader: a coding agent (Emil) and its human reviewer. Shape: dependency-ordered phases, each with objective, requirements, technical notes, DO NOT CHANGE list, runnable acceptance criteria. Do: research current docs first. Avoid: one giant spec; scope implied by omission.

**Design brief** (template `design-brief.md`)
Reader: Rebecca. Shape: problem, user situation and emotions, promise, proof, constraints, screens in scope, metrics, references. Do: give the problem, not the pixels. Avoid: prescribing the layout.

## D. Delivery and communication

**Release plan / 출시 계획서** (`specs-and-deliverables.md` section 11)
Reader: engineering, release, support. Shape: scope, stages, flags, go/no-go criteria, monitoring, rollback trigger, communications, owners. Do: agree the go/no-go criteria before launch day. Avoid: criteria invented on the day.

**Launch checklist and go/no-go**
Reader: the launch team. Shape: checklist by function (product, engineering, QA, docs, support, legal, marketing) with owners; go/no-go poll with criteria. Do: include rollback rehearsal. Avoid: checklists nobody owns.

**Release notes / 릴리스 노트**
Reader: users. Shape: grouped as new, improved, fixed; each item a user benefit in one or two sentences; links to docs. Do: write what changed for them. Avoid: internal ticket titles and jargon.

**Status report / 주간 보고** (template `status-update.md`)
Reader: the team and leadership. Shape: status (on track / at risk / off track) with reason, progress vs goals, risks with owners, decisions needed, next. Do: honest colors, under 250 words. Avoid: activity lists with no outcome.

**Executive or stakeholder update**
Reader: leadership, partners. Shape: TL;DR, status, outcomes vs goals, risks and mitigations, specific asks with deadlines. Do: under 300 words. Avoid: burying the ask.

**Investor update**
Reader: investors and advisors. Shape: highlights, lowlights, key metrics in the same format each time, cash and runway if relevant, asks (intros, hires, advice). Do: send consistently, including in bad months. Avoid: only good news.

**Leadership deck / review deck**
Reader: a meeting audience. Shape: one message per slide with an action title; the deck's argument readable from titles alone; appendix for data. Do: Rebecca designs it from Jennifer's storyline. Avoid: dense text slides that work as neither document nor presentation.

**Meeting agenda and notes / 회의 안건, 회의록**
Reader: attendees and absentees. Shape: agenda with goal and the decisions needed, sent beforehand; notes with decisions, action items (owner, date), open questions. Do: send notes the same day. Avoid: transcripts in place of decisions.

**Quarterly business review**
Reader: leadership. Shape: goals vs results, what we learned, what changes next quarter, asks. Do: tie to OKRs. Avoid: a feature-shipped list.

**Sunset / end-of-life plan**
Reader: users, support, engineering. Shape: decision and reasons, timeline with notice period, migration path, data export, what happens to data, support end date, communications sequence (internal first, then key users, then everyone). Do: give generous notice and an export. Avoid: surprising paying users. Legal review where contracts are involved.

## E. Learning and review

**Experiment design and readout** (`metrics-experiments.md` section 6)
Reader: the team. Shape: design written before the run (hypothesis, metrics, MDE, sample, decision rule); readout with effect size and interval, guardrails, decision. Do: write the decision rule first. Avoid: stopping early; fishing in segments.

**Post-launch review / 출시 회고** (template `post-launch-review.md`)
Reader: the team and leadership. Shape: target vs actual, why, guardrails, learnings, decision, memory updates. Do: write it for failures too. Avoid: claiming causation from coincidence.

**Retrospective**
Reader: the team. Shape: what went well, what didn't, what we'll change (with owners). Do: blameless, focused on process. Avoid: action items without owners.

**Post-incident review**
Reader: engineering and leadership. Shape: summary, user impact (who, how long, what they saw, data loss), timeline, contributing factors, what went well, actions with owners and dates. Do: blameless; product impact stated plainly. Avoid: single "root cause" stories for multi-cause failures.

## F. Business and funding

**Business plan / 사업계획서 (PSST)** (`business-growth.md`)
Reader: grant reviewers, investors. Shape: follow the program's required template exactly (Korean programs typically use problem, solution, scale-up, team). Do: sourced numbers, honest risks, the reviewer's scoring criteria addressed point by point. Avoid: removing or reordering required sections; leaving template guide text.

**Pitch narrative**
Reader: investors, partners. Shape: the shift in the world, the problem it creates, the promised outcome, how we deliver it, evidence and traction, team, ask. Do: tell a story of change. Avoid: a feature tour.

**Grant application**
Reader: a review panel. Shape: the program's template, mapped to its evaluation criteria. Do: build a criteria-to-section map before writing; meet every eligibility rule; track deadlines. Avoid: generic text reused across programs.

**Proposal and RFP response / 제안서**
Reader: a prospective partner or customer. Shape: their problem in their words, proposed solution, scope, deliverables, timeline, team, price, terms, why us. Do: answer every RFP requirement explicitly in its order. Avoid: commitments that legal hasn't reviewed.

## G. Choosing the right document

| You need to... | Write |
|---|---|
| Decide whether to pursue an idea | One-pager, or PR/FAQ for big bets |
| Make a hard choice between options | Decision memo, then decision record |
| Align on direction | Strategy document or narrative memo |
| Tell builders what to build | PRD + agent spec or issues; policy doc and screen spec for complex UI |
| Turn messy input into work | Developer-ready issues plus a clarification list |
| Report progress | Status report or executive update |
| Learn from what happened | Post-launch review, retrospective, or post-incident review |
| Ask for money | Business case, business plan, grant application, or pitch |
