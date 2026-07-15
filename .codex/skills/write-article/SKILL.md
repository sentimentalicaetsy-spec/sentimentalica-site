---
name: write-article
description: Front door of the ideation funnel. Handles "напиши статью", "напиши N статей", "напиши статью под <листинг>", and "предложи/собери идеи". Runs the 5-agent marketing funnel (marketing-director → desire-scout → audience-strategist → product-bridge → marketing-critic) to fill a demand-first slate, writes ideas to content_plan.xlsx, then (auto mode) produces each article through the /article machinery with the image-critic and the critic code-gate.
---
# /write-article — demand-first ideation funnel → articles

Philosophy (AGENTS.md, PIN_STRATEGY.md): lead with what a person WANTS; the
product rides along. ~65% of articles are lead magnets, not product pieces.

## 1. Parse the request
- **N** = number of articles (default 1). "напиши 5 статей" → N=5.
- **explicit listing?** "напиши статью под <name>" → single listing-bound article
  (skip the slate; go straight to product-bridge with that listing, then write).
- **mode:**
  - *auto* (default for "напиши…") — write the articles now.
  - *curated* ("предложи идеи", "собери идеи", "накидай тем") — fill idea rows in
    content_plan.xlsx and STOP for Ksenia to tick `approved`. Don't write articles.

## 2. Build the slate (marketing-director)
Run `python tools/content_planner.py slate N` — it returns the mix (lead/listing,
seasonal/eternal) and which seasons are OPEN today. Then invoke the
**marketing-director** agent to assign each slot a concrete Desire-Library
territory (or the open season) + a working angle, deduped against the Plan.
Do NOT override the allocator's 65/35 or its seasonal windows.

## 3. Run the funnel per slot (quality gate)
For each slot, in order:
1. **desire-scout** → one sharp, timely, save-worthy angle + target query.
2. **audience-strategist** → who + emotional hook + article type.
3. **product-bridge** → tie strength (center/end/none), on-theme LIVE listing(s)
   or none, related_ids from fresh live-shop data, funnel stage. It MAY return
   tie=none (pure lead magnet) — that's fine.
4. **marketing-critic** (ideation gate) → PASS or re-sharpen (max 2 rounds, then
   surface to Ksenia). Only PASS ideas proceed.
Collect each PASS as a plan row (Title/angle, Type, Theme, Listings, Notes with
audience+hook+target query).

## 4. Write to the plan
`plan_io.append_plan_rows(rows, status=...)` — status `approved` (auto) or `idea`
(curated). Dedup is automatic. In curated mode, STOP here and report the slate.

