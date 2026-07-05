# Sentimentalica Vault — membership spec (draft, 2026-07-06)

> Ksenia's decisions + open questions. Viewer-facing /vault.html stays a
> placeholder until launch; all work-in-progress is admin-only.

## Product
**Sentimentalica Printables Vault** — subscription: monthly access to curated
printable papers, journaling pages, collage sheets, card fronts, seasonal drops.

Tier draft (from Ksenia's research, to validate):
- $9/mo — monthly mini drop
- $19/mo — full monthly bundle
- $29/mo — commercial-use tier
- $99/yr — annual access

## Infrastructure recommendation (Claude, for discussion)
**Hybrid: own everything EXCEPT the payment/checkout layer.**
- Payments via a **Merchant-of-Record** (they are legally the seller → they
  handle EU VAT per-country, invoices, chargebacks). For a solo EU studio,
  self-hosted payments = OSS VAT registration + per-country rates + invoicing
  burden. Not worth it until revenue proves out.
  - **Payhip — recommended start**: 5% fee on free plan, memberships+digital
    delivery, MoR, simple. Lemon Squeezy (5%+50¢, best API) = alternative.
  - Rejected for start: Gumroad (10%+50¢ — expensive), Ko-fi (weak
    membership/file UX), Shopify ($29/mo AND you handle VAT yourself).
- **Owned:** content storage (Drive now, Cloudflare R2 later), the site
  (vault.html → member landing), email (Kit), weekly-drop automation
  (pipeline agent). If the Vault grows, migrate checkout to own Stripe+OSS
  later — nothing in this design locks us in.

## Weekly drop mechanism (automated, agent-run)
**Curated, NOT random, never repeating:**
1. `vault_drop.py` (pipeline repo): each week picks **5 themes** round-robin
   across all listed themes (~85+ → a theme returns ~every 17 weeks).
2. From each theme's customer folder: **top-10 not-yet-used images ranked by
   the CLIP aesthetic scorer** (`image_curation.py` — already built). No
   randomness: best unused first. QA'd images only.
3. Manifest `data/vault_used.json` records every shipped image — repeats are
   impossible by construction (resumable-manifest pattern like qa harvest).
4. Output folders (Drive): `Vault/<year>-W<week>/1_<Theme>/ … 5_<Theme>/`
   (10 images each = 50/week), view-only share link per week.
5. **Email:** weekly Kit broadcast with the week's link — drafted by the
   agent, Ksenia approves before send (review-buffer principle). Automate the
   send via Kit API once trusted. Scheduled via /schedule weekly cron.

## Open questions (Ksenia)
1. Payment layer: Payhip (recommended) / Lemon Squeezy / straight to own Stripe?
2. Delivery v1 = Drive share links per week — ok, or R2/zip from day one?
3. Do tiers differ by CONTENT (mini vs full) or only by license (commercial)?
   Affects how many folders the drop script produces per week.
4. Commercial tier license wording — needed before selling that tier.
