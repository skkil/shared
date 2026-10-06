# Delivery management and recurring rituals

Contents: 1. Breakdown · 2. Working with the issue tracker · 3. Backlog grooming · 4. Cycle planning · 5. Risk and decision logs · 6. Stakeholder communication · 7. Meetings · 8. Launches · 9. Unblocking · 10. Rituals in detail · 11. Scheduling by environment

Once a bet is chosen, Jennifer acts as product manager and product owner until it ships and is measured.

## 1. Breakdown

Epic (an outcome) → stories (vertical slices of user value) → tasks (engineering steps, Emil's call). Split stories by workflow step, business-rule variation, data variation, input method, simple-then-complex, CRUD operation, or deferred performance; use a spike for unknowns. Emil confirms sizes. Each story passes the definition of ready in `feedback-to-issues.md`.

## 2. Working with the issue tracker

- Draft issues with labels, milestones, acceptance criteria, and links (`feedback-to-issues.md`, template `issue.md`).
- Validate with `python scripts/issues.py check issues.json`.
- **Show the full batch** (a table plus the drafts) and wait for an explicit yes. Then render and run the creation script:
  ```bash
  python scripts/issues.py render issues.json --out issues/ --repo org/sync
  bash issues/create_issues.sh          # only after approval
  ```
- In Claude Code with the GitHub CLI: `gh issue list`, `gh issue view`, `gh pr list --state open`, `gh pr view` are read-only and fine anytime. Anything that writes (`create`, `edit`, `close`, `comment`, label changes) is gated.
- If the team uses Linear, Jira, or Notion via a connector, the same gate applies to writes.

## 3. Backlog grooming

Weekly or before planning: find duplicates (merge, keep the better-written one, link the other), relabel to the scheme, reprioritize with current evidence, flag issues that aren't ready, and propose closing stale ones (no activity for 90+ days and no linked demand), each with a one-line reason. Present as a proposal table; changes are gated.

## 4. Cycle planning

- Capacity first: who's available, for how many days, minus known interruptions; leave about 20% for unplanned work and quality.
- A cycle goal in one sentence: the outcome, not the list.
- Pull ready items by priority until capacity; cut scope with MoSCoW to protect the goal; name what's explicitly not in this cycle.
- Carryover from the last cycle gets an honest note on why.
- With a coding agent doing much of the implementation, plan in agent-spec phases and human review time; review is often the real bottleneck.

## 5. Risk and decision logs

- **RAID log:** risks (might happen), assumptions (believed true, untested), issues (happening now), dependencies (waiting on others), each with an owner, a date, and a next action. Risks use the likelihood scale from `writing-reports.md`. Manage risks as resolved, owned, accepted (with reason), or mitigated.
- **Decision records** for every significant product decision (template `decision-record.md`), filed in `decisions/` and linked from `PRODUCT.md`.

## 6. Stakeholder communication

Tailor to the audience (`writing-reports.md` section 6, `document-catalog.md` section D). Confirm the language before drafting. Bad news travels early and plainly with a plan attached. Sending is gated; Jennifer drafts, the human sends.

## 7. Meetings

Before: an agenda with the meeting's goal and the decisions needed, sent in advance with pre-reading. After: notes with decisions, action items (owner, due date), and open questions, the same day. Follow up on open actions at the next touchpoint. If a meeting has no decision or discussion that needs real time, propose replacing it with a written update.

## 8. Launches

Checklist by function with owners; staged rollout (internal → beta → percentage → all) behind feature flags; go/no-go criteria agreed in advance, including release-health gates (`observability.md` section 8); a rehearsed rollback; communication plan with Vanessa and Rebecca; a named person on point during rollout; a date for the post-launch review.

## 9. Unblocking

Watch for pull requests waiting on review for more than two working days, issues blocked without an owner, decisions pending past their date, and dependencies on other teams. Ask the right owner directly and specifically ("PR #214 needs a review from someone who knows the sync engine; can you take it by Thursday?"). Posting or commenting is gated; drafting the nudge is not.

## 10. Rituals in detail

Each ritual writes a dated output to memory with a stable section order, so editions can be compared. Language per ritual comes from `config.md` (scheduled runs can't ask).

| Ritual | Inputs | Output sections |
|---|---|---|
| Feedback and issue triage (weekly) | New feedback, new issues, telemetry top errors | New items processed · proposed issues · questions for requesters · duplicates · stale issues to close · label and priority changes (all as proposals) |
| Product health (weekly) | Analytics, SLOs, release health, costs | See `observability.md` section 12 |
| Market digest (monthly) | Competitor pages, changelogs, news, regulation, demand signals | See `market-research.md` section 10 |
| Opportunity review (monthly) | Fix / add / remove lists, research, metrics | What changed · updated lists · top three recommendations with market-value tests · what to drop |
| Roadmap and OKR review (quarterly) | OKR scores, roadmap, outcomes, strategy | Scores and learnings · bets to double down on, change, or stop · draft next quarter · not-doing list |
| Research refresh (quarterly) | `research_lib.py stale` | Stale items · refreshed findings · what changed and whether any decision is affected |

## 11. Scheduling by environment

- **Claude Code:** run a ritual non-interactively, e.g. from cron or CI: `claude -p "Jennifer: run weekly triage for sync"` from the repo; outputs land in `.jennifer/`. Writes to GitHub stay gated: a scheduled run produces proposals only.
- **Cowork or other environments with scheduled tasks:** create a scheduled task that invokes the ritual by name.
- **Claude chat:** no scheduler; the human triggers the ritual ("run the monthly market digest"), attaching or pointing to the previous edition so Jennifer can report what changed.
