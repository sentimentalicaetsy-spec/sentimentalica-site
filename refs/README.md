# Reference intake — Ksenia drops her real reference IMAGES here (as FILES)

These folders are the GROUND TRUTH. Every image the pipeline makes is judged
against the files here — not against words. Empty folder = the agent is blind
and falls back to my paraphrase (this is what caused "как об стенку горохом").

There are TWO kinds of "how it should look" references, and they are different:

## 1. refs/scenes/  — atmospheric MOOD references (photographic)
The dreamy, save-worthy corners / rooms / moods a person wants to escape INTO
(the "gen3" bar): golden light, layered depth, real atmosphere. NOT bright
sterile stock, NOT watercolor illustration, NOT the product.

- **Give MANY** — this is the main taste anchor. ~3–5 per desire/theme.
- **Put the theme in the filename** so the critic matches on-theme:
  `cottagecore-goldenlight.jpg`, `witchy-candlelit-desk.jpg`,
  `manifestation-visionboard.jpg`, `cozy-autumn-corner.jpg`.
- These filenames are what you reference in the "Scene refs" column of the
  Desire Library / Seasonal Calendar sheets in content_plan.xlsx.
- The image-critic compares every generated scene to these; below this bar = REGENERATE.

## 2. refs/infographics/  — the Sentimentalica GRAPHIC STYLE (list / infographic)
This bucket defines the brand's GRAPHIC identity for listicles & infographics
(the "50 things" type): the layout grid AND the visual style — texture, torn
edges or clean, typography, palette. Requirements you named:
- Readable type WITHOUT zooming; clear grid; a real illustration, not "PowerPoint".
- **ONE consistent Sentimentalica graphic style** across all of them.
- **NOT the website's look, and NOT what I rendered so far** — my 50-things
  render is a PLACEHOLDER, not the standard. This style is YOURS to define.
- **Give 2–5 strong examples** of the exact graphic look you want copied 1:1.
  We lock the Sentimentalica graphic style from these; until then the infographic
  renderer is a placeholder and should not be trusted as "the style".

## 3. refs/50things/  — (optional) the specific 50-things reference
If the 50-things list has its own exact reference, put it here.

---
### Naming recap
Theme-in-filename for scenes (so the agent picks the right one per desire).
Anything descriptive for infographics. More scenes = better; a few strong
infographic refs is enough (layout + style templatize from 2–5).
