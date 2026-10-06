# Reports, operational docs, help content and release content

## Reports and decision memos

A report exists to change a decision or a belief. Before writing, name who reads it and what they should decide, do, or believe afterward; if you can't, it isn't ready to write.

- **Bottom line first** (두괄식 in Korean): the answer, why it matters to this reader, the recommendation, what you need from them. A reader who stops after three lines should act correctly.
- **Headings are claims**, so skimming them tells the story.
- **Keep observation, interpretation and recommendation visibly separate**, so readers can see where the reasoning could be wrong.
- **Name the alternatives** you considered and why you rejected them, a line each.
- **Numbers** carry their source and date; ranges over false precision.

Korean reports: 두괄식, a one-line summary box at the top, 개조식 with a consistent symbol hierarchy (□ → ○ → - → ·) when the audience expects it, 합니다체 or 개조식 but never mixed (`language-ko.md` §2). Keep the actor and the source on lines where responsibility or certainty matters.

Product decision documents (PRDs, strategy, market research) are Jennifer's. When asked to edit one, see `editing-and-audits.md` and `team-handoffs.md`.

## Status updates

Use a fixed shape so readers find things in the same place every week. A good default is Progress, Plans, Problems (Anthropic's internal-comms skill): what moved, what's next, what's blocked and who can unblock it. Lead with what changed since last time; if nothing did, say so in one line.

## Runbooks

Written for someone mid-incident, possibly woken up, on a phone. Title by symptom or alert name. Then:

1. **When to use this**: the alert, the symptom, the dashboard reading.
2. **Impact**: who is affected and how badly.
3. **Access you need** before starting.
4. **Steps**: one action each, the exact command, the expected output, and how to tell it worked. Put dangerous steps behind an explicit check.
5. **Rollback**: how to undo each risky step.
6. **Escalation**: who to call, when, and how.

Short sentences, no background, commands copyable. Verify every command (`sources-and-citation.md` §7) or mark it unverified.

## SOPs, internal guidelines and policies

- **SOP:** purpose in one line, scope, roles, numbered steps with owners, records to keep, review date.
- **Guideline:** the rule first, then the reason, then examples of doing it and not doing it, then exceptions and who grants them. People follow rules they understand.
- **Policy:** scope, the rule, who it applies to, exceptions, the owner, the effective date and next review. Any policy with legal effect (privacy, terms, employment, compliance) gets a visible "Draft: needs lawyer review" banner, and the delivery note says which parts need review and why.

## Help-center articles and troubleshooting

Readers arrive from search with a problem. Title by the task or the symptom in the user's words ("Can't sign in after changing your phone"), answer in the first lines, steps next. Troubleshooting guides order causes by how common they are, each as symptom → cause → fix → how to confirm. Link related articles; don't repeat them.

## Release notes, changelogs and announcements

See `technical-docs.md` (release notes and changelogs) and `marketing-copy.md` (launch announcements). Turning a PRD into release content follows the rules for Jennifer's documents: clarity edits only, questions for anything ambiguous.
