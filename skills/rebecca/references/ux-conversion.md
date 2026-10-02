# UX, conversion, onboarding, microcopy, AI features

## 1. Surface modes
- **Persuade** (landing, pricing, launch): earn a decision. Bold direction, one primary action, proof near the action.
- **Operate** (app, dashboard, tool): get work done. Conventions, density, speed, keyboard, states.
- **Read** (docs, articles, changelogs): comprehension. Measure, hierarchy, navigation, code blocks.
- **Experience** (showcase, game, portfolio): feeling and exploration. Highest motion budget.
Pick the mode per surface; it sets dials (creative_roll.py does this automatically).

## 2. Landing pages that convert
- **5-second test**: what is it, who is it for, what do I do. The first viewport answers all three.
- **Show the product working** (real UI, demo, output) instead of describing it.
- **One primary CTA** that names the outcome; a sticky or repeated CTA on long pages; secondary actions visually quieter.
- **Specific, named proof near the CTA**: customer name, role, outcome with a number; logos only with permission.
- **Handle objections** in the order a buyer has them (price, effort to switch, security, "will it work for me").
- **Message match**: ad/email/referrer promise = headline promise.
- **Speed is conversion**: LCP under ~2.5s on mobile; motion loads after content.
- Short forms: ask only what is needed now; social sign-in where appropriate.
- Structure follows the STORY in the direction contract, not a section template (anti-slop.md 4.3).

## 3. Onboarding and activation
- Define the **aha moment** (the first time the user gets real value) and the shortest path to it.
- Value first: let users do the core action before account setup where possible.
- Empty states are onboarding: one sentence of value, one primary action, an example of a filled state.
- A 3-5 item checklist for multi-step setup; celebrate real milestones only (once, briefly).
- Progressive disclosure: advanced options appear when needed.
- Measure time-to-value and activation rate; design to move those.

## 4. Forms and flows
- Labels always visible (not placeholder-only), inline validation after blur, errors next to the field.
- Error messages: what happened, why, how to fix ("Card declined by your bank. Try another card or contact them.").
- Destructive actions name the object and consequence ("Delete 'Q3 roadmap' and its 14 tasks?"); offer undo where possible.
- Respect platform input types, autofill, and keyboard types on mobile.

## 5. Microcopy
- Verbs on buttons, named outcomes, consistent nouns (one name per concept across UI, docs, marketing).
- Sentence case. Short. The user's vocabulary, not internal jargon.
- Voice from DESIGN.md; tone adapts (playful in success, plain in errors, serious in money and data).
- No buzzwords, no em-dash cadence, no aphorisms (slop_lint enforces the common ones).

## 6. Delight (proportional)
One delight thesis per product, tied to its job: a mascot that reacts to real events, a satisfying completion
moment, a tactile control, an easter egg. Delight never slows a frequent task or appears in error/money moments.

## 7. Designing AI features
- Make inputs and outputs explicit: what the AI uses, what it produces, how confident it is, where it came from.
- Balance control and automation: suggest → preview → apply; always editable; easy undo.
- Design latency (streaming, skeletons with real structure, progress you can trust) and failure (clear fallbacks).
- Treat the AI as its own layer in the UI with consistent affordances, not sprinkled sparkles.
- Narrow scope beats a general chat box; watch users' workarounds to find the real job.
- Avoid AI clichés: sparkle icons everywhere, purple gradients for "AI," fake typing.

## 8. Trust and ethics
No dark patterns (fake scarcity, confirmshaming, hidden costs, pre-checked upsells, roach-motel cancellation).
Honest pricing, clear data use, accessible by default.
