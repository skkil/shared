# Brand identity and product marketing

## 1. Identity
- **Positioning line**: For [who] who [need], [product] is the [category] that [key benefit], unlike [alternative].
- **Personality**: 3-4 traits as sliders (e.g. playful ←→ serious), each with a do/don't example.
- **Logo**: built as code (SVG) so it is editable and crisp.
  - Wordmark with one custom detail drawn from the product's mechanism, or a symbol derived from what the product
    does (not a generic spark, hexagon, or gradient blob).
  - Design in one color first; build symbols on a 100-unit grid from boolean shapes, never live `<text>`.
  - Make 3+ logo sets, each with one sentence naming the mechanism it borrows from the product. At least one set
    must avoid every default in anti-slop.md.
  - Contact sheet of every set at 16 and 32 px, on light and dark grounds (`post.py sheet` on exported PNGs);
    a mark that turns to mush at 16 px is cut or simplified. Two fix rounds, then stop and let the user pick;
    never pick for them.
  - Deliver: SVG (full, mark, mono, reversed), PNG exports, clear-space and minimum-size rules.
- **Color, type, voice, illustration, motion**: from DESIGN.md; the brand board shows all of them on one page.
  Palette roles come from `palette.py roles "<key>"` (solved against contrast floors), then `palette.py cvd`
  so no pair collapses under color blindness.
- **Measured vs judged:** label every claim in the guidelines. Contrast, color-blindness, glyph coverage, font
  license and file validity are measured; everything else is a labelled judgement.
- **Deliverables:** SVG/PNG logo set (full color, one color, reversed, app icon, favicon), tokens (CSS, Tailwind,
  DTCG JSON), a brand board, and a short guidelines page (HTML → PDF via `capture.py`).
- **Refresh of an existing brand:** extract what is actually shipped before changing it (discovery.md §1).
- **Mascot** (optional): character bible + rig (character-animation.md). A mascot must have a job in the product.

## 2. Launch and marketing kit (render from HTML templates + capture.py for consistency)
| Asset | Size (verify current platform specs) |
|---|---|
| Open Graph / link preview | 1200×630 |
| X / LinkedIn post image | 1600×900 or 1200×1200 |
| Instagram feed / portrait / story | 1080×1080, 1080×1350, 1080×1920 |
| YouTube thumbnail | 1280×720 |
| Product Hunt gallery | 1270×760 |
| App icon masters | 1024×1024 (iOS), 512×512 (Play) |
| Email header | 1200 wide, live text below |
| Launch video | video-remotion.md, 16:9 + 9:16 cuts |
Each asset: one key visual from the direction, one specific claim, the product visible.

## 3. Content atomization (one launch, many pieces)
From one core story: 10-15s clips (3-5), one 60-90s cut, 3 quote cards with real quotes, one carousel (one idea per
slide), a blog post, an email, store screenshot captions. Same visual system throughout; vary the hook, not the brand.

## 4. Ads and social
- The hook is the first frame/line; the product appears early; captions on.
- Make 2-3 variants that differ in one variable (hook, visual, claim) to learn something.
- Never fake testimonials, numbers, or "as seen on" logos; label AI-generated imagery where required.
