# Asset generation (images, sprites, 3D, video) with paid APIs

Generation costs the user real money. They cannot afford to "try ideas" through the API, so the designer does the
exploring for free (sketches in code, style frames, existing assets, post-processing) and spends only on
approved, specific outputs.

## Contents
1. The spend protocol (mandatory)
2. Reuse and free alternatives first
3. The cost ladder
4. Provider routing
5. Prompt anatomy and recipes by style
6. Consistency: character bibles and series
7. Making generated images not look generated
8. Rating and salvage
9. Licensing and ethics
10. Per-environment notes

---

## 1. The spend protocol (mandatory, every time)

1. **Search the library first.** `python scripts/assets.py find <words> --tag <tag>`. Rejected and salvage-rated
   assets count: post-processing often rescues them (section 8).
2. **Consider free routes** (section 2). Generate only what code, post-processing, or existing assets cannot do.
3. **Check the schema** for any endpoint not used before in this project: `python scripts/media.py schema <endpoint>`
   (free; prints live input schema and pricing). Parameter names differ between models.
4. **Write a spec** (`assets/templates/generation-spec.example.json`) with one job per distinct output, a `why`, tags,
   and the exact prompt. Batch everything needed for this step into one plan.
5. **Plan it:** `python scripts/media.py plan spec.json`. This is free. It estimates cost (Retro Diffusion quotes are
   exact and free), lists reuse candidates, and blocks unknown prices or caps.
6. **Show the user the plan table** (in chat, as a table), with total cost, reuse candidates, and what each output is
   for. Say what you will do with failures (salvage). Then **stop and wait.**
7. **Proceed only on an explicit yes** that clearly refers to this plan ("yes", "go", "approved"). Silence, "looks
   interesting", a question, or approval of a different plan is not a yes. If the user edits the plan, re-plan and
   ask again; the hash check refuses edited plans.
8. **Run** with the code and the user's words:
   `python scripts/media.py run PLAN-... --approve go-xxxxxx --user-said "<their exact words>"`.
9. **Review everything:** `python scripts/assets.py sheet --plan PLAN-...`, look at the sheet, then rate every output
   `keep`, `salvage` (with a note of what part is usable), or `reject`. Never delete.
10. **Report spend** in one line ("Spent $0.42 of the $3 plan; $4.10 of $30 total").

Never do any of these:
- Run a paid call without step 7, including "just one quick test," retries of failed jobs, or variations.
  A retry is a new approval unless the original plan's approval clearly covered it.
- Raise the budget or per-plan cap on your own. Only `media.py budget` with numbers the user gave.
- Put API keys in code, prompts, logs or chat. Keys live in `.env.design` (gitignored) or the environment.
- Use an MCP connector to bypass this protocol. MCP tools cost the same money; show the same plan, get the same yes.

Default caps when the user has not set any: $3.00 per plan. Ask once early in a project: "What's your budget for
generated assets, total and per batch?" and record it with `media.py budget --cap X --per-plan Y`.

## 2. Reuse and free alternatives first

Before paying, ask whether the asset can come from:
- **The library**: existing keep/salvage assets, recomposed, recolored, cropped, mirrored, re-timed.
- **Code**: SVG illustrations and characters (see character-animation.md), CSS/Canvas/WebGL generative art seeded
  from product data, three.js scenes from primitives, patterns and textures (post.py tile, grain, halftone), charts.
- **The product itself**: real screenshots captured with `capture.py`, real data, real UI states. Often the strongest hero.
- **The user**: photos, logos, existing brand assets (`assets.py import`).
- **Free libraries** for commodity needs: icon families (Phosphor, Lucide, Tabler, Heroicons; pick one and keep it),
  open fonts (Google Fonts, Fontshare), CC0 textures. Check the license and record it in the asset notes.

Generate when the need is a distinctive authored asset: a mascot, a hero illustration, a 3D object, a texture with
character, a pixel world, a video loop.

## 3. The cost ladder

Spend money in proportion to certainty:
1. **Explore free**: describe 2-3 candidate compositions in words, or sketch them as quick SVG/HTML style frames.
2. **Draft cheap**: lowest-cost settings that answer the open question (GPT Image 2 `quality: low`, Retro Diffusion
   `rd_fast__*`, small sizes). 3-4 drafts in one job.
3. **Pick and refine with the draft as reference**: use an edit endpoint with the chosen draft as input rather than
   regenerating from scratch. Changes cost less and preserve what worked.
