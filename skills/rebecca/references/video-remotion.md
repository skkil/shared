# Promotional and product video with Remotion

Remotion renders React components frame by frame into video. It is deterministic, versionable, cheap to iterate,
and uses the product's real tokens, fonts and UI. Use it for launch videos, feature explainers, social cuts, app
store previews, animated mascot clips, and data stories.

## Contents
1. Process (with approval gates)
2. Pacing rules
3. Formats and safe areas
4. Remotion essentials
5. Footage, camera and sound
6. Mixing in AI video
7. Environment fallbacks

## 1. Process

1. **Brief**: goal, audience, channel(s), length, one message, CTA. (templates/brief.md)
2. **Script**: one idea per scene; on-screen text ≤ 7 words per beat; optional VO.
3. **Storyboard**: `assets/templates/storyboard.md`; every shot has one motion idea and an asset source
   (library id / code / to-generate). **Gate: user approves the storyboard.**
4. **Style frames**: build 2-3 key frames as real Remotion compositions and render stills
   (`npx remotion still <comp> --frame=N out.png`). **Gate: user approves the look.**
5. **Animatic**: timing only (blocks and text at final timing) to lock rhythm, ideally on the music's beat grid.
6. **Build** scenes; reuse components across scenes; tokens from DESIGN.md.
7. **Audio**: music bed (licensed), SFX for key actions, optional VO; captions burned in.
8. **Render** variants (16:9, 9:16, 1:1) from the same scenes with layout props, not copies.
9. **Review**: render a frame strip (every ~15 frames) + the video; run the fresh critic on stills; fix; re-render.

## 2. Pacing rules

- One motion idea per shot. If a shot needs two, it is two shots.
- Hold the brand mark at least 1s; the final frame (product + CTA) at least 1.5s.
- Rest ~0.5s after any batch of animation before the next beat.
- Give the opening action ~3s to land; the first 1-2 seconds must already show the product or the hook.
- At most 3 full-frame "slam" beats per video.
- Cut on the beat; move on the off-beat. Human reviewers consistently ask for "slower": default slower.
- Real UI moves at real UI speed; a cursor travels in arcs, eases in and out, and clicks with a small press.

## 3. Formats and safe areas (verify current platform specs before final render)

| Use | Size | Notes |
|---|---|---|
| Website hero, YouTube, X/LinkedIn landscape | 1920×1080 @30 (or 60 for UI-heavy) | Keep text inside 90% action-safe |
| Reels, TikTok, Shorts, Stories | 1080×1920 | Keep key text out of the bottom ~20% and top ~12% (platform UI) |
| Feed square / portrait | 1080×1080, 1080×1350 | Captions large: ≥ 48px at 1080w |
| App Store preview | device-specific portrait/landscape, 15-30s | Must show the app in use; check Apple's current resolutions |
| Google Play promo | YouTube link | Landscape |
For 1080-wide frames use ~80px side and ~100px top/bottom safe margins; headline type ≥ 84px.

## 4. Remotion essentials (install the official skill for exact APIs)

- Companion skill: `npx skills add remotion-dev/skills`. New project: `npx create-video@latest`.
- Everything animates from `useCurrentFrame()` with `interpolate()` (clamp extrapolation), `spring()`, and
  `Easing`. **CSS transitions/animations and timers do not render.** No `Math.random()`: use `random("seed")`.
- Structure: `<Composition>` per format; `<Sequence>`/`<Series>` for scenes; `@remotion/transitions` for cuts;
  `premountFor` on heavy sequences.
- Assets via `staticFile()`; fonts via `@remotion/google-fonts` or local font loading; images/video with
  `<Img>`, `<OffthreadVideo>`; audio with `<Audio>` and volume curves.
- Preview `npx remotion studio`; stills `npx remotion still`; render `npx remotion render <comp> out.mp4`.
- 3D with `@remotion/three`; Lottie with `@remotion/lottie`; captions with `@remotion/captions`.
- License: Remotion is free for individuals and very small companies; larger companies need a company license.
  Check remotion.dev/license and tell the user if it may apply.

## 5. Footage, camera and sound

- **Real product, not div mockups.** Capture real screens at 2x (`capture.py`, Playwright scripts for flows),
  real data, real states. Put them on the page's ground or in a clean device frame.
- **2.5D camera**: perspective + rotateX/Y on a UI plane, slow push-ins (scale 1 → 1.06 over 3-4s), parallax layers.
  Cinematic feel comes from camera, light, rhythm and sound, not from effects.
- **Type**: kinetic only at beats; otherwise set, hold, cut.
- **Characters**: the mascot rig in Remotion form (assets/templates/remotion-mascot-scene.tsx).
- **Sound**: SFX for clicks/whooshes at low volume; music ducked under VO; captions for every spoken word.

## 6. Mixing in AI video

Use fal video models only where code cannot do it (organic motion, physical materials, scene transitions between
two approved stills). Every clip is a paid job: plan, approve, run (asset-generation.md). Generate on a flat
chroma background when the clip will be layered, key it, and import as `<OffthreadVideo>` with alpha (WebM VP9).
Keep AI clips short (3-5s) and treat them as one layer among real footage and code animation.

## 7. Environment fallbacks

- **Claude Code**: full Remotion workflow including rendering (Chrome headless is downloaded on first render).
- **Claude Chat**: write the full Remotion project files and give the exact commands; or build an HTML/GSAP
  animated artifact the user can screen-record when Remotion can't render in the sandbox.
- **Claude Design**: storyboard frames as artboards; hand off to Claude Code for the build.
