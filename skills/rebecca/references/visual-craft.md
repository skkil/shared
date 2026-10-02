# Visual craft: type, color, layout, detail

## Typography
- **Choose faces from the world, not the default list.** Use the rolled type voice and its candidates; check the
  overused list in `slop_lint.py`. One display face + one text face is enough; add mono only for code/data.
- Scale: pick a ratio (1.2 for dense apps, 1.25-1.333 for marketing, 1.5+ for poster pages). At least one big jump
  (≥ 1.5×) between hero and body; flat hierarchies read generated.
- Body 16-18px web (17pt iOS body), line-height 1.45-1.65, measure 60-75ch. Display line-height 0.95-1.15,
  optical tracking (tighten large type slightly, never destructively).
- Tabular numerals for data; real quotes and apostrophes; no faux bold/italic; check every weight used is loaded.
- Licensing: prefer OFL fonts; note commercial fonts in DESIGN.md.

## Color
- Choose a **strategy** (Restrained, Committed, Full, Drenched, Two-ink, Tonal, Image-led) before choosing hues.
- Build ramps in OKLCH (`palette.py ramp`) so steps are perceptually even; name semantic tokens
  (ground, ink, brand, accent, signal) on top of the ramp.
- Check every text pair (`palette.py matrix`): body ≥ 4.5:1, large ≥ 3:1, UI/icons ≥ 3:1.
- Light vs dark comes from the scene sentence (who, where, what light). Dark mode is redesigned, not inverted:
  lift surfaces with lighter tones instead of shadows; desaturate large fields.
- Gray on color looks dead: use a darker/lighter shade of the ground hue instead.

## Layout and composition
- A grid you can name (12-col, 6-col, modular) and a strong primary axis. Break the grid once, on purpose.
- One focal point per viewport. Size, contrast, isolation and position establish order; everything else steps back.
- Rhythm: tight groups inside, generous separation between groups; vary section density.
- Asymmetry reads authored; symmetry everywhere reads generated (unless the world is formal, e.g. institutional).
- First viewport is complete on its own: what it is, why it matters, what to do.

## Spacing, shape, depth
- Spacing scale on a 4/8 base; use it everywhere.
- Radius scale tied to size and role (small controls < cards < sheets), or a committed sharp system.
- Elevation only where layering is real; shadows tinted with the ground hue, never pure black at 10% on everything.

## Iconography and imagery
- One icon family, one stroke weight matched to the text weight, optical sizes for small use.
- One illustration medium and one light direction across all imagery (DESIGN.md asset system).
- Photography: documentary over stock; real product and real people with consent.

## States and details that signal craft
- Every interactive element: default, hover, focus-visible, active, disabled, loading. Every view: empty, loading,
  error, partial, success.
- Optical alignment (icons and round shapes nudged to look centered), hanging punctuation for big quotes,
  balanced headline wraps, no orphans in key lines.
- Selection color, caret color, scrollbar styling, focus ring in brand, favicon, OG image.
- Spend boldness in one place per surface; everything around it gets quieter.
