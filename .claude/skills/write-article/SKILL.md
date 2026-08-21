---
name: write-article
description: Front door of the ideation funnel. Handles requests to write one or more articles, write an article for a named listing, or propose article ideas. Runs the marketing funnel to fill a demand-first slate, writes ideas to content_plan.xlsx, then produces approved articles through the article machinery with listing-rotation and image-critic code gates.
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
3. **product-bridge** → first run `python3 tools/listing_rotation.py summary`,
   then choose tie strength (center/end/none) and on-theme LIVE listing(s) that
   have never appeared in another published article. Verify candidates with
   `python3 tools/listing_rotation.py check <ID...>`. A used ID is ineligible,
   even for an end-only bridge, unless Ksenia explicitly requested that exact
   listing again. It MAY return tie=none (pure lead magnet) — that's fine.
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
images, palette-as-image, mockups, listicle→infographic in Ksenia's ref style,
mandatory thin atmospheric scene for every article, scenes judged vs refs/scenes/
by the **image-critic**, then the **critic code-gate**
in publish_post.py (publish is blocked without every image PASS). Then
`plan_io.mark_published(slug)`.
Lead-magnet/neutral rows: pure value, product at the END only, every image
illustrates its adjacent paragraph. On-theme listings only — never off-theme animals.
Every article gets a thin atmospheric scene from `refs/scenes/`; it is a mood
image around the topic, not a junk-journal mockup. Single-listing rows also need
3 palette images from 3 different showpiece real listing pages, one separate
junk-journal/process scene, and a real-page carousel. Multi-listing comparison
rows need up to 4 LIVE listings from one coherent category/theme cluster, one
palette image per featured listing, plus one mockup/process image and a 2–3
real-page carousel from a represented listing.

### Listing palette protocol — hard publish gate

Palette articles promote the listing through its real artwork. Fetch source pages
from the shared Drive folder that contains the individual full-size printable
JPEGs for that exact listing. A listing thumbnail, revised-thumbnail folder,
Etsy collage, montage, mockup sheet, contact sheet, screenshot, or any filename
containing `thumb`/`thumbnail` is forbidden. For a single-listing palette article,
use three distinct showpiece pages from that listing; never repeat one page with
different crops.

Each palette visual is a portrait 1000x1500 composition with one real listing
page full bleed and exactly four compact square swatches in one vertical column.
Choose left, right, or center placement from genuine negative space so the
swatches do not cover the page's focal artwork. Each swatch contains `01`–`04`,
an elegant readable color name, and uppercase HEX. Curate four colors visibly
present in the source page: a dark anchor, a light paper tone, a middle bridge,
and a distinctive accent. The only footer is exactly `sentimentalica.com`.
Never use wide horizontal bars, an opaque side panel, a generic card grid, or a
palette detached from the promoted listing.

Render these deterministic overlays with `tools/render_palette_card.py` and its
square layout. This is the sole exception to the image-generation requirement
below: the authenticated listing page is the artwork and code supplies only the
precise swatch geometry and text. Before publication, compare the results at
full size with these approved examples:
`public/blog/img/velvet-vow-romantic-junk-journal-color-palette/palette-1.jpg`,
`public/blog/img/foxglove-hollow-woodland-journal-color-palette/palette-2.jpg`,
and `public/blog/img/moon-forest-palette-for-quiet-halloween-journals/palette-3.jpg`.
Reject any image whose source identity is unclear, whose swatches hide the focal
art, whose labels are cramped, or whose palette is not visibly grounded in the
page. Repair deployed palette assets under versioned filenames to bypass CDN
caches.
Visual refs are typed: `refs/branding/` = global Sentimentalica look,
`refs/infographics/` = useful graphics, `refs/iphone notes/` = authentic
iPhone Notes subtype with no emoji at the start of list items,
`refs/scrapbook and junk jornal scenes/` = realistic journal/mockup/process,
`refs/scenes/` = atmospheric mood and the mandatory thin article scene.
Never place the Sentimentalica bird, a bird-shaped brand mark, or any other
graphic logo inside article images. Branding references provide style context
only; do not reproduce their logo motif. Infographics and palette images may
carry only the exact plain text `sentimentalica.com` where the workflow requires
it. Atmospheric, process, mockup, iPhone Notes, and real-listing images receive
no logo, URL, or site mark.
For every non-iPhone infographic except the deterministic listing-page palette
cards defined above, the actual image-generation call MUST include
approved files from both `refs/infographics/approved-codex/` and
`refs/branding/`. If reference-enabled generation fails, stop; never replace it
with a reference-free prompt, generic card grid, shortened prompt, PIL/template,
or another improvised workflow. Do not publish until an unmistakably
Sentimentalica, reference-grounded visual passes the critic.

