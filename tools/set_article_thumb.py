#!/usr/bin/env python3
"""Set an article's thumbnail (blog card + og:image + JSON-LD).

RULE (Ksenia 2026-07-06): the article thumbnail must NEVER be the Etsy
listing's own cover — use a marketing-appealing image (usually the gen2
mockup scene). Usage: python3 tools/set_article_thumb.py <slug> <image.jpg>
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG = REPO / "public" / "blog"
SITE = "https://sentimentalica.com"

slug, img = sys.argv[1], sys.argv[2]
rel = f"blog/img/{slug}/{img}"
url = f"{SITE}/{rel}"
assert (BLOG / "img" / slug / img).exists(), f"missing {rel}"

idx_p = BLOG / "index.json"
idx = json.loads(idx_p.read_text())
for post in idx["posts"]:
    if post["slug"] == slug:
        post["thumb"] = rel
        post["thumbAbs"] = url
idx_p.write_text(json.dumps(idx, indent=2) + "\n")

page = BLOG / f"{slug}.html"
h = page.read_text()
h = re.sub(r'(<meta property="og:image" content=")[^"]*(")', rf'\g<1>{url}\g<2>', h)
h = re.sub(r'("image":\s*")[^"]*(")', rf'\g<1>{url}\g<2>', h, count=1)
page.write_text(h)
print(f"thumb -> {rel}")
