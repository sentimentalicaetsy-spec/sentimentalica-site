/**
 * Sentimentalica — Etsy live listings feed
 *
 * Fetches the latest active listings for the shop (server-side, so the API key
 * is never exposed to the browser), attaches the primary image of each, and
 * returns a small clean JSON payload with CORS enabled.
 *
 * Results are cached at the edge for CACHE_SECONDS so we never hammer Etsy and
 * the homepage loads instantly.
 *
 * Secrets / vars (set via `wrangler secret put` / wrangler.toml):
 *   ETSY_API_KEY  — "keystring:shared_secret" (the x-api-key header value)
 *   SHOP_ID       — numeric Etsy shop id (e.g. 17787065)
 */

const ETSY = 'https://openapi.etsy.com/v3/application';
const CACHE_SECONDS = 3 * 60 * 60; // 3 hours
const INCOMPLETE_CACHE_SECONDS = 60; // payload missing an image — retry soon
const DEFAULT_LIMIT = 8;
const MAX_LIMIT = 12;
const MAX_IDS = 6;        // max specific listings per ?ids= request
const MEDIA_CONCURRENCY = 2; // parallel image/video lookups (Etsy-rate-safe)

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }
    if (request.method !== 'GET') {
      return json({ error: 'Method not allowed' }, 405);
    }

    const url = new URL(request.url);

    // ?ids=123,456 — specific listings (used by blog post inline product
    // cards). Otherwise: newest ?limit=N listings (homepage grid).
    const idsParam = (url.searchParams.get('ids') || '')
      .split(',').map((s) => parseInt(s.trim(), 10))
      .filter((n) => Number.isFinite(n) && n > 0).slice(0, MAX_IDS);

    let limit = parseInt(url.searchParams.get('limit') || DEFAULT_LIMIT, 10);
    if (!Number.isFinite(limit) || limit < 1) limit = DEFAULT_LIMIT;
    if (limit > MAX_LIMIT) limit = MAX_LIMIT;

    // Edge cache keyed by the query shape so variants don't collide.
    const cacheSuffix = idsParam.length
      ? `ids=${idsParam.join(',')}` : `limit=${limit}`;
    const cacheKey = new Request(`https://etsy-feed.cache/listings?v=6&${cacheSuffix}`, request);
    const cache = caches.default;
    const cached = await cache.match(cacheKey);
    if (cached) return withCors(cached);

    try {
      const data = idsParam.length
        ? await fetchListingsByIds(env, idsParam)
        : await fetchListings(env, limit);
      // If any listing is missing its image, cache briefly so the blank card
      // self-heals on the next fetch instead of sticking around for hours.
      const complete = (data.listings || []).every((l) => l.image && l.image.src);
      const maxAge = complete ? CACHE_SECONDS : INCOMPLETE_CACHE_SECONDS;
      const res = json(data, 200, {
        'Cache-Control': `public, max-age=${maxAge}`,
      });
      ctx.waitUntil(cache.put(cacheKey, res.clone()));
      return res;
    } catch (err) {
      return json({ error: 'Could not load listings', detail: String(err) }, 502);
    }
  },
};

async function fetchListings(env, limit) {
  const key = env.ETSY_API_KEY;
  const shopId = env.SHOP_ID;
  if (!key || !shopId) throw new Error('Missing ETSY_API_KEY or SHOP_ID');

  const headers = { 'x-api-key': key };

  // 1. Newest active listings.
  const listRes = await fetch(
    `${ETSY}/shops/${shopId}/listings/active?limit=${limit}&sort_on=created&sort_order=desc`,
    { headers }
  );
  if (!listRes.ok) throw new Error(`listings ${listRes.status}`);
  const listJson = await listRes.json();
  const results = listJson.results || [];

  const listings = await attachMedia(results, headers);
  return { updated: new Date().toISOString(), count: listings.length, listings };
}

