# Attributions

This skill is original work that adapts ideas, methods and research from the sources below. No code was copied;
scripts were written from scratch. Where an idea comes from a licensed project, that project's license applies to
the original, and this notice credits it.

## Open-source projects (ideas and methods adapted)
- **Impeccable** (Apache License 2.0): surface modes (persuade/operate/read/experience), deriving directions from
  the audience's world across material families, a dice roll to assign direction, the direction contract,
  color strategies, light/dark from a scene sentence, the overused-font list, and the antipattern catalog that
  informed `slop_lint.py`'s rule set.
- **taste-skill** by Leonxlnx (MIT): design-read and variance/motion/density dials, the combinatorial variation
  engine idea, and parts of the AI-tells list (no fake div screenshots, no placeholder people, no perfect numbers,
  buzzword bans).
- **UI/UX Pro Max** by Next Level Builder (MIT): master design file plus per-surface overrides as persistent memory.
- **video-shotcraft** (Apache License 2.0): pacing rules for product video, real screenshots over mockups,
  independent reviewer passes, seeded randomness.
- **Anthropic skills** (see each skill's LICENSE.txt): frontend-design, canvas-design, algorithmic-art, theme-factory,
  brand-guidelines, slack-gif-creator, web-artifacts-builder; and the design plugin skills (critique, handoff,
  design system, UX copy, accessibility review, user research, research synthesis).
- **Impeccable** v4 (late 2026): the `detect` CLI's CI outputs and stale-waiver reporting, and `doctor`'s
  DESIGN.md drift findings, which informed `slop_lint.py`'s `--github`, stale-allowance and `--tokens` checks; the
  refinement verbs (bolder, quieter, distill, polish, harden, clarify, adapt, delight) behind
  `references/refinement-passes.md`.
- **taste-skill** v2.5 by Leonxlnx (MIT): multi-viewport browser checks (1440/768/390) as part of the gate.
- **oil-ui** by oil-oil (MIT): directions that share at most one trait, the squint test, and a hint-free UX
  walkthrough by an isolated reviewer.
- **interface-design** by Dammyjay93 (MIT): the pre-component checkpoint naming intent and tokens before building.
- **ux-ui-agent-skills** by plugin87 (MIT): the 280px overflow check.
- **emil-design-eng** (master5d/claude-design-skills, after Emil Kowalski's published guidance): the
  interaction-frequency motion budget, no animation on keyboard-initiated actions, no `scale(0)` entries, press
  scale, hover gating by pointer type.
- **open-3d-skills** by Moh4696 (MIT): procedural three.js kit (lathe, sweep, instanced kits), staged exploded
  views, performance budgets and quality tiers, virtual-clock frame capture.
- **motion-graphics-skills** by charlie947 (MIT): one-clock HTML motion pieces, loop frame-match, Reels safe zone,
  delivery encode settings and ffprobe verification that shaped `video_check.py`.
- **claude-drawing-skill** by cloveric (MIT): painting with numpy + Pillow (ink ridges, washes, mist, hatching,
  iso-lines), render-look-fix rounds against a per-style failure list, staged draw-on frames; `draw.py` is
  written from scratch.
- **genart-skill** by camilleroux (MIT): seeded determinism with named sub-streams, contact sheets over single
  renders, attribution and living-artist rules.
- **tastemaker** by codeswithroh (MIT): solving palette role lightness against contrast floors, behind
  `palette.py roles`.
- **brand-identity-skill** by fatihaydost (MIT): mechanism sentence per logo set, 16/32 px logo sheets, measured
  versus judged labels, stopping at the pick checkpoint, color-blindness checks.
- **genjutsu** by AThevon (MIT): hygiene checks (layout-property animation, outline removal, clickable non-buttons,
  timer-driven animation, perpetual motion, instant hover) adapted into `slop_lint.py`.
- **dembrandt** CLI and skills (MIT): extracting live design tokens from a URL and measuring drift (used as a tool).
- **styleseed** by bitjaru (MIT) and **forever-ai-components** by isas1 (MIT): hardcoded-hex checks; faceted
  component registry with agent metadata and pre-retrieval quality gates.
- **Remotion** official agent skills and documentation: frame-driven animation rules (install the official skill
  with `npx skills add remotion-dev/skills`; Remotion has its own license terms at remotion.dev/license).
- **GSAP** official agent skills: referenced as a companion (`npx skills add https://github.com/greensock/gsap-skills`).
- **Retro Diffusion** API documentation: endpoints, styles, idempotency and low-poly export targets.
- **fal.ai** documentation: queue API and per-model `llms.txt` schemas and pricing.

## Articles and research
- Anshu Chimala, "How to turn your AI into a world-class designer" (Lenny's Newsletter): seed strings for real
  variety, ambitious specific prompts, fresh-context critic against a studio bar with reference images, image and
  video generation instead of gradient filler, polish as removal.
- Tridip Thrizu, "AI design slop: the tells, and how I built a tool to catch them" (solodesign.cc, June 2026):
  measurement that written guidance underperforms a mechanical gate, tell migration, scoping rules, never gating motion.
- Codrops' reverse-engineering of an animated product mascot: rect-built SVG characters, anticipation, asymmetric
  easing, landing overshoot, per-frame holds.
- Paul Lacey (Beaver Builder masterclass): approval gates before building.
- Meta, Belmont, the Designer's Field Guide, Kirupa / uxdesign.cc, Debora Vieira, and Figma guides on prompting and
  designing with AI: briefs, user promise, problem framing, content atomization, AI-feature design.
- Richard MacManus, "Skill engineering and the case against one-shot AI design" (Latent Space, 2026): adjectives
  need operational meaning; refinement is human-steered, not one-shot.
- Platform facts on iOS 27 / Liquid Glass and Flutter from Apple coverage and Very Good Ventures (June-Sept 2026).
