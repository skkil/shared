# Design systems, tokens, and handoff

## 1. DESIGN.md as memory
- `DESIGN.md` (template in assets/templates) is the master: product truth, direction contract, tokens, asset system,
  voice, platform notes, allowances, decision log. Read it at the start of every session; update it when decisions change.
- Voice section: if `.vanessa/voice.md` exists, it is the full voice and tone guide; keep this section as a summary that points to it.
- Surface overrides in `.design/surfaces/<surface>.md` (e.g. marketing site bolder than the app) win for that surface only.
- The decision log prevents re-litigating choices and records what was tried and rejected.

## 2. Token architecture
- **Primitive** (raw ramps: `blue.600`, `space.4`), **semantic** (`color.ink`, `color.action`, `space.section`),
  **component** (`button.primary.bg`). Components only reference semantic tokens.
- Name by role, not value. Include motion (durations, easings, springs), radius scale, elevation scale, type roles.

## 3. Emitting tokens per platform
- Web: CSS custom properties; Tailwind v4 `@theme { --color-ink: ...; }`; light/dark via `color-scheme` and data attributes.
- Flutter: `ColorScheme` + `TextTheme` + a `ThemeExtension<AppTokens>` for custom tokens (spacing, radii, motion).
- SwiftUI: Color assets with light/dark variants (or `Color` extensions), `Font` extensions for type roles, a
  `Motion` enum for springs/durations.
- Compose: `MaterialTheme(colorScheme, typography, shapes)` + `CompositionLocal` for custom tokens.
- Multi-platform at scale: Style Dictionary (or Tokens Studio JSON) generating all of the above from one source.

## 4. Component specs
For each component: purpose, anatomy, variants, sizes, states (default, hover, focus, active, disabled, loading,
error), content rules (max lengths, truncation), accessibility (role, name, keyboard, focus order, target size),
motion, platform differences, do/don't. Audit for hardcoded values (colors, sizes not from tokens) and naming drift.

## 5. Handoff spec (designer → engineer, even when both are agents)
Layout (grid, breakpoints, spacing tokens), tokens used, component props, interaction states, responsive behavior,
edge cases (long text, empty, error, offline, RTL), motion specs (trigger, property, duration, easing, reduced-motion
behavior), assets (library ids, formats, sizes, export settings), accessibility notes, open questions.

## 6. Claude Design and Claude Code
- In Claude Design: set up the design system (tokens, type, components) from DESIGN.md before artboards, so every
  artboard inherits it. Export or hand off to Claude Code with the handoff spec.
- In Claude Code: generate token files from DESIGN.md first, then components, then pages. Run slop_lint on the diff.