async function fetchListingsByIds(env, ids) {
  const key = env.ETSY_API_KEY;
  if (!key) throw new Error('Missing ETSY_API_KEY');
  const headers = { 'x-api-key': key };

  // Batch endpoint: one call for all requested listings.
  const res = await fetch(
    `${ETSY}/listings/batch?listing_ids=${ids.join(',')}`,
    { headers }
  );
  if (!res.ok) throw new Error(`batch ${res.status}`);
  const data = await res.json();
  // Preserve the order the caller asked for (post layout order).
  const byId = new Map((data.results || []).map((l) => [l.listing_id, l]));
  const ordered = ids.map((id) => byId.get(id)).filter(Boolean)
    .filter((l) => l.state === 'active');

  const listings = await attachMedia(ordered, headers);
  return { updated: new Date().toISOString(), count: listings.length, listings };
}

// Attach primary image + video to each listing, MEDIA_CONCURRENCY at a time
// (Etsy rate-limits bursts; results are edge-cached for hours anyway).
async function attachMedia(results, headers) {
  const out = new Array(results.length);
  let next = 0;
  async function workerLoop() {
    while (next < results.length) {
      const i = next++;
      const l = results[i];
      const [image, video] = await Promise.all([
        fetchPrimaryImage(l.listing_id, l.title, headers),
        fetchPrimaryVideo(l.listing_id, headers),
      ]);
      const p = l.price || {};
      const amount = p.amount != null && p.divisor ? p.amount / p.divisor : null;
      // If the image lookup failed but the video has a poster, use the poster
      // so the card never renders blank.
      const safeImage = image || (video && video.poster
        ? { src: video.poster, srcLarge: video.poster, alt: l.title }
        : null);
      out[i] = {
        id: l.listing_id,
        title: l.title,
        url: l.url,
        price: amount != null ? amount.toFixed(2) : null,
        currency: p.currency_code || 'USD',
        image: safeImage,
        video,
      };
    }
  }
  await Promise.all(
    Array.from({ length: Math.min(MEDIA_CONCURRENCY, results.length) }, workerLoop)
  );
  // Rescue pass: a listing with neither image nor video almost certainly hit
  // Etsy's rate limit (real listings always have at least one photo). Refetch
  // those one at a time after letting the rate-limit window recover.
  for (let i = 0; i < out.length; i++) {
    if (out[i].image || out[i].video) continue;
    await sleep(1000);
    const l = results[i];
    const [image, video] = await Promise.all([
      fetchPrimaryImage(l.listing_id, l.title, headers),
      fetchPrimaryVideo(l.listing_id, headers),
    ]);
    out[i].image = image || (video && video.poster
      ? { src: video.poster, srcLarge: video.poster, alt: l.title }
      : null);
    out[i].video = video;
  }
  return out;
}

async function fetchPrimaryImage(listingId, title, headers, attempts = 4) {
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(`${ETSY}/listings/${listingId}/images`, { headers });
      if (res.ok) {
        const data = await res.json();
        const first = (data.results || [])[0];
        if (first) {
          return {
            src: first.url_570xN,
            srcLarge: first.url_fullxfull,
            alt: first.alt_text || title,
          };
        }
        return null; // listing genuinely has no image
      }
      if (res.status === 429 || res.status >= 500) {
        await sleep(500 * (i + 1)); // back off and retry
        continue;
      }
      return null; // other error — give up on this one
    } catch (_) {
      await sleep(400 * (i + 1));
    }
  }
  return null;
}

async function fetchPrimaryVideo(listingId, headers, attempts = 4) {
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(`${ETSY}/listings/${listingId}/videos`, { headers });
      if (res.ok) {
        const data = await res.json();
        const v = (data.results || []).find((x) => x.video_state === 'active') || (data.results || [])[0];
        return v && v.video_url ? { src: v.video_url, poster: v.thumbnail_url || null } : null;
      }
      if (res.status === 429 || res.status >= 500) {
        await sleep(500 * (i + 1));
        continue;
      }
      return null;
    } catch (_) {
      await sleep(400 * (i + 1));
    }
  }
  return null;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function json(obj, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS, ...extraHeaders },
  });
}

function withCors(res) {
  const r = new Response(res.body, res);
  for (const [k, v] of Object.entries(CORS)) r.headers.set(k, v);
  return r;
}
