#!/usr/bin/env python3
"""Render a branded Sentimentalica infographic (blue #163087 on cream + dove).

The default infographic style (see refs/branding/BRAND.md): cream paper base,
brand-blue display title, a script sub-banner, a grid of soft cream cards with
blue headers + heart-bulleted items, the dove logo in a corner, and a script CTA.
The decorative background (blue florals/washi around the edges) is SD-generated
into refs/.../brand_infobg.jpg; if missing, a plain cream base is used.

This is iteration 1 — approximates the brand feeling; fonts are system (no bubbly
brand face yet). Text is composited by CODE (never SD) so it stays crisp.

Usage: python tools/render_brand_infographic.py  (renders the demo)
       or import render(title, subtitle, sections, cta, out, bg=..., logo=...)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = Path(__file__).resolve().parent.parent
W, H = 1024, 1536
BLUE = (22, 48, 135)          # #163087 brand blue
BLUE_SOFT = (86, 116, 196)
CREAM = (250, 246, 238)
CARD = (255, 253, 248)
INK = (60, 60, 66)
SNELL = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SF = "/System/Library/Fonts/SFNS.ttf"
HELV = "/System/Library/Fonts/Helvetica.ttc"
LOGO = REPO / "refs" / "branding" / "logo.png"


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


def script(size):
    try:
        return ImageFont.truetype(SNELL, size, index=0)
    except Exception:
        return font(size)


def _wrap(d, text, fnt, maxw):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


def _centered(d, text, fnt, cx, y, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def _heart(d, cx, cy, s, color):
    r = s / 2
    d.ellipse([cx - r, cy - r, cx, cy], fill=color)
    d.ellipse([cx, cy - r, cx + r, cy], fill=color)
    d.polygon([(cx - r, cy - r / 4), (cx + r, cy - r / 4), (cx, cy + r)], fill=color)


def _card(canvas, x, y, w, header, items):
    d = ImageDraw.Draw(canvas)
    # measure height
    hf, itf = font(34, bold=True), font(27)
    pad = 30
    inner = w - 2 * pad
    lines = []
    for it in items:
        segs = _wrap(d, it, itf, inner - 40)
        lines.append(segs)
    body_h = sum(len(s) * 36 + 12 for s in lines)
    h = pad + 48 + 16 + body_h + pad
    # shadow + card
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x + 6, y + 10, x + w + 6, y + h + 10],
                                         radius=26, fill=(22, 48, 135, 40))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=CARD,
                        outline=(224, 231, 246), width=2)
    # header
    d.text((x + pad, y + pad), header.upper(), font=hf, fill=BLUE)
    cy = y + pad + 60
    for segs in lines:
        _heart(d, x + pad + 8, cy + 16, 20, BLUE_SOFT)
        for k, seg in enumerate(segs):
            d.text((x + pad + 36, cy), seg, font=itf, fill=INK)
            cy += 36
        cy += 12
    return h


def render(title, subtitle, sections, cta, out,
           bg=REPO / "staging/overnight/assets/_samples/brand_infobg.jpg"):
    base = Image.new("RGB", (W, H), CREAM)
    if bg and Path(bg).exists():
        b = Image.open(bg).convert("RGB").resize((W, H), Image.LANCZOS)
        base = Image.blend(base, b, 0.85)
        # lighten the center so text/cards read
        veil = Image.new("RGB", (W, H), CREAM)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([-160, 120, W + 160, H - 60], fill=170)
        base = Image.composite(veil, base, m.filter(ImageFilter.GaussianBlur(80)))
    canvas = base.convert("RGBA")
    d = ImageDraw.Draw(canvas)

    # dove logo, top-right
    if LOGO.exists():
        lg = Image.open(LOGO).convert("RGBA")
        lg.thumbnail((150, 150), Image.LANCZOS)
        canvas.alpha_composite(lg, (W - lg.width - 54, 46))

    # title (blue, bold, wraps, centered)
    tf = font(78, bold=True)
    y = 70
    for line in _wrap(d, title, tf, W - 260):
        _centered(d, line, tf, W / 2 - 40, y, BLUE)
        y += 88
    # script sub-banner
    if subtitle:
        sf = script(52)
        bw = d.textlength(subtitle, font=sf) + 80
        d.rounded_rectangle([W / 2 - bw / 2, y + 6, W / 2 + bw / 2, y + 74],
                            radius=34, fill=BLUE)
        _centered(d, subtitle, sf, W / 2, y + 8, (255, 255, 255))
        y += 104

    # two-column card grid
    margin, gap = 54, 30
    colw = (W - 2 * margin - gap) / 2
    colx = [margin, margin + colw + gap]
    coly = [y, y]
    for i, (header, items) in enumerate(sections):
        c = 0 if coly[0] <= coly[1] else 1
        hh = _card(canvas, colx[c], coly[c], colw, header, items)
        coly[c] += hh + gap

    # CTA script at the bottom (+ a real heart, not a font glyph)
    yb = min(max(coly) + 10, H - 120)
    cf = script(60)
    cta = cta.replace("♥", "").strip()
    tw = d.textlength(cta, font=cf)
    tx = W / 2 - (tw + 46) / 2
    d.text((tx, yb), cta, font=cf, fill=BLUE)
    _heart(d, tx + tw + 34, yb + 42, 34, BLUE)
    d.line([(W / 2 - 210, yb + 84), (W / 2 + 210, yb + 84)], fill=BLUE_SOFT, width=3)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=92)
    return out


if __name__ == "__main__":
    demo = render(
        "What is a Junk Journal?",
        "collect moments, not things",
        [("Signatures", ["Folded pages stitched together —", "they form the spine of your journal."]),
         ("Ephemera", ["Loose found paper and treasures", "that add beauty and meaning."]),
         ("Pockets", ["Tucked-in spots that hold tags,", "notes and little surprises."]),
         ("Tags", ["Pull-out pieces for journaling,", "listing or hidden meaning."])],
        "check out my shop  ♥",
        "staging/overnight/assets/_samples/brand_infographic_demo.jpg")
    print("wrote", demo)
