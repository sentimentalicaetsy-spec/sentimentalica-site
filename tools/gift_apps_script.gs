/**
 * Sentimentalica — free gift signup backend (Google Apps Script).
 *
 * This file is a TEMPLATE kept in the repo for reference. The live copy runs
 * inside Ksenia's Google account, bound to a PRIVATE Google Sheet (the email
 * list must never live in this repo — the repo is public). See GIFT_SETUP.md
 * for the one-time setup steps.
 *
 * What it does on each signup from public/freebie.html:
 *   1. appends the email + timestamp to the Sheet (private, in Google Drive)
 *   2. emails the person the gift link (sent from the Gmail account that owns
 *      the script — free, ~100 recipients/day quota on consumer Gmail)
 *   3. sends a Telegram message: who signed up + total list size
 *
 * Fill in the constants below IN THE APPS SCRIPT EDITOR (not here — real
 * values must not be committed to the public repo).
 */

const GIFT_LINK = 'PASTE_YOUR_GOOGLE_DRIVE_FOLDER_LINK_HERE';
const GIFT_NAME = 'your free vintage paper pack';
const FROM_NAME = 'Ksenia from Sentimentalica';
// Optional: a "Send mail as" alias already configured in Gmail settings,
// e.g. 'hello@sentimentalica.com'. Leave '' to send from the Gmail address.
const FROM_ALIAS = '';
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
    if (sheet.getLastRow() === 0) sheet.appendRow(['email', 'signed up', 'source']);
    const existing = sheet.getLastRow() > 1
      ? sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues().flat().map(String)
      : [];
    const already = existing.indexOf(email) !== -1;
    if (!already) sheet.appendRow([email, new Date(), String(p.source || 'freebie page')]);

    sendGiftEmail(email);
    if (!already) notifyTelegram(email, existing.length + 1);

    // `link` lets the page show an instant "open your gift" button too,
    // so a spam-foldered email doesn't lose the visitor.
    return respond({ ok: true, already: already, link: GIFT_LINK });
  } finally {
    lock.releaseLock();
  }
}

function sendGiftEmail(to) {
  const subject = 'Your free gift from Sentimentalica 🎁';
  const htmlBody =
    '<div style="background:#faf3e6;padding:32px 16px;font-family:Georgia,serif;color:#2a2a3a">' +
    '<div style="max-width:520px;margin:0 auto;background:#fffdf8;border:1px solid #c9b896;border-radius:6px;padding:36px 32px;text-align:center">' +
    '<div style="font-size:22px;letter-spacing:.04em;color:#163087;margin-bottom:6px">Sentimentalica</div>' +
    '<div style="font-size:12px;color:#7a6f5e;letter-spacing:.08em;margin-bottom:26px">- a little gift for you -</div>' +
    '<p style="font-size:16px;line-height:1.6;margin:0 0 10px">Thank you for joining the Sentimentalica letter.</p>' +
    '<p style="font-size:16px;line-height:1.6;margin:0 0 26px">Here is ' + GIFT_NAME + ' - yours to keep, print, and cut into your next junk journal spread.</p>' +
    '<a href="' + GIFT_LINK + '" style="display:inline-block;background:#163087;color:#faf3e6;text-decoration:none;padding:13px 30px;border-radius:4px;font-size:15px;letter-spacing:.03em">Open your free pack &rarr;</a>' +
    '<p style="font-size:12px;color:#7a6f5e;line-height:1.6;margin:28px 0 0">If the button does not work, copy this link:<br>' +
    '<a href="' + GIFT_LINK + '" style="color:#163087">' + GIFT_LINK + '</a></p>' +
    '</div>' +
    '<p style="max-width:520px;margin:14px auto 0;font-size:11px;color:#7a6f5e;text-align:center;line-height:1.6">' +
    'You received this because you requested the free pack at sentimentalica.com.<br>' +
    'No more emails will come unless you hear from the letter - reply &ldquo;unsubscribe&rdquo; any time.</p>' +
    '</div>';
  const opts = { name: FROM_NAME, htmlBody: htmlBody };
  if (FROM_ALIAS) opts.from = FROM_ALIAS;
  GmailApp.sendEmail(to, subject,
    'Thank you for joining Sentimentalica! Your free pack: ' + GIFT_LINK, opts);
}

function notifyTelegram(email, total) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;
  try {
    UrlFetchApp.fetch('https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage', {
      method: 'post',
      payload: {
        chat_id: TELEGRAM_CHAT_ID,
        text: '🎁 New gift signup: ' + email + '\nTotal on the list: ' + total,
      },
      muteHttpExceptions: true,
    });
  } catch (err) {
    // Never let a Telegram hiccup break the signup itself.
  }
}

/**
 * Run this once from the Apps Script editor (Run ▸ testSetup) after filling
 * the constants: it sends the gift email to yourself and a Telegram ping,
 * and triggers the permission-consent screen on first run.
 */
function testSetup() {
  const me = Session.getActiveUser().getEmail();
  sendGiftEmail(me);
  notifyTelegram(me + ' (test)', 0);
  Logger.log('Test email sent to ' + me);
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
