/**
 * Sentimentalica — free gift signup backend (Google Apps Script).
 *
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │ RULE (Ksenia, 2026-07-27): we do NOT send emails to users. Not here, │
 * │ not anywhere. The gift is delivered on the page (the backend returns │
 * │ the folder link, the present opens it). Reasons: a sent link lands   │
 * │ in spam, and sentimentalica.etsy@gmail.com is used for other things. │
 * │ A proper domain mailbox comes later — until then this script asks    │
 * │ for NO mail permission at all. Do not re-add MailApp/GmailApp.       │
 * └──────────────────────────────────────────────────────────────────────┘
 *
 * This file is a TEMPLATE kept in the repo for reference. The live copy runs
 * inside Ksenia's Google account, bound to a PRIVATE Google Sheet (the email
 * list must never live in this repo — the repo is public). See GIFT_SETUP.md.
 *
 * What it does on each signup from public/freebie.html:
 *   1. appends the email + timestamp to the Sheet (private, in Google Drive)
 *      — a repeat signup increments that row's `times` counter, no duplicates
 *   2. returns the gift-folder link so the page can open the present
 *   3. sends a Telegram message: who signed up + total list size
 *
 * Fill in the constants below IN THE APPS SCRIPT EDITOR (not here — real
 * values must not be committed to the public repo).
 */

const GIFT_LINK = 'PASTE_YOUR_GOOGLE_DRIVE_FOLDER_LINK_HERE';
// From @BotFather / your chat id. Leave both '' to skip Telegram notifications.
const TELEGRAM_BOT_TOKEN = '';
const TELEGRAM_CHAT_ID = '';

function doGet() {
  // Lets you sanity-check the deployed URL in a browser.
  return respond({ ok: true, service: 'sentimentalica gift signup' });
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const p = (e && e.parameter) || {};
    // Honeypot field: humans never see it, bots fill it. Pretend success.
    if (p.website) return respond({ ok: true });

    const email = String(p.email || '').trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return respond({ ok: false, error: 'bad email' });
    }

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) sheet.appendRow(['email', 'signed up', 'source', 'times']);
    const existing = sheet.getLastRow() > 1
      ? sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues().flat().map(String)
      : [];
    const at = existing.indexOf(email);
    const already = at !== -1;
    if (already) {
      // No duplicate rows - just count how many times this email came back.
      const timesCell = sheet.getRange(at + 2, 4);
      timesCell.setValue((Number(timesCell.getValue()) || 1) + 1);
    } else {
      sheet.appendRow([email, new Date(), String(p.source || 'freebie page'), 1]);
      notifyTelegram(email, existing.length + 1,
        SpreadsheetApp.getActiveSpreadsheet().getUrl());
    }

    // `link` is how the gift is delivered: the page opens it as the present.
    // It is never in the page source, so the email really is the gate.
    return respond({ ok: true, already: already, link: GIFT_LINK });
  } finally {
    lock.releaseLock();
  }
}

// listUrl is read from the bound Sheet at call time, so the private list URL
// never has to be written into this (public) file.
function notifyTelegram(email, total, listUrl) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;
  try {
    const text = '🎁 New gift signup: ' + email +
      '\nTotal on the list: ' + total +
      (listUrl ? '\n\n📄 Open the list: ' + listUrl : '');
    UrlFetchApp.fetch('https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage', {
      method: 'post',
      payload: {
        chat_id: TELEGRAM_CHAT_ID,
        text: text,
        disable_web_page_preview: 'true', // keep the message compact
      },
      muteHttpExceptions: true,
    });
  } catch (err) {
    // Never let a Telegram hiccup break the signup itself.
  }
}

/**
 * Run once from the Apps Script editor (Run ▸ testSetup) to trigger the
 * permission-consent screen and check Telegram. Sends NO user email.
 */
function testSetup() {
  notifyTelegram('test@sentimentalica.com (test ping)', 0,
    SpreadsheetApp.getActiveSpreadsheet().getUrl());
  Logger.log('Telegram test sent. Gift link: ' + GIFT_LINK);
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
