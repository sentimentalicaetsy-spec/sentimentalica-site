# Free gift funnel — how it works (LIVE since 2026-07-27)

The freebie page is connected end to end. Nothing is left to set up; this file
is now the operating manual. **All free — no paid services.**

## What happens on each signup

1. Visitor enters an email on <https://sentimentalica.com/freebie> and clicks
   **Claim my free pack**. The reveal starts immediately — the 8 taped pictures
   flip over and a present appears.
2. The email is saved to a **private Google Sheet** in Drive (only Ksenia can
   see it). A repeat signup does **not** add a row — it increments that row's
   `times` counter.
3. The backend replies with the gift-folder link; clicking the present opens it.
   The link is **not** in the page source, so the email is a real gate.
4. Ksenia gets a **Telegram message**: who signed up + total list size (new
   signups only, so duplicates don't spam the chat).

> **We never email users.** (Rule 0 in `AGENTS.md`, decided 2026-07-27.) Sent
> links land in spam, and `sentimentalica.etsy@gmail.com` is used for other
> things. The script requests **no mail permission at all** — never re-add
> `MailApp`/`GmailApp`, and never let page copy promise letters or an inbox.
> A domain mailbox may change this later; until Ksenia says so, the rule holds.

## The pieces

| Piece | Where |
|---|---|
| Landing page | `public/freebie.html` (`FORM_ENDPOINT` = the `/exec` URL) |
| Backend code (public-safe template) | `tools/gift_apps_script.gs` |
| Backend code (real values, gitignored) | `~/sentimentalica-pipeline/config/gift_apps_script_FILLED.gs` |
| Live script | Apps Script project **Sentimentalica gift signup**, bound to the Sheet |
| Email list | private Sheet **Sentimentalica gift signups** (in `000_Free_Gift`) |
| The gift | Drive `000_Free_Gift / Sentimentalica Free Gift Pack` — 100 pictures, shared anyone-with-link **viewer** (view + download, no edit) |
| Telegram | reuses the pipeline bot (`~/sentimentalica-pipeline/config/config.yaml`) |

Links to the Sheet, the gift folder, and the script live in the Obsidian vault
note **Workflows / Free Gift Funnel** — not here, since this repo is public.

## Everyday tasks

- **Read the list** — open the Sheet. Columns: `email · signed up · source ·
  times`. Export CSV any time; importable into a mailing tool later.
- **Change the gift** — drop files into the Drive folder. The link never
  changes, nothing to redeploy.
- **Change the backend code** — edit the FILLED copy, then from its folder:
  `clasp push --force` and `clasp deploy --deploymentId <id> --description "…"`.
  Keep `tools/gift_apps_script.gs` (scrubbed) in sync. The `/exec` URL survives
  redeploys, so the site needs no change.
- **Spam bots** — a hidden honeypot field on the form; anything that fills it is
  silently dropped. Malformed emails are rejected both on the page and again in
  the backend.
