#!/usr/bin/env python3
"""Pinterest palette image.

Approved rule:
- one beautiful real listing page as the full-bleed background
- max 5 large square swatches
- visible color name and HEX/number label
- soft feathered airbrush/blur haze under swatches and URL
- bottom text is exactly "sentimentalica.com"
- no split side panel, framed stack, hard rectangle, border, or extra CTA

Usage:
  python3 tools/render_palette_card.py <image.jpg> "<Theme Title>" <out.jpg> \
      [--palette "Name:#hex,Name:#hex,..."]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from gen_article_assets import name_of, palette_from  # noqa: E402

W, H = 1000, 1500
BLUE = (28, 78, 165)
INK = (42, 48, 54)
CREAM = (255, 252, 246)
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
F = lambda p, s: ImageFont.truetype(p, s)


def parse_palette(img_path):
    if "--palette" in sys.argv:
        pal = []
        for part in sys.argv[sys.argv.index("--palette") + 1].split(","):
            name, hexv = part.split(":")
            hexv = hexv.strip().lstrip("#")
            rgb = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
            pal.append({"name": name.strip(), "hex": "#" + hexv, "rgb": rgb})
        return pal[:5]

    pal = palette_from([img_path], n=5)
    for c in pal:
        hexv = c["hex"].lstrip("#")
        c["rgb"] = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
    return pal[:5]


def airbrush(size, rect, alpha=142, blur=28):
    """Soft irregular haze, not a straight rectangle."""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = rect
    d.rounded_rectangle((x0, y0, x1, y1), radius=84, fill=alpha)
    d.ellipse((x0 - 42, y0 + 40, x0 + 92, y1 - 20), fill=int(alpha * 0.82))
    d.ellipse((x1 - 92, y0 + 12, x1 + 48, y1 - 55), fill=int(alpha * 0.76))
    d.ellipse((x0 + 26, y0 - 54, x1 - 18, y0 + 104), fill=int(alpha * 0.66))
    d.ellipse((x0 + 18, y1 - 104, x1 - 30, y1 + 54), fill=int(alpha * 0.66))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    haze = Image.new("RGBA", size, CREAM + (0,))
    haze.putalpha(mask)
    return haze


def text_color(rgb):
    return INK if sum(rgb) / 3 > 155 else CREAM


def fit_label(draw, text, max_width, base_size, bold=False):
    path = GEO_B if bold else GEO
    for size in range(base_size, 12, -1):
        f = F(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
    return F(path, 12)


def main():
    img_path, _title, out = sys.argv[1], sys.argv[2], sys.argv[3]
    src = Image.open(img_path).convert("RGB")
    pal = parse_palette(img_path)

    cv = ImageOps.fit(src, (W, H), Image.Resampling.LANCZOS).convert("RGBA")

    # Slight wash so labels remain readable without turning into a white panel.
    wash = Image.new("RGBA", (W, H), (255, 250, 240, 28))
    cv.alpha_composite(wash)

    sw = 166
    gap = 24
    x = 92
    total_h = len(pal) * sw + (len(pal) - 1) * gap
    y0 = (H - total_h) // 2 - 30
    haze_pad_x = 52
    haze_pad_y = 64
    cv.alpha_composite(
        airbrush(
            (W, H),
            (x - haze_pad_x, y0 - haze_pad_y,
             x + sw + haze_pad_x, y0 + total_h + haze_pad_y),
            alpha=168,
            blur=34,
        )
    )

    d = ImageDraw.Draw(cv)
    for i, c in enumerate(pal, 1):
        y = y0 + (i - 1) * (sw + gap)
        rgb = c["rgb"]
        d.rectangle((x, y, x + sw, y + sw), fill=rgb)
        tcol = text_color(rgb)
        number = f"{i:02}"
        hexv = c["hex"].upper()
        name = c.get("name") or name_of(rgb)
        name_f = fit_label(d, name, sw - 24, 24, bold=True)
        hex_f = fit_label(d, hexv, sw - 24, 20)
        d.text((x + 14, y + 12), number, font=F(GEO_B, 22), fill=tcol)
        d.text((x + sw / 2, y + sw - 62), name, font=name_f, fill=tcol, anchor="mm")
        d.text((x + sw / 2, y + sw - 30), hexv, font=hex_f, fill=tcol, anchor="mm")

    site = "sentimentalica.com"
    site_f = F(GEO_B, 30)
    site_w = d.textlength(site, font=site_f)
    sx0 = int((W - site_w) / 2 - 44)
    sx1 = int((W + site_w) / 2 + 44)
    cv.alpha_composite(airbrush((W, H), (sx0, H - 118, sx1, H - 48), alpha=126, blur=22))
    d = ImageDraw.Draw(cv)
    d.text((W / 2, H - 78), site, font=site_f, fill=BLUE, anchor="mm")

    cv.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
