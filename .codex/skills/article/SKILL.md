---
name: article
description: End-to-end article functionality for sentimentalica.com — given one listing (e.g. "064_Poison_Bloom" or just "poison bloom"), produces and publishes a complete themed article: real palette, real listing images, live Etsy product card, SD-generated scene images (generated now if A1111 is running, otherwise slotted for later insertion). Use when Ksenia says "proceed with article for <listing>", "напиши статью для <листинга>", or /article <listing>.
---

# /article — one listing → one complete published article

Repo: /Users/kseniateter/sentimentalica-site (work here)
PY = /Users/kseniateter/sentimentalica-pipeline/.venv/bin/python

## Steps (all of them, every time)

1. **Resolve** the listing:
   `python3 tools/resolve_listing.py "<user's listing words>"`
   → `NNN_Theme|etsy_id|thumbs_dir`. If it exits with NOT FOUND / NO ETSY_ID /
   NO IMAGES / AMBIGUOUS — stop and tell Ksenia exactly that; don't improvise.
2. **Assets:** `PY tools/gen_article_assets.py "<resolved line>"`
   → staging/overnight/assets/<listing>/{img1..img4.jpg, meta.json}
   (meta.json: theme, etsy_id, named palette).
3. **Write the article** to `staging/overnight/assets/<listing>/post.html`:
   - Voice + structure reference (READ IT before writing):
     `public/blog/colorful-junk-journal-ideas-for-maximalists-and-a-palette-to-steal.html`
   - Front matter: `title / category / excerpt / thumb: ./img1.jpg /
     related_ids: <fresh topic-related LIVE Etsy IDs from product-bridge>`.
     Title: buyer-intent, theme-specific, 45–70 chars, no listing numbers.
   - 550–850 words, warm small-studio voice, genuinely useful craft content.
     NO exclamation marks, no "digital/instant download" phrases, no page counts.
   - Pick the archetype that best fits the theme (vary across articles):
     theme spotlight · ideas list · palette study · how-to project.
   - MUST include the visual package required by article type:
     single-listing = 3 palette images from 3 different showpiece real listing
     pages (not thumbnails/collages), 1 thin atmospheric scene from `refs/scenes/`,
     1 realistic junk journal/process scene inspired by the listing palette,
     a 3–5 real-page carousel, ONE `{{etsy:ETSY_ID}}` near the end, and a soft
     closing link to `../blog.html`. Multi-listing comparison = up to 4 LIVE
     listings from one coherent shop/vault category or tight theme cluster, one
     palette image per featured listing, plus one thin atmospheric scene, one
     mockup/process image, and a 2–3 real-page carousel from a represented
     listing. Neutral/lead/listicle = useful graphic/infographic plus the
     mandatory thin atmospheric scene; product stays at the end only if it
     honestly fits.
   - Add gentle article CTAs: "save this idea", "open the full guide", "browse
     more Sentimentalica journal ideas", or "use the matching printable pages"
     where natural. No hard sell.
4. **Prompts file** `staging/overnight/prompts/<slug>.json` (slug = the one
   publish will produce — lowercase-hyphenated title): create every generated
   slot needed by the visual package, schema:
   `{"slug":..., "slots":[{"id":"gen1","prompt":"<photorealistic cozy junk-journal
   scene matching the theme & its palette, concrete: desk/light/props, 30-60
   words>","negative":"text, watermark, logo, low quality, deformed hands",
   "width":1216,"height":832,"caption":"<alt>","type":"thin-atmosphere|journal-scene|mockup|infographic|palette"}, ...]}`
   The thin-atmosphere prompt is wide/letterbox mood-only: no listing pages, no
   open-journal mockup, no hands/process hero.
