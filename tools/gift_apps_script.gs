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
 * On each signup from public/freebie.html:
 *   1. the email is written to the Sheet — a repeat signup increments that
 *      row's `times` counter instead of adding a duplicate
 *   2. the gift-folder link is returned so the page can open the present
 *   3. Telegram gets a message (with a link to the list)
 *
 * FLOOD HANDLING (2026-07-27). The endpoint must be public, so anyone can
 * POST to it. Three rules keep that from hurting:
 *   • Nothing is ever discarded. Above SPIKE_PER_HOUR new signups in a rolling
 *     hour, rows go to the `review` tab instead of the main list — so a viral
 *     pin never loses a real subscriber, and the main list stays clean.
 *   • The phone stays quiet: during a spike Telegram gets ONE alert, then at
 *     most one digest per hour, instead of a buzz per signup.
 *   • The visitor ALWAYS gets the gift, in every branch, whatever else fails.
 * This contains and quiets abuse; it does not prevent it. A sustained flood
 * can still exhaust the daily Apps Script runtime quota and take the funnel
 * offline until midnight. Fixing that needs Turnstile or a Cloudflare Worker
 * in front — deliberately not built yet (no abuse has happened).
 *
 * Fill in the constants below IN THE APPS SCRIPT EDITOR (not here — real
 * values must not be committed to the public repo).
 */

const GIFT_LINK = 'PASTE_YOUR_GOOGLE_DRIVE_FOLDER_LINK_HERE';
// From @BotFather / your chat id. Leave both '' to skip Telegram notifications.
const TELEGRAM_BOT_TOKEN = '';
const TELEGRAM_CHAT_ID = '';

// More than this many NEW signups in a rolling hour looks like a flood, not a
// good day. Ksenia's normal traffic is a handful a day, and a genuinely viral
// pin still loses nothing — overflow only moves to the `review` tab.
const SPIKE_PER_HOUR = 25;
// Back to normal once the rolling hour drops to this (hysteresis, so traffic
// hovering at the threshold doesn't flap in and out of spike mode).
const CALM_PER_HOUR = 10;
const REVIEW_TAB = 'review';
const HOUR_MS = 3600000;

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
    if (p.website) return respond({ ok: true, link: GIFT_LINK });

    const email = String(p.email || '').trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return respond({ ok: false, error: 'bad email' });
    }

    // Everything below is best-effort: a bookkeeping failure must never cost
    // the visitor their present.
    try {
      record(email, String(p.source || 'freebie page'));
    } catch (err) {
      console.error('signup bookkeeping failed: ' + err);
    }

    // The reply is deliberately IDENTICAL in every case: any per-email detail
    // (e.g. an `already` flag) would let anyone probe whether a given address
    // is on the list. Never add per-email detail to this response.
    return respond({ ok: true, link: GIFT_LINK });
  } finally {
    lock.releaseLock();
  }
}

/** Write the signup, choosing the main list or the `review` tab. */
function record(email, source) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const main = ss.getSheets()[0];
  if (main.getLastRow() === 0) main.appendRow(HEADER);

  // A returning email just bumps its counter — wherever it already lives.
  if (bumpExisting(main, email) || bumpExisting(ss.getSheetByName(REVIEW_TAB), email)) return;

  const props = PropertiesService.getScriptProperties();
  const now = Date.now();
  const hits = JSON.parse(props.getProperty('hits') || '[]')
    .filter((t) => now - t < HOUR_MS);
  hits.push(now);
  props.setProperty('hits', JSON.stringify(hits));

  const wasSpiking = props.getProperty('spike') === '1';
  const spiking = wasSpiking ? hits.length > CALM_PER_HOUR : hits.length > SPIKE_PER_HOUR;

  if (spiking) {
    if (!wasSpiking) {
      props.setProperty('spike', '1');
      props.setProperty('digestFrom', String(now));
      props.setProperty('pending', '0');
      tg('⚠️ Unusual signup rate: ' + hits.length + ' in the last hour.' +
         '\nNew signups now go to the "' + REVIEW_TAB + '" tab so your list stays clean.' +
         '\nNothing is discarded, and visitors still get the gift.' +
         '\n\n📄 ' + ss.getUrl());
    }
    appendTo(getReviewSheet(ss), email, source);
    queueDigest(props, ss);
    return;
  }

  if (wasSpiking) {
    props.setProperty('spike', '');
    flushDigest(props, ss); // report whatever is still pending
    tg('✅ Signup rate back to normal (' + hits.length + ' in the last hour).' +
       '\nNew signups go to the main list again.' +
       '\nWorth a look at the "' + REVIEW_TAB + '" tab.' +
       '\n\n📄 ' + ss.getUrl());
  }

  appendTo(main, email, source);
  tg('🎁 New gift signup: ' + email +
     '\nTotal on the list: ' + Math.max(0, main.getLastRow() - 1) +
     '\n\n📄 Open the list: ' + ss.getUrl());
}

const HEADER = ['email', 'signed up', 'source', 'times'];

function appendTo(sheet, email, source) {
  sheet.appendRow([email, new Date(), source, 1]);
}

/** If the email is already in this sheet, increment its `times`. */
function bumpExisting(sheet, email) {
  if (!sheet || sheet.getLastRow() < 2) return false;
  const col = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues().flat().map(String);
  const at = col.indexOf(email);
  if (at === -1) return false;
  const cell = sheet.getRange(at + 2, 4);
  cell.setValue((Number(cell.getValue()) || 1) + 1);
  return true;
}

function getReviewSheet(ss) {
  let sheet = ss.getSheetByName(REVIEW_TAB);
  if (!sheet) {
    sheet = ss.insertSheet(REVIEW_TAB);
    sheet.appendRow(HEADER);
  }
  return sheet;
}

/** During a spike: count signups, and report at most once an hour. */
function queueDigest(props, ss) {
  props.setProperty('pending', String((Number(props.getProperty('pending')) || 0) + 1));
  const from = Number(props.getProperty('digestFrom')) || 0;
  if (Date.now() - from >= HOUR_MS) flushDigest(props, ss);
}

function flushDigest(props, ss) {
  const pending = Number(props.getProperty('pending')) || 0;
  props.setProperty('pending', '0');
  props.setProperty('digestFrom', String(Date.now()));
  if (pending > 0) {
    tg('📬 +' + pending + ' signups in the last hour (in the "' + REVIEW_TAB + '" tab).' +
       '\n\n📄 ' + ss.getUrl());
  }
}

/** Telegram, fire and forget — a hiccup here must never break a signup. */
function tg(text) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;
  try {
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
    console.error('telegram failed: ' + err);
  }
}

/**
 * Run once from the Apps Script editor (Run ▸ testSetup) to trigger the
 * permission-consent screen and check Telegram. Sends NO user email.
 */
function testSetup() {
  tg('🔔 Sentimentalica gift signup: test ping.' +
     '\n\n📄 ' + SpreadsheetApp.getActiveSpreadsheet().getUrl());
  Logger.log('Telegram test sent. Gift link: ' + GIFT_LINK);
}

/** Clears spike mode by hand, if it ever gets stuck. */
function resetSpikeState() {
  PropertiesService.getScriptProperties()
    .setProperties({ hits: '[]', spike: '', pending: '0', digestFrom: '0' });
  Logger.log('Spike state cleared.');
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
