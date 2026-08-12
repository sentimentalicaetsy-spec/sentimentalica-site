# Sentimentalica — Pinterest Pin Strategy (canonical)

> Source of truth for the pin-strategist / Copywriter / Visual agents.
> Author: Ksenia (2026-07-05). Supersedes the earlier thin style brief for the
> MARKETING logic of pins. Composition rules live in `CONTENT_STYLE_BRIEF.md`;
> this file governs WHY each pin exists and what it says.

## Core principle
The agent does NOT start from "how do I show the images nicely?" It starts from:
**"What pain, desire, or idea does this pin solve?"** Every pin has exactly ONE
marketing reason to exist. If a pin only says "pretty images" or "150 images",
rewrite it.

A pin can sell: (1) a pain solution · (2) a concrete idea ("20 gothic journaling
ideas") · (3) an aesthetic ("dark romance", "cottagecore", "faith-based") ·
(4) a quick start ("start creating today", "save this palette") · (5) a
commercial-use benefit ("use for cards, wall art, covers, invitations, digital
products").

**Not every pin should look like "I'm selling an Etsy product."** Some pins must
look like genuinely useful Pinterest content that LEADS to the product
(e.g. "20 Romantic Things to Add to Your Journal" — the visual uses listing
images, the description/link point to the Etsy listing as the image source).

## Product-language accuracy (STRICT)
The product = **commercial-use watercolor-style image packs** (~150–300 themed
printable images: portraits, florals, frames, illustrations, scenes, patterns,
backgrounds — content varies per listing).

**Never** advertise as: PNG clipart, transparent clipart, ephemera kit, sticker
pack, background-only paper pack, frame bundle, tag pack, pocket kit, or seamless
pattern pack — UNLESS that listing specifically includes those exact file types.
**Use broader accurate language:** commercial-use watercolor images · printable
image pack · image collection · themed art collection · design asset library ·
creative image bundle · digital product resources · printable art bundle.
Never promise templates/POD if the license/files don't include them
("use for", "create with", "design ideas" — not "templates included").

## Per-pin output contract (agent must produce ALL fields)
Pin number · Pin type · Target audience · Buyer problem/desire/curiosity ·
Main text overlay (≤8 words) · Small supporting text · CTA · Visual structure ·
Which parts use ACTUAL listing images · Which parts may be Stable-Diffusion
generated · Pinterest SEO title · Pinterest SEO description · 5–10 keywords.

## Volume standard (Ksenia, 2026-07-05)
**Minimum 10 pins per listing.** Pick the 10+ best-fitting of the 18 types for
that listing's character (a gothic listing leans dark/idea/aesthetic pins; a
seller-friendly pack leans use-case/commercial pins). Optional types 19–21 count
toward the 10 when the theme fits.

## The 18 core pins (make for every large listing)
| # | Type | Sells | Main-text example |
|---|------|-------|-------------------|
| 1 | Problem Solver | pain solution | "Your journal feels flat?" |
| 2 | Stuck / Idea Text | idea, saveable | "Stuck on what to create?" / "30 journal theme ideas" |
| 3 | List / Ideas | saveable list | "20 Gothic Journal Ideas" (show 5–8 items) |
| 4 | Aesthetic Match | identity | "For dark romantic creators" |
| 5 | Color Palette / Moodboard | mood via color | "[Theme] Color Palette" (5–8 real swatches) |
| 6 | Theme Board | ready theme | "Gothic Romance Journal Theme" |
| 7 | Transformation | result | "From blank page to beautiful spread" |
| 8 | Use Case | what you can make | "Use them in journals, cards & collage" |
| 9 | Collection Variety | scale, not "150 imgs" | "One collection, endless project ideas" |
| 10 | Close-Up Detail | quality | "Tiny details for beautiful projects" |
| 11 | Scrapbook / Collage | craft audience | "Build layered scrapbook pages" |
| 12 | Card / Invitation | card makers | "Create cards with watercolor art" |
| 13 | Etsy Seller Product Ideas | sellers | "Need art for your next Etsy product?" |
| 14 | Digital Product Starter | digital creators | "Start your next digital product faster" |
| 15 | Design Asset Library | reusable resource | "Build your design library" |
| 16 | Small Business / Branding | small biz | "Soft visuals for your small business" |
| 17 | Product Mockup Ideas | commercial products | "Turn watercolor art into products" |
| 18 | Keyword / Long-Tail SEO | search intent | "Commercial Use Watercolor Images" |

### Optional (only when the theme fits)
19. Teacher / Worksheet Creator — seasonal/kids/faith/botanical/educational.
20. Church / Faith Creator — Christian / Easter / angel / Bible / faith only.
21. Seasonal Search — Easter/Christmas/Halloween/autumn/spring/summer/Valentine/wedding.

(Full per-pin briefs — audience, problem, text placement, visual, CTA — are in
Ksenia's spec message dated 2026-07-05; this table is the working index.)

## Visual direction rules
- Actual listing images are the main product evidence — SD may generate
  backgrounds, desks, journals, mockups, textures, lighting, rooms,
  frames, styled scenes, but must NOT replace the product images.
  NEVER scissors/hands/fingers/people — banned (classic AI slop).
- Insert real listing images INTO any generated mockup.
- Readable on mobile; high contrast for text-heavy pins; big bold hook (small
  tasteful text gets scrolled past — the goal is the CLICK).
- Do NOT repeat the same hook across pins; match every pin to the listing's
  aesthetic; some pins look like useful content, some like direct product previews.
- Composition building blocks (from validated mockups): "chaos scatter"
  (→ Variety/Problem), "bold hero + band" (→ Aesthetic/Theme), "big-number/
  question" (→ Stuck/Idea/Transformation). See `refs/mockups/`.
- Never add a bird logo, bird-shaped brand mark, or any other graphic logo to a
  Pin/article image. CSV rows reuse the published article images as they are;
  do not alter them just for bulk upload. Only infographics and palette cards
  may already carry the exact plain text `sentimentalica.com`. Atmospheric,
  process, mockup, carousel/listing-page, and iPhone Notes images remain
  unmarked. Do not add CTA overlays such as `full guide`, `more ideas`,
  `read the article`, or `save this` to these exported article images.
- New ref taxonomy (2026-07-09):
  `refs/branding/` defines the overall Sentimentalica visual identity and logo
  blue; `refs/infographics/` defines useful/saveable graphic structures and the
  special iPhone Notes format; `refs/scrapbook and junk jornal scenes/` defines
  realistic journal/process/mockup imagery; `refs/scenes/` defines atmospheric
  mood rooms/desks/workspaces.

## Marketing rule (final gate, enforced by QA)
Each pin must solve one problem, trigger one desire, or offer one useful idea.
"Pretty images" / "150 images" alone = reject and rewrite.

## Мини-шаблон каждого пина (обязательные поля)
Pin number · Pin type · Target audience · Buyer problem/desire · Main overlay
text (≤8 слов) · Small supporting text · CTA · Visual structure · Use actual
listing images for · Stable Diffusion may generate · Pinterest title ·
Pinterest description · Keywords (5–10).

## Как агент должен мыслить (пример: dark gothic pack)
- Плохо: «200 Gothic Images» — ноль причин сохранять.
- Лучше: «20 Dark Romantic Journal Ideas» — полезная идея, картинки листинга
  становятся способом создать этот mood.
- Ещё лучше: «Your journal needs a darker mood?» — названа боль.
- Другая аудитория: «Build your gothic design library» — sellers/creators.
Правило: у пина ОДНА маркетинговая причина существовать; «pretty images» /
«150 images» → переписать.

## Article-first (Ксения, 2026-07-06)
Сначала статья — потом Pinterest, НО статья конструируется ДЛЯ Pinterest:
каждый её блок (карусель кита, картинка каждого пункта, палитра, мокапы) —
будущий пин. Картинка обязана быть либо потрясающе красивой, либо полезной
(инфографика: список/problem-solution прямо НА картинке). Реклама листинга
сама по себе — «nobody cares»: сперва польза, продукт — путь к ней.

## Pinterest bulk-upload CSV contract (updated 2026-08-10)

Official format source:
`https://help.pinterest.com/en/business/article/bulk-upload-video-pins`.

Follow Pinterest's current bulk-upload template exactly. Header order:
`Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords`.

- Maximum 200 rows per uploaded CSV.
- `Title` is required and has a 100-character maximum.
- `Media URL` is required and must be a public direct file URL. Sentimentalica
  image rows use the published `.jpg`, `.jpeg`, or `.png` URL, never a local
  path, Google Drive preview, article page URL, or dynamically loaded Etsy image.
- **Pinterest-ready article image gate:** every future article content image must
  be suitable for a later Pinterest CSV even when no CSV is requested during the
  article run. New generated scenes, infographics, palette images, and mockups
  should normally be portrait 2:3 at 1000x1500 px or larger. Real customer/listing
  pages may keep their native portrait ratio, but must be large enough to read as
  a Pin. Do not publish landscape-only, tiny, animated, or unsupported assets as
  article content images that will later be expected in a CSV.
- The filename extension, decoded file format, and public HTTP `Content-Type`
  must agree exactly: `.jpg`/`.jpeg` = genuine JPEG bytes served as `image/jpeg`;
  `.png` = genuine PNG bytes served as `image/png`. A PNG merely renamed to
  `.jpg` is a hard failure even if browsers display it. JPEG output should be
  RGB; PNG may be RGB or RGBA. Use one still frame only.
- Before creating or handing off a CSV, validate every Media URL twice: locally
  decode the file and confirm format/dimensions, then fetch the exact live URL
  and require HTTP 200, the matching image MIME type, and decodable matching
  bytes. CSV creation is blocked until every row passes. If a deployed image has
  to be repaired, do not trust a query string to bypass CDN cache; publish a new
  versioned filename in the same article image folder, use that new URL in the
  retry CSV, and verify the exact URL live. Retry CSVs contain only failed rows.
- `Pinterest board` is required. The canonical exact-name allowlist is
  `PINTEREST_BOARDS.txt`; use one name from that file for every row. Assign the board per
  image according to what that image actually solves or shows. Images from one
  article may and often should go to different boards. Never invent a new board,
  guess a near-match, or silently send every image to one generic board. A
  section is written as `Board name/Section name` only when that exact entry is
  present in the supplied list.
- `Thumbnail` stays blank for image Pins. It is required only for video Pins;
  this article-image workflow does not generate video rows.
- `Description` is optional in Pinterest's schema but required by the
  Sentimentalica workflow; keep it accurate and at most 500 characters.
- `Link` is mandatory and points to the exact Sentimentalica article that owns
  the image, so the funnel remains Pinterest → relevant useful article → Etsy
  or freebie. Never use the shop homepage, blog index, unrelated article, or a
  direct Etsy URL in this CSV workflow. The image URL and article link must
  share the same article slug.
- Pinterest's bulk importer rejects repeated identical destination strings in
  one CSV as `Duplicate Pin link`, even when Media URLs differ. For a multi-image
  article, give every row a unique, real section fragment such as
  `article.html#palette-example`; the matching `id` must exist on that image or
  section in the live article. Do not fabricate unrelated URLs or use tracking
  parameters merely to bypass deduplication. A retry CSV contains only failed
  rows, never the row Pinterest already created successfully.
- `Publish date` may be blank for immediate publishing, `YYYY-MM-DD`, or
  `YYYY-MM-DDTHH:MM:SS`; a timed value represents UTC.
- `Keywords` is mandatory: 5–10 unique comma-separated Pinterest search terms
  genuinely relevant to that specific image and its adjacent article section.
  Lead with the primary search phrase, then add close topic, technique,
  aesthetic, and use-case phrases. No generic stuffing, duplicate phrases, or
  irrelevant high-volume keywords.

### Article image coverage and board assignment

Create one row for every unique content image published in the article:
infographics, atmospheric scenes, process/mockup images, palette images, and
every image inside every real-page carousel. Include the article thumbnail only
when it is a distinct content image not already represented by its Media URL.
Exclude navigation/site logos, favicon, decorative CSS assets, AI disclosure
elements, and Etsy thumbnails injected dynamically by the related-products
widget. Do not create multiple rows for the same Media URL in one batch.

Write the title, description, keywords, and board independently for each image.
Use the visible subject plus the problem or idea in its adjacent article section;
do not copy one generic title/description/board across all images from an article.

### Pinterest SEO title and CTA contract

Every title uses **CTA first, keyword phrase second**, separated by a colon:
`See More Pictures: Silver Wedding Junk Journal Pages`. Keep it below 100
characters. The phrase after the colon must be a natural Pinterest keyword a
searcher could use, not merely a poetic theme name. The description expands the
search intent naturally and supports the same promise. Do not use vague
clickbait such as `Click here`, `You need this`, or `Learn more`.

Never use an em dash (`—`) or en dash (`–`) in Pinterest titles or descriptions.
Use a colon in the title and ordinary short sentences in the description. This
keeps the copy natural and avoids punctuation that reads like AI-generated text.

Match the CTA to the visual:

- **Junk-journaling hack, infographic, or technique:** invite the reader to
  check the article for the full method, more junk-journaling hacks, or the
  remaining steps. Example title: `See the Full Method: 3 Junk Journal Pattern Hacks`.
- **Real listing/carousel picture:** invite the reader to see more pictures and,
  when the linked article actually contains the freebie, to check the article
  for more free pictures. Never call paid listing images free. Example title:
  `Find More Free Pictures: Vintage Floral Journal Page`.
- **Atmospheric scene:** invite the reader to get more inspiration or related
  journal ideas from the article. Example title:
  `See More Ideas: Cozy Patchwork Journal Inspiration`.
- **Color palette:** invite the reader to explore the palette method, matching
  color ideas, or the full color guide. Example title:
  `Get More Color Ideas: Teal and Coral Junk Journal Palette`.
- **Process/mockup scene:** invite the reader to see the complete process,
  layout recipe, or step-by-step article.

CTA wording must remain truthful to the landing article. If an article does not
contain free pictures or a freebie link, use `see more printable inspiration`
instead of promising free pictures.

## Permanent Pinterest tracker contract

The durable source of truth is stored in the tracked repository directory
`data/pinterest/`, not only in ignored working files under `staging/pins/`:

- `PINTEREST_ARTICLE_TRACKER.csv` is the readable one-row-per-article tracker.
- `PIN_MEDIA_LEDGER.csv` is the exact Media URL ledger used for deduplication.
- `PINTEREST_BATCH_LEDGER.csv` records each batch and its handoff state.
- `batches/` contains durable copies of CSVs that were handed to Ksenia or
  confirmed uploaded.

Never treat these states as interchangeable:

1. **Historical CSV record** means an image appeared in an older CSV, but its
   delivery and Pinterest result were not independently confirmed.
2. **CSV provided** means the finished file was handed to Ksenia (including a
   confirmed Google Drive mirror). It does not mean Pinterest created the Pin.
3. **Pinterest upload confirmed** is used only after Ksenia explicitly says the
   batch was uploaded or supplies Pinterest's result. A schedule date alone is
   not upload confirmation.

Mandatory workflow whenever Ksenia requests a Pinterest CSV:

1. Run `python3 tools/pinterest_tracker.py refresh` and then
   `python3 tools/pinterest_tracker.py check <article-slug> [...]` before making
   the batch. Read `PIN_MEDIA_LEDGER.csv` and exclude Media URLs that already
   have a CSV record unless Ksenia explicitly requests a retry of failed rows.
2. Create and fully validate only the missing/currently requested rows under
   the bulk-upload contract above.
3. After the complete validated CSV has actually been handed off or mirrored,
   run `python3 tools/pinterest_tracker.py record-batch <csv-path> --status
   provided --date YYYY-MM-DD`. This archives the exact batch, updates both
   ledgers, and rebuilds the per-article tracker.
4. If Ksenia later confirms the upload, run the same command with `--status
   uploaded`. Do not infer this state from file creation, scheduling, or Drive.
5. Run `check` again and report prepared/provided/upload-confirmed counts
   separately. Commit and push the tracker, ledger, archived handed-off batch,
   and any real article anchors needed by its Links so the next agent can use
   the same source of truth.

For a current article whose image set changes after a CSV was created, the
tracker compares the ledger to the article's current `<div class="post-body">`
images. New images appear as `Images with no CSV record`; removed images remain
in the audit ledger but do not inflate current article coverage.
