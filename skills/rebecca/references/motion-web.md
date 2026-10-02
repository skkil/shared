# Motion and visuals on the web (CSS, View Transitions, Motion, GSAP, Three.js/R3F, Lottie, Rive)

## Contents
1. Principles and tokens
2. Choosing the technique
3. Recipes
4. Performance and accessibility
5. Companion skills (Claude Code)

## 1. Principles and tokens

Motion has four jobs: **orient** (where am I, what changed), **feedback** (I heard you), **continuity** (this became
that), **delight** (the one signature moment). Anything that does none of these is noise. Spend motion boldness in
one place per surface; everything else is quick, quiet feedback.

Duration tokens (UI): micro 100-150ms (press, toggle) · small 200-250ms (hover, tooltip, chip) · medium 300-400ms
(panel, modal, accordion) · large 450-700ms (page transitions, hero choreography). Exits ~20-30% shorter than entrances.
Big distance or big size → longer; frequent interactions → shorter.

Easing tokens: enter/standard `cubic-bezier(0.16, 1, 0.3, 1)` (expo-out) or `(0.2, 0, 0, 1)`; exit
`cubic-bezier(0.4, 0, 1, 1)`; on-screen movement `cubic-bezier(0.65, 0, 0.35, 1)`. Springs for gestures and
physical UI: stiffness 300-500, damping 25-35 for UI; lower damping (more bounce) only for characters and toys.
Never linear for UI movement (linear is for progress, rotation loops, marquee-like scrubs).

Choreography: stagger 30-60ms, max ~6 items before grouping; one leader element moves first; content is
visible by default and animates from a visible state, so a failed script never hides content.

Write motion tokens into DESIGN.md and use them as CSS custom properties / JS constants everywhere.

## 2. Choosing the technique

| Need | Use | Why / notes |
|---|---|---|
| Hover, press, focus, simple state changes | CSS transitions | Zero JS; animate transform/opacity/filter/clip-path only |
| Looping decoration, simple keyframes | CSS `@keyframes` | Pause offscreen; respect reduced motion |
| Page-to-page or state-to-state continuity | **View Transitions API** (`document.startViewTransition`, cross-document `@view-transition`) | Shared-element morphs with `view-transition-name`; graceful no-op where unsupported |
| Scroll-linked reveal or progress without JS | **CSS scroll-driven animations** (`animation-timeline: view()` / `scroll()`) | Runs off the main thread; feature-detect with `@supports` |
| React state, layout changes, gestures, exit animations | **Motion** (`motion/react`: `motion.div`, `AnimatePresence`, `layout`, `useScroll`, `useSpring`, drag) | Declarative; springs by default; `MotionConfig reducedMotion="user"` |
| Complex sequenced timelines, scrollytelling, SVG morphs, text splitting | **GSAP** (timelines, ScrollTrigger, SplitText, Flip, MorphSVG, DrawSVG; all plugins free) | Use `useGSAP` in React; `gsap.matchMedia()` for reduced motion and breakpoints |
| Designer-authored vector animation (icons, illustrations) | **Lottie / dotLottie** | Small; play/pause/segments; designers can edit in AE/LottieFiles |
| Interactive characters/mascots with states across platforms | **Rive** (state machines; web, iOS, Android, Flutter runtimes) | Needs the Rive editor to author; ideal handoff for long-lived mascots |
| 3D objects, product viewers, scenes | **Three.js** or **React Three Fiber + drei** | See three-d.md for look-dev and asset pipeline |
| Lightweight 2D WebGL (particles, sprites, shaders) | PixiJS, OGL, or raw WebGL | Cheaper than three.js for 2D |
| Generative art seeded by data | Canvas 2D / p5.js / fragment shaders | Seed from real data or a recorded seed; never a gradient-orb shader |
| Sequencing a 3D scene like a film | Theatre.js (+ R3F) or GSAP timelines driving three.js | |
| Video in the page (loops, transitions) | `<video muted playsinline loop>`; alpha via WebM VP9 (Chrome/Firefox) + HEVC-with-alpha .mov (Safari) | Poster frame, preload metadata, pause offscreen |

## 3. Recipes

**Hero load choreography (the one orchestrated moment).** One GSAP timeline (or Motion variants): leader (headline)
→ supporting copy (+80ms) → product visual (+120ms) → CTA (+60ms). Total under 900ms. Everything already visible if JS
fails (animate `from` a near-final state, not from opacity 0 on critical text).

**Scroll-scrubbed object.** Image sequence on canvas (preload, draw frame = round(progress × n)), or a three.js
scene whose camera follows a GSAP ScrollTrigger timeline with `scrub: 0.5`. Pin only while the object transforms;
release immediately after. Provide a static poster for reduced motion.

**Sticky story.** Product pinned on one side, steps scroll on the other; the pinned visual changes state per step
(crossfade or Flip). Each step's text is readable without the visual.

**Shared-element transition.** View Transitions: give the thumbnail and the detail hero the same
`view-transition-name`; tune `::view-transition-group(*)` duration/easing from tokens.

**Physical UI.** Motion `drag` with `dragConstraints` and `dragElastic` 0.1-0.2, spring return; or GSAP Draggable +
Inertia. Haptics on mobile web via `navigator.vibrate` only where supported and meaningful.

**Kinetic headline (once).** SplitText into chars/words; animate variable-font axes (`font-variation-settings`
weight/width) or y-offset with 20-30ms stagger; runs once on load, never loops.

**Video matte loop over UI.** Generate (or render in Remotion) on a flat chroma background, key to alpha,
export WebM alpha + HEVC alpha; layer above the page; one loop, slow, pauses offscreen.

**Keyframe-interpolated transition between two stills.** Two approved stills → fal image-to-video with start/end
frames (paid: plan + approval) → scrub with scroll. Alternative free route: crossfade + subtle scale in CSS.

**Interactive mascot.** See character-animation.md; GSAP rig in `assets/templates/mascot-rig.html`.

## 4. Performance and accessibility

- Animate `transform`, `opacity`, `filter`, `clip-path`. Never width/height/top/left/margin (layout thrash).
  For height reveals, animate `grid-template-rows: 0fr → 1fr`.
- `will-change` only during an animation, removed after. Pause loops and WebGL render loops offscreen
  (IntersectionObserver) and when the tab is hidden.
- WebGL: clamp DPR to `Math.min(devicePixelRatio, 2)`; lazy-load the canvas after LCP; poster image first;
  keep hero GLBs under ~2-3 MB (three-d.md).
- Reduced motion: `@media (prefers-reduced-motion: reduce)`, Motion `MotionConfig reducedMotion="user"`,
  `gsap.matchMedia()`. Reduced means: no parallax, no autoplay loops, no large movement; keep opacity fades and the
  final state. Do not remove feedback.
- No flashing more than 3 times per second. Provide pause controls for anything that moves longer than 5 seconds.
- Test on a mid-range phone, not only a fast laptop.

## 5. Companion skills (Claude Code)

This skill decides the direction, timing and taste; official companion skills supply exact, current APIs:
- GSAP: `npx skills add https://github.com/greensock/gsap-skills` (core, timelines, ScrollTrigger, React, plugins, performance)
- Remotion: `npx skills add remotion-dev/skills` (see video-remotion.md)
- Three.js / R3F: community packages exist (e.g. OpenAEC-Foundation Three.js skill package); verify versions.
If a companion skill is installed, follow its API guidance; keep this skill's tokens, restraint, and gates.
