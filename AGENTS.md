# Sentimentalica — project context for ANY AI agent (Codex, Claude, etc.)

This file is the single context map. Codex reads `AGENTS.md` automatically;
Claude Code reads the same rules from `ARTICLE_FUNCTION.md`. Open THIS folder
(`~/sentimentalica-site`) in either tool — it is the one home base. The empty
`~/Documents/Ksenia/Agentic Workflows` folder is NOT the project; ignore it.

## What this project is
Sentimentalica — Etsy shop selling AI-generated watercolor junk-journal
printable image packs. Strategy: Pinterest → sentimentalica.com → Etsy.
Owner: Ksenia. She dictates visual taste; agents execute. Tool is chosen LAST.

## Where everything lives
- **This repo `~/sentimentalica-site`** — the website + the content factory:
  - `tools/` — the engine: `publish_post.py` (md→live post), `insert_generated_images.py`
    (SDXL image gen; Claude-style embedded-page mockups are banned), `critic_gate.py` (HARD publish gate),
    `render_list_infographic.py`, `gen_article_assets.py`, `pin_csv.py`, `resolve_listing.py`.
  - `.claude/agents/` — copywriter, image-critic, qa-critic, pin-strategist, pinterest-seo…
  - `.claude/skills/` — `article`, `write-article`, `listing-content`, `content-cycle`.
  - `refs/` — **Ksenia's reference images (GROUND TRUTH)**:
    `branding/` (global Sentimentalica look + logo blue), `infographics/`
    (useful/list graphics), `iphone notes/` (authentic iPhone Notes subtype),
    `scrapbook and junk jornal scenes/`
    (realistic journal/mockup/process scenes), `scenes/` (atmospheric mood),
    `50things/`.
  - `content_plan.xlsx` — idea bank + used-ledger (Sheet 'Plan'). Read with openpyxl; pick an
    unused row, match its `Scene refs` FILES, build, mark row published. Sheet 'How to use' explains columns.
  - Canonical docs: `ARTICLE_FUNCTION.md` (the runbook — READ FIRST),
    `PIN_STRATEGY.md`, `SCENE_STYLE.md`, `CONTENT_STYLE_BRIEF.md`, `PROJECT.md`.
  - `staging/` — work in progress (`staging/overnight/critic/` = critic verdicts).
- **`~/sentimentalica-pipeline`** — the Etsy listing pipeline + A1111 scripts.
- **Obsidian vault `~/Tower media/`** — `Listings/` (194 notes, each with `etsy_id:`),
  `Workflows/`, `Prompts/`, `Reference/`. Grant Codex read access to this path.
- **A1111** at `http://127.0.0.1:7860` (SDXL) — image generation.
- **Python with PIL:** `/Users/kseniateter/sentimentalica-pipeline/.venv/bin/python` (system python3 has no PIL).

