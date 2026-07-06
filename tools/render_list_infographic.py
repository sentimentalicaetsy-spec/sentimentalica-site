#!/usr/bin/env python3
"""Categorized-list infographic (Ksenia's ref: '50 things to do in a journal').
A full pin-image devoted to the article's list — saved by thousands, links to
the article where each item is expanded.

Usage: python3 tools/render_list_infographic.py <spec.json> <out.jpg>
spec: {"title","subtitle","plaque","categories":[{"name","color":"#hex","items":[...]}]}
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 1500
CREAM = (250, 246, 238); INK = (58, 50, 44); MUTED = (122, 111, 94)
YES = "/Users/kseniateter/sentimentalica-pipeline/config/fonts/YesevaOne-Regular.ttf"
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEO_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
F = lambda p, s: ImageFont.truetype(p, s)


def tint(hexv, f=0.85):
    h = hexv.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return tuple(int(c + (255 - c) * f) for c in (r, g, b))


def main():
    spec = json.loads(open(sys.argv[1]).read())
    cv = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(cv)
    # Title auto-wraps to fit the width (2 lines max)
    title = spec["title"]
    font_t = F(YES, 52)
    if d.textlength(title, font=font_t) > W - 80:
        words = title.split()
        best = min(range(1, len(words)),
                   key=lambda i: abs(d.textlength(" ".join(words[:i]), font=font_t)
                                     - d.textlength(" ".join(words[i:]), font=font_t)))
        l1, l2 = " ".join(words[:best]), " ".join(words[best:])
        d.text((W//2, 62), l1, font=font_t, fill=INK, anchor="mm")
        d.text((W//2, 122), l2, font=font_t, fill=INK, anchor="mm")
        sub_y = 172
    else:
        d.text((W//2, 78), title, font=font_t, fill=INK, anchor="mm")
        sub_y = 138
    d.text((W//2, sub_y), spec["subtitle"], font=F(GEO_I, 28), fill=MUTED, anchor="mm")

    cats = spec["categories"]
    pad, gap = 36, 22
    col_w = (W - pad*2 - gap) // 2
    x_positions, y = [pad, pad + col_w + gap], [212, 212]
    for i, cat in enumerate(cats):
        col = 0 if y[0] <= y[1] else 1
        x, yy = x_positions[col], y[col]
        header_h, line_h = 46, 30
        ph = header_h + len(cat["items"]) * line_h + 22
        base = tint(cat["color"], 0.88)
        d.rounded_rectangle([x, yy, x + col_w, yy + ph], 16, fill=base)
        d.rounded_rectangle([x, yy, x + col_w, yy + header_h], 16, fill=tint(cat["color"], 0.55))
        d.rectangle([x, yy + header_h - 16, x + col_w, yy + header_h], fill=tint(cat["color"], 0.55))
        d.text((x + col_w//2, yy + header_h//2), cat["name"], font=F(GEO_B, 24), fill=INK, anchor="mm")
        ty = yy + header_h + 14
        for n, it in cat["items"]:
            d.text((x + 20, ty), f"{n}.", font=F(GEO_B, 19), fill=MUTED)
            d.text((x + 58, ty), it, font=F(GEO, 19), fill=INK)
            ty += line_h
        y[col] = yy + ph + gap

    yb = max(y) + 6
    d.rounded_rectangle([W//2 - 330, yb, W//2 + 330, yb + 86], 14, fill=tint("#b8956a", 0.75))
    d.text((W//2, yb + 30), spec["plaque"], font=F(GEO_I, 24), fill=INK, anchor="mm")
    d.text((W//2, yb + 60), "Future-you will be grateful.", font=F(GEO_B, 22), fill=INK, anchor="mm")
    d.text((W//2, H - 46), "sentimentalica.com", font=F(GEO_B, 24), fill=INK, anchor="mm")
    cv.save(sys.argv[2], "JPEG", quality=88, optimize=True)
    print(sys.argv[2])


if __name__ == "__main__":
    main()
