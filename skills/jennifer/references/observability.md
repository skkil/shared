# Observability: what to track, and what to steer by

Contents: 1. Two kinds of telemetry · 2. Signal frameworks · 3. Client and mobile quality · 4. SLIs, SLOs, and error budgets · 5. Choosing what to track · 6. Metrics that guide the product · 7. Metrics by product type · 8. Observability-driven product work · 9. Instrumentation in every spec · 10. Privacy in telemetry · 11. Tools · 12. Weekly product health

Users experience reliability and speed as product quality: a sync that silently fails is a broken feature, whatever the roadmap says. Jennifer treats operational telemetry as product evidence and co-owns reliability targets with Emil and Otto.

## 1. Two kinds of telemetry

- **Product analytics** answer "what do users do?": events such as `file_shared`, funnels, cohorts, retention. Tools: PostHog, Amplitude, Mixpanel, GA4.
- **Operational observability** answers "how does the system behave?": metrics (counts, rates, latencies), logs (structured events with context), traces (one request across services), and sometimes profiles. **OpenTelemetry** is the vendor-neutral standard for collecting them.
- **Client telemetry** (real-user monitoring, crash reporting) sits between the two: it measures what each user actually experienced.

The most useful questions need both, joined by a user, session, or request ID: "Did users who hit sync errors in week one retain worse?" Make sure the IDs exist in both systems (without putting personal data into logs; section 10).

## 2. Signal frameworks

Pick the framework that fits what you're measuring:

