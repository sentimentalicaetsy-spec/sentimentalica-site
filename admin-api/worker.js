/**
 * Sentimentalica — admin API worker (v2, source now lives IN the repo).
 *
 * Rebuilt 2026-07-05 to add editing of published posts + file-based image
 * uploads. Deployed over the same worker name, so existing Cloudflare secrets
 * persist. Reads secrets under several likely names (the original worker's
 * exact names are unknown — its source lived only on Cloudflare).
 *
 * Secrets:
 *   ADMIN_PASSWORD (or PASSWORD / ADMIN_PWD)   — admin panel password
 *   GITHUB_TOKEN   (or GH_TOKEN / TOKEN)       — repo+workflow token
 *
 * Endpoints (all POST, JSON body with {password}):
 *   /ping                       → {ok}
 *   /publish                    → writes public/blog/<slug>.html (v2 template,
 *                                 same as tools/publish_post.py: post.css,
 *                                 post.js, canonical/OG/JSON-LD), updates
 *                                 index.json + sitemap.xml. Overwrites an
 *                                 existing slug → THIS IS ALSO "EDIT".
 *   /get-post {slug}            → published post's title/excerpt/content for
 *                                 loading into the editor
 *   /upload-image {name,data}   → commits image to public/blog/img/uploads/,
 *                                 returns its URL (no more base64 in posts)
 *   /save-draft /get-draft /delete-draft /list-drafts
 *                               → drafts as JSON files under drafts/ in the
 *                                 repo (NOTE: repo is public — drafts are not
 *                                 secret; publish when it matters)
 */

const REPO = 'sentimentalicaetsy-spec/sentimentalica-site';
const API = 'https://api.github.com';
const SITE = 'https://sentimentalica.com';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const pwd = (env) => env.ADMIN_PASSWORD || env.PASSWORD || env.ADMIN_PWD;
const ghToken = (env) => env.GITHUB_TOKEN || env.GH_TOKEN || env.TOKEN;

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
    if (request.method !== 'POST') return json({ error: 'POST only' }, 405);

    const url = new URL(request.url);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'bad json' }, 400); }

    if (!pwd(env) || !ghToken(env)) {
      return json({ error: 'Worker secrets missing (ADMIN_PASSWORD / GITHUB_TOKEN) — re-add them in the Cloudflare dashboard.' }, 500);
    }
    if (body.password !== pwd(env)) return json({ ok: false, error: 'wrong password' }, 401);

    try {
      switch (url.pathname) {
        case '/ping': return json({ ok: true });
        case '/publish': return await publish(env, body);
        case '/get-post': return await getPost(env, body);
        case '/delete-post': return await deletePost(env, body);
        case '/upload-image': return await uploadImage(env, body);
        case '/save-draft': return await saveDraft(env, body);
        case '/get-draft': return await getDraft(env, body);
        case '/delete-draft': return await deleteDraft(env, body);
        case '/list-drafts': return await listDrafts(env);
        default: return json({ error: 'not found' }, 404);
      }
    } catch (e) {
      return json({ ok: false, error: String(e) }, 500);
    }
  },
};

/* ── GitHub helpers ─────────────────────────────────────────────────────── */

async function gh(env, method, path, payload) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${ghToken(env)}`,
      'User-Agent': 'sentimentalica-admin',
      Accept: 'application/vnd.github+json',
      ...(payload ? { 'Content-Type': 'application/json' } : {}),
    },
    body: payload ? JSON.stringify(payload) : undefined,
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`GitHub ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return res.json();
}

async function getFile(env, path) {
  return gh(env, 'GET', `/repos/${REPO}/contents/${path}`);
}

async function putFile(env, path, contentB64, message, sha) {
  return gh(env, 'PUT', `/repos/${REPO}/contents/${path}`, {
    message, content: contentB64, ...(sha ? { sha } : {}),
  });
}

const b64encode = (s) => btoa(unescape(encodeURIComponent(s)));
const b64decode = (s) => decodeURIComponent(escape(atob(s.replace(/\n/g, ''))));

