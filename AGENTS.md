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
  - `refs/` — **Ksenia's reference images (GROUND TRUTH)**: `scenes/`, `infographics/`, `50things/`.
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
2. **References are FILES, not words.** Judge every image against `refs/scenes/` and
   `refs/infographics/`. Empty folder = you are blind; ask Ksenia for references.
3. **Scenes must be save-worthy** — atmospheric escape (golden light, layered depth,
   mood), NOT bright sterile stock. "Nice" is not "save".
4. **Product-language accuracy is absolute** — commercial-use watercolor IMAGE packs.
   Never "clipart / stickers / ephemera kit / seamless patterns / templates" unless the
   listing truly includes them.
5. **On-theme only.** No cats/dogs (or any off-theme listing) shoved into unrelated
   articles. Pick listings that match the article's theme. No animal photo in a neutral article.
6. **Only LIVE listings** (`resolve_listing.py` checks Etsy). Etsy drafts only — never publish Etsy listings.
7. **Neutral/listicle article = pure value**; products at the END only; every image
   illustrates its adjacent paragraph. Listicle → full infographic in Ksenia's ref style.

## How to produce an article (the pipeline, in order)
1. Pick a topic from `content_plan.xlsx` (an unused row) or take Ksenia's request.
2. `resolve_listing.py` — confirm the listing is LIVE; get palette/thumbs.
3. Write the article (voice = approved articles; see `colorful-junk-journal-ideas…`).
4. Generate images (`insert_generated_images.py`) — scenes judged vs `refs/scenes/`.
5. **image-critic LOOKS at each image**, records verdict via `critic_gate.record(slug, slot, PASS|REGENERATE)`.
6. `publish_post.py --push` — BLOCKS if any image isn't PASS. Fix, re-record, retry.
7. Mark the `content_plan.xlsx` row used (status=published + date + slug).
8. pinterest-seo → pins → `pin_csv.py` (auto-mirrors CSV to Google Drive).

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
Inputs Ksenia owns: `refs/scenes/`, `refs/infographics/`, and the Desire Library
+ Seasonal Calendar sheets in `content_plan.xlsx`.

## Secrets
Never in git. Cloudflare worker secrets / GitHub Actions secrets only
(ETSY_API_KEY, ADMIN_PASSWORD, GITHUB_TOKEN, CLOUDFLARE_API_TOKEN). This repo is public.
