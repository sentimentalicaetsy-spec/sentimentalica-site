#!/usr/bin/env python3
"""Categorized-list infographic v2 — Ksenia's reference style:
SD-generated aged-paper sheet with ephemera borders as the CANVAS, torn-paper
panels with soft shadows, vintage + script typography. Not PowerPoint.

Usage: python3 tools/render_list_infographic.py <spec.json> <out.jpg> [--bg bg.jpg]
"""
import json
import random
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1000, 1500
INK = (74, 58, 44); MUTED = (128, 106, 84); ROSE = (150, 92, 92)
YES = "/Users/kseniateter/sentimentalica-pipeline/config/fonts/YesevaOne-Regular.ttf"
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SNELL = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
F = lambda p, s: ImageFont.truetype(p, s)


def torn_panel(w, h, fill=(249, 244, 232), jag=7):
    """Paper panel with torn (jittered) edges + subtle fibre noise."""
    random.seed(w * h)
    pad = jag + 4
    p = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    pts = []
    steps = 28
    for i in range(steps):        # top
        pts.append((pad + w * i / steps + random.uniform(-2, 2), pad + random.uniform(-jag, jag)))
    for i in range(steps // 2):   # right
        pts.append((pad + w + random.uniform(-jag, jag), pad + h * i / (steps // 2)))
    for i in range(steps):        # bottom
        pts.append((pad + w * (1 - i / steps), pad + h + random.uniform(-jag, jag)))
    for i in range(steps // 2):   # left
        pts.append((pad + random.uniform(-jag, jag), pad + h * (1 - i / (steps // 2))))
    d.polygon(pts, fill=fill + (245,))
    # fibre noise
    npx = p.load()
    for _ in range(w * h // 60):
        x = random.randint(pad, pad + w - 1); y = random.randint(pad, pad + h - 1)
        r, g, b, a = npx[x, y]
        if a: npx[x, y] = (r - 6, g - 6, b - 8, a)
    return p, pad


def paste_torn(cv, panel, pad, xy):
    sh = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    a = panel.split()[3].point(lambda v: 70 if v > 0 else 0)
    s = Image.new("RGBA", panel.size, (60, 45, 30, 0)); s.putalpha(a)
    sh.paste(s, (xy[0] - pad + 6, xy[1] - pad + 9), s)
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    cv.alpha_composite(panel, (xy[0] - pad, xy[1] - pad))


def main():
    spec = json.loads(open(sys.argv[1]).read())
    bg_path = sys.argv[sys.argv.index("--bg") + 1] if "--bg" in sys.argv else None
    if bg_path:
        cv = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    else:
        cv = Image.new("RGBA", (W, H), (243, 234, 216, 255))
    d = ImageDraw.Draw(cv)

    # Title on its own torn banner
    tp, pad = torn_panel(840, 208, jag=8)
    paste_torn(cv, tp, pad, (80, 44))
    d = ImageDraw.Draw(cv)
    title = spec["title"]; font_t = F(YES, 46)
    words = title.split()
    best = min(range(1, len(words)),
               key=lambda i: abs(d.textlength(" ".join(words[:i]), font=font_t)
                                 - d.textlength(" ".join(words[i:]), font=font_t)))
    d.text((W//2, 92), " ".join(words[:best]), font=font_t, fill=INK, anchor="mm")
    d.text((W//2, 144), " ".join(words[best:]), font=font_t, fill=INK, anchor="mm")
    d.text((W//2, 206), spec["subtitle"], font=F(SNELL, 38), fill=ROSE, anchor="mm")

    # Category panels: torn paper, script headers, serif items
    cats = spec["categories"]
    margin, gap = 78, 16
    col_w = (W - margin * 2 - gap) // 2
    xs, ys = [margin, margin + col_w + gap], [278, 278]
    for cat in cats:
        col = 0 if ys[0] <= ys[1] else 1
        x, y = xs[col], ys[col]
        head_h, line_h = 50, 27
        ph = head_h + len(cat["items"]) * line_h + 18
        panel, pad = torn_panel(col_w, ph)
        paste_torn(cv, panel, pad, (x, y))
        d = ImageDraw.Draw(cv)
        d.text((x + col_w // 2, y + 26), cat["name"], font=F(SNELL, 36), fill=ROSE, anchor="mm")
        d.line([x + 40, y + head_h - 6, x + col_w - 40, y + head_h - 6], fill=(190, 170, 145), width=1)
        ty = y + head_h + 8
        for n, it in cat["items"]:
            d.text((x + 26, ty), f"{n}.", font=F(GEO_B, 17), fill=MUTED)
            d.text((x + 64, ty), it, font=F(GEO, 17), fill=INK)
            ty += line_h
        ys[col] = y + ph + gap

    # Closing plaque
    yb = max(ys) + 4
    plq, pad = torn_panel(680, 118, jag=6)
    paste_torn(cv, plq, pad, ((W - 680) // 2, yb))
    d = ImageDraw.Draw(cv)
    d.text((W//2, yb + 38), spec["plaque"], font=F(SNELL, 34), fill=ROSE, anchor="mm")
    d.text((W//2, yb + 86), "Future-you will be grateful.", font=F(GEO_B, 20), fill=INK, anchor="mm")
    d.text((W//2, H - 40), "s e n t i m e n t a l i c a . c o m", font=F(GEO_B, 20), fill=INK, anchor="mm")
    cv.convert("RGB").save(sys.argv[2], "JPEG", quality=90, optimize=True)
    print(sys.argv[2])


if __name__ == "__main__":
    main()
