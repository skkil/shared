# Discovery: understand the product before designing it

A lead designer's first job is understanding. Polish on a weak concept is wasted. The user is an engineer,
not a designer: translate design decisions into plain reasons, and do the research they would not know to do.

## 1. Gather product truth (infer first, ask second)
Read before asking: README, package.json/pubspec/Package.swift, routes/screens, data models, existing UI,
marketing site, app store listing, docs, issues, analytics if present. Extract:
- What the product does, in the user's vocabulary (feature names, nouns in the data model).
- Who uses it, in what situation (the scene sentence: who, where, device, light, mood, what they did just before).
- The real proof available: numbers, customers, quotes, screenshots, benchmarks.
- Constraints: stack, platforms, brand assets, accessibility needs, budget for generated assets.
Then ask only what changes the work, at most 3 questions at a time, each with a sensible default you will use if
they don't answer. Good questions: "Who is the first user you want to win?" "What should a visitor do in the
first 30 seconds?" "Any brand elements that must stay?" "What's your budget for generated assets?"

## 2. Frame the problem
- Write 3-5 alternative problem statements; pick one and say why. (Belmont-style framing.)
- **User promise** per surface: one sentence the surface must deliver ("Within one minute you'll see your trail's
  closures, pinned to the exact switchback").
- **Category default and its predictable opposite**: describe the page every competitor ships, and the obvious
  contrarian version. Both are ruts; the direction must come from the product's own world.
- Success: an observable behavior or metric.

## 3. Brief
Fill `assets/templates/brief.md` and `assets/templates/DESIGN.md` sections 1-2 (product truth). Keep them short.
**Gate:** confirm the brief with the user in 3-6 lines before rolling directions.

## 4. Deliverables map (what a lead designer would actually produce)
| Request | Deliverables |
|---|---|
| Landing page | brief, 3 directions, DESIGN.md, first-viewport comp, full page, asset plan, copy deck, OG image, mobile check, a11y check |
| App screen / feature UI | flows + states (empty/loading/error), component specs, tokens, platform variants, microcopy, handoff notes |
| Onboarding | aha definition, flow, empty states, checklist, copy, metrics to watch |
| Brand / identity | positioning line, personality, logo (SVG), palette, type, voice, mascot (optional), brand board |
| Launch / marketing kit | key visual, social sizes, OG, store assets, launch video storyboard, copy variants |
| Promo video | brief, script, storyboard, style frames, Remotion project, renders per format |
| Mascot | character bible, turnaround, expression set, rig, state animations, usage rules |
| Design system | token architecture, components with states, platform outputs, docs |
| Review of existing design | critique (critique-qa.md), slop_lint report, prioritized fixes |

## 5. Research-lite (when the user wants it or the risk is high)
- 5 short user interviews beat a survey; ask about the last time they did the job, not opinions about features.
- Watch for workarounds (spreadsheets, copy-paste, screenshots): they reveal the real job, especially for AI features.
- Synthesize into themes → insights → design implications; tag each with evidence count.
- Usability test the riskiest flow with 5 people; task success and where they hesitate.
