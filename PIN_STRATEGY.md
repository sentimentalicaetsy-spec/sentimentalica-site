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
  backgrounds, desks, journals, mockups, textures, lighting, hands, rooms,
  frames, styled scenes, but must NOT replace the product images.
- Insert real listing images INTO any generated mockup.
- Readable on mobile; high contrast for text-heavy pins; big bold hook (small
  tasteful text gets scrolled past — the goal is the CLICK).
- Do NOT repeat the same hook across pins; match every pin to the listing's
  aesthetic; some pins look like useful content, some like direct product previews.
- Composition building blocks (from validated mockups): "chaos scatter"
  (→ Variety/Problem), "bold hero + band" (→ Aesthetic/Theme), "big-number/
  question" (→ Stuck/Idea/Transformation). See `refs/mockups/`.

## Marketing rule (final gate, enforced by QA)
Each pin must solve one problem, trigger one desire, or offer one useful idea.
"Pretty images" / "150 images" alone = reject and rewrite.