/* ── Publish (create OR edit) ───────────────────────────────────────────── */

function makeSlug(t) {
  return t.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim()
    .replace(/\s+/g, '-').replace(/-+/g, '-').substring(0, 80);
}

function esc(s) {
  return String(s || '').replace(/[&<>"]/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function renderPage({ title, slug, excerpt, content, dateIso, thumbUrl }) {
  const canonical = `${SITE}/blog/${slug}.html`;
  const d = new Date(dateIso);
  const dDisplay = d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const words = content.replace(/<[^>]+>/g, ' ').split(/\s+/).filter(Boolean).length;
  const readMin = Math.max(1, Math.round(words / 220));
  const ogImage = thumbUrl || `${SITE}/assets/logo.png`;
  const ld = JSON.stringify({
    '@context': 'https://schema.org', '@type': 'BlogPosting',
    headline: title, datePublished: dateIso.slice(0, 10),
    description: excerpt || '', image: ogImage, url: canonical,
    author: { '@type': 'Organization', name: 'Sentimentalica' },
  });
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)} — Sentimentalica</title>
<meta name="description" content="${esc(excerpt)}">
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(excerpt)}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${esc(ogImage)}">
<link rel="icon" type="image/png" href="../assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/styles.css">
<link rel="stylesheet" href="../assets/post.css">
<script type="application/ld+json">${ld}</script>
</head>
<body>

<nav class="site-nav">
  <a href="../index.html" class="logo-link">
    <img src="../assets/logo.png" alt="Sentimentalica" class="logo-mark">
    <span class="logo-block">
      <span class="logo-text">Sentimentalica</span>
      <span class="logo-tagline">Junk Journal, Art Journal and Scrapbook Digital Papers</span>
    </span>
  </a>
  <ul>
    <li><a href="../index.html">Home</a></li>
    <li><a href="../blog.html">Journal</a></li>
    <li><a href="../vault.html">Vault</a></li>
    <li><a href="../about.html">About</a></li>
    <li><a href="https://pinterest.com/sentimentalica" target="_blank" rel="noopener">Pinterest</a></li>
    <li><a class="nav-shop" href="https://www.etsy.com/shop/sentimentalica" target="_blank" rel="noopener">Shop on Etsy</a></li>
  </ul>
</nav>

<article>
  <header class="post-hero">
    <div class="post-cat">Journal</div>
    <h1>${esc(title)}</h1>
    <div class="post-hero-meta">${dDisplay} · ${readMin} minute read</div>
  </header>
  <div class="post-body ql-content">
${content}
  </div>
</article>

<footer>
  <div>© ${d.getFullYear()} Sentimentalica</div>
  <div>
    <a href="https://www.etsy.com/shop/sentimentalica" target="_blank" rel="noopener">Etsy</a>
    <a href="https://pinterest.com/sentimentalica" target="_blank" rel="noopener">Pinterest</a>
    <a href="mailto:hello@sentimentalica.com">Contact</a>
  </div>
</footer>

