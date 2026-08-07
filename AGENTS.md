# AGENTS.md

> Compact ramp-up guide for AI agents working in this repo.

## Language

Commit messages, PR descriptions and reviews are written in **Korean** (한국어),
matching the rest of the organization. `README.md` is Korean.

`AGENTS.md` and anything under `docs/` is written in **English**.

Everything this repository *publishes* — package names, rule names, workflow
inputs, ADR titles, action outputs — is **English**, so it reads the same way as
the upstream tools it extends (`eslint`, `tsc`, `actions/*`, `terraform`).

---

## What this is

`shared` holds the configuration and conventions that every repository in the
skkil organization consumes. Lint and formatter rules, TypeScript bases,
reusable CI workflows, Terraform modules, ADRs, the org-wide half of the agent
context, and — as the one deliberate exception — copy-once starting-point
templates for files GitHub itself gives no cross-repository reference for.

It exists because the alternative is what `sync` already demonstrates: a
`.eslintrc` and a `tsconfig.json` and a CI matrix that the second application
will copy, after which the two copies drift silently and nobody notices until
they disagree about something that matters.

**This repository is a set of artifacts other repositories point at.** That
sentence is the whole design. Everything below follows from it.

---

## The split with `skkil`

`skkil` (`github.com/skkil/skkil`) already owns org-wide *tooling*. The two
repositories are not competitors, and the boundary between them is sharp:

|                | `skkil`                            | `shared`                                  |
| -------------- | ---------------------------------- | ----------------------------------------- |
| Role           | Control plane                      | Data plane                                |
| Contains       | Verbs — things that run            | Nouns — things that are referenced        |
| Ships as       | A versioned Go binary              | Versioned files resolved by other tools   |
| Consumed by    | `skkil <command>` on a workstation | `extends`, `uses`, `source`, `dependsOn`  |
| Per-repo input | `skkil.yml`                        | A version pin                             |

**The failure mode is a shell script in `shared` that duplicates a `skkil`
subcommand.** If a proposed addition *does* something rather than *declares*
something, it belongs in `skkil`. Check the CLI's command list before adding
anything executable here.

---

## Current state

This repository contains `README.md`, `AGENTS.md`, `CLAUDE.md`, and
`templates/` — the one exception to "reference, never copy," explained below.
Nothing else yet: no packages, no workflows, no modules, and no release tags.

Do not document, reference, or write code against anything not in the left
column — it does not exist yet.

| Exists                      | Does not exist yet                              |
| --------------------------- | ----------------------------------------------- |
| `README.md`, `AGENTS.md`, `CLAUDE.md` | Any published package                 |
| `templates/` — see "The `templates/` exception" | Reusable workflows (`.github/workflows/`) |
| The admission test, below   | Shared agent context (`agents/`)                |
| The versioning policy, below | ADRs (`docs/adr/`)                             |
| The layout plan, below      | Terraform modules, k8s bases                    |

The first thing to land as referenced infrastructure is whatever has two real
consumers. Nothing does yet except lint and formatter config, which is the
agreed starting point. `templates/` is exempt from that bar — see below.

---

## The admission test

Two questions, both of which must be answered before anything is added.

### 1. What breaks if a repository ignores this?

If the answer is "nothing," it is documentation. Documentation is welcome —
ADRs, onboarding, runbooks all belong here — but file it as documentation and
do not count it as shared infrastructure. Infrastructure is the subset that a
machine enforces.

### 2. How does a consumer resolve it?

**By reference, never by copy.** An artifact a human copies out of this
repository has already drifted; there is no signal when it does, and no way to
roll a fix out to the copies. Every artifact needs a resolver:

