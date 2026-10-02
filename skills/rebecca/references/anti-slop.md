# Removing AI tells

Read this before any visual or copy work, and again before delivery.

## Contents
1. Why AI design looks like AI design
2. What actually makes an agent comply (the system)
3. Tell migration: what the model reaches for next
4. The catalog, by layer (visual, structure, copy, motion, imagery, native, desktop, marketing, slides)
5. Self-check questions

---

## 1. Why AI design looks like AI design

A model predicts the most probable output. Every decision you leave open (font, accent, layout, hero, copy) gets
filled with the training-data average, and the average is now recognizable as a fingerprint. Three findings shape
everything in this skill:

1. **Written guidance alone can make it worse.** Measured runs (solodesign.cc, June 2026) compared no skill, written
   anti-slop guidance, and a mechanical gate. Written guidance scored equal to or worse than no skill on 5 of 6
   components. The model read "be distinctive" as "add more," and more is the slop. Only a mechanical gate the agent
   had to pass brought failures near zero.
2. **Banning a default moves the model to the next default.** Ban indigo and it picks emerald. Ban Inter and it picks
   a trendy serif. Ban gradients and it adds glows. The cure is not a longer ban list. It is making the decision
   *before* the model gets to default: external randomness, product grounding, and tokens locked in DESIGN.md.
3. **Anti-slop skills created a second generation of slop.** The cream background, italic serif hero, terracotta
   accent, dotted eyebrow label and mono captions became "tasteful AI" because many skills pushed models away from
   purple SaaS toward "editorial." Distinctive for one project becomes a uniform across thousands.

A real brand spec fixes *distinctiveness* (the brand already made the hard calls) but not *slop*: with no brand to
follow, the model falls straight back to its defaults. You need both a direction and a gate.

## 2. What actually makes an agent comply

Use all of these together. Each one covers a failure the others miss.

| Mechanism | What it fixes | How in this skill |
|---|---|---|
| **Decide before generating** | defaults fill open decisions | Brief + product truth + `creative_roll.py` directions, then lock tokens in DESIGN.md before code |
| **External randomness** | LLM near-determinism, sameness across projects | `creative_roll.py deal` (seeded, history-aware), seed strings for inspiration |
| **Ground in the product's world** | random-but-arbitrary choices | Every rolled pick is fused with who uses the product, where, and what it proves |
| **Mechanical gate** | known tells, every build | `slop_lint.py` must exit 0. Fix FAILs, review WARNs, re-run. Loop until it passes |
| **Positive alternatives** | tell migration | Every lint rule names what to do instead. Use that, not "something else" |
| **Fresh-context critic** | the ceiling no rule can reach | Subagent sees screenshots only, scores against a studio bar (critique-qa.md) |
| **Subtraction pass** | "add more" reflex | Before delivery, remove one decorative element per section; keep only what serves the story |
| **Approval gates** | the AI deciding for the user | User picks direction, approves comps, approves every paid generation |
| **Scoped rules + allowances** | false positives, fighting the brief | Rules fire on decorative contexts only; `.design/slop-allow.json` records brief-mandated exceptions |

### Rules for using the gate well
- **Never gate the existence of motion.** When a gate failed builds for motion without a reduced-motion fallback,
  the model stopped writing motion entirely and pages went dead. Gate repetition (entrance spam) and missing
  reduced-motion handling as a warning, never motion itself.
- **Don't trust a zero score blindly.** A detector that reports zero can be broken. Look at the screenshots.
- **A clean lint is the floor, not the goal.** It proves known tells are absent, not that the design is good.
- **The brief wins.** If the user asked for cream paper and italic serifs, allow those rules with the quoted reason
  and make that look excellent. Tells are defaults nobody chose. A chosen look is not a tell.
- **When you remove a tell, replace it with a decision from DESIGN.md**, never with the next-nearest default.

## 3. Tell migration

When you remove the left column, the model reaches for the right column. Pre-empt both.

| Removed | Next default it reaches for | Pre-empt with |
|---|---|---|
| Indigo/purple accent | Emerald, then acid green, then terracotta | A hue chosen from the product world, recorded with a reason |
| Inter | Geist, Space Grotesk, then Fraunces/Instrument Serif | A face picked from the type deck for this world |
| Purple gradient hero | Dark ground + colored glow, then cream + serif | Ground from the scene sentence; committed color fields |
| Three icon cards | Bento grid with six accent colors | Show the product working; one dominant item |
| Gradient orbs | Grid/dot-field background, then grain overlay everywhere | Authored asset or an honest flat field |
| Eyebrow label | Numbered section labels, then mono captions | Let headings stand alone |
| "Seamless" copy | "Thoughtfully crafted," "designed for humans" | Concrete nouns and verbs from the product's domain |
| Em-dashes | Colons and "Here's the thing:" cadence | Short declarative sentences |
| Fade-up on scroll | Stagger-everything, then parallax everywhere | One orchestrated moment + interaction feedback |

