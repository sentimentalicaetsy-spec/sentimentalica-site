# Free gift signup — one-time setup

The freebie page (`public/freebie.html`) is wired and waiting. What happens on
each signup once you finish the steps below — **all free, no paid services**:

1. The visitor's email is saved to a **private Google Sheet in your Drive**
   (only you can see it — the list never touches this public repo).
2. They instantly receive a **gift email from your Gmail** with the link,
   plus an "open your gift right now" button on the page itself.
3. You get a **Telegram message**: who signed up + total list size.

Everything runs on a free Google Apps Script in your own Google account.
The code is ready in [`tools/gift_apps_script.gs`](tools/gift_apps_script.gs) —
you just paste it in. ~15 minutes total.

---

## Step 1 — The gift itself (✅ folder already created)

The shared folder already exists on Drive (created 2026-07-16 via the
pipeline's Drive OAuth, same structure as listing customer folders):
`000_Free_Gift / Sentimentalica Free Gift Pack` — the inner folder is shared
"anyone with link – viewer". The link is your `GIFT_LINK`; it's kept in the
Obsidian vault note **Workflows / Free Gift Funnel** (not here — this repo is
public and the link shouldn't be scrapeable without signing up).

All that's left: drop the freebie files into the inner folder (papers,
ephemera, the quick-start guide). Only ever put things there that you're
happy to give away — the outer `000_Free_Gift` folder stays private for
working files.

## Step 2 — The private email list + script (✅ Sheet created, just paste)

The private Sheet **Sentimentalica gift signups** already exists inside the
`000_Free_Gift` Drive folder (created 2026-07-16, header row prefilled,
not shared with anyone). Link in the Obsidian note **Free Gift Funnel**.

1. Open the Sheet → **Extensions → Apps Script**.
2. Delete the placeholder code and paste the whole contents of
   `~/sentimentalica-pipeline/config/gift_apps_script_FILLED.gs` — the gift
   link and Telegram credentials are already filled in (that file is
   gitignored; this repo only carries the scrubbed template in
   `tools/gift_apps_script.gs`).
3. Click the 💾 save icon. Nothing to edit.

## Step 3 — Telegram notifications (✅ nothing to do)

The pipeline's Telegram bot is reused — its token and chat id are already
baked into the FILLED script from Step 2. Gift signups arrive in the same
chat as pipeline alerts, prefixed with 🎁.

## Step 4 — Test it (1 min)

In the Apps Script editor, select the function **`testSetup`** in the toolbar
dropdown and click **Run**. The first run asks for permissions — approve them
(it needs Gmail-send + this Sheet + external requests for Telegram).
You should receive the gift email yourself and a Telegram ping.
This is your review buffer: check the email looks right before going live.

## Step 5 — Deploy and connect (3 min)

1. In the Apps Script editor: **Deploy → New deployment → Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**  ← required so the site form can post to it;
     the URL only accepts signups, it can't read your Sheet.
2. Copy the Web app URL (ends in `/exec`).
3. In `public/freebie.html`, paste it into `FORM_ENDPOINT` (near the bottom
   of the file), then commit + push.
4. Open https://sentimentalica.com/freebie.html, sign up with a second email
   address of yours, and confirm: row in the Sheet ✓ gift email ✓ Telegram ✓.

---

## Afterwards

- **Reading the list**: it's just the Google Sheet — sort, count, export CSV.
  Later you can import it into Kit/MailerLite if you outgrow this.
- **Changing the gift**: drop new files into the Drive folder — the link
  stays the same, nothing to redeploy.
- **Changing the email text**: edit `sendGiftEmail` in the Apps Script and
  save. Code changes need **Deploy → Manage deployments → ✏️ → New version**
  to go live (constants like `GIFT_LINK` too).
- **Quota**: consumer Gmail sends ~100 emails/day via Apps Script — plenty
  for a freebie list; if a viral pin ever exceeds it, signups still land in
  the Sheet and the on-page "open your gift" button still works.
- **Duplicates**: the script de-duplicates — a repeat signup re-sends the
  gift email but doesn't add a row or ping Telegram.
- **Spam bots**: the form has a hidden honeypot field; anything that fills
  it is silently dropped.