5. **Publish:** `python3 tools/publish_post.py staging/overnight/assets/<listing>/post.html`
6. **Images — fully automatic (Ksenia never runs a follow-up command):**
   a. `curl -s -m 3 http://127.0.0.1:7860/sdapi/v1/progress` — if the API is down,
      START IT YOURSELF: `cd ~/stable-diffusion-webui && nohup ./webui.sh --api > /tmp/a1111.log 2>&1 &`
      then poll up to 6 min: `until curl -s -m 3 http://127.0.0.1:7860/sdapi/v1/progress >/dev/null; do sleep 10; done`
   b. When up: `PY tools/insert_generated_images.py` (NO --slug — fills this
      article AND backfills any pending slots from earlier articles).
   c. If A1111 truly won't start within 6 min (check /tmp/a1111.log): publish
      without scenes, say so in the report — the NEXT /article run backfills
      them automatically. Never hand Ksenia a command to remember.
7. **Ship:** `git add public && git pull --rebase && git commit -m "post: <title>" && git push`
8. **Verify + report:** wait ~60s, `curl -sL "https://sentimentalica.com/blog/<slug>?cb=$RANDOM" | head -3`;
   then print: live URL · images used · palette names · gen-images status
   (inserted now / 3 slots pending) · anything skipped.

