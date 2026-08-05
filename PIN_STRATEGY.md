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

## Pinterest bulk-upload CSV contract (updated 2026-08-05)

Official format source:
`https://help.pinterest.com/en/business/article/bulk-upload-video-pins`.

Follow Pinterest's current bulk-upload template exactly. Header order:
`Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords`.

- Maximum 200 rows per uploaded CSV.
- `Title` is required and has a 100-character maximum.
- `Media URL` is required and must be a public direct file URL. Sentimentalica
  image rows use the published `.jpg`, `.jpeg`, or `.png` URL, never a local
  path, Google Drive preview, article page URL, or dynamically loaded Etsy image.
- `Pinterest board` is required. Wait for Ksenia's canonical board list, then
  use an exact board name from that list for every row. Assign the board per
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

Every title must be a natural Pinterest search phrase first, with the concrete
topic in the opening words. Keep it below 100 characters and add a short CTA
that accurately matches both the image and the linked article. The description
must expand the search intent naturally and end with the same promise. Do not
use vague clickbait such as `Click here`, `You need this`, or `Learn more`.

Match the CTA to the visual:

- **Junk-journaling hack, infographic, or technique:** invite the reader to
  check the article for the full method, more junk-journaling hacks, or the
  remaining steps. Example title: `3 Junk Journal Pattern Hacks — See the Full Method`.
- **Real listing/carousel picture:** invite the reader to see more pictures and,
  when the linked article actually contains the freebie, to check the article
  for more free pictures. Never call paid listing images free. Example title:
  `Vintage Floral Journal Page — Find More Free Pictures`.
- **Atmospheric scene:** invite the reader to get more inspiration or related
  journal ideas from the article. Example title:
  `Cozy Patchwork Journal Inspiration — See More Ideas`.
- **Color palette:** invite the reader to explore the palette method, matching
  color ideas, or the full color guide. Example title:
  `Teal and Coral Junk Journal Palette — Get More Color Ideas`.
- **Process/mockup scene:** invite the reader to see the complete process,
  layout recipe, or step-by-step article.

CTA wording must remain truthful to the landing article. If an article does not
contain free pictures or a freebie link, use `see more printable inspiration`
instead of promising free pictures.
