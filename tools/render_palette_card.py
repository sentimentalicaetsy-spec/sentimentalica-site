#!/usr/bin/env python3
"""Pinterest palette image.

Approved rule:
- one beautiful real listing page as the full-bleed background
- 4-5 large swatches, rectangles or square columns chosen for the background
- visible color name and HEX/number label
- approved layout: centered large column of wide rectangles, no backing/blur
- bottom text is exactly "sentimentalica.com"
- no main character/portrait/animal portrait source images
- no split side panel, framed stack, swatch border, airbrush, blur, or extra CTA

Usage:
  python3 tools/render_palette_card.py <image.jpg> "<Theme Title>" <out.jpg> \
      [--palette "Name:#hex,Name:#hex,..."] [--layout allover]
      [--shape rect|square] [--position upper|bottom|left|right|center]
      [--desaturate 0.88]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from gen_article_assets import name_of, palette_from  # noqa: E402

W, H = 1000, 1500
BLUE = (28, 78, 165)
INK = (42, 48, 54)
CREAM = (255, 252, 246)
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
F = lambda p, s: ImageFont.truetype(p, s)


def color_distance(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def normalize_palette(pal, img_path):
    """Guarantee 4-5 visibly distinct swatches, preferring 5 when available."""
    out = []
    for c in pal:
        rgb = c["rgb"]
        if all(color_distance(rgb, x["rgb"]) >= 34 for x in out):
            out.append(c)
        if len(out) == 5:
            break

    if len(out) < 5:
        add_quantized_colors(out, img_path)

    if len(out) < 4:
        raise SystemExit("Palette extraction produced fewer than 4 distinct colors.")
    return out[:5]


def add_quantized_colors(out, img_path):
    img = Image.open(img_path).convert("RGB")
    img.thumbnail((220, 330), Image.Resampling.LANCZOS)
    q = img.quantize(colors=14, method=Image.Quantize.MEDIANCUT)
    pal_raw = q.getpalette()
    counts = sorted(q.getcolors() or [], reverse=True)
    for _count, idx in counts:
        rgb = tuple(pal_raw[idx * 3:idx * 3 + 3])
        if max(rgb) > 246 or min(rgb) < 8:
            continue
        if all(color_distance(rgb, x["rgb"]) >= 34 for x in out):
            out.append({
                "name": name_of(rgb),
                "hex": "#%02x%02x%02x" % rgb,
                "rgb": rgb,
            })
        if len(out) == 5:
            break


def parse_palette(img_path):
    if "--palette" in sys.argv:
        pal = []
        for part in sys.argv[sys.argv.index("--palette") + 1].split(","):
            name, hexv = part.split(":")
            hexv = hexv.strip().lstrip("#")
            rgb = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
            pal.append({"name": name.strip(), "hex": "#" + hexv, "rgb": rgb})
        if len(pal) < 4:
            raise SystemExit("Palette images require 4-5 colors.")
        return pal[:5]

    pal = palette_from([img_path], n=5)
    for c in pal:
        hexv = c["hex"].lstrip("#")
        c["rgb"] = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
    return normalize_palette(pal[:5], img_path)


def text_color(rgb):
    return INK if sum(rgb) / 3 > 155 else CREAM


def boost_contrast(rgb, bg):
    """Nudge swatch display color away from the image behind it without changing labels."""
    if color_distance(rgb, bg) >= 118:
        return rgb
    avg = sum(rgb) / 3
    factor = 0.62 if avg > 142 else 1.34
    nudged = tuple(max(0, min(255, int(c * factor))) for c in rgb)
    if color_distance(nudged, bg) < 118:
        # Last resort: push toward a readable deep or pale version of the same swatch family.
        nudged = tuple(max(0, min(255, int(c * (0.5 if avg > 142 else 1.55)))) for c in rgb)
    return nudged


def fit_label(draw, text, max_width, base_size, bold=False):
    path = GEO_B if bold else GEO
    for size in range(base_size, 12, -1):
        f = F(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
    return F(path, 12)


def main():
    img_path, _title, out = sys.argv[1], sys.argv[2], sys.argv[3]
    layout = "allover"
    if "--layout" in sys.argv:
        layout = sys.argv[sys.argv.index("--layout") + 1].strip().lower()
    if layout not in {"allover"}:
        raise SystemExit("--layout must be allover")
    shape = sys.argv[sys.argv.index("--shape") + 1].strip().lower() if "--shape" in sys.argv else "rect"
    if shape not in {"rect", "square"}:
        raise SystemExit("--shape must be rect or square")
    position = sys.argv[sys.argv.index("--position") + 1].strip().lower() if "--position" in sys.argv else "upper"
    if position not in {"upper", "bottom", "left", "right", "center"}:
        raise SystemExit("--position must be upper, bottom, left, right, or center")
    desaturate = float(sys.argv[sys.argv.index("--desaturate") + 1]) if "--desaturate" in sys.argv else 0.82
    src = Image.open(img_path).convert("RGB")
    src = ImageEnhance.Color(src).enhance(desaturate)
    pal = parse_palette(img_path)
    if shape == "square":
        pal = pal[:4]

    cv = ImageOps.fit(src, (W, H), Image.Resampling.LANCZOS).convert("RGBA")

    # Slight wash so labels remain readable without turning into a white panel.
    wash = Image.new("RGBA", (W, H), (255, 250, 240, 28))
    cv.alpha_composite(wash)

    if shape == "rect":
        sw_w = int(W * 0.74)
        sw_h = 178
        gap = 24
        x = (W - sw_w) // 2
    else:
        sw_w = sw_h = 300
        gap = 16
        if position == "left":
            x = 86
        elif position == "right":
            x = W - sw_w - 86
        else:
            x = (W - sw_w) // 2
    total_h = len(pal) * sw_h + (len(pal) - 1) * gap
    if shape == "rect" and position == "bottom":
        y0 = H - total_h - 160
    elif shape == "square" or position == "center":
        y0 = int(H * 0.5 - total_h / 2)
    else:
        y0 = max(96, int(H * 0.26 - total_h / 2))

    d = ImageDraw.Draw(cv)
    for i, c in enumerate(pal, 1):
        y = y0 + (i - 1) * (sw_h + gap)
        rgb = c["rgb"]
        bg_crop = cv.crop((x, y, x + sw_w, y + sw_h)).convert("RGB").resize((1, 1), Image.Resampling.BOX)
        bg = bg_crop.getpixel((0, 0))
        # Curated palettes are already contrast/taste-checked. Do not mutate
        # soft rose, cream, or sage into muddy display colors at render time.
        display_rgb = rgb
        d.rectangle((x, y, x + sw_w, y + sw_h), fill=display_rgb)
        tcol = text_color(display_rgb)
        number = f"{i:02}"
        hexv = c["hex"].upper()
        name = c.get("name") or name_of(rgb)
        name_f = fit_label(d, name, sw_w - 28, 34, bold=True)
        hex_f = fit_label(d, hexv, sw_w - 28, 27)
        d.text((x + 16, y + 14), number, font=F(GEO_B, 24), fill=tcol)
        d.text((x + sw_w / 2, y + sw_h - 64), name, font=name_f, fill=tcol, anchor="mm")
        d.text((x + sw_w / 2, y + sw_h - 30), hexv, font=hex_f, fill=tcol, anchor="mm")

    site = "sentimentalica.com"
    site_f = F(GEO_B, 30)
    d.text((W / 2, H - 44), site, font=site_f, fill=BLUE, anchor="mm")

    cv.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
