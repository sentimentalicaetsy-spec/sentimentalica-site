#!/usr/bin/env python3
"""Prepare per-listing assets for an article: palette + optimized images.

Usage: python3 tools/gen_article_assets.py "NNN_Theme|etsy_id|/path/to/revised thumbnails"
Writes: staging/overnight/assets/<listing>/  (img1..img4.jpg resized <=1200px,
        meta.json with theme words, etsy_id, named palette)
Prints the meta.json path.
"""
import colorsys
import json
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
OUT_ROOT = REPO / "staging" / "overnight" / "assets"

NAMES = [("Dusty Blue", (96, 119, 160)), ("Deep Navy", (35, 48, 90)),
         ("Coral", (214, 116, 98)), ("Blush", (226, 180, 170)),
         ("Sage", (148, 164, 128)), ("Antique Cream", (238, 226, 200)),
         ("Terracotta", (186, 101, 71)), ("Plum", (112, 72, 110)),
         ("Golden Ochre", (206, 164, 92)), ("Teal", (64, 124, 128)),
         ("Rose", (196, 123, 123)), ("Olive", (120, 120, 70)),
         ("Charcoal", (52, 50, 48)), ("Lavender", (168, 152, 190))]


def name_of(c):
    return min(NAMES, key=lambda n: sum((a - b) ** 2 for a, b in zip(n[1], c)))[0]


def palette_from(images, n=6):
    strip = Image.new("RGB", (240 * len(images), 240))
    for i, p in enumerate(images):
        im = Image.open(p).convert("RGB")
        im.thumbnail((240, 240))
        strip.paste(im.resize((240, 240)), (i * 240, 0))
    q = strip.quantize(colors=24)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    picked = []
    for _, idx in counts:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if l < 0.10 or l > 0.97:
            continue
        if all(abs(r - pr) + abs(g - pg) + abs(b - pb) > 100 for pr, pg, pb in picked):
            picked.append((r, g, b))
        if len(picked) == n:
            break
    seen, out = set(), []
    for c in picked:  # unique names, keep order
        nm = name_of(c)
        if nm not in seen:
            seen.add(nm)
            out.append({"name": nm, "hex": "#%02x%02x%02x" % c})
    return out


def main():
    listing, etsy_id, thumbs = sys.argv[1].split("|")
    tdir = Path(thumbs)
    imgs = sorted([p for p in tdir.iterdir()
                   if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if len(imgs) < 3:
        sys.exit(f"ERROR: only {len(imgs)} images in {tdir}")

    out = OUT_ROOT / listing
    out.mkdir(parents=True, exist_ok=True)
    # hero = 1.jpg (her curated cover), inline = next best spread
    pick = [imgs[0]] + imgs[1:4]
    saved = []
    for i, p in enumerate(pick, 1):
        im = Image.open(p).convert("RGB")
        im.thumbnail((1200, 1200))
        f = out / f"img{i}.jpg"
        im.save(f, "JPEG", quality=80, optimize=True)
        saved.append(f.name)

    theme_words = " ".join(listing.split("_")[1:])
    meta = {
        "listing": listing,
        "theme": theme_words,
        "etsy_id": etsy_id,
        "palette": palette_from(imgs[:6]),
        "images": saved,
        "assets_dir": str(out),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(out / "meta.json")


if __name__ == "__main__":
    main()
