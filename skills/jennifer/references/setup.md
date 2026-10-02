# Setup, memory, and environments

Contents: 1. First session · 2. Config decisions and defaults · 3. Memory layout · 4. PRODUCT.md · 5. Environments · 6. Useful connectors · 7. Hygiene

## 1. First session

1. Scaffold memory: `python scripts/research_lib.py init` (creates `.jennifer/` in the current directory, or `$JENNIFER_HOME`). In Claude chat, skip this and keep memory in attached files (section 5).
2. Walk the human through the config decisions in section 2. Ask them in one short batch; offer the defaults; don't block on any of them.
3. Pick one or two starting products. For each, build `PRODUCT.md` from the product's sources (`discovery.md` section 2): feature inventory, flow map, stage, segments, job, open issues.
4. If nothing is instrumented, propose an event tracking plan and SLOs for critical journeys as the first deliverables.
5. Record which tools are connected (GitHub, analytics, error tracking, Slack, docs) in `config.md`.

## 2. Config decisions and defaults

| Decision | Why it matters | Default if unanswered |
|---|---|---|
| What "market value" means here (revenue, adoption, research impact, grant fit, a mix) | Weights the market-value test | Ask per product; record in `PRODUCT.md` |
| Markets: Korea, global, or both | Sets default sources and competitors | Both |
| Ritual languages | Scheduled runs can't ask | The language the human uses most |
| Starting products | Focus | The product with the most issue activity |
| Analytics and telemetry instrumented today | Decides whether to start with a tracking plan | Assume none until shown |
| Where work is tracked (GitHub Issues/Projects, Linear, Jira, Notion) | Where issues go | GitHub Issues |
| Research budget (total and per study) | Paid data, panels, API-billed simulations | Zero without approval |
| Simulated-interview backend | Which separate-agent route to use | `auto` (Claude CLI, then API, then manual) |
| Autonomy for rituals | Drafts only, or post somewhere | Drafts only |
| Stakeholders and formats | Who gets which updates | The human only |
| Research with real people under IRB? | University research ethics | Ask before recruiting |

Document language is not a config default: Jennifer asks for each new document.

## 3. Memory layout

```
.jennifer/
  config.md
  products/<product>/PRODUCT.md
  research/YYYY-MM-DD-<topic>.md         market briefs, competitor scans, digests
  research/index.json                    maintained by research_lib.py
  domains/<domain>.md                    domain primers
  interviews/<id>-card.md                persona cards and participant profiles
  interviews/<id>.json                   simulated-interview sessions (sim_interview.py)
  interviews/<id>-transcript.md          exported transcripts
  ideas/journal.md
  decisions/YYYY-MM-DD-<decision>.md
  lens_history.json
```

Default staleness horizons for `research_lib.py add --stale-days`: competitor pricing 30 days; market data and competitor scans 90; user research and domain primers 180; strategy documents 180.

## 4. PRODUCT.md

The product memory, one per product (template `assets/templates/PRODUCT.md`): vision; target users and the job; stage; North Star and input metrics; critical journeys and SLOs; positioning; business model and the market-value definition; current bets and roadmap; fix / add / remove lists; opportunity solution tree; assumptions log (with how each will be tested); decision log; tried-and-rejected log (with reasons and the evidence that would reopen each); links to research and primers. Keep it under a few pages by linking out; it's read at the start of every session.

## 5. Environments

| Capability | Claude Code | Cowork | Claude chat |
|---|---|---|---|
| Read the product's code and docs | Yes, directly | Files in the workspace | Only what's attached or connected |
| Memory | `.jennifer/` files | Workspace files | Attached `PRODUCT.md` or Project knowledge; Jennifer outputs updates to save |
| GitHub | `gh` CLI (writes gated) | Connector if available | Connector if available |
| Web research | Web search and fetch tools | Same | Same |
| Separate agent for simulated interviews | `sim_interview.py` with `claude` CLI or API; subagents | Same | `manual` backend (human pastes into a separate chat) or API from the code sandbox if a key is configured |
| Scheduled rituals | cron or CI with `claude -p` | Scheduled tasks | On request |
| Document formats | Markdown in the repo | Files | The environment's document tools, or markdown; Word, PowerPoint, Excel on request |
| Scripts | Yes | Yes | Yes, in the code sandbox |

## 6. Useful connectors

GitHub (issues, PRs, discussions), product analytics (PostHog, Amplitude, Mixpanel, GA4), error tracking (Sentry, Crashlytics), Slack and calendar (updates, meetings), docs (Google Drive, Notion), trackers (Linear, Jira), survey tools (Google Forms, Typeform), and a browser tool for competitor teardowns. Jennifer uses what's connected and suggests a connector only when a task needs one.

## 7. Hygiene

- Never store secrets, tokens, or real participants' personal data in `.jennifer/`. Anonymize real-interview transcripts before saving; add real-participant files to `.gitignore` if the folder is committed.
- Teammate skills (Rebecca, Emil, Wren, Otto, Quinn, Sasha, Kil) may not be installed; Jennifer writes handoffs as standalone documents the human can pass on.
