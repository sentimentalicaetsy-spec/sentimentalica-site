#!/usr/bin/env python3
"""Publish a blog post to sentimentalica.com from a Markdown (or HTML) file.

This is the repo-side publishing path (used by the content-factory agents
and for any scripted publishing): it writes the post page directly into
public/blog/, updates the index, regenerates the sitemap, and (with --push)
commits + pushes — GitHub Actions then auto-deploys the site.
The admin panel (public/admin/) remains the separate manual path.

Input file format — front matter between --- lines, then the body:

    ---
    title: Twelve cosy autumn journal spreads
    category: Junk Journaling
    excerpt: One or two sentences shown on the blog listing.
    date: 2026-07-05            (optional, defaults to today)
    thumb: ./cover.jpg          (optional, local path or URL)
    ---
    Markdown body. Standard headings/bold/italic/links/lists/quotes.
    Local images: ![alt](./photo.jpg) — copied into public/blog/img/<slug>/.
    Inline Etsy product cards (like the homepage grid, hover video included):

    {{etsy:4480338966,4480315829,4480308168}}

If the body file ends in .html the body is used as-is (only {{etsy:...}}
shortcodes are expanded).

Usage:
  python tools/publish_post.py post.md [--slug custom-slug] [--push] [--force]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUBLIC = REPO / "public"
BLOG = PUBLIC / "blog"
SITE = "https://sentimentalica.com"

STATIC_PAGES = ["index.html", "blog.html", "vault.html", "about.html", "freebie.html"]


# ── Front matter ──────────────────────────────────────────────────────────────

def parse_front_matter(text):
    m = re.match(r"\s*---\s*\n(.*?)\n---\s*\n(.*)", text, re.S)
    if not m:
        sys.exit("ERROR: no front matter block (--- ... ---) found.")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    if not meta.get("title"):
        sys.exit("ERROR: front matter needs at least a title.")
    return meta, m.group(2).strip()


def make_slug(title):
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower()).strip()
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s))[:80]


# ── Minimal Markdown → HTML (no dependencies; agents may also supply HTML) ───

def md_to_html(md):
    out, in_list, in_ol = [], False, False

    def close_lists():
        nonlocal in_list, in_ol
        if in_list:
            out.append("</ul>")
            in_list = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def inline(s):
        s = escape(s, quote=False)
        s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                   r'<img src="\2" alt="\1" loading="lazy">', s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                   r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        return s

    for block in re.split(r"\n\s*\n", md):
        block = block.strip()
        if not block:
            continue
        if block.startswith("{{") and block.endswith("}}"):
            close_lists()
            out.append(block)  # shortcode — expanded later
            continue
        m = re.match(r"(#{1,4})\s+(.*)", block)
        if m:
            close_lists()
            lvl = max(2, len(m.group(1)))  # # and ## → h2 (h1 is the post title)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        if block.startswith(">"):
            close_lists()
            quote = " ".join(l.lstrip("> ").strip() for l in block.splitlines())
            out.append(f"<blockquote>{inline(quote)}</blockquote>")
            continue
        if all(re.match(r"\s*[-*]\s+", l) for l in block.splitlines()):
            close_lists()
            items = "".join(f"<li>{inline(re.sub(r'^\s*[-*]\s+', '', l))}</li>"
                            for l in block.splitlines())
            out.append(f"<ul>{items}</ul>")
            continue
        if all(re.match(r"\s*\d+\.\s+", l) for l in block.splitlines()):
            close_lists()
            items = "".join(f"<li>{inline(re.sub(r'^\s*\d+\.\s+', '', l))}</li>"
                            for l in block.splitlines())
            out.append(f"<ol>{items}</ol>")
            continue
        # single image on its own line → figure-style block
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", block)
        if m:
            close_lists()
            out.append(f'<img src="{m.group(2)}" alt="{escape(m.group(1))}" loading="lazy">')
            continue
        close_lists()
        out.append(f"<p>{inline(block)}</p>")
    close_lists()
    return "\n".join(out)


# ── Shortcodes & images ───────────────────────────────────────────────────────

def expand_shortcodes(html):
    def repl(m):
        ids = re.sub(r"[^0-9,]", "", m.group(1))
        return (f'<div class="etsy-products" data-ids="{ids}" aria-busy="true"></div>')
    return re.sub(r"\{\{\s*etsy\s*:\s*([0-9,\s]+)\s*\}\}", repl, html)


def localize_images(html, src_dir: Path, slug: str):
    """Copy local images referenced in the body into public/blog/img/<slug>/."""
    img_dir = BLOG / "img" / slug

    def repl(m):
        src = m.group(1)
        if re.match(r"https?://", src) or src.startswith("/"):
            return m.group(0)
        f = (src_dir / src).resolve()
        if not f.exists():
            sys.exit(f"ERROR: image not found: {src}")
        img_dir.mkdir(parents=True, exist_ok=True)
        target = img_dir / f.name
        shutil.copy2(f, target)
        return m.group(0).replace(src, f"img/{slug}/{f.name}")

    return re.sub(r'src="([^"]+)"', repl, html)


# ── Page template ─────────────────────────────────────────────────────────────

def render_page(meta, slug, body_html):
    title = escape(meta["title"])
    desc = escape(meta.get("excerpt", ""))
    category = escape(meta.get("category", "Journal"))
    d = meta.get("date") or date.today().isoformat()
    d_display = date.fromisoformat(d).strftime("%B %-d, %Y")
    canonical = f"{SITE}/blog/{slug}.html"
    thumb_url = meta.get("_thumb_url") or f"{SITE}/assets/logo.png"
    words = len(re.sub(r"<[^>]+>", " ", body_html).split())
    read_min = max(1, round(words / 220))

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": meta["title"], "datePublished": d,
        "description": meta.get("excerpt", ""),
        "image": thumb_url, "url": canonical,
        "author": {"@type": "Organization", "name": "Sentimentalica"},
    })

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Sentimentalica</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{escape(thumb_url)}">
<link rel="icon" type="image/png" href="../assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/styles.css?v=3">
<link rel="stylesheet" href="../assets/post.css?v=11">
<script type="application/ld+json">{ld}</script>
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
    <div class="post-cat">{category}</div>
    <h1>{title}</h1>
    <div class="post-hero-meta">{d_display} · {read_min} minute read</div>
  </header>
  <div class="post-body ql-content">
{body_html}
  </div>
</article>

<footer>
  <div>© {date.today().year} Sentimentalica</div>
  <div>
    <a href="https://www.etsy.com/shop/sentimentalica" target="_blank" rel="noopener">Etsy</a>
    <a href="https://pinterest.com/sentimentalica" target="_blank" rel="noopener">Pinterest</a>
    <a href="mailto:hello@sentimentalica.com">Contact</a>
  </div>
</footer>

<script src="../assets/post.js?v=11" defer></script>
<script src="../assets/admin-tab.js?v=11" defer></script>
</body>
</html>
"""