| Artifact                | Mechanism                                              |
| ----------------------- | ------------------------------------------------------ |
| ESLint / Prettier rules | Published package — `extends: "@skkil/eslint-config"`  |
| TypeScript base         | Published package — `extends: "@skkil/tsconfig/next"`  |
| CI                      | `uses: skkil/shared/.github/workflows/x.yml@v1`        |
| Composite CI steps      | `uses: skkil/shared/.github/actions/x@v1`              |
| Terraform               | `source = "git::…//modules/x?ref=v1"`                  |
| Gradle                  | Version catalog / convention plugin, resolved by Maven |
| ADRs, runbooks          | Read by humans — documentation, per question 1         |

A file that has no row here has no way into a consumer, which means it does not
belong in this repository yet. Add the mechanism first.

---

## The `templates/` exception

Everything above assumes an artifact has a resolver — `extends`, `uses`,
`source`. `templates/` exists for the files that do not: GitHub gives every
repository its own `.github/pull_request_template.md`, `ISSUE_TEMPLATE/`, and
`copilot-instructions.md`, and provides no mechanism for one repository to
reference another's. The only native alternative is an org-wide `.github`
repository serving org-wide defaults, which is a different mechanism entirely
and one this organization has not adopted.

`skkil templates install` (`github.com/skkil/skkil`) shallow-clones this
repository and copies each file a consuming `skkil.yml` declares under
`templates.files` into that repository's root. Once copied, the file belongs
to the consuming repository — there is no version pin, no re-sync, and
divergence afterward is expected, not a defect. That is the opposite of every
other artifact here, which is exactly why it is scoped this narrowly:

- **Only for files with no reference mechanism.** The day GitHub (or any other
  tool) grows one for something currently in `templates/`, that mechanism
  wins and the file moves out. `.github/workflows/` content never belongs in
  `templates/` — reusable workflows already have `uses:`, and copying a
  workflow file instead is the exact anti-pattern this repository exists to
  remove.
- **Not subject to the two-consumer bar.** A bad addition to referenced
  infrastructure costs every consumer at once — a wrong workflow version
  breaks every build that pins it. A bad template costs nothing beyond an
  unused file sitting here; no repository is forced to adopt it. `templates/`
  can hold a repository's first real example of something, not only patterns
  already duplicated twice.
- **Not tag-pinned.** `skkil templates install` always installs from this
  repository's default branch. That decision — no `ref` field, no caching —
  lives in `skkil`'s own `docs/config/v1/example.yml`; do not add a version
  knob here to compensate for it.

---

## Versioning

**Tag releases. Consumers pin tags. Never `@main`.** `templates/` is the one
exception, by design — see "The `templates/` exception" above.

A repository consumed at `@main` means any push to this repository changes every
downstream build simultaneously — which is precisely the coupling the repository
was created to remove. `skkil` already gets this right with its release
binaries; match that discipline.

Blast radius is not uniform, and the rules scale with it:

- **Lint and formatter rules** — a bad change is an annoying PR. Pin anyway.
- **CI workflows** — a bad change breaks every build in the org at once.
- **Anything on a deploy path** — a bad change breaks every deploy at once, at
  the moment when reasoning about what changed is hardest. **Staggered
  adoption is mandatory**: one repository moves to the new tag, runs real
  deploys, and only then does the next one move. Never in a single PR.

---

## Deliberate omissions

Recorded so they are not re-proposed as oversights. Each has a reason and a
condition under which it changes.

- **No deploy scripts.** `sync/scripts/cd/prod-deploy.sh` and `prod-certbot.sh`
  contain a genuinely reusable core — resolve the ECR registry, tag by
  `git rev-parse --short=12 HEAD`, find the EC2 instance by `tag:Project` and
  `tag:Environment`, base64 a script into `ssm send-command`, wait, then report
  Status/stdout/stderr. That block is already duplicated *between those two
  files*, which is the real seam. But it has exactly one consuming platform:
  `skkil` ships as a release binary and never touches EC2. Extracting at n=1 is
  guessing at what platform #2 needs, and deploy is the worst place to guess —
  a wrong abstraction there resolves into `if [[ $PROJECT_NAME == sync ]]`
  branches inside a production path. **Extract when a second platform needs an
  SSM deploy**, as a composite action, and use the two real examples to place
  the seams. Dedupe within `sync` first.

