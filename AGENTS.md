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
    (SDXL image gen + v4 mockups), `critic_gate.py` (HARD publish gate),
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
3. **Images must be save-worthy/click-worthy** — branded, useful, realistic, or
   atmospheric depending on type. "Nice" is not "save"; "pretty but ignored" is
   not enough.
4. **Product-language accuracy is absolute** — commercial-use watercolor IMAGE packs.
   Never "clipart / stickers / ephemera kit / seamless patterns / templates" unless the
   listing truly includes them.
5. **On-theme only.** No cats/dogs (or any off-theme listing) shoved into unrelated
   articles. Pick listings that match the article's theme. No animal photo in a neutral article.
6. **Only LIVE listings** (`resolve_listing.py` checks Etsy). Etsy drafts only — never publish Etsy listings.
7. **Multi-listing articles use one coherent live category.** If an article
   promotes several listings, pick up to four LIVE listings from one shop/vault
   category or tight theme cluster only: e.g. background/base-paper/swatches,
   nature/botanical/floral, or dark-academia/library/gothic. Never mix random
   pretty listings just to fill product slots.
8. **Related-shop ads must be freshly relevant.** Any Etsy product card or
   related-shop block in an article must use LIVE listings fetched/checked at
   article-creation time and related to that exact topic/category. Floral article
   → floral options; dark academia → dark academia; animals → animals. No random
   "other shop listings" and no stale hardcoded defaults.
9. **Neutral/listicle article = pure value**; products at the END only; every image
   illustrates its adjacent paragraph. Listicle → full infographic in Ksenia's ref style.
10. **Generated Pinterest/article images carry the site.** Add a subtle bottom
   `sentimentalica.com` footer plus a gentle CTA when the format allows. iPhone
   Notes images are exempt and should not be blog thumbnails.
11. **Every article has a thin atmospheric scene.** It is a wide mood image from
   `refs/scenes/`, like the bicycle example: atmosphere around the topic, not a
   junk-journal mockup, not product proof. Listing articles also need palette
   images from real showpiece listing pages, real-page carousels, and separate
   process/mockup visuals as defined in `ARTICLE_FUNCTION.md`.
12. **AI disclosure + affiliates.** Every article includes a quiet AI image
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