## 4. The catalog

Each tell lists a fix. "Lint" marks tells `slop_lint.py` detects mechanically. The rest need the critic and your eyes.

### 4.1 Visual: first generation (2024-25)
- Purple/indigo/violet gradients, indigo→pink heroes (lint) → one committed brand color owning whole regions.
- Gradient text on headings or metrics (lint) → size/weight/solid accent.
- Inter/Roboto/Poppins/Montserrat everywhere (lint) → a face from the world; Inter only for a dense Operate UI with a written reason.
- Row of three rounded cards with icon tiles (lint) → show the feature working; vary scale.
- Glassmorphism on content cards (lint) → translucency only on the control layer, as platforms do.
- Blurred gradient orbs behind the hero (lint) → authored imagery or flat.
- Dark mode + neon accents + colored glows (lint) → choose dark only when the scene says so; real elevation.
- Everything centered, symmetric, equally spaced → asymmetry with a strong axis; rhythm of tight and loose.
- One border-radius and one soft shadow on everything (lint) → radius and elevation scales tied to role.
- Thick colored left border on cards/callouts (lint) → spacing, type, or a full tinted surface.
- Hairline border + wide diffuse shadow on the same card (lint) → commit to one.

### 4.2 Visual: second generation (2026, "tasteful AI")
- Warm cream/beige ground (#F4F1EA family) (lint) → ground from the scene and materials.
- Oversized italic serif hero (Fraunces, Playfair, Instrument Serif, Newsreader) (lint) → match face to register; italic only where content earns it.
- Terracotta/clay accent (lint) → product-world hue.
- Tiny uppercase tracked eyebrow above headings, often with a leading dot or trailing rule (lint) → delete.
- Monospace captions/labels/body as a "technical" costume (lint) → mono only for code/data.
- Colored glow on dark sections, radial spotlight behind hero (lint) → light from the scene.
- Emerald or acid-green default accent (lint) → chosen hue.
- 01/02/03 numbered sections on non-sequences (lint) → number only real steps.
- Middot meta strings "Design · Code · Ship" (lint) → sentence or columns.
- Bento grid where every tile has a different accent hue → one dominant tile, shared palette.
- Hairline "broadsheet" rules everywhere, tiny serif footnotes → only where the content is genuinely editorial.

### 4.3 Structure
- The template page: hero → logo strip → 3 features → testimonial carousel → pricing → FAQ → CTA → mega footer.
  → Build the page from the STORY in the direction contract; sections follow the argument, not a template.
- Hero-metric template: big number + label + gradient accent → one honest chart or a real outcome.
- Fake product UI built from divs (skeleton bars, fake charts) → real screenshots, real states, real data.
- Every section the same height and density → vary rhythm: a dense section, then a breather.
- Generic nav (Features, Pricing, About, Blog, Contact) on a one-page product → only links that exist.
- Mega footer with dead links and fake social icons → minimal real footer.
- Logo strip of "trusted by" brands the product does not have → real customers with permission, or nothing.
- Testimonial cards with stock avatars → real names, roles, photos, or no testimonials.
- FAQ that answers nothing → real objections from sales/support.

### 4.4 Copy
- Buzzwords: elevate, seamless, unleash, supercharge, empower, cutting-edge, all-in-one, leverage, streamline (lint).
- Manufactured-contrast aphorisms: "Not a tool. A revolution." "No X. No Y. Just Z." "X. Reimagined." (lint).
- Triads: "Fast. Simple. Powerful." → one specific claim.
- Em-dash cadence (lint) → periods.
- CTAs that name no outcome: Get Started, Learn More (lint) → "Create your first board."
- Arrow glyphs on every link (lint) → label carries the action.
- Invented stats: 99.9%, 10x, 10,000+ teams (lint) → real numbers with sources, or none.
- Placeholder people and companies: Jane Doe, Acme (lint) → realistic, locale-appropriate sample content, labeled as sample.
- Emoji as icons or heading decoration (lint) → one icon family.
- "Scroll to explore," "Welcome to X," "Introducing X" (lint for scroll cue) → a first viewport that is complete.
- Over-labeled UI (headings that restate the obvious, helper text under every field) → cut.
- AI-writing cadence: "Here's the thing," "Let's dive in," "In a world where," rhetorical questions in headlines.

### 4.5 Motion
- The same fade/slide-up on every section (lint) → one orchestrated moment.
- Infinite marquees and logo carousels (lint) → static curated proof.
- Typewriter text and blinking cursors (lint) → real product state.
- Bounce/elastic easing on UI (lint) → exponential ease-out; springs with low bounce. Overshoot belongs to characters.
- Hover-scale on every image (lint) → stillness or a meaningful reveal.
- Parallax on everything, scroll-jacking, pinned sections that trap the reader → one scrubbed object at most.
- Pulsing "live" dots with nothing live (lint) → only for real state.
- Content hidden at rest waiting for a reveal that fails → content visible by default; animate from visible states.
- Missing reduced-motion handling (lint, warning) → render the end state.

### 4.6 AI imagery
Tells: plastic skin and surfaces, over-smooth gradients, centered symmetric subject, three-quarter "hero" angle every
time, rim light + bokeh, teal/orange or purple/cyan grade, glossy "default render" 3D, floating objects with no contact
shadow, impossible hands and text, every image the same lighting, dense meaningless background detail, abstract
3D blob sculptures as filler, the "diverse team smiling at a laptop" stock look, isometric everything.

Fixes, in order of cost:
1. **Direct it.** Name the medium, lens, light direction, materials, wear, and palette hexes. Specify a flat solid background for anything you will composite.
2. **Pick the right tool.** True pixel art from Retro Diffusion, not a "pixel art style" prompt on a general model. Vectors from Recraft. Type in images from GPT Image.
3. **Composite honestly.** Key the subject (post.py key), ground it with a real contact shadow (post.py shadow), place it on the brand's ground.
4. **Bring it onto the palette.** post.py palette-map, duotone, or riso. This alone removes most of the "AI grade."
5. **Add tactile imperfection.** post.py grain, halftone, riso. Crop aggressively and asymmetrically.
6. **Combine with real material.** Real type, real UI screenshots, real photos of the product or team.
7. **Keep one system.** Same medium, light, palette, outline weight across every asset (the DESIGN.md asset system).

### 4.7 Mobile and native apps
- Untouched starter themes: Flutter `ColorScheme.fromSeed(seedColor: Colors.deepPurple)`, Compose Purple40/80, Android purple_500 (lint) → theme from DESIGN.md tokens.
- Stock Material/Cupertino with no brand expression at all → brand in color, display type, iconography, illustration, empty states, haptics.
- The opposite failure: web-landing-page styling inside an app (giant heroes, marketing copy) → Operate mode: platform conventions, brand in details.
- Custom glass on content cards. On iOS 27, Liquid Glass belongs to the control/navigation layer floating over content (lint flags glass overuse).
- Three-screen illustrated onboarding carousel ("Welcome to X") → value-first onboarding: get to the aha moment.
- FAB on every screen, elevation 2 on every card, gradient app icon with a white glyph → icon from the brand world, tested at small sizes and in tinted/dark variants.
- Ignoring Dynamic Type / font scaling, tap targets under 44pt/48dp → accessibility is part of craft.
- Splash screen with a pulsing logo → fast launch to real content.

### 4.8 Desktop apps
- "Website in a window" (Electron/Tauri): web nav bar, hero header, huge padding, hamburger menu → native-feeling title bar, menus, shortcuts, context menus, density.
- No keyboard support; modal dialogs for everything → keyboard-first, inline editing, undo.
- Ignoring the OS: no dark mode, no accent color, wrong font rendering → respect system appearance and materials (macOS Liquid Glass sidebars, Windows Mica).

### 4.9 Marketing, social, video, slides
- Glowing product on a dark gradient; slow push-in on a glossy object; generic AI-video sameness → real product footage, the world's own materials, cuts on beat.
- Template social carousels ("3 reasons why...") with icons → one strong image + one specific claim.
- Stock-like AI people in ads → real customers, illustration, or the product itself.
- Slides: title + 3 bullets + an icon per bullet → one idea per slide, a real image or chart, large type.
- OG images with the logo centered on a gradient → the product's key visual + the page's specific claim.

## 5. Self-check questions (answer before showing anything)

1. Could someone guess this aesthetic from the product category alone? Then it is the category default. Revisit the roll.
2. What is the one thing in the first viewport that only this product could show?
3. If I removed all text and logos, is it still recognizably this product's world?
4. Did I choose every font, color, radius and motion, or did any arrive by default? Name each one's reason.
5. Is any element decoration that serves nothing? Remove it.
6. Does every claim have proof we actually have?
7. Does `slop_lint.py` pass, and did I look at the screenshots anyway?
8. Would the critic's memory test produce a specific thing, not a mood?