4. **Final quality only for winners**: high quality / pro tiers only for the assets that will ship.
5. **Derive the rest for free**: crops, recolors, pixelations, cutouts, sprite slices, GIFs, textures (post.py).

Efficiency tricks:
- **Sheets, not singles**: one image containing a turnaround, an expression sheet, or a set of 4 icons in a grid,
  then `post.py slice`. One call, many assets, guaranteed consistency.
- **Flat chroma backgrounds** (`#00B140` green, or flat white for dark subjects) make keying free and clean.
  Use `background: transparent` where the model supports it (GPT Image 2).
- **Generate at the needed size.** Upscaling a small image is cheaper than generating huge.
- **One model per series.** Switching models mid-series breaks consistency and wastes drafts.

## 4. Provider routing

Model ids and prices change. Verify with `media.py schema <endpoint>` (fal) or the free Retro Diffusion
`check_cost` before planning; record what you used in DESIGN.md.

| Need | First choice | Notes |
|---|---|---|
| True pixel art (sprites, items, tiles, scenes) | Retro Diffusion `inferences`, `rd_pro__*` final, `rd_fast__*` drafts | Grid-true pixels, palette control (`input_palette`), `remove_bg`, reference images (up to 9) for consistency |
| Pixel animation (walk, idle, jump, attack, custom action, 8-dir rotate) | Retro Diffusion `rd_advanced_animation__*` with `input_image` | Start from an approved neutral-pose sprite; `return_spritesheet: true` then `post.py slice/gif` |
| Low-poly 3D with rig and animations | Retro Diffusion `lowpoly/generate` (+ `/animate`) | Free `estimate`; exports `web` (.glb for three.js), `godot`, `unity`, `unreal`, `blender`, `obj`, `mp4`, `gif`, `sheet` |
| Cute 2D characters, stickers, mascots | `openai/gpt-image-2` (transparent bg) or `fal-ai/nano-banana-2` | GPT Image for clean flat shapes and any text; Nano Banana with reference images for consistent series |
| Realistic 3D-render style assets (clay, toy, product renders) | `openai/gpt-image-2` high, `fal-ai/nano-banana-pro` | Specify material, light direction, lens; flat bg; contact shadow added in post |
| Image edits, variations from a chosen draft | `openai/gpt-image-2/edit`, `fal-ai/nano-banana-2/edit`, FLUX Kontext | Cheaper and more consistent than regenerating |
| Brand-style vectors, icon-ish illustration, patterns | Recraft (current endpoint on fal) | Can output vector styles; verify SVG support in schema |
| Background removal | `post.py key` (free) first; Bria/BiRefNet on fal for hair/fur/glass | |
| Upscale | `post.py upscale --nearest` for pixel art (free); fal upscalers for photos | |
| Image to 3D model (GLB) | `fal-ai/trellis-2` (~$0.25-0.30), `fal-ai/hunyuan3d/v2` (~$0.16) | Input: single object, 3/4 view, flat light, plain bg. Optimize after (three-d.md) |
| Short video loops, image-to-video, keyframe transitions | fal video models (Kling, Seedance, Veo families) | Price per second: always set `est_cost_usd` from live pricing. Prefer Remotion/code for anything that must be exact |

## 5. Prompt anatomy and recipes

Order: **subject → pose/action → composition/camera → light → material/medium → palette (hex) → background →
constraints**. Positive phrasing beats negatives ("plain flat #00B140 background" rather than "no background").
Never name living artists or studios; describe the qualities instead (shape language, line weight, palette).

**Cute 2D character (mascot, sticker)**
"Full-body character, a [species/object] [doing the product's core action], [proportions: head 1.2x body, stubby
limbs], thick even [color] outline at constant weight, flat fills in [3-4 hexes], one small highlight per form,
centered with generous margin, plain flat #00B140 background, no text, no ground shadow."

**Character turnaround / expression sheet** (one call, then slice)
"Character sheet of the same [character] in a 4x1 row: front, three-quarter, side, back, identical scale and
proportions, evenly spaced, [style lines from the bible], plain flat #00B140 background, no labels."
Expression sheet: "2x3 grid of the same face: neutral, happy, surprised, thinking, sleepy, worried..."

**3D render-style asset (clay, toy, product)**
"Studio render of a [object] made of [matte clay with visible fingerprints | glossy vinyl toy plastic | brushed
aluminium and frosted acrylic], [shape details], three-quarter view from slightly above, 50mm lens look, soft key
light from top-left, gentle fill, [palette hexes], centered on a plain flat [bg hex] background, no floor, no text."
Then `post.py key` → `post.py shadow` for a grounded contact shadow on the real page ground.

