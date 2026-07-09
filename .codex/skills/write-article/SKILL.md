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
   or none, funnel stage. It MAY return tie=none (pure lead magnet) — that's fine.
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
scenes judged vs refs/scenes/ by the **image-critic**, then the **critic code-gate**
in publish_post.py (publish is blocked without every image PASS). Then
`plan_io.mark_published(slug)`.
Lead-magnet/neutral rows: pure value, product at the END only, every image
illustrates its adjacent paragraph. On-theme listings only — never off-theme animals.

## 6. Pins → CSV (MANDATORY finale of every article — do not skip)
After each article is live, invoke the **pinterest-seo** agent on it: it writes
title/description/keywords/board/drip-date rows via `tools/pin_csv.py add ...`
for every image worth pinning (mockups, palette, hero scenes, strong pages),
mixing content pins (→ article) and product pins (→ Etsy listing). The CSV
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
- Продукт едет следом, не впереди. product-bridge вправе сказать «никак».
- image-critic смотрит ВСЁ визуальное; критик-гейт в коде блокирует публикацию.
- Промпты сцен — по SCENE_STYLE.md и refs/scenes/ (файлы, не слова).
- Один вызов может дать несколько статей (batch) — делай их последовательно.
- Product-language accuracy АБСОЛЮТНА; только ЖИВЫЕ листинги.
- Если Desire Library пуста — воронка всё равно работает на широких безопасных
  территориях; предупреди Ксению, что идеи будут точнее, когда она её наполнит.
