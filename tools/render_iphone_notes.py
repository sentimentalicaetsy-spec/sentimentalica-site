#!/usr/bin/env python3
"""Render an AUTHENTIC iPhone Notes screenshot as a Pinterest infographic.

Ksenia's refs (refs/iphone notes/): a real iOS Notes note — status bar, "< Notes"
nav, bold title (may hold 1-2 emoji), a small EMOJI CLUSTER row under the title,
then list items as CHECKBOX CIRCLES or DASHES with plain text. Emoji may TRAIL an
item, but NEVER lead every bullet. Bottom iOS toolbar. Natural, not overdesigned.

Usage:
  python tools/render_iphone_notes.py --title "journal ideas 💖" \
      --emojis "💌🎧📓🤎" --bullet circle --lines "Welcome page 💐" "Things I love 💕" ...
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SF = "/System/Library/Fonts/SFNS.ttf"
HELV = "/System/Library/Fonts/Helvetica.ttc"
EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI_STRIKE = 48
NOTES_YELLOW = (240, 185, 20)


def font(size, bold=False):
    try:
        f = ImageFont.truetype(SF, size)
        try:
            f.set_variation_by_name("Bold" if bold else "Regular")
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.truetype(HELV, size, index=1 if bold else 0)


_emoji_font = ImageFont.truetype(EMOJI, EMOJI_STRIKE)


def _is_emoji(cp):
    return (cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF
            or 0x2190 <= cp <= 0x21FF or cp in (0x203C, 0x2049, 0x2122, 0x2139))


def _emoji_img(ch, size):
    im = Image.new("RGBA", (EMOJI_STRIKE + 20, EMOJI_STRIKE + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 2), ch, font=_emoji_font, embedded_color=True)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    r = size / max(1, im.height)
    return im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)


def _tokens(text):
    out, buf, i = [], "", 0
    while i < len(text):
        cp = ord(text[i])
        if _is_emoji(cp):
            if buf:
                out.append(("t", buf)); buf = ""
            ch = text[i]; j = i + 1
            while j < len(text) and (ord(text[j]) in (0xFE0F, 0x200D)
                                     or 0x1F3FB <= ord(text[j]) <= 0x1F3FF):
                ch += text[j]; j += 1
                if j < len(text) and _is_emoji(ord(text[j])):
                    ch += text[j]; j += 1
            out.append(("e", ch)); i = j
        else:
            buf += text[i]; i += 1
    if buf:
        out.append(("t", buf))
    return out


def draw_rich(d, canvas, xy, text, fnt, fill, emoji_size=None):
    x, y = xy
    es = emoji_size or int(fnt.size * 1.02)
    ascent = fnt.getbbox("Ag")[3]
    for kind, val in _tokens(text):
        if kind == "t":
            d.text((x, y), val, font=fnt, fill=fill)
            x += int(d.textlength(val, font=fnt))
        else:
            try:
                em = _emoji_img(val, es)
                canvas.paste(em, (x + 3, y + (ascent - es) // 2 + 2), em)
                x += em.width + 8
            except Exception:
                x += es
    return x


def _rich_width(d, text, fnt):
    es = int(fnt.size * 1.02)
    return sum(d.textlength(v, font=fnt) if k == "t" else es + 8
               for k, v in _tokens(text))


def _statusbar(d, carrier="CLARO CL"):
    d.text((44, 22), "22:32", font=font(34, bold=True), fill=(0, 0, 0))
    bx = W - 268
    for i, h in enumerate((10, 16, 22, 28)):
        d.rounded_rectangle([bx + i * 16, 52 - h, bx + i * 16 + 10, 52], radius=2, fill=(0, 0, 0))
    # wifi: three stacked arcs
    wx, wy = W - 176, 50
    for rr, wd in ((30, 6), (20, 6), (10, 6)):
        d.arc([wx - rr, wy - rr, wx + rr, wy + rr], 220, 320, fill=(0, 0, 0), width=wd)
    d.ellipse([wx - 4, wy - 4, wx + 4, wy + 4], fill=(0, 0, 0))
    d.rounded_rectangle([W - 96, 26, W - 40, 50], radius=6, outline=(0, 0, 0), width=3)
    d.rounded_rectangle([W - 92, 30, W - 62, 46], radius=3, fill=(0, 0, 0))
    d.rounded_rectangle([W - 38, 33, W - 33, 43], radius=2, fill=(0, 0, 0))


def _navbar(d, y=84):
    d.line([(60, y + 14), (40, y + 30), (60, y + 46)], fill=NOTES_YELLOW, width=6, joint="curve")
    d.text((74, y + 8), "Notes", font=font(38), fill=NOTES_YELLOW)
    cx = W - 92
    d.ellipse([cx - 26, y + 4, cx + 26, y + 56], outline=NOTES_YELLOW, width=5)
    for dx in (-11, 0, 11):
        d.ellipse([cx + dx - 3, y + 27, cx + dx + 3, y + 33], fill=NOTES_YELLOW)


def _bottombar(d):
    y = H - 96
    d.line([(0, y - 30), (W, y - 30)], fill=(232, 232, 234), width=2)
    # checklist
    x = 70
    for oy in (0, 26):
        d.ellipse([x, y + oy, x + 18, y + oy + 18], outline=NOTES_YELLOW, width=4)
        d.line([(x + 30, y + oy + 9), (x + 78, y + oy + 9)], fill=NOTES_YELLOW, width=4)
    # camera
    cx = W // 2 - 150
    d.rounded_rectangle([cx, y, cx + 70, y + 50], radius=10, outline=NOTES_YELLOW, width=4)
    d.ellipse([cx + 22, y + 12, cx + 48, y + 38], outline=NOTES_YELLOW, width=4)
    # pen in circle
    px = W // 2 + 60
    d.ellipse([px, y, px + 50, y + 50], outline=NOTES_YELLOW, width=4)
    d.line([(px + 16, y + 34), (px + 34, y + 16)], fill=NOTES_YELLOW, width=4)
    # compose
    ex = W - 150
    d.line([(ex, y + 46), (ex + 40, y + 6)], fill=NOTES_YELLOW, width=6)
    d.line([(ex + 40, y + 6), (ex + 52, y + 18), (ex + 12, y + 58), (ex, y + 46)],
           fill=NOTES_YELLOW, width=5, joint="curve")


def render(title, lines, out, emojis="", bullet="circle", dark=False):
    bg = (28, 28, 30) if dark else (255, 255, 255)
    ink = (40, 40, 42) if dark else (44, 44, 46)
    grey = (150, 150, 155)
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    if not dark:
        _statusbar(d)
    _navbar(d)

    x0, y = 60, 190
    tf = font(70, bold=True)
    for line in _wrap(d, title, tf, W - 2 * x0):
        draw_rich(d, canvas, (x0, y), line, tf, (26, 26, 28), emoji_size=64)
        y += 92
    # emoji cluster row under the title (decorative — NOT per-bullet)
    if emojis:
        draw_rich(d, canvas, (x0 + 4, y), emojis, font(46), grey, emoji_size=52)
        y += 76
    else:
        y += 12

    bf = font(46)
    tx = x0 + 82  # text start after the bullet marker
    for line in lines:
        segs = _wrap(d, line, bf, W - tx - x0)
        # bullet marker on the first wrapped segment
        if bullet == "dash":
            d.text((x0 + 6, y - 2), "–", font=font(48), fill=grey)
        else:
            d.ellipse([x0 + 6, y + 8, x0 + 44, y + 46], outline=(178, 178, 182), width=4)
        for k, seg in enumerate(segs):
            draw_rich(d, canvas, (tx, y), seg, bf, ink)
            y += 70
        y += 8
    _bottombar(d)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)
    return out


def _wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if _rich_width(d, t, fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--emojis", default="")
    ap.add_argument("--bullet", choices=["circle", "dash"], default="circle")
    ap.add_argument("--lines", nargs="+", required=True)
    ap.add_argument("--out", default="staging/overnight/assets/_samples/iphone_notes.png")
    ap.add_argument("--dark", action="store_true")
    a = ap.parse_args()
    print("wrote", render(a.title, a.lines, a.out, a.emojis, a.bullet, a.dark))


if __name__ == "__main__":
    main()