<script src="../assets/post.js" defer></script>
</body>
</html>
`;
}

async function publish(env, body) {
  const title = (body.title || '').trim();
  if (!title) return json({ ok: false, error: 'title required' });
  const slug = (body.slug || makeSlug(title)).trim();
  const content = body.content || '';

  // Existing post? keep its date; else today.
  const idxFile = await getFile(env, 'public/blog/index.json');
  const idx = idxFile ? JSON.parse(b64decode(idxFile.content)) : { posts: [] };
  const existing = idx.posts.find((p) => p.slug === slug);
  const dateIso = (existing && existing.date ? existing.date : new Date().toISOString().slice(0, 10)) + 'T12:00:00Z';

  // Thumbnail: data-URI from the panel → commit as a file.
  let thumbUrl = existing ? existing.thumbAbs || null : null;
  let thumbRel = existing ? existing.thumb || null : null;
  if (body.thumbnail && body.thumbnail.data) {
    const m = body.thumbnail.data.match(/^data:image\/(\w+);base64,(.+)$/s);
    if (m) {
      const ext = m[1] === 'jpeg' ? 'jpg' : m[1];
      const path = `public/blog/img/${slug}/thumb.${ext}`;
      const prev = await getFile(env, path);
      await putFile(env, path, m[2], `thumb: ${slug}`, prev && prev.sha);
      thumbRel = `blog/img/${slug}/thumb.${ext}`;
      thumbUrl = `${SITE}/${thumbRel}`;
    }
  }

  const html = renderPage({ title, slug, excerpt: body.excerpt || '', content, dateIso, thumbUrl });
  const postPath = `public/blog/${slug}.html`;
  const prevPost = await getFile(env, postPath);
  await putFile(env, postPath, b64encode(html), `post: ${title}`, prevPost && prevPost.sha);

  // index.json
  const words = content.replace(/<[^>]+>/g, ' ').split(/\s+/).filter(Boolean).length;
  const d = new Date(dateIso);
  const entry = {
    slug, title, category: (existing && existing.category) || 'Journal',
    excerpt: body.excerpt || '',
    date: dateIso.slice(0, 10),
    dateDisplay: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    readTime: `${Math.max(1, Math.round(words / 220))} min read`,
    thumb: thumbRel, thumbAbs: thumbUrl,
  };
  idx.posts = idx.posts.filter((p) => p.slug !== slug);
  idx.posts.unshift(entry);
  idx.posts.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  await putFile(env, 'public/blog/index.json', b64encode(JSON.stringify(idx, null, 2) + '\n'),
    `index: ${slug}`, idxFile && idxFile.sha);

  // sitemap
  const pages = ['', 'blog.html', 'vault.html', 'about.html', 'freebie.html'];
  const urls = pages.map((p) => `${SITE}/${p}`).concat(idx.posts.map((p) => `${SITE}/blog/${p.slug}.html`));
  const sm = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${u}</loc></url>`).join('\n')}\n</urlset>\n`;
  const smFile = await getFile(env, 'public/sitemap.xml');
  await putFile(env, 'public/sitemap.xml', b64encode(sm), `sitemap: ${slug}`, smFile && smFile.sha);

  // delete the source draft if publishing from one
  if (body.draftSlug) {
    const df = await getFile(env, `drafts/${body.draftSlug}.json`);
    if (df) await gh(env, 'DELETE', `/repos/${REPO}/contents/drafts/${body.draftSlug}.json`,
      { message: `draft published: ${body.draftSlug}`, sha: df.sha });
  }

  return json({ ok: true, slug, edited: !!existing });
}

/* ── Get a published post for editing ───────────────────────────────────── */

async function getPost(env, body) {
  const slug = (body.slug || '').replace(/[^a-z0-9-]/g, '');
  const f = await getFile(env, `public/blog/${slug}.html`);
  if (!f) return json({ ok: false, error: 'post not found' });
  const html = b64decode(f.content);
  const title = (html.match(/<h1>([\s\S]*?)<\/h1>/) || [])[1] || slug;
  const excerpt = (html.match(/<meta name="description" content="([^"]*)"/) || [])[1] || '';
  const bodyM = html.match(/<div class="post-body[^"]*">\n?([\s\S]*?)\n?  <\/div>\n<\/article>/);
  return json({
    ok: true,
    post: {
      slug,
      title: title.replace(/<[^>]+>/g, ''),
      excerpt,
      content: bodyM ? bodyM[1] : '',
    },
  });
}

/* ── Delete a published post (file + index + sitemap) ───────────────────── */

async function deletePost(env, body) {
  const slug = (body.slug || '').replace(/[^a-z0-9-]/g, '');
  if (!slug) return json({ ok: false, error: 'slug required' });
  const f = await getFile(env, `public/blog/${slug}.html`);
  if (!f) return json({ ok: false, error: 'post not found' });
  await gh(env, 'DELETE', `/repos/${REPO}/contents/public/blog/${slug}.html`,
    { message: `delete post: ${slug}`, sha: f.sha });

  const idxFile = await getFile(env, 'public/blog/index.json');
  if (idxFile) {
    const idx = JSON.parse(b64decode(idxFile.content));
    idx.posts = idx.posts.filter((p) => p.slug !== slug);
    await putFile(env, 'public/blog/index.json',
      b64encode(JSON.stringify(idx, null, 2) + '\n'), `index: -${slug}`, idxFile.sha);

    const pages = ['', 'blog.html', 'vault.html', 'about.html', 'freebie.html'];
    const urls = pages.map((p) => `${SITE}/${p}`)
      .concat(idx.posts.map((p) => `${SITE}/blog/${p.slug}.html`));
    const sm = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${u}</loc></url>`).join('\n')}\n</urlset>\n`;
    const smFile = await getFile(env, 'public/sitemap.xml');
    await putFile(env, 'public/sitemap.xml', b64encode(sm), `sitemap: -${slug}`,
      smFile && smFile.sha);
  }
  return json({ ok: true });
}

/* ── Image upload (file in repo, not base64-in-post) ────────────────────── */

async function uploadImage(env, body) {
  const m = (body.data || '').match(/^data:image\/(\w+);base64,(.+)$/s);
  if (!m) return json({ ok: false, error: 'bad image data' });
  const ext = m[1] === 'jpeg' ? 'jpg' : m[1];
  const safe = (body.name || 'img').toLowerCase().replace(/[^a-z0-9._-]/g, '-').replace(/\.(\w+)$/, '');
  const path = `public/blog/img/uploads/${Date.now()}-${safe}.${ext}`;
  await putFile(env, path, m[2], `img: ${safe}`);
  return json({ ok: true, url: `${SITE}/${path.replace('public/', '')}` });
}

/* ── Drafts (JSON files in repo; repo is public — drafts are not secret) ── */

async function saveDraft(env, body) {
  const slug = (body.slug || makeSlug(body.title || 'draft')).replace(/[^a-z0-9-]/g, '');
  const path = `drafts/${slug}.json`;
  const prev = await getFile(env, path);
  const data = {
    slug, title: body.title || '', excerpt: body.excerpt || '',
    content: body.content || '', thumbnail: body.thumbnail || null,
    savedAt: new Date().toISOString(),
  };
  await putFile(env, path, b64encode(JSON.stringify(data)), `draft: ${slug}`, prev && prev.sha);
  return json({ ok: true, slug });
}

async function getDraft(env, body) {
  const f = await getFile(env, `drafts/${(body.slug || '').replace(/[^a-z0-9-]/g, '')}.json`);
  if (!f) return json({ ok: false, error: 'draft not found' });
  return json({ ok: true, draft: JSON.parse(b64decode(f.content)) });
}

async function deleteDraft(env, body) {
  const slug = (body.slug || '').replace(/[^a-z0-9-]/g, '');
  const f = await getFile(env, `drafts/${slug}.json`);
  if (f) await gh(env, 'DELETE', `/repos/${REPO}/contents/drafts/${slug}.json`,
    { message: `draft deleted: ${slug}`, sha: f.sha });
  return json({ ok: true });
}

async function listDrafts(env) {
  const dir = await gh(env, 'GET', `/repos/${REPO}/contents/drafts`);
  if (!dir) return json({ ok: true, drafts: [] });
  const drafts = [];
  for (const f of dir.filter((x) => x.name.endsWith('.json')).slice(0, 30)) {
    const file = await getFile(env, `drafts/${f.name}`);
    if (file) {
      const d = JSON.parse(b64decode(file.content));
      drafts.push({ slug: d.slug, title: d.title, savedAt: d.savedAt });
    }
  }
  drafts.sort((a, b) => (b.savedAt || '').localeCompare(a.savedAt || ''));
  return json({ ok: true, drafts });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
  });
}
