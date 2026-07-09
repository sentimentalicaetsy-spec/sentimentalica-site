#!/usr/bin/env python3
"""Render an AUTHENTIC iPhone Notes screenshot as a Pinterest infographic.

Ksenia's special infographic subtype: a graphic that looks like a real iOS Notes
note — status bar, "< Notes" nav, bold title, grey date, casual lines with REAL
colour emoji. Natural, not overdesigned (the one mode that is NOT the branded
paper style). Text is code-rendered; emoji use Apple Color Emoji.

Usage:
  python tools/render_iphone_notes.py --title "..." --lines "line1" "line2" ... \
      [--out path.png] [--dark]
Emoji: put the emoji as the first character(s) of a line, or inline — handled.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SF = "/System/Library/Fonts/SFNS.ttf"
HELV = "/System/Library/Fonts/Helvetica.ttc"
EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI_STRIKE = 48  # a valid Apple Color Emoji bitmap size
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
    """Split a string into ('t', run) text and ('e', ch) emoji tokens."""
    out, buf, i = [], "", 0
    while i < len(text):
        cp = ord(text[i])
        if _is_emoji(cp):
            if buf:
                out.append(("t", buf)); buf = ""
            ch = text[i]; j = i + 1
            while j < len(text) and ord(text[j]) in (0xFE0F, 0x200D) or (
                    j < len(text) and 0x1F3FB <= ord(text[j]) <= 0x1F3FF):
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
    es = emoji_size or int(fnt.size * 1.05)
    ascent = fnt.getbbox("Ag")[3]
    for kind, val in _tokens(text):
        if kind == "t":
            d.text((x, y), val, font=fnt, fill=fill)
            x += int(d.textlength(val, font=fnt))
        else:
            try:
                em = _emoji_img(val, es)
                canvas.paste(em, (x, y + (ascent - es) // 2 + 2), em)
                x += em.width + 6
            except Exception:
                x += es
    return x


def _statusbar(d, canvas):
    d.text((54, 22), "9:41", font=font(34, bold=True), fill=(0, 0, 0))
    # cellular bars
    bx = W - 260
    for i, h in enumerate((10, 16, 22, 28)):
        d.rounded_rectangle([bx + i * 16, 52 - h, bx + i * 16 + 10, 52],
                            radius=2, fill=(0, 0, 0))
    # wifi (three arcs approximated by a filled fan)
    wx = W - 170
    d.pieslice([wx, 24, wx + 46, 70], 200, 340, fill=(0, 0, 0))
    # battery
    d.rounded_rectangle([W - 96, 26, W - 40, 50], radius=6, outline=(0, 0, 0), width=3)
    d.rounded_rectangle([W - 92, 30, W - 52, 46], radius=3, fill=(0, 0, 0))
    d.rounded_rectangle([W - 38, 33, W - 33, 43], radius=2, fill=(0, 0, 0))


def _navbar(d, canvas, y=84):
    d.line([(64, y + 14), (44, y + 30), (64, y + 46)], fill=NOTES_YELLOW, width=6, joint="curve")
    d.text((78, y + 8), "Notes", font=font(38), fill=NOTES_YELLOW)
    # right icons: share + compose (simple glyphs)
    sx = W - 190
    d.rounded_rectangle([sx, y + 12, sx + 44, y + 52], radius=8, outline=NOTES_YELLOW, width=5)
    d.line([(sx + 22, y + 6), (sx + 22, y + 34)], fill=NOTES_YELLOW, width=5)
    d.line([(sx + 12, y + 16), (sx + 22, y + 6), (sx + 32, y + 16)], fill=NOTES_YELLOW, width=5, joint="curve")
    cx = W - 108
    d.line([(cx, y + 48), (cx + 40, y + 8)], fill=NOTES_YELLOW, width=6)
    d.line([(cx + 40, y + 8), (cx + 52, y + 20), (cx + 12, y + 60), (cx - 2, y + 50)],
           fill=NOTES_YELLOW, width=5, joint="curve")


def render(title, lines, out, dark=False):
    bg = (28, 28, 30) if dark else (255, 255, 255)
    ink = (245, 245, 247) if dark else (26, 26, 26)
    grey = (150, 150, 155)
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    if not dark:
        _statusbar(d, canvas)
    _navbar(d, canvas)

    x0, y = 66, 200
    # title (bold, wraps)
    tf = font(64, bold=True)
    for line in _wrap(d, title, tf, W - 2 * x0):
        draw_rich(d, canvas, (x0, y), line, tf, ink)
        y += 82
    # date subtitle (centered grey)
    sub = "Today  9:41"
    sf = font(30)
    d.text(((W - d.textlength(sub, font=sf)) / 2, y + 4), sub, font=sf, fill=grey)
    y += 74
    # body lines
    bf = font(46)
    for line in lines:
        for seg in _wrap(d, line, bf, W - 2 * x0):
            draw_rich(d, canvas, (x0, y), seg, bf, ink)
            y += 74
        y += 12
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)
    return out


def _wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        # emoji count as ~1.3 chars width; approximate with textlength on text-only
        tl = sum(d.textlength(v, font=fnt) if k == "t" else fnt.size * 1.1
                 for k, v in _tokens(t))
        if tl <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--lines", nargs="+", required=True)
    ap.add_argument("--out", default="staging/overnight/assets/_samples/iphone_notes.png")
    ap.add_argument("--dark", action="store_true")
    a = ap.parse_args()
    print("wrote", render(a.title, a.lines, a.out, a.dark))


if __name__ == "__main__":
    main()
