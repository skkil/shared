# Domain immersion: learning a field fast, from the user's seat

Contents: 1. When to immerse · 2. The protocol · 3. Where to look · 4. The domain primer · 5. Seeing from the user's seat · 6. Validating what you learned

A PM who doesn't understand the user's world writes specs in the product's vocabulary and solves problems users don't have. Jennifer often lands in domains she knows only from text: dental clinics, lab equipment booking, Korean tax filing, music licensing. Before judging ideas there, she learns the domain well enough to describe a user's week in their own words.

## 1. When to immerse

Run this protocol when any of these is true:
- You can't write a plausible "last time they did the job" story for the target user.
- You don't know the domain's key terms, roles, rules, or how money flows.
- The request uses jargon you'd have to guess at.
- You're about to build persona cards for simulated interviews (they must be grounded in a primer).

Size it to the decision: 20-40 minutes of focused research for a feature in a new domain, a few hours across sessions for a new product. Check `domains/` in memory first; refresh a stale primer rather than starting over.

## 2. The protocol

1. **Write down what you know and don't.** Three short lists: what you're confident about, what you think but aren't sure of, and the questions you can't answer. This keeps background knowledge from passing as research.
2. **Ask the human first.** "What do you already know about [domain], and do you know anyone who works in it?" The fastest source is a person; the human may have users, colleagues, or documents.
3. **Plan the sources** (section 3): at least three different source types, so you don't learn the domain only through vendors' marketing or only through complaints.
4. **Read for the user's world, not for solutions.** Collect: roles, goals, daily and seasonal workflows, tools and artifacts, rules, money, pains, workarounds, and what practitioners consider good work.
5. **Write the primer** (section 4, template `assets/templates/domain-primer.md`). Label each claim with its evidence type and source.
6. **Walk in their shoes** (section 5): day-in-the-life narratives and the moments that matter.
7. **Validate** (section 6), then store in `domains/<domain>.md` with a staleness horizon (`research_lib.py add ... --stale-days 180`).

## 3. Where to look

| Source type | What it reveals | Examples |
|---|---|---|
| Practitioner voices | Real pains, vocabulary, workarounds, what they complain about to peers | Subreddits and forums for the profession; Korean communities (Naver cafes for the trade, Blind, Clien, DC갤러리 for the field, 지식iN); YouTube "day in the life" videos; practitioners' blogs and newsletters |
| Job postings | Tasks, tools, required skills, how success is measured | LinkedIn, Indeed, 사람인, 잡코리아, 원티드 postings for the role |
| Training and certification material | The domain's structured knowledge and official workflows | Course syllabi, licensing exam outlines, textbooks' tables of contents, professional training manuals |
| Associations and standards bodies | Norms, standards, ethics, industry statistics | Professional associations, 협회 websites, standards documents |
| Regulation | Hard constraints and liabilities | Laws and regulator guidance for the field (law.go.kr for Korea); flag anything legal for professional review |
| Tools practitioners use | Current solutions and their gaps | Vendor docs and pricing pages; reviews of those tools (app stores, G2, Capterra, Korean reviews) |
| Case studies and research | How the work functions at scale, known problems | Review papers, government reports, industry analyses |
| Workforce and market statistics | How many people, where, how they're organized | National statistics (KOSIS), labor statistics, association surveys |

Prefer recent sources; domains change (regulation especially). Note the date of each.

## 4. The domain primer

A primer is useful when someone new could read it in 10 minutes and then follow a conversation between practitioners. Sections:

- **Overview:** what the field does, for whom, at what scale, in one paragraph.
- **Glossary:** 20-50 terms with plain definitions, in the languages the team works in (e.g., Korean and English), including abbreviations and slang practitioners actually use.
- **Actors:** who uses, who pays, who decides, who is affected, and what each one wants. The user and the buyer are often different people with different goals.
- **Workflows:** the core jobs step by step, with frequency, duration, tools, and handoffs. Mark where errors and delays happen.
- **Calendar:** seasonality, deadlines, peak periods (fiscal year-end, exam seasons, harvest, holidays such as Chuseok).
- **Rules:** regulations, standards, professional norms, liabilities.
- **Money:** how revenue and costs flow; what practitioners are paid for; what they'd pay for.
- **Pains and workarounds:** with counts and sources where available.
- **What good looks like:** the quality measures practitioners use for their own work.
- **Sensitivities:** taboos, trust issues, sensitive data, status dynamics.
- **Open questions** and **sources** with dates.

## 5. Seeing from the user's seat

Knowledge isn't the same as perspective. After the primer, Jennifer does these before forming opinions about solutions:

- **Day-in-the-life narratives** for two or three roles: a specific person on a specific day, hour by hour, including the boring parts and the interruptions. Label what's evidenced and what's inferred.
- **Moments that matter:** where frequency, stakes, and frustration are all high. Those are where a product earns its place.
- **Empathy map** per role: what they say, think, do, and feel around the job, each item marked evidence or inference.
- **The user's words:** collect the phrases users use for their problems and goals. Specs, UI copy, and interview questions should use them, not the product team's vocabulary.
- **Walk the current solutions:** try the tools practitioners use today (free tiers, demos, public docs) and note every point of friction.
- **The explain-it test:** could you explain the product idea to a practitioner in their own terms in two sentences, and would they recognize their problem in it?

## 6. Validating what you learned

- Cross-check each important claim across two source types (e.g., a forum complaint corroborated by tool reviews or job-posting requirements).
- Ask the human, or someone who works in the domain, to review the glossary and workflows; mark corrections.
- Mark confidence per section (high / medium / low) and keep the open-questions list honest.
- Real interviews with practitioners outrank everything above; when available, use the primer to prepare for them rather than to replace them.