## 6. Pinterest CSV is opt-in only
Do not create, append, mirror, validate, or report a Pinterest CSV during the
normal article workflow. Do not run `pin_csv.py`, `pins_status.py`, or the
Pinterest CSV agent unless Ksenia explicitly asks for a CSV for named articles.
When explicitly requested, Link every row to the exact Sentimentalica article
that owns that image; never use a direct Etsy link. Follow the
canonical bulk-upload contract in `PIN_STRATEGY.md`: export every unique article
content image, including every carousel image; assign each image independently
to an exact name from `PINTEREST_BOARDS.txt`, even when one article spans several
boards. Never invent a board or reuse one generic board for the whole article.
Keywords are mandatory (5–10 image-specific Pinterest search phrases). Write a
search-led title and truthful image-type CTA for every row using the SEO/CTA
mapping in `PIN_STRATEGY.md`. Never repeat an identical Link within one CSV:
multi-image articles require a unique real `#section-anchor` per row, present in
the live article. Retry CSVs include failed rows only, not successful Pins.
Every Title within one CSV must also be unique and image-specific. Pinterest's
downloaded result marks later repeats as `Multiples rows with the same title`;
retry only its nonblank-error rows and never resend blank-error rows.
Format every title as `CTA first: Pinterest keyword phrase`. Never use em/en
dashes in Pinterest titles or descriptions; use plain human sentences.

Every article must leave all content images Pinterest/CSV-ready even when CSV
generation is not requested in that run. New generated visuals default to a
portrait 2:3 canvas at 1000x1500 px or larger; real listing pages may retain
their native readable portrait ratio. File extension, decoded bytes, and live
HTTP MIME must match exactly: JPEG files use `.jpg`/`.jpeg` and `image/jpeg`;
PNG files use `.png` and `image/png`. PNG bytes renamed to `.jpg` are a hard
failure. Before any CSV handoff, fetch every exact live Media URL and require
HTTP 200, matching MIME, and decodable matching still-image bytes. Repair
deployed assets under a new versioned filename rather than relying on a CDN
cache-busting query string.

For every explicitly requested CSV, use the permanent tracker in
`data/pinterest/`. Before building it, run `python3 tools/pinterest_tracker.py
refresh` and `python3 tools/pinterest_tracker.py check <slug> [...]`, then omit
Media URLs already recorded unless the request is specifically a failed-row
retry. Once the complete validated CSV is handed to Ksenia, run
`python3 tools/pinterest_tracker.py record-batch <csv-path> --status provided`.
Use `--status uploaded` only after Ksenia explicitly confirms Pinterest's
upload. Never describe a provided or scheduled CSV as successfully pinned.
Commit the resulting tracked ledgers, per-article tracker, and durable batch
copy so the state remains available to future agents.

## 7. Report
Per article: URL · angle & why · audience/hook · tie (center/end/none) · listing
and confirmation it was previously unused · image status. Plus the slate
summary (how many lead/listing, seasonal/eternal). Mention Pinterest CSV only
when Ksenia explicitly requested one.

## Rules (inherited — never skip)
- Демандный слейт: не переопределяй пропорции content_planner.py; сезон — только
  если окно открыто сегодня (никакого моря осенью).
- Продукт едет следом, не впереди. product-bridge вправе сказать «никак».
- Любой Etsy block / related_ids — только из свежей проверки live shop/feed
  product-bridge и только по теме статьи. Unused relevant LIVE listings are
  mandatory; a listing already promoted in any published article must be
  skipped. Reuse is allowed only when Ksenia explicitly requests that exact
  listing; record `allow_repeated_listings: true` in that exceptional post.
  Unrelated shop ads are forbidden.
- image-critic смотрит ВСЁ визуальное; критик-гейт в коде блокирует публикацию.
- Промпты сцен — по SCENE_STYLE.md и refs/scenes/ (файлы, не слова).
- Один вызов может дать несколько статей (batch) — делай их последовательно.
- Product-language accuracy АБСОЛЮТНА; только ЖИВЫЕ листинги.
- Если Desire Library пуста — воронка всё равно работает на широких безопасных
  территориях; предупреди Ксению, что идеи будут точнее, когда она её наполнит.
