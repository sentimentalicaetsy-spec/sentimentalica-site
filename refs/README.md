# Reference intake — Ksenia drops her real reference IMAGES here (as FILES)

These folders are the GROUND TRUTH. Every image the pipeline makes is judged
against the files here — not against words. Empty folder = the agent is blind
and falls back to my paraphrase (this is what caused "как об стенку горохом").

Important: previous outputs from Claude/Codex/renderers, staging assets, live
article images, or demo graphics are **not** references. Ksenia's references are
only the files she intentionally puts under `refs/`.

Refs are visual ground truth for taste, structure, and critique. Do **not** copy
or publish a ref image itself as an article/pin asset unless Ksenia explicitly
marks that exact file as a production/brand-owned asset to reuse.

There are FIVE kinds of "how it should look" references, and they are different:

## 1. refs/branding/ — global Sentimentalica visual identity
This is the overall brand taste for **everything**: articles, pins, infographics,
palette cards, graphic elements, and occasional logo/blue-bird motifs.

Use it as the default visual north star even when a topic changes:
- Sentimentalica blue (the logo blue) should recur as a brand signal.
- The logo / bird shape may appear periodically as a woven, stamped, lace,
  paper-cut, or printed motif — subtle, not slapped on.
- Infographics should be adapted into this brand feeling unless explicitly using
  the iPhone Notes format below.
- Goal: recognizable, saveable, clickable, feminine paper-craft identity.

## 2. refs/infographics/  — saveable graphic/list styles
This bucket defines useful Pinterest graphics: lists, diagrams, reminders,
charts, "what to keep", "what to add", etc.

Default infographic rule:
- Take the useful structure from the selected infographic ref.
- Rebuild it in the Sentimentalica branding direction from `refs/branding/`.
- Keep text readable on mobile without zoom.
- It must feel useful enough to save, not like an ad.

Special recurring subtype:
- **iPhone Notes infographic**: a graphic that looks authentically like a real
  iPhone Notes screenshot/list, with check circles/dashes and short natural
  lines. Emoji are allowed and often good when the reference supports them:
  use them in the title, a small cluster, inline, or at the end of a line.
  Do **not** use emoji as the first character of list items or as bullet markers.
  This is the only infographic mode that may deliberately NOT look like the
  branded paper-collage style. It should feel natural, not overdesigned.
  Put these refs in Ksenia's folder `refs/iphone notes/` first. Legacy/extra
  refs may also live in `refs/infographics/iphone-notes/`.

## 3. refs/scrapbook and junk jornal scenes/ — realistic journal/scrapbook scenes
This folder is what we previously called "mockup" direction. These are realistic
craft images: a journal held or opened, pages being used, scrapbook spreads,
desk process shots, cropped girl/hands, real-life journal context.

Use these for:
- Article mockups.
- Pinterest product/use-case visuals.
- "People buy the dream" scenes where the reader sees herself using the pages.

Human presence rule:
- Hands, partial arms, a cropped girl holding a journal, and scissors/tools are
  allowed **only when they are natural, realistic, and reference-backed by files
  in this folder**.
- They are still a QA risk. Bad hands, melted fingers, creepy skin, fake scissors,
  or hands as the focal point = REGENERATE.
- Product pages must remain real listing/customer pages inserted into the scene,
  not AI-invented watercolor pages.

## 4. refs/scenes/  — atmospheric MOOD references (photographic)
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

## 5. refs/50things/  — (optional) the specific 50-things reference
If the 50-things list has its own exact reference, put it here.

---
### Naming recap
Theme-in-filename for scenes (so the agent picks the right one per desire).
For iPhone Notes refs, use `refs/iphone notes/` and include `iphone-notes` in
the filename when possible. More realistic journal/scrapbook scenes = better.
Branding refs define the global look.
