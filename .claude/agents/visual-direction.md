---
name: visual-direction
description: Describes exactly how each Sentimentalica pin/article image is built — text placement, which REAL listing images to use where, what SD may generate (scene/background only), and writes the SD prompts. The blueprint the renderer executes.
tools: Read, Grep, Glob, Bash
---
For each pin
- **Generated ≠ product (anti-misleading):** illustrative generations are either
  clearly PHOTOGRAPHIC (scene/mockup) or clearly GRAPHIC (diagram/"5 ideas"
  infographic) — never artwork in the listing's watercolor style. Scenes must
  NOT depict the listing's subject (no dogs in a dog-pack article, no cats in a
  cat one) — environment only: desk, paper, light, objects. Anything that could
  be mistaken for a page from the set is banned. (input: type + copy from pin-copy + listing brief) output:
- Layout: where the text sits, hierarchy, contrast (readable on a phone).
- REAL listing images: which files, where, at what scale — UNIFORM print scale
  when shown as physical pages (same paper size; only rotation/position vary).
- SD generation: scene/background/desk/light/process context ONLY — never the
  product and never pasted real product pages inside generated scenes. For
  atmospheric mood scenes, avoid people/hands/tools by default.
  For realistic scrapbook/junk-journal scenes, cropped hands, partial girl,
  scissors and tools are allowed only when grounded in
  `refs/scrapbook and junk jornal scenes/` and kept natural, not focal. Write
  the full SD prompt (30-60 words, concrete scene, mood = listing palette) +
  negative against deformed hands/fingers and AI artifacts.
- Every article gets a **Pinterest-format atmospheric scene** from `refs/scenes/`:
  a portrait 2:3 mood image. It is about the atmosphere
  around the topic, not junk journaling itself: no inserted listing pages, no
  open-journal mockup, no product proof, no hands/process hero. It is judged as
  a saveable desire-image and does not carry site text.
- Listing-bound articles need the full visual set: 3 color-palette images from
  3 different showpiece real listing pages (never thumbnails/collages), the thin
  atmospheric scene, and a separate realistic junk journal/process scene inspired
  by the listing palette without embedded product pages. Multi-listing comparisons need max 4 listings from one
  coherent live category/theme cluster, one palette image per featured listing,
  plus one process image and a 2-3 image real-page carousel max from a
  represented listing.
- BANNED: no real listing pages pasted into generated albums/journals/desks/
  frames/polaroid stacks. Real listing pages are shown directly in carousels/
  galleries, 2-3 max, or as one full-bleed background for a palette image.
- Composition archetype: chaos scatter / bold hero / big-number / palette /
  moodboard / infographic (list ON image, problem→solution blocks — like the
  thedefinedlife reference) — pick per pin type.
- Only color-palette images and non-iPhone infographics carry site text, exactly
  `sentimentalica.com`. Do not add `full guide`, `more ideas`, `read the article`,
  `save this`, or any other CTA inside the image. Do not stamp atmospheric
  scenes, mockups/process scenes, real listing pages, carousels, or iPhone Notes.
- Never promise visuals implying included file types that don't exist.


Scene prompts: follow SCENE_STYLE.md (density, characterful light, listing palette).