## 5. Produce each article (auto mode only)
For each approved row, run the full **/article machinery** (see ARTICLE_FUNCTION.md
— it holds ALL the hard rules): real live-listing check, real pages, per-point
images, palette-as-image, process scenes, listicle→infographic in Ksenia's ref style,
mandatory Pinterest-format atmospheric scene for every article, scenes judged vs refs/scenes/
by the **image-critic**, then the **critic code-gate**
in publish_post.py (publish is blocked without every image PASS). Then
`plan_io.mark_published(slug)`.
Lead-magnet/neutral rows: pure value, product at the END only, every image
illustrates its adjacent paragraph. On-theme listings only — never off-theme animals.
Every article gets a portrait 2:3 Pinterest-format atmospheric scene from `refs/scenes/`; it is a mood
image around the topic, not a junk-journal mockup. Single-listing rows also need
3 palette images from 3 different showpiece real listing pages, one separate
junk-journal/process scene without embedded product pages, and a 2-3 image
real-page carousel max. Multi-listing comparison
rows need up to 4 LIVE listings from one coherent category/theme cluster, one
palette image per featured listing, plus one process image and a 2–3
real-page carousel from a represented listing.
Scene reference rule: first LOOK through `refs/scenes/` for a close, relatable
reference. If one exists, use it as the visual anchor. If none exists for the
topic, create a new topic-specific scene yourself in Sentimentalica taste and
note that no close scene reference existed.
Visual refs are typed: `refs/branding/` = global Sentimentalica look,
`refs/infographics/` = useful graphics, `refs/iphone notes/` = authentic
iPhone Notes subtype with no emoji at the start of list items,
`refs/scrapbook and junk jornal scenes/` = realistic journal/mockup/process,
`refs/scenes/` = atmospheric mood and the mandatory Pinterest-format article scene.
Infographic two-source rule: use `refs/infographics/` only for the composition
or useful-content archetype, then rebuild the final image in the Sentimentalica
brand from `refs/branding/`. Never use prior Claude/Codex outputs, `public/`,
`staging/`, demos, or generated samples as reference images.
Exception: if Ksenia explicitly names a published image as good, use it as an
approved quality/composition benchmark only, not as source artwork to copy.
Every infographic background must vary by article/topic; no repeated generic
brand background across a batch. Keep the same quality/brand system, but create
a fresh world, prop set, framing, background asset, and mood for every article.
Reusing a good background is still a failure.
Non-iPhone infographics must be object-led like the approved Rainy Afternoon
and One Receipt examples: large readable title, physical collage objects doing
the explaining, numbered steps/labeled examples/arrows where useful, and strong
Pinterest save-value. A pretty background with four small floating text cards is
a failure. `tools/render_list_infographic.py` / local PIL torn-card grids are
banned as the final infographic path; rough layout tests only. Every approved
non-iPhone infographic includes a small `sentimentalica.com` centered at the
bottom, with no extra CTA text.
Before making one, inspect `refs/infographics/approved-codex/` as the current
Ksenia-approved quality bar.
Color-palette images: always use one beautiful real listing page as the full-bleed
background, but do not choose main character images (portraits, animal
portraits, single-subject hero characters). Never use files from `revised
thumbnails/` for palette backgrounds or listing-page source images; those are
Etsy preview/collage assets. Use the actual listing page folder instead (for
example `.../<Listing Name>/<Listing Name>/*.jpg`). Do not use geometric
patchwork/grid/all-over rectangle pages as palette backgrounds; repeated
rectangle structure competes with swatches. Use 4-5 colors only, chosen
as a beautiful cohesive palette from the listing image itself rather than just
the most common extracted colors. Before rendering, run
`tools/curate_palette.py <actual-listing-page.jpg>` or equivalent logic:
over-extract 10-15 candidates, reject muddy middle grays, near-duplicates,
neons, pure shadows/highlights, micro-detail colors, and noise colors, then
curate exactly four roles: Dark Anchor, Strict Light Neutral, Support Mid-tone,
Hero Accent. Neutral must be clean cream/linen/ivory/parchment with lightness
> 80%, never muddy gray/taupe/dirty green. Accent must come from the hero
object or highest-contrast hero feature, even if it has lower pixel count.
Respect massive color blocks; ignore tiny stems/noise; avoid value clumping.
Use the vision/LLM prompt: "You are an Expert Art Director and Color Theorist
for Sentimentalica. Analyze the image like a human designer, not a pixel
counter. Identify the focal/hero object and massive color blocks; reject muddy,
duplicate, neon, micro-detail, and cheap colors; assign Dark Anchor, Strict
Light Neutral, Support Mid-tone, and Hero Accent; slightly adjust saturation/
lightness for a harmonious vintage tone; output 4 hex codes with role and
thematic name." Swatches are plain unframed color
rectangles/squares with color name and/or HEX/number labels. Current approved
layout is chosen per actual listing image: large rectangle stack or large
square column, preserving the best visible subject area. No side belt, opacity
strip, backing/blur, airbrush, or frames. Slightly desaturate the real listing
background so swatches read clearly; curated swatches render as their exact
approved HEX and are not auto-darkened into mud. Bottom
text is exactly `sentimentalica.com`. No thumbnail, collage, split side panel,
framed stack, swatch border, or extra CTA text. If a listing lacks three
distinct valid non-character pages, do not duplicate weak palette pins; keep the
valid palette image(s) and add other approved visual types instead.
Banned visual path: never use Claude-style album/mockup embedding where real
listing pages are pasted into a generated journal/album/desk scene. Real pages
belong in direct carousel/gallery images, 2-3 max, or as the single full-bleed
background for palette images only.

## 6. Pins → CSV (MANDATORY finale of every article — do not skip)
After each article is live, invoke the **pinterest-seo** agent on it: it writes
title/description/keywords/board/drip-date rows via `tools/pin_csv.py add ...`
for every image worth pinning (mockups, palette, hero scenes, strong pages),
using the sentimentalica.com article as the CSV Link by default. Pin titles
must be CTA-to-article titles (search phrase + reason to click), and
descriptions end with a gentle site CTA. Direct Etsy links are exceptions only
when Ksenia explicitly asks. The CSV
auto-mirrors to Google Drive → `Sentimentalica/Pinterest_CSV/`. Then run
`python tools/pins_status.py` — every published article must show `✓ pins`.
An article without pins is NOT done (this step was silently skipped for the
first 6 articles — never again).

## 7. Report
Per article: URL · angle & why · audience/hook · tie (center/end/none) · listings ·
image status · pins added (CSV path). Plus the slate summary (how many
lead/listing, seasonal/eternal), and the `pins_status.py` result.

## Rules (inherited — never skip)
- Демандный слейт: не переопределяй пропорции content_planner.py; сезон — только
  если окно открыто сегодня (никакого моря осенью).
- Google Drive source assets are READ/COPY ONLY: never delete, move, rename,
  overwrite, reorganize, or clean up anything inside
  `/Users/kseniateter/My Drive/Sentimentalica/` or listing asset folders.
  Agents may read/inspect Drive files and copy derivatives into `staging/` or
  `public/blog/img/`, but must never mutate the originals. If Drive looks wrong,
  stop and ask Ksenia.
- Продукт едет следом, не впереди. product-bridge вправе сказать «никак».
- Любой Etsy block / related_ids — только из свежей проверки live shop/feed
  product-bridge и только по теме статьи. Fresh relevant new listings beat old
  defaults; unrelated shop ads are forbidden.
- image-critic смотрит ВСЁ визуальное; критик-гейт в коде блокирует публикацию.
- Промпты сцен — по SCENE_STYLE.md и refs/scenes/ (файлы, не слова).
- Один вызов может дать несколько статей (batch) — делай их последовательно.
- Product-language accuracy АБСОЛЮТНА; только ЖИВЫЕ листинги.
- Если Desire Library пуста — воронка всё равно работает на широких безопасных
  территориях; предупреди Ксению, что идеи будут точнее, когда она её наполнит.