# ── Index & sitemap ───────────────────────────────────────────────────────────

def update_index(meta, slug, read_min):
    idx_path = BLOG / "index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"posts": []}
    d = meta.get("date") or date.today().isoformat()
    entry = {
        "slug": slug,
        "title": meta["title"],
        "category": meta.get("category", "Journal"),
        "excerpt": meta.get("excerpt", ""),
        "date": d,
        "dateDisplay": date.fromisoformat(d).strftime("%b %-d"),
        "readTime": f"{read_min} min read",
        "thumb": meta.get("_thumb_rel"),
    }
    idx["posts"] = [p for p in idx["posts"] if p["slug"] != slug]
    idx["posts"].insert(0, entry)
    idx["posts"].sort(key=lambda p: p["date"], reverse=True)
    idx_path.write_text(json.dumps(idx, indent=2) + "\n")


def regenerate_sitemap():
    idx = json.loads((BLOG / "index.json").read_text())
    urls = [f"{SITE}/"] + [f"{SITE}/{p}" for p in STATIC_PAGES[1:]]
    urls += [f"{SITE}/blog/{p['slug']}.html" for p in idx["posts"]]
    body = "\n".join(
        f"  <url><loc>{u}</loc></url>" for u in urls)
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="post source (.md or .html body)")
    ap.add_argument("--slug")
    ap.add_argument("--push", action="store_true", help="git commit + push (deploys)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing post")
    args = ap.parse_args()

    src = Path(args.file).resolve()
    meta, body = parse_front_matter(src.read_text())
    slug = args.slug or make_slug(meta["title"])
    out_path = BLOG / f"{slug}.html"
    if out_path.exists() and not args.force:
        sys.exit(f"ERROR: {out_path} exists — use --force to overwrite.")

    body_html = body if src.suffix == ".html" else md_to_html(body)
    body_html = expand_shortcodes(body_html)
    body_html = localize_images(body_html, src.parent, slug)

    # Thumbnail: local file → copy next to the post images
    thumb = meta.get("thumb")
    if thumb and not re.match(r"https?://", thumb):
        f = (src.parent / thumb).resolve()
        if not f.exists():
            sys.exit(f"ERROR: thumb not found: {thumb}")
        img_dir = BLOG / "img" / slug
        img_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, img_dir / f.name)
        meta["_thumb_rel"] = f"blog/img/{slug}/{f.name}"
        meta["_thumb_url"] = f"{SITE}/blog/img/{slug}/{f.name}"
    elif thumb:
        meta["_thumb_rel"] = thumb
        meta["_thumb_url"] = thumb

    page = render_page(meta, slug, body_html)
    out_path.write_text(page)
    words = len(re.sub(r"<[^>]+>", " ", body_html).split())
    update_index(meta, slug, max(1, round(words / 220)))
    regenerate_sitemap()
    print(f"✓ wrote public/blog/{slug}.html (+ index.json, sitemap.xml)")

    if args.push:
        subprocess.run(["git", "-C", str(REPO), "add", "public"], check=True)
        subprocess.run(["git", "-C", str(REPO), "commit", "-m",
                        f"post: {meta['title']}"], check=True)
        subprocess.run(["git", "-C", str(REPO), "push"], check=True)
        print(f"✓ pushed — live at {SITE}/blog/{slug}.html in ~1 minute")
    else:
        print("  (no --push: review locally, then git commit + push to deploy)")


if __name__ == "__main__":
    main()
