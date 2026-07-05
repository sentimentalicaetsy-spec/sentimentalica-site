# Sentimentalica — Website Project Reference

Last updated: 2026-07-05

## What this is
Marketing website + blog for the Etsy shop **Sentimentalica** (digital junk-journal /
art-journal / scrapbook printables). Strategy: Pinterest → website → Etsy shop.
The site is a conversion landing page that shows the shop's newest listings live and
drives clicks to Etsy, plus a blog ("Journal") and an email freebie opt-in.

- **Live site:** https://sentimentalica.com
- **Etsy shop:** https://www.etsy.com/shop/Sentimentalica

## Repositories (GitHub org: sentimentalicaetsy-spec)
- **Website:** `sentimentalicaetsy-spec/sentimentalica-site` — branch `main`
  - Clone (SSH): `git clone git@github.com:sentimentalicaetsy-spec/sentimentalica-site.git`
- **Listing pipeline (separate project, not the website):** `sentimentalicaetsy-spec/sentimentalica`
  - Local copy: `/Users/kseniateter/sentimentalica-pipeline`

## Hosting & deploy
- **Cloudflare Workers (static assets).** Auto-deploys on every push to `main` via
  GitHub Actions (`.github/workflows/deploy.yml`). Just commit + push to publish.
- Static-site worker name (in `wrangler.toml`): `sparkling-recipe-a8ee`, assets dir `./public`.
- **Cloudflare account:** Teter.album@gmail.com — account_id `f8ad0de6193a285dec8719ac848a991c`

## Repo layout
```
public/
  index.html          Homepage: live "Newest in the shop" grid + hero + journal teaser
  about.html          "About the Studio" + (autoplay) process video
  freebie.html        Free-gift email opt-in (lead magnet) page
  blog.html           All blog posts
  blog/index.json     Blog post metadata index (drives blog.html + homepage teaser)
  blog/*.html         Individual post pages (generated on publish by admin)
  admin/index.html    Password-protected Quill.js writing interface
  assets/styles.css   Main site styles (shared by all pages)
  assets/post.css     Blog post styles
  assets/logo.png, favicon.png, about-process.mp4
etsy-feed/            Cloudflare Worker SOURCE for the live listings feed (deployed separately)
wrangler.toml         Static-site worker config
```

## Cloudflare Workers (3 of them)
1. **`sparkling-recipe-a8ee`** — serves the static site (this repo, auto-deploy).
2. **`sentimentalica-etsy-feed`** — returns the newest Etsy listings as JSON for the
   homepage grid. URL: https://sentimentalica-etsy-feed.teter-album.workers.dev/?limit=8
   - Source: `etsy-feed/worker.js` + `etsy-feed/wrangler.toml` in this repo.
   - Deploy: `cd etsy-feed && CLOUDFLARE_API_TOKEN=<token> wrangler deploy`
   - Caches results ~3h at the edge; cache-key has a `v=N` version — bump it to force refresh.
   - Fetches active listings + each listing's primary image + video (sequential w/ retry).
3. **`sentimentalica-admin-api`** — handles publish/drafts for the admin panel via the
   GitHub API. URL: https://sentimentalica-admin-api.teter-album.workers.dev
   - IMPORTANT: this worker's source is **not in any repo** — it lives only on Cloudflare.
     Edit it in the Cloudflare dashboard or via `wrangler` from a local copy.

## Etsy integration
- Shop name: **Sentimentalica**, **shop_id `17787065`** (~66 active listings).
- Etsy Open API v3, public/read-only (no OAuth needed for active listings).
- **Gotcha:** the `x-api-key` header must be `KEYSTRING:SHARED_SECRET` (both, colon-separated).
  Keystring alone returns "Shared secret is required."
- Endpoints used:
  - `GET /v3/application/shops/{shop_id}/listings/active?sort_on=created&sort_order=desc`
  - `GET /v3/application/listings/{id}/images`
  - `GET /v3/application/listings/{id}/videos`
- The API key is stored as the Worker secret **`ETSY_API_KEY`** on `sentimentalica-etsy-feed`
  (not in git).

## Homepage behavior
- "Newest in the shop" grid loads the 8 newest listings from the etsy-feed worker
  (`fetch(..., {cache:'no-store'})` so new data/fields show without waiting on browser cache).
- Product cards: image, title, NO price (price is shown on Etsy). Hover on desktop
  crossfades to the listing's muted looping video. Each card links straight to the Etsy listing.