**Pixel art (Retro Diffusion)**
Prompt the subject only ("a small otter mechanic holding a wrench"); the `prompt_style` carries the look. Lock the
palette with `input_palette` (extracted from DESIGN.md tokens), set exact `width/height` (32-128 typical for sprites),
`remove_bg: true` for sprites, and pass the canonical sprite in `reference_images` for series consistency.

**Isometric scene / diorama**
"Isometric [30-degree] miniature of [place where the product's job happens], [3-5 named objects that represent real
features], [material language], soft daylight from the left, [palette], cut-away base block, plain flat bg."

**Textures and patterns**
Retro Diffusion `tile_x/tile_y` options or a general model with "seamless tileable [material] texture, even lighting,
no perspective". Then `post.py tile` and `post.py palette-map` to bring it on-palette.

**Hero illustration for a landing page**
Start from the direction contract's FIRST VIEWPORT. Describe the scene as a composition with the CTA zone kept empty:
"...subject placed in the right 55% of the frame, calm open area on the left third for headline text..."

## 6. Consistency

- **Character bible in DESIGN.md**: shape language, proportions in heads, outline weight, palette hexes, accessories,
  forbidden variations, canonical reference asset ids.
- **Always pass the canonical reference** (edit endpoints / reference_images) when generating a new pose or scene.
- **Same model, same style settings, same background** for a series. Record seed and settings in the asset record.
- **Prefer deriving to regenerating**: new poses by rigging the cutout (character-animation.md), new colors by
  palette-map, new sizes by resize.

## 7. Making generated images not look generated

Apply the fixes in anti-slop.md 4.6. The default finishing recipe for marketing rasters, adjusted per world:
`post.py key` (if compositing) → `post.py palette-map --palette <brand hexes>` or `duotone` → `post.py grain --amount 0.04 --mono`
→ crop asymmetrically for the layout. For print-world directions, `post.py riso` or `halftone` instead of grain.
Record the recipe in DESIGN.md so every asset gets the same treatment.

## 8. Rating and salvage

"Failed" generations are raw material. Salvage before regenerating:

| Problem | Free fix |
|---|---|
| Background wrong or busy | `key` (flat bg) or `crop` to the good region |
| Colors off-brand, "AI grade" | `palette-map`, `duotone`, `grade`, `riso` |
| One bad region (extra limb, glitch, stray object) | `crop`, `mask`, `composite` a good part over it, or `flip` a good half |
| Too glossy or plastic | `grain`, `posterize`, `halftone` |
| Blurry or non-grid "pixel art" | `pixelate --px N --palette <hexes> --outline <hex>` |
| Good pose, wrong style | use it as the reference input for a cheaper edit job, or trace it as SVG |
| Incomplete set (3 of 4 directions) | `flip` to mirror; rig the cutout for missing poses |
| Wrong aspect for a placement | `crop --aspect`, `resize --fit contain` on the brand ground, or extend with a flat field |
| A background you didn't want | a texture source: `crop` + `tile` + `palette-map` |
| Unusable as a hero | a thumbnail, sticker, loading-state illustration, social avatar, or a Remotion layer |

Rate after salvage too. `assets.py spend` reports how much spend was recovered through derivation.

## 9. Licensing and ethics

- Retro Diffusion grants commercial use. On fal, each model carries its own license; check the model page for
  commercial terms before shipping and note it in the asset record.
- No living artists' names or studio styles in prompts; no trademarked characters; no real people's likeness without consent.
- Never generate fake customers, testimonial photos, or "team" photos presented as real.
- Keep provenance (library records) so anyone can see what was generated, by which model, at what cost.

## 10. Per-environment notes

- **Claude Code**: full protocol with scripts. Keys in `.env.design` at the project root (add to `.gitignore`).
- **Claude Chat (claude.ai)**: the sandbox network allows package registries but not fal.ai or Retro Diffusion, so
  `media.py run` fails safely at $0. Options: (a) if the user has connected the fal or Retro Diffusion MCP connector,
  use it, but still show the plan table and wait for the yes; (b) give the user the spec and the exact `media.py`
  commands to run on their machine, then import the results with `assets.py import`.
- **Claude Design**: no shell. Write the generation plan as a table (asset, model, prompt, size, est. cost, purpose),
  get approval, and have the user generate via a connector or locally; place labeled placeholders sized to the
  final assets so layouts don't shift when real assets arrive.
