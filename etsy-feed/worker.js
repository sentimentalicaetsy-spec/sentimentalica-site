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
const DEFAULT_LIMIT = 8;
const MAX_LIMIT = 12;

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
    let limit = parseInt(url.searchParams.get('limit') || DEFAULT_LIMIT, 10);
    if (!Number.isFinite(limit) || limit < 1) limit = DEFAULT_LIMIT;
    if (limit > MAX_LIMIT) limit = MAX_LIMIT;

    // Edge cache keyed by the limit so different sizes don't collide.
    const cacheKey = new Request(`https://etsy-feed.cache/listings?v=2&limit=${limit}`, request);
    const cache = caches.default;
    const cached = await cache.match(cacheKey);
    if (cached) return withCors(cached);

    try {
      const data = await fetchListings(env, limit);
      const res = json(data, 200, {
        'Cache-Control': `public, max-age=${CACHE_SECONDS}`,
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

  // 2. Primary image per listing. Etsy rate-limits bursts, so fetch
  // sequentially with a small retry — the result is cached for hours.
  const listings = [];
  for (const l of results) {
    const image = await fetchPrimaryImage(l.listing_id, l.title, headers);
    const p = l.price || {};
    const amount = p.amount != null && p.divisor ? p.amount / p.divisor : null;
    listings.push({
      id: l.listing_id,
      title: l.title,
      url: l.url,
      price: amount != null ? amount.toFixed(2) : null,
      currency: p.currency_code || 'USD',
      image,
    });
  }

  return { updated: new Date().toISOString(), count: listings.length, listings };
}

async function fetchPrimaryImage(listingId, title, headers, attempts = 3) {
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
        await sleep(250 * (i + 1)); // back off and retry
        continue;
      }
      return null; // other error — give up on this one
    } catch (_) {
      await sleep(200 * (i + 1));
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