## The non-negotiable rules (full list in ARTICLE_FUNCTION.md)
1. **Critic is a CODE GATE, not a wish.** `publish_post.py` refuses to publish
   unless every generated image has a PASS in `staging/overnight/critic/<slug>.json`.
   You cannot skip it — the code exits. (This holds for Codex too — it's in Python, not an agent.)
2. **References are FILES, not words.** Judge every visual against files in
   `refs/`: branding for global look, infographics for useful graphics,
   scrapbook/junk journal scenes for realistic mockups/process, scenes for
   atmospheric mood. Empty folder = you are blind; ask Ksenia for references.
   Previous Claude/Codex outputs, `public/` article images, `staging/` assets,
   demo graphics, and generated samples are **not references** and must never be
   used as visual examples. Only images Ksenia intentionally placed in `refs/`
   are visual ground truth.
   Exception: when Ksenia explicitly names an already-published article image
   as "good" (for example `rainy-afternoon-journal-ideas` or
   `start-a-journal-page-with-one-receipt`), use it as an **approved quality and
   composition benchmark**, not as source artwork to copy. For current
   non-iPhone infographic quality, first look at the approved files in
   `refs/infographics/approved-codex/`.
   **Infographic two-source rule:** `refs/infographics/` is for composition
   inspiration and information archetypes only (grid, prompt list, diagram,
   checklist, object map). The final look must be rebuilt in the Sentimentalica
   identity from `refs/branding/` (logo blue, paper collage, lace, flowers,
   handwriting, bird/logo motifs, soft feminine scrapbook feel). Do not copy an
   infographic ref's outside brand, colors, logo, website, or exact artwork.
   Infographic backgrounds must vary per article/topic; never reuse one generic
   branded paper backdrop across a batch. The quality/brand language should stay
   consistent, but the actual world, props, framing, background asset, and mood
   must be newly made for each article. Reusing a good background is still a
   failure.
   Non-iPhone infographics must be object-led and useful like the approved
   Rainy Afternoon / One Receipt examples: large readable title, physical
   collage objects doing the explaining, numbered steps or labeled examples,
   arrows/labels where useful, and enough detail to save on Pinterest. A pretty
   background with four small floating text cards is a failure, even if branded.
   A faded generated background with a transparent/white overlay panel and
   plain coded text is also a failure. The typography must feel designed into
   torn papers, tags, tickets, labels, notes, stamps, ribbon, lace, or other
   physical collage pieces, not pasted over a washed-out photo.
   `tools/render_list_infographic.py` / local PIL torn-card grids are banned as
   the final infographic path; rough layout tests only. Every approved
   non-iPhone infographic includes a small `sentimentalica.com` centered at the
   bottom, with no extra CTA text.
3. **Images must be save-worthy/click-worthy** — branded, useful, realistic, or
   atmospheric depending on type. "Nice" is not "save"; "pretty but ignored" is
   not enough.
   **Quality gate before progress:** if any visual looks weak, generic,
   template-like, low-contrast, off-brand, or below the approved references,
   stop and redo the visual. Do not continue to article assembly, critic PASS,
   publishing, CSV, commit, or deploy just to finish. A bad image blocks the
   workflow exactly like a failed critic verdict.
4. **Google Drive listing/source files are READ/COPY ONLY.** Never delete, move,
   rename, overwrite, reorganize, or clean up anything inside
   `/Users/kseniateter/My Drive/Sentimentalica/` or listing asset folders.
   Listing pages, thumbnails, refs, and customer/export images are source-of-
   truth assets. Agents may read them, inspect them, and copy derivatives into
   `staging/` or `public/blog/img/`, but must never mutate the Drive originals.
   If a Drive file looks wrong, duplicated, missing, or misplaced, stop and ask
   Ksenia instead of "fixing" it.
5. **Product-language accuracy is absolute** — commercial-use watercolor IMAGE packs.
   Never "clipart / stickers / ephemera kit / seamless patterns / templates" unless the
   listing truly includes them.
6. **On-theme only.** No cats/dogs (or any off-theme listing) shoved into unrelated
   articles. Pick listings that match the article's theme. No animal photo in a neutral article.
7. **Only LIVE listings** (`resolve_listing.py` checks Etsy). Etsy drafts only — never publish Etsy listings.
8. **Multi-listing articles use one coherent live category.** If an article
   promotes several listings, pick up to four LIVE listings from one shop/vault
   category or tight theme cluster only: e.g. background/base-paper/swatches,
   nature/botanical/floral, or dark-academia/library/gothic. Never mix random
   pretty listings just to fill product slots.
9. **Related-shop ads must be freshly relevant.** Any Etsy product card or
   related-shop block in an article must use LIVE listings fetched/checked at
   article-creation time and related to that exact topic/category. Floral article
   → floral options; dark academia → dark academia; animals → animals. No random
   "other shop listings" and no stale hardcoded defaults.
10. **Neutral/listicle article = pure value**; products at the END only; every image
   illustrates its adjacent paragraph. Listicle → full infographic in Ksenia's ref style.
11. **Only palette images and infographics carry the site text.** Add exactly
   `sentimentalica.com` on color-palette images and non-iPhone infographics.
   Do not add extra CTA text (`full guide`, `more ideas`, etc.) inside the image.
   Do not stamp the site on atmospheric scenes, mockups, process scenes, real
   listing pages, or iPhone Notes screenshots.
   Color-palette images must always use one beautiful real listing page as the full-
   bleed background. Do not choose a main character image for palette art:
   no portraits, animal portraits, or single-subject hero characters. No
   thumbnail, no collage, no split white side panel, no framed card stack, no
   border around swatches, and no generic Pinterest-template look. Do not use
   geometric patchwork/grid/all-over rectangle pages as palette backgrounds:
   the repeated rectangular structure competes with the palette swatches and
   makes the pin look confused. Never use
   files from `revised thumbnails/` for palette backgrounds or listing-page
   source images; those are Etsy preview/collage assets. Use the actual listing
   page folder (for example `.../<Listing Name>/<Listing Name>/*.jpg`) when
   choosing real pages. Use 4-5
   colors only. Do not blindly use the most common extracted colors: choose a
   beautiful, cohesive palette from the listing image itself (anchor dark or
   midtone, soft neutral, supporting muted color, and one real accent when
   present). Reject muddy, repetitive, or ugly combinations even if the colors
   are technically present. Required palette curation process before rendering:
   run `tools/curate_palette.py <actual-listing-page.jpg>` or equivalent logic
   to over-extract 10-15 colors, reject muddy middle grays, near-duplicate
   hues, neons, pure shadows/highlights, micro-detail colors, and noise colors,
   then curate exactly four roles: **Dark Anchor**, **Strict Light Neutral**,
   **Support Mid-tone**, **Hero Accent**. The neutral must be clean cream,
   linen, ivory, or parchment with lightness > 80%, never muddy gray/taupe/
   dirty green. The accent must come from the image's hero object or highest-
   contrast hero feature (rose, blue roof, lavender flower, teal wash, radish-red shape, brick path,
   lantern, barn, candle), even when it has lower pixel count. Respect massive
   color blocks as support/anchor and ignore tiny stems/noise. Values must not
   clump: one dark, one light, one mid support, one clear accent. The vision/LLM
   instruction is: "You are an Expert Art Director and Color Theorist for
   Sentimentalica. Analyze the image like a human designer, not a pixel counter.
   Identify the focal/hero object and massive color blocks; reject muddy,
   duplicate, neon, micro-detail, and cheap colors; assign Dark Anchor, Strict
   Light Neutral, Support Mid-tone, and Hero Accent; slightly adjust saturation/
   lightness for a harmonious vintage tone; output 4 hex codes with role and
   thematic name." Swatches are plain unframed color rectangles/squares
   with the actual color name and/or HEX/number label visible. Current approved
   layout: large swatches chosen by composition. Wide horizontal rectangles are
   about 60-70% of image width; square columns are much larger than small side
   chips and sit where they preserve the best subject. Before rendering, inspect
   the listing page, decide what must remain visible, then place swatches around
   that subject. No side belt, opacity strip, backing/blur, airbrush, or frames.
   The listing background is slightly desaturated so the palette reads more
   clearly; curated swatches render as their exact approved HEX and are not
   auto-darkened into mud. Bottom text is
   exactly `sentimentalica.com`. If a listing does not have three distinct
   valid non-character pages for palette images, do not duplicate weak palette
   pins; keep the valid palette image(s) and add different approved visuals
   instead.
12. **Every article has a Pinterest-format atmospheric scene.** It is a portrait
   2:3 mood image from `refs/scenes/`: atmosphere around the topic, not a
   junk-journal mockup, not product proof. Listing articles also need palette
   images from real showpiece listing pages, real-page carousels, and separate
   process/mockup visuals as defined in `ARTICLE_FUNCTION.md`.
   **Scene reference rule:** first LOOK through `refs/scenes/` for a close,
   relatable reference (same kind of atmosphere/place/object, not just same
   color). If a close file exists, use it as the visual anchor. If no close file
   exists for the topic (Christmas, Halloween, dark academia, lantern street,
   etc.), create a new topic-specific scene yourself in Sentimentalica taste and
   state in the notes/critic record that no close scene reference existed.
13. **Banned Claude mockup logic:** never embed real listing pages into a
   generated album/journal/desk scene via SD inpaint/compositing. It looks fake
   and is not an accepted Sentimentalica visual. Real listing pages appear as
   direct carousel/gallery images or as the single full-bleed background for a
   palette image. Process scenes may be generated only as mood/process scenes
   inspired by the listing palette, without pasted product pages.
14. **Carousels are 2–3 images max.** Use real listing/customer page images only,
   never Etsy thumbnails/previews, and never 4+ images in an article carousel.
15. **AI disclosure + affiliates.** Every article includes a quiet AI image
   disclosure near the end, before the final related/shop block. Amazon
   affiliate links require a clear disclosure before the first affiliate link
   and must not be added until Ksenia provides the affiliate/tag system.

## How to produce an article (the pipeline, in order)
1. Pick a topic from `content_plan.xlsx` (an unused row) or take Ksenia's request.
2. `resolve_listing.py` — confirm the listing is LIVE; get palette/thumbs.
3. Write the article (voice = approved articles; see `colorful-junk-journal-ideas…`).
4. Generate images (`insert_generated_images.py`) — visuals judged vs the
   correct `refs/` bucket for their type.
5. **image-critic LOOKS at each image**, records verdict via `critic_gate.record(slug, slot, PASS|REGENERATE)`.
6. `publish_post.py --push` — BLOCKS if any image isn't PASS. Fix, re-record, retry.
7. Mark the `content_plan.xlsx` row used (status=published + date + slug).
8. pinterest-seo → pins → `pin_csv.py` (auto-mirrors CSV to Google Drive).
   Pinterest links go to sentimentalica.com articles by default; article pages
   then softly route to relevant Etsy listings. Pin titles/descriptions must
   include a gentle reason to click through to the article.

## The ideation funnel (how ideas get chosen — demand-first)
Trigger: "напиши статью" / "напиши N статей" / "напиши статью под <listing>" /
"предложи идеи" → skill `.claude/skills/write-article`.
- `tools/content_planner.py` — deterministic slate: 65% lead-magnet / 35%
  listing-bound; seasonal slots ONLY for windows open today (Pinterest ~30-45d
  lead). Reads the Seasonal Calendar sheet. No off-season ideas.
- `tools/plan_io.py` — reads Desire Library / Seasonal Calendar, appends idea
  rows (auto-dedup), marks published.
- 5 agents: **marketing-director** (allocates the slate + assigns territories) →
  **desire-scout** (sharp timely angle) → **audience-strategist** (who + hook) →
  **product-bridge** (product center/end/NONE — reach is valid) →
  **marketing-critic** (ideation gate: kills product-first + off-season).
- Modes: *auto* writes the articles; *curated* just fills `idea` rows for Ksenia
  to tick `approved`. Everything flows through the /article machinery + critic gate.
Inputs Ksenia owns: `refs/branding/`, `refs/infographics/`,
`refs/scrapbook and junk jornal scenes/`, `refs/scenes/`, and the Desire Library
+ Seasonal Calendar sheets in `content_plan.xlsx`.

## Secrets
Never in git. Cloudflare worker secrets / GitHub Actions secrets only
(ETSY_API_KEY, ADMIN_PASSWORD, GITHUB_TOKEN, CLOUDFLARE_API_TOKEN). This repo is public.
