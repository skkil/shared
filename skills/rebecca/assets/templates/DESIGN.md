# DESIGN.md (design memory)

This file is the design memory for the project. Every agent session reads it before designing and
updates it when a durable decision changes. Surface-specific overrides live in `.design/surfaces/<surface>.md`
and win over this file for that surface only.

## 1. Product truth
- **What it is (one sentence, user's words):**
- **Who uses it, where, under what light (the scene):**
- **The job it does (JTBD):** When ___, I want to ___, so I can ___.
- **User promise per key surface:** landing: ___ / onboarding: ___ / main screen: ___
- **Proof we actually have (real numbers, customers, quotes, screenshots):**
- **Claims we must NOT make:**
- **Category default (the page every competitor ships) and its predictable opposite (both are the rut):**

## 2. Direction contract (locked after the user picks a direction)
- **Name / seed key:** (from creative_roll.py; record it with `creative_roll.py record`)
- **THESIS:** the one idea this product's surfaces own, and the category default they refuse.
- **OWN-WORLD:** palette + materials + component language, specific enough to recognize with all content removed.
- **STORY:** what the visitor understands, believes, then does.
- **FIRST VIEWPORT:** exact composition: what is where, at what scale, where the primary action sits.
- **SIGNATURE MOMENT:** the one memorable interaction or motion.
- **WHAT WE SAID NO TO:** defaults deliberately avoided (helps future sessions stay on course).

## 3. Tokens (source of truth; generate platform files from here)
### Color (OKLCH-derived ramps via `palette.py`; record contrast for every text pair)
| token | value | role | passes on |
|---|---|---|---|
| color.ground | # | page/app background | |
| color.ink | # | primary text | ground x.x:1 |
| color.brand | # | committed brand color | |
| color.accent | # | actions only | |
| color.signal.success / warning / danger | # | states | |
Color strategy: Restrained | Committed | Full palette | Drenched | Two-ink | Tonal | Image-led
Light/dark decided by the scene sentence, not by category.

### Type
| role | family | weights | size / line-height / tracking | why this face |
|---|---|---|---|---|
| display | | | | |
| text | | | | |
| mono (code/data only) | | | | |
Scale ratio: ___  Body measure: 60-75ch  Licensing: OFL / commercial (note it)

### Shape, space, depth, motion
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96 (or project's own)
- Radius scale tied to size/role: ___ (never one radius on everything)
- Elevation scale (only where layering is real): ___
- Motion: durations (micro/small/medium/large) ___ ; easings ___ ; springs ___ ; reduced-motion behavior ___
- Iconography: one family ___, stroke ___, sizes ___

## 4. Illustration & asset system
- Medium (pixel / clay 3D / cute 2D / photo / ...):
- Character bible (if any): shape language, proportions in heads, palette hexes, outline weight, accessories, do/don't
- Canonical reference assets (library ids): A-____ (front), A-____ (3/4) ...
- Generation defaults: provider/model, background (#00B140 flat for keying), sizes
- Post-processing recipe applied to every raster (e.g. palette-map -> grain 0.04):

## 5. Voice
- If `.vanessa/voice.md` exists, it is the full voice and tone guide; keep this section as a summary that points to it.
- Voice: ___ (from the voice deck or custom). Vocabulary we use: ___ Words we never use: ___
- Error / empty / success patterns:

## 6. Platform notes
- Web: ___   iOS: ___ (Liquid Glass on controls layer only)   Android: ___   Flutter: ___   Desktop: ___

## 7. Allowances (where the brief overrides slop rules) -> mirrored in .design/slop-allow.json
| rule | reason quoted from the brief |
|---|---|

## 8. Decision log & tried log (newest first)
- YYYY-MM-DD: decision / what was tried and rejected and why