- **`local-deploy.sh` is not ours.** Despite living in `scripts/cd/`, it starts
  LocalStack, boots minikube, applies Terraform, loads images, helm-installs
  External Secrets Operator, applies kustomize overlays and port-forwards. That
  is a development environment, which is `skkil dev`'s job — the heavyweight
  mode that has not made it into the CLI yet (`sync/skkil.yml` declares only the
  lightweight `bootRun` + `pnpm dev` path). It belongs in `skkil`, not here.

- **No thin CI wrappers.** `sync`'s `scripts/ci/build-server.sh` is three lines
  and `build-web.sh` is eight. There is nothing to extract. What is worth
  sharing from CI is the workflow around them, not the scripts.

- **No `.env` templates.** `sync/scripts/setup/web.sh` writes placeholder
  values that are per-repository by definition. Environment remains owned by
  each repository's `.envrc`.

---

## Planned layout

Directories are created when their first real artifact lands, not in advance.
An empty directory with a `.gitkeep` is a promise this repository cannot keep.

```
templates/           files skkil templates install copies into a consuming repo, once
packages/            published npm packages — eslint-config, prettier-config, tsconfig
.github/workflows/   reusable workflows, called with workflow_call
.github/actions/     composite actions
agents/              the org-wide half of AGENTS.md, included by each repo
docs/adr/            architecture decision records
modules/             Terraform modules, once a second environment needs them
```

---

## Consumers

Every addition should name the repositories that will resolve it. Today:

| Repository                    | Stack                          | Plausibly consumes            |
| ----------------------------- | ------------------------------ | ----------------------------- |
| `skkil` (`skkil/skkil`)       | Go 1.26, cobra, GoReleaser     | CI workflows, agent context, ADRs |
| `sync` (`skkil/sync`)         | Java 25 / Spring, Next.js, pnpm | Everything                   |
| `tabs` (`skkil/tabs`)         | Java 26 / Spring, Flutter      | `templates/`, eventually everything else |

`templates/`'s current PR template, issue templates and Copilot instructions
were generalized from `sync`'s `.github/`, which already had them. `tabs` and
`clip` have no `.github/` yet and are the intended next consumers via
`skkil templates install`.

Three repositories, one of which is tooling rather than a product. The shared
surface is genuinely thin right now — CI, agent context, documentation
conventions, and the lint and formatter rules that motivated this repository.

**Rule of three applies.** An abstraction validated once is worse than
duplication: it carries the maintenance cost of a shared artifact plus the
coupling, and the shape is usually wrong. Resist pre-populating this repository
against platforms that do not exist.

---

## Conventions

- **No comments.** Configuration and code published from here must be
  self-explanatory. This is an organization-wide rule, not a preference of this
  repository. Where a rule genuinely needs justification, that justification is
  an ADR, not an inline comment.
- **Every artifact names its consumers.** A PR adding something here states
  which repositories will point at it, and at least one of them should be
  updated to do so in the same change or immediately after. An artifact with no
  consumer is dead on arrival.
- **Additive over editing, across versions.** When a published contract changes
  shape, add the new version alongside the old rather than editing in place, and
  give consumers a tag to move to on their own schedule. `skkil` follows the
  same rule with `docs/config/v<n>/`.
- **Breaking changes are announced in the release notes**, in Korean, naming
  every consuming repository and what each must do.

---

## Tech Stack Quick Reference

|             |                                                        |
| ----------- | ------------------------------------------------------ |
| Consumers   | `skkil/skkil` (Go), `skkil/sync` (Spring + Next.js), `skkil/tabs` (Spring + Flutter) |
| Publishes   | npm packages, reusable workflows, composite actions, `templates/` (copy-once) |
| Versioning  | Git tags; consumers pin, never `@main`                 |
| Companion   | `skkil` CLI — control plane to this repository's data  |