| Framework | For | Signals |
|---|---|---|
| Four golden signals (Google SRE) | Any user-facing system | **Latency** (separate successful and failed requests), **traffic** (demand), **errors** (explicit, implicit such as wrong content, and policy failures such as too slow), **saturation** (how full the most constrained resource is) |
| RED | Request-driven services and APIs | **Rate**, **errors**, **duration** per endpoint |
| USE | Resources: CPU, memory, disk, queues, connection pools | **Utilization**, **saturation**, **errors** |
| DORA keys | The delivery process itself | Deployment frequency, lead time for changes, change failure rate, time to restore service (DORA's model evolves; check the latest report) |

Always look at **percentiles** (p50, p95, p99), not averages: an average latency of 200 ms can hide 5% of users waiting 4 seconds, and those users are the ones who churn.

## 3. Client and mobile quality

- **Web, Core Web Vitals** (Google; measured at the 75th percentile of real page loads): **LCP** (largest contentful paint, loading) good at ≤ 2.5 s; **INP** (interaction to next paint, responsiveness; replaced FID in March 2024) good at ≤ 200 ms; **CLS** (cumulative layout shift, visual stability) good at ≤ 0.1. Lab tools (Lighthouse) are for debugging; field data (real users) is what counts.
- **Android:** Google Play's core vitals are user-perceived crash rate and user-perceived ANR (app not responding) rate. Above the overall bad-behavior thresholds of **1.09%** and **0.47%** respectively, Play may reduce the app's visibility; there is also a per-phone-model threshold of 8%. Also track cold-start time and frozen frames.
- **iOS:** crash rate, hang rate, launch time, and disk and battery use (Xcode Organizer, MetricKit).
- **Crash-free users and sessions** per release version: the standard release-health measure; compare each new version with the previous one during rollout.
- **Desktop apps, CLIs, browser extensions:** opt-in crash reporting, command or action success rate, execution time percentiles, and the versions in use (old versions in the wild are a support cost).

## 4. SLIs, SLOs, and error budgets

- **Critical user journeys** first: the 3-5 things users must be able to do (sign in, sync a file, share a document, run a search). Reliability is defined per journey, not per server.
- **SLI** (service level indicator): good events ÷ valid events for a journey, measured as close to the user as possible. "Proportion of sync jobs that complete successfully within 30 s."
- **SLO** (objective): the target for the SLI over a window. "99.5% of sync jobs complete within 30 s, over 28 days." Choose it from what users notice and tolerate, informed by current performance. Never 100%: perfect reliability is infinitely expensive, and users can't tell 99.99% from 100% through their own network.
- **Error budget** = 1 − SLO. At 99.5% over 28 days, 0.5% of sync jobs may fail or be slow. The budget is a product decision tool: while budget remains, ship features and take risks; when it's exhausted, the agreed **error-budget policy** shifts the team toward reliability work until it recovers. Jennifer drafts the policy with Emil and Otto; the human approves it.
- **Alert on symptoms, not causes:** page a human when the SLO is burning fast (users are hurting now), not when CPU is high. Everything else is a ticket or a dashboard.
- Keep SLOs few: one or two per critical journey. Template: `assets/templates/slo-sheet.md`.

## 5. Choosing what to track

A metric earns its place only if someone will act when it changes. For each candidate, write: the question it answers, who acts on it, what action, and at what threshold. If nobody would act, don't build a dashboard for it; logs can answer one-off questions later.

Rules of thumb:
- Measure journeys, not components; the user doesn't care which microservice failed.
- Segment by platform, app version, region, plan, and new vs returning users. Problems hide in segments (one Android model, one ISP, the newest release).
- Leading signals (error rate during rollout) protect lagging outcomes (monthly retention).
- High-cardinality labels (user IDs on metrics) explode cost; put those in logs and traces instead.
- Every metric has a written definition in the metric dictionary (`metrics-experiments.md`).

## 6. Metrics that guide the product

Steer by a small, layered set, and say which layer each decision touches:

1. **Outcome:** the North Star and its input metrics (product analytics). These decide what to build.
2. **Quality guardrails:** SLOs for critical journeys, crash-free rate, Core Web Vitals or app vitals. These decide whether a release is healthy and when reliability outranks features. A feature that moves the North Star while breaking a guardrail isn't a win.
3. **Efficiency:** infrastructure cost per active user, AI cost per successful task, support tickets per 1,000 active users. These decide whether growth is sustainable and which plans are viable.

Proxy traps to avoid: uptime of servers (users may still fail), average latency (hides the tail), raw error counts (rise with traffic; use rates), and number of alerts (measures noise).

## 7. Metrics by product type

| Product | Journey SLIs and quality signals worth tracking |
|---|---|
| Sync or storage tool | Sync success rate; time to consistency across devices (p95); conflict rate; data-loss incidents (target zero, each one reviewed); upload and download throughput by network type |
| Web SaaS | Key-action success rate; API latency p95 per key endpoint; LCP and INP on main pages; error rate on save and submit; background job delay |
| Mobile app | Crash-free users per version; ANR rate; cold start; push delivery and open; offline-to-online recovery success |
| CLI or developer tool | Command success rate; execution time p95; install success; version adoption; crash reports (opt-in) |
| Browser extension | Injection or activation success on target sites; page-load overhead added; error rate after browser updates |
| AI feature | Time to first token and total latency; timeout, error, and refusal rates; eval pass rate on sampled production traffic; cost per successful task; user corrections or thumbs-down rate; fallback rate when the model fails |

## 8. Observability-driven product work

- **Top errors by users affected** feed the Fix list every week (rank by unique users hit, not raw counts).
- **Reliability vs retention:** compare retention of users who hit a failure on a critical journey in their first week with those who didn't. This is usually the strongest argument for reliability work, and it puts reliability in product terms.
- **Release health gates:** staged rollouts proceed only if the new version's crash-free rate and SLIs are no worse than the previous version's. Write the gate into the release plan.
- **Post-incident reviews** include product impact: users and journeys affected, duration, data loss, what users saw, how we told them, and what we'll change. Blameless; focused on the system.
- **Performance budgets** in specs: "Opening a folder of 1,000 files renders the first screen in under 1 s at p95 on a mid-range Android phone."

## 9. Instrumentation in every spec

A feature isn't done until it can be observed. The PRD's analytics section lists:
- product events (tracking plan),
- the SLI for the feature's journey and whether it joins an existing SLO,
- structured logs needed to debug it, with correlation IDs,
- traces for multi-step flows,
- the dashboard panel and any alert, each with an owner,
- sampling and retention.

These become acceptance criteria: "Given the feature flag is on, when a share completes, then `file_shared` fires once with `share_type`, and the share-journey SLI counts it."

## 10. Privacy in telemetry

- No personal data in logs, metric labels, or event properties unless the privacy review approved it; scrub emails, names, tokens, file contents, and free text. Under GDPR, IP addresses and device identifiers can be personal data.
- Analytics consent where law requires it (cookie and tracking rules in the EU; Korea's PIPA for personal information).
- Retention limits per data type, enforced by configuration.
- Sasha reviews the telemetry fields of every new feature. Session replay tools need masking of inputs and sensitive screens by default.

## 11. Tools

Options, not endorsements; choose with Emil based on stack and budget: OpenTelemetry for collection; Prometheus and Grafana for metrics and dashboards; Sentry or Firebase Crashlytics for errors, crashes, and release health; Honeycomb, Datadog, or New Relic for full observability; PostHog (analytics, feature flags, session replay), Amplitude, Mixpanel, or GA4 for product analytics; Google Play Console (Android vitals) and Xcode Organizer for app stores; PageSpeed Insights and the Chrome UX Report for field Web Vitals. Paid plans go through the spending gate.

## 12. Weekly product health

The weekly ritual output, one screen:
1. Bottom line: healthy / watch / act, and why.
2. North Star and inputs vs last week and target.
3. SLOs: current attainment and error budget remaining per critical journey; burn-rate alerts fired.
4. Release health: crash-free rate and vitals for the current and previous versions.
5. Top three errors by users affected, with linked issues.
6. Cost per active user, if tracked.
7. What changed and what Jennifer recommends (each with an owner).
