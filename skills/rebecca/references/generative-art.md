# Code-drawn illustration and generative art

Painting with code is free, exact to the palette, reproducible from a seed, and never looks like an image model.
Use it for heroes, section art, backgrounds, textures, covers, posters, data-adjacent art and draw-on animation.

## 1. Routes

| Need | Use |
|---|---|
| Ink-wash landscape, flow lines, topographic contours, engraving/hatching of any image | `scripts/draw.py` (numpy + Pillow) |
| Crisp vector art, icons, logos, plotter output | Hand-written SVG; seeded JS or Python to emit paths |
| Live, interactive or animated in the page | Canvas 2D / p5.js / SVG + JS; shaders for full-screen fields |
| Draw-on video | `draw.py ... --stages DIR` frames → Remotion or ffmpeg |
| Painterly look on an existing raster | `draw.py hatch --from`, then `post.py palette-map / riso / grain` |

## 2. The loop

1. Write one sentence: subject, mood, where it sits on the page, how much empty space it needs.
2. Contact sheet first: `draw.py sheet flow --seeds 1-12 --size 800x500 --palette "<ink>,<paper>,<accent>"`.
   Pick a seed by composition, not by detail.
3. Render the chosen seed at full size, open it, check it against §4, change **one** parameter, re-render.
   Save versions (`_v1`, `_v2`); 2-4 rounds is normal.
4. Record seed, command and palette in DESIGN.md so the art can be regenerated at any size.

## 3. Techniques (draw.py functions; import them for custom scenes)

- `fbm2(rng, w, h, cell, octaves)`: fractal value noise. Large `cell` = broad forms; octaves add detail.
- `ink`: layered ridges from `fbm1`, washes that decay below each ridge, mist bands between layers, paper tooth.
  Nearer layers are darker and sharper (atmospheric perspective).
- `flow_lines`: particles follow an angle field from noise. `cell` sets the scale of swirls; `curl` their twist;
  line count sets density. Accent color on ~4% of lines.
- `iso_lines(field, levels)`: contour lines of a height field with constant pixel width (gradient-normalized).
- `hatch_from(lum, spacing)`: up to four hatch layers at different angles and luminance thresholds, like an
  engraving. Auto-levels the source.
- Paper: low-frequency fibre + high-frequency tooth multiplied into the ground.
- Determinism: everything draws from one `numpy.random.default_rng(seed)`. Same seed + same args = same pixels.
  For live JS art use a seeded PRNG (sfc32/mulberry32) and named sub-streams per element so adding one element
  does not reshuffle the rest; never `Math.random()`.

## 4. Failure checklist

- **No focal point:** uniform texture everywhere. Fix: vary density, leave a calm area for the headline.
- **Too full:** ink and line art need at least ~40% empty paper. Fix: fewer layers/lines, raise the mist.
- **Muddy color:** more than ink, paper and one or two accents. Fix: palette from DESIGN.md only.
- **Digital edges:** perfectly clean lines on flat ground. Fix: paper tooth, varied line width, grain in post.
- **Screensaver look:** symmetric, centered, evenly spaced. Fix: rule-of-thirds anchor, a dominant mass.
- **Competes with text:** busy art behind copy. Fix: lower contrast under text or move the art to one side;
  text over art still needs 4.5:1 (`palette.py check`).

## 5. Ethics and credit

Credit an algorithm or palette you borrow. Never reproduce a named living artist's signature style or work.
Claim determinism only after rendering the same seed twice and comparing.
