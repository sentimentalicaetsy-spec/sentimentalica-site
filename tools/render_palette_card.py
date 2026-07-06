#!/usr/bin/env python3
"""Palette card — Ksenia's rule (2026-07-06): the palette is always an IMAGE —
swatches with HEX + names ON a beautiful listing photo (refs 7-8).
Doubles as the article palette block and a Pinterest palette pin.

Usage:
  python3 tools/render_palette_card.py <image.jpg> "<Theme Title>" <out.jpg> \
      [--palette "Name:#hex,Name:#hex,..."]   (default: extracted from image)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from gen_article_assets import palette_from, name_of  # noqa: E402

W, H = 1000, 1500
CREAM = (250, 246, 238); INK = (58, 50, 44); MUTED = (122, 111, 94)
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEO_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
F = lambda p, s: ImageFont.truetype(p, s)


def main():
    img_path, title, out = sys.argv[1], sys.argv[2], sys.argv[3]
    pal_arg = None
    if "--palette" in sys.argv:
        pal_arg = sys.argv[sys.argv.index("--palette") + 1]
    src = Image.open(img_path).convert("RGB")
    if pal_arg:
        pal = []
        for part in pal_arg.split(","):
            name, hexv = part.split(":")
            hexv = hexv.strip().lstrip("#")
            pal.append({"name": name.strip(),
                        "hex": "#" + hexv,
                        "rgb": tuple(int(hexv[i:i+2], 16) for i in (0, 2, 4))})
    else:
        pal = palette_from([img_path], n=6)
        for c in pal:
            hexv = c["hex"].lstrip("#")
            c["rgb"] = tuple(int(hexv[i:i+2], 16) for i in (0, 2, 4))
    pal = pal[:6]

    cv = Image.new("RGB", (W, H), CREAM)
    # left 58%: the beautiful image, full-bleed top-to-bottom
    from PIL import ImageOps
    lw = int(W * 0.58)
    cv.paste(ImageOps.fit(src, (lw, H), Image.LANCZOS), (0, 0))
    d = ImageDraw.Draw(cv)
    # right column: title + swatches with hex + name
    rx = lw
    d.rectangle([rx, 0, W, H], fill=CREAM)
    cx = rx + (W - rx) // 2
    d.text((cx, 90), "Color Palette", font=F(GEO_B, 52), fill=INK, anchor="mm")
    d.text((cx, 150), title, font=F(GEO_I, 30), fill=MUTED, anchor="mm")
    n = len(pal)
    block_h = 170
    y0 = 220
    for i, c in enumerate(pal):
        y = y0 + i * block_h
        d.rectangle([rx + 40, y, W - 40, y + block_h - 26], fill=c["rgb"])
        light = sum(c["rgb"]) / 3 > 150
        tcol = INK if light else (250, 246, 238)
        d.text((cx, y + 48), c["hex"].upper(), font=F(GEO_B, 30), fill=tcol, anchor="mm")
        d.text((cx, y + 92), c["name"], font=F(GEO, 24), fill=tcol, anchor="mm")
    # bottom: mood words + circles echoing the palette
    yb = y0 + n * block_h + 14
    r = 26
    total = n * (2 * r) + (n - 1) * 18
    x = cx - total // 2 + r
    for c in pal:
        d.ellipse([x - r, yb, x + r, yb + 2 * r], fill=c["rgb"],
                  outline=(255, 255, 255), width=3)
        x += 2 * r + 18
    d.text((cx, yb + 2 * r + 44), "elegant · soft · calm", font=F(GEO_I, 26),
           fill=MUTED, anchor="mm")
    d.text((cx, H - 60), "SENTIMENTALICA", font=F(GEO_B, 24), fill=INK, anchor="mm")
    cv.save(out, "JPEG", quality=88, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
