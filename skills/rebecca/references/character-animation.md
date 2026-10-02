# Character animation in code (mascots, sprites, cutouts)

The goal is a character that feels authored and alive, built and animated with code so it can be reused across
web, apps, and video without paying for each new motion.

## Contents
1. Design the character for animation
2. Pipelines A-H (pick one)
3. The principles, with numbers
4. States for product mascots
5. Accessibility and restraint

## 1. Design the character for animation

- **Shape language**: circles read friendly, squares stable, triangles dynamic. Pick one dominant shape from the product's world.
- **Silhouette test**: filled solid black, the character must still read in every key pose.
- **Proportions**: cute = large head (head ≈ body), short limbs, eyes low on the face, wide spacing.
- **Few, separable parts**: body, head (or one body-head), eyes, mouth, 2 arms, 2 feet, one accessory tied to the product.
  Every part is a separate group with a sensible pivot. This makes rigging trivial.
- **Constant outline weight** (or none), 3-5 flat colors from DESIGN.md, one highlight shape at most.
- **Expression set**: neutral, happy, surprised, thinking, sleepy, worried. Expressions come from eyes and mouth shapes, not new drawings.
- Record all of it in the DESIGN.md character bible.

## 2. Pipelines

**A. Code-drawn SVG + GSAP (default for web; free).** Build the character from rects, rounded rects and simple
paths (the approach behind well-known product mascots). Groups with pivots via `svgOrigin`, a clipPath for the
ground line if the character disappears into it, timelines per state. Template: `assets/templates/mascot-rig.html`.

**B. Generated character → cutout rig (one paid image, unlimited motion).** Generate a front-facing character on a
flat chroma background (plan + approval), then: `post.py key` → `post.py crop` each part (arms, head, eyes...) →
reassemble as layered `<image>` elements in an SVG (or PNG layers) with pivots → animate exactly like A.
Paint over joints with a small overlap so rotations don't open gaps.

**C. Pixel sprites.** Retro Diffusion animation styles from an approved neutral sprite (`rd_advanced_animation__walking`,
`idle`, `jump`, `attack`, `custom_action`, `rotate`; `return_spritesheet: true`), or build frames in code on a pixel
grid. Play with CSS `steps()`, canvas, or GSAP frame swaps; export with `post.py gif --holds` or `post.py sheet`.
Scale only by integers with nearest-neighbor (`image-rendering: pixelated`).

**D. Rive (interactive, cross-platform, long-lived mascots).** State machines with inputs (hover, click, progress)
and runtimes for web, iOS, Android, Flutter. Authoring needs the Rive editor, so treat it as a handoff: deliver the
character bible, parts, state list, and timing specs from this file.

**E. Lottie.** For designer-authored vector animation that ships to many platforms; pairs with After Effects.

**F. Remotion (video).** The same character driven by `useCurrentFrame()`, `interpolate`, `spring`, and
`random(seed)` for deterministic blinks. Template: `assets/templates/remotion-mascot-scene.tsx`.
CSS animations and transitions do not render in Remotion.

**G. 3D.** Retro Diffusion low-poly generates a rigged model; `/animate` adds named animations from a prompt;
export `web` (.glb) and play with three.js `AnimationMixer`. Image-to-3D models (trellis-2, Hunyuan) arrive unrigged.

**H. Native.** SwiftUI: `PhaseAnimator`, `KeyframeAnimator`, `Canvas` + `TimelineView`, springs.
Compose: `Animatable`, `updateTransition`, `rememberInfiniteTransition`, `Canvas`. Flutter: `CustomPainter` +
`AnimationController`, `flutter_animate`, or the Rive/Lottie packages. Share timing tokens with the web rig.

## 3. The principles, with numbers (30fps / ms)

- **Anticipation**: 80-120ms (3-4 frames) in the opposite direction before any big action (crouch before jump,
  arm dips before wave).
- **Squash and stretch**: keep volume: scaleX ≈ 1/√scaleY. Typical squash 0.84-0.9 on impact, stretch 1.06-1.1 in flight.
- **Asymmetric easing**: going up decelerates (`sine.out`), coming down accelerates (`power3.in`). Mixing these up
  is the most common reason code animation looks floaty.
- **Impact and settle**: 2-3 frames of squash, then a spring/elastic settle (overshoot 3-8%). Overshoot is for
  characters; UI stays exponential.
- **Follow-through and overlap**: appendages lag the body by 40-80ms and swing past the rest pose before settling.
- **Arcs**: move x and y on separate eases (or a motion path) so paths curve.
- **Holds**: key poses hold 250-400ms (8-12 frames). Per-frame hold times give rhythm: `post.py gif --holds "0:3,4:2"`.
- **Secondary action**: blinks every 2-6s at seeded random intervals; breathing scale 1 → 1.02-1.03 over 2.5-4s.
- **Timing on twos**: pixel and cartoon looks often read better at 12fps stepped (`steps()` / frame holds) than at 60fps tweening.
- **Staging**: one action at a time; the face looks where the action is going.
- **Mirroring**: reuse a timeline for the other side by flipping (`scaleX: -1`) instead of animating twice.

## 4. States for product mascots

Map states to real product events only (no fake busyness):
`idle` (breathing, blinks) · `attend` (cursor near, input focused: eyes track) · `react` (click: small jump) ·
`working` (real loading: looping task gesture, stops when done) · `success` (real completion: one celebration) ·
`error` (gentle, never comic in money or data-loss moments) · `sleep` (long inactivity). One state at a time,
a guard against overlapping timelines, and every state returns to idle.

## 5. Accessibility and restraint

- Reduced motion: static key poses; state changes become instant pose swaps.
- Decorative characters: `aria-hidden="true"` or `role="img"` with a short label if they carry meaning.
- Pause loops offscreen. A character never covers content or the primary action.
- One mascot moment per screen. The character supports the product; it is not the product.