9. **Pins + CSV (mandatory finale):** run the `pinterest-seo` agent over the
   article's pinnable images -> `tools/pin_csv.py add <listing> ...` rows.
   The CSV auto-mirrors to **Google Drive -> Sentimentalica/Pinterest_CSV/**
   where Ksenia picks it up for Pinterest bulk upload. Report path + row count.

## Rules
- **Listicle -> infographic is mandatory** (render_list_infographic.py, SD
  canvas in the theme palette + torn panels) — top of article, cover, pin.
- **image-critic reviews EVERYTHING visual before publish** — SD generations
  AND rendered graphics (infographics, palette cards, mockups). Nothing ships
  without its PASS.
- **Covers must not repeat one template.** Adjacent Journal cards must differ
  in TYPE: pages-mockup / atmospheric scene / one striking page / infographic.
  Check existing thumbs (blog/index.json) and pick a DIFFERENT type.
- **Mockups never repeat.** The thumb mockup (gen2) is not re-injected in the
  body (engine enforces it). A body mockup is a SECOND, different one
  (different pages/scene, slot gen4 type=mockup).
- **Realistic generations are ALWAYS in the listing's theme and palette
  (non-negotiable)** at a save-for-the-aesthetic bar: beautiful composition,
  beautiful colors, editorial light. Scene prompts must name 2-3 palette
  colors. Every generated image is reviewed by the `image-critic` agent
  (it LOOKS at the file): PASS or REGENERATE with a concrete prompt fix
  (max 2 rounds).
- **Generated ≠ product (anti-misleading):** illustrative generations are either
  clearly PHOTOGRAPHIC (atmospheric scene / realistic scrapbook-journal scene /
  mockup) or clearly GRAPHIC (diagram/"5 ideas" infographic / iPhone Notes list
  from `refs/iphone notes/`, with emoji allowed in the title/cluster/inside or
  after lines, but never as the first character/bullet marker)
  — never artwork in the listing's watercolor style. Scenes must NOT depict the
  listing's subject (no dogs in a dog-pack article, no cats in a cat one) —
  environment/process only: desk, journal, paper, light, tools. Anything that
  could be mistaken for a page from the set is banned.
- **Infographic two-source rule:** for every non-iPhone infographic, look at
  files in `refs/infographics/` for composition/usefulness only, then rebuild
  the final visual identity from files in `refs/branding/`. The result must feel
  like Sentimentalica: logo blue, paper collage, lace, botanicals, handwriting,
  bird/logo motifs, romantic scrapbook/journal texture. Do not use old outputs
  from Claude/Codex, `public/`, `staging/`, demos, or generated samples as
  references.
  Each infographic background must be different and topic-specific; do not reuse
  one generic branded collage background across a batch. Keep the same quality
  and brand language, but create a new world, prop set, framing, background
  asset, and mood for every article. Reusing a good background is still a
  REGENERATE.
- **The article is built FOR Pinterest**: every block is a future pin. Images
  must be either stunning or useful (infographic-style). Pure listing ads are
  banned — value first.
- **Pinterest lead funnel:** pins should send people to the article on
  sentimentalica.com first; the article should then softly propose relevant
  live listings when possible. Neutral/listicle = value first, product at END.
- **Related ads are topic-matched and fresh:** every `{{etsy:...}}` block and
  front matter `related_ids:` must come from product-bridge's fresh live-shop
  check at article-creation time. Use up to 4 LIVE IDs that match the article's
  exact category/theme; prefer newer listings when equally relevant. Floral
  article -> floral options; dark academia -> dark academia/library/gothic;
  animals -> animals; backgrounds/swatches -> background/base-paper/swatches.
  If no fresh relevant listing fits, omit `related_ids` and do not show random
  shop ads.
- **Image footer:** generated pin/article images must carry a subtle bottom
  `sentimentalica.com` footer plus a gentle CTA when composition allows.
  iPhone Notes images are the exception and must not be used as blog thumbnails.
- **Visual density:** an iPhone Notes/list infographic does NOT replace the
  rest of the image plan. Every article needs both saveable useful graphics and
  desire visuals. Every article, including infographic/iPhone Notes articles,
  must have a thin atmospheric scene: a wide mood image from `refs/scenes/` about
  the world around the topic, not a junk-journal mockup and not product proof.
  When a listing is involved, include a 3-5 image carousel in the product section
  using real `pageN.jpg`/customer assets, not Etsy thumbnails/previews.
- **Single-listing visual package:** use 3 palette images from 3 different
  showpiece real listing pages (not thumbnails/collages), 1 thin atmospheric
  scene inspired by the listing mood, 1 separate realistic junk journal/process
  scene inspired by the listing palette, a real-page carousel, and the live Etsy
  card. The thin scene and the journal/process scene are different images.
- **Multi-listing comparison package:** one palette image per featured listing
  and max 4 featured listings total. They must all come from one coherent
  live-shop/vault category or tight theme cluster, such as background/base-paper/
  swatches, nature/botanical/floral, or dark academia/library/gothic. Add one
  shared thin atmospheric scene, one mockup/process image, and a 2-3 image
  real-page carousel from at least one represented listing. Use real
  listing/customer images only, never Etsy thumbnails/previews.
- **Kit carousel** (single-listing article): use a `<div class="kit-carousel">`
  with >=3 REAL kit pages (pageN.jpg from the customer folder — NEVER Etsy
  thumbnails; arrows+dots auto-added). For neutral/listicle articles, keep this
  carousel near the product section so the article remains value-first.
- **An image for EVERY numbered point** (6 ways = 6 images): real pages/crops
  or generated scenes. People look, they don't read.
- **Hands/scissors/partial girl are allowed only in realistic reference-backed
  journal scenes:** use `refs/scrapbook and junk jornal scenes/` as the bar.
  In atmospheric scenes avoid them by default. Bad hands/fingers/tools =
  REGENERATE.
- **Article thumbnail must NEVER equal the Etsy cover** — after generation run
  `python3 tools/set_article_thumb.py <slug> gen2.jpg` (mockup scene as the
  marketing thumb; if SD failed, any pageN/imgN except img1).
- **LIVE listings only** — the resolver verifies the listing is active on Etsy
  and refuses (NOT LIVE) for drafts: article links must work for buyers.
- **Every article image is click-through** to the Etsy listing (post.js rule,
  automatic for all articles).
- **Slot gen2 = mockup**: mark it `"type":"mockup",
  "insert_images":["page1.jpg","page2.jpg","page3.jpg"],"mood":"<theme palette>"`
  — up to 3 REAL customer pages (asset tool saves them as pageN.jpg) in the prompts JSON — **v4 native embedding**: the REAL pages are laid down FIRST and mask-protected;
  SD inpaints the whole dreamy scene AROUND them — occlusion impossible by
  construction, edges blend naturally. Portrait 832×1216. At least one in
  listing-involved articles, but it never replaces the mandatory thin
  atmospheric scene.
- Explicit `/article <listing>` stays one listing per invocation. A multi-listing
  comparison article is allowed only when write-article/product-bridge creates
  one approved row with up to 4 LIVE listings from one category; unrelated
  listing batch requests still run sequentially.
- Never invent Etsy IDs or facts about the kit; everything from meta.json/vault.
- Titles must not collide with existing posts (check public/blog/index.json).
- If publish fails, report the exact error — do not hand-edit generated output.