- Order: header → shop grid → compact hero + CTA → journal teaser → final Etsy CTA → footer.

## Design system (assets/styles.css :root)
- Colors: --navy #163087, --navy-deep #0f2466, --cream #faf3e6, --cream-warm #f0e4cd,
  --paper #f7ecd6, --ink #2a2a3a, --muted #7a6f5e, --line #c9b896, --accent #b8956a,
  --rose #c47b7b, --pale-blue #e6ecf7
- Fonts: Cormorant Garamond (headings), Lora (body). One mobile breakpoint at max-width:900px.
- Nav appears on every page (root pages use bare paths e.g. `blog.html`; posts in /blog/ use `../`).

## Blog publishing — TWO paths (since 2026-07-05)
1. **Scripted/agent path (preferred):** `python3 tools/publish_post.py <post.md> --push`
   — Markdown with front matter → full post page (canonical/OG/JSON-LD, post.css,
   post.js), local images copied to `public/blog/img/<slug>/`, index.json + sitemap.xml
   updated, commit+push auto-deploys. Supports `{{etsy:ID1,ID2}}` shortcodes →
   **inline live product cards** (same look/hover-video as the homepage grid).
2. **Admin panel (manual):** unchanged Quill flow via `sentimentalica-admin-api`.
   ⚠️ Its post template lives in that worker (source NOT in repo) — admin-published
   posts don't load `post.js`, so `{{etsy}}` embeds don't work there. Images from the
   admin embed as base64 (page bloat). Prefer path 1 for anything rich.

### Inline product cards (any post page)
`<div class="etsy-products" data-ids="123,456" aria-busy="true"></div>` — hydrated by
`assets/post.js` via the feed worker's new `?ids=` param (max 6 IDs, edge-cached 3h,
sold-out/delisted listings silently drop out). All three legacy posts now load post.js
too, so embeds can be added to them directly.

### etsy-feed worker v4 (2026-07-05)
- `?ids=1,2,3` — specific listings via Etsy batch endpoint, order preserved,
  inactive filtered.
- Image/video lookups now parallel (4 at a time) — cold-cache response ~4× faster.
- **Auto-deploys from CI** (`deploy-etsy-feed` job in deploy.yml) — no manual
  `wrangler deploy` needed anymore.

### SEO (2026-07-05)
`robots.txt` (+admin disallow) & `sitemap.xml` (regenerated by publish_post.py);
all posts have canonical/OG; scripted posts also get JSON-LD BlogPosting.
Legacy posts had a committed Cloudflare-challenge `<script>` — removed.

## Status / open items (as of 2026-06-15)
- **Header banner:** currently a clean pale-blue bar. A custom banner PNG is planned
  (2400×600, transparent, artwork only — torn-paper collage; text added in code). Drop it in
  as the `.site-nav` background and overlay the wordmark/menu.
- **About page video:** `about.html` is set up to autoplay `assets/about-process.mp4`
  (autoplay, muted, loop, playsinline). Add the mp4 file to `public/assets/` and commit.
- **Freebie email:** `freebie.html` opt-in form is built but not yet connected. Set the
  `FORM_ENDPOINT` constant in `freebie.html` to the chosen email tool's form action
  (Kit/ConvertKit recommended, or MailerLite) which auto-delivers the freebie on confirm.
- **Next planned:** block-based blog template (reusable sections + inline live product cards).

## Secrets (KEEP PRIVATE — values are NOT in this file)
Look them up in Ksenia's password manager / Cloudflare; never commit them:
- **GitHub token** (repo + workflow + secrets scopes) — for pushing / admin-api.
- **Cloudflare API token** (`cfut_...`) — for `wrangler deploy` of the workers.
- **Etsy API keystring + shared secret** — stored as Worker secret `ETSY_API_KEY`.
- **Admin panel password** — Cloudflare Worker secret on `sentimentalica-admin-api`.

## How to make a change
1. `git clone git@github.com:sentimentalicaetsy-spec/sentimentalica-site.git`
2. Edit files under `public/`.
3. `git commit` + `git push origin main` → GitHub Actions auto-deploys to sentimentalica.com.
4. For worker changes (etsy-feed): edit `etsy-feed/`, then
   `cd etsy-feed && CLOUDFLARE_API_TOKEN=<token> wrangler deploy`.
5. Verify live: `curl -s "https://sentimentalica.com/?cb=$RANDOM" | grep ...`
