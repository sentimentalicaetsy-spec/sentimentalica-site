"""Render the 10-pin bundle for 091_Vivid_Medley — ready-to-go pictures.
Maps PIN_STRATEGY types -> real 1000x1500 compositions on REAL listing images.
Pure PIL. Output: ~/sentimentalica-site/refs/mockups/091_Vivid_Medley/"""
import colorsys
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

SRC = Path("/Users/kseniateter/My Drive/Sentimentalica/Sentimentalica_01/00_LISTED/091_Vivid_Medley/Vivid Medley")
OUT = Path("/Users/kseniateter/sentimentalica-site/refs/mockups/091_Vivid_Medley")
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1000, 1500

CREAM = (250, 243, 230); PAPER = (243, 233, 210); NAVY = (22, 48, 135)
INK = (42, 42, 58); ACCENT = (184, 149, 106); ROSE = (196, 123, 123); WHITE = (255, 255, 255)
YESEVA = "/Users/kseniateter/sentimentalica-pipeline/config/fonts/YesevaOne-Regular.ttf"
GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEO_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
def F(p, s): return ImageFont.truetype(p, s)

imgs = sorted(SRC.glob("*.jpg"))
random.seed(11)
POOL = random.sample(imgs, 40)
def load(p, box): return ImageOps.fit(Image.open(p).convert("RGB"), box, Image.LANCZOS)

def card(im, border=10, radius=18):
    w, h = im.size
    c = Image.new("RGB", (w + border*2, h + border*2), WHITE)
    c.paste(im, (border, border))
    m = Image.new("L", c.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, c.size[0]-1, c.size[1]-1], radius, fill=255)
    o = Image.new("RGBA", c.size, (0, 0, 0, 0)); o.paste(c, (0, 0), m)
    return o

def shadow_paste(cv, crd, xy, blur=14, alpha=90, off=(8, 12)):
    sh = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    a = crd.split()[3].point(lambda p: alpha if p > 0 else 0)
    s = Image.new("RGBA", crd.size, (30, 25, 20, 0)); s.putalpha(a)
    sh.paste(s, (xy[0]+off[0], xy[1]+off[1]), s)
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    cv.alpha_composite(crd.convert("RGBA"), xy)

def T(d, xy, text, font, fill, anchor="mm"):
    d.text(xy, text, font=font, fill=fill, anchor=anchor)

def wordmark(d, cx, y, color=NAVY):
    T(d, (cx, y), "SENTIMENTALICA", F(GEO_B, 23), color)
    d.text((cx, y+21), "junk journal & watercolor printables", font=F(GEO_I, 17),
           fill=ACCENT, anchor="ma")

def cta(d, cy, label, fill=NAVY, tcol=WHITE, w=420):
    d.rounded_rectangle([(W-w)//2, cy, (W+w)//2, cy+84], 42, fill=fill)
    T(d, (W//2, cy+42), label, F(GEO_B, 32), tcol)

def canvas(bg=CREAM): return Image.new("RGBA", (W, H), bg + (255,))

# ── real palette extraction ───────────────────────────────────────────────────
def listing_palette(n=6):
    strip = Image.new("RGB", (300*6, 300))
    for i, p in enumerate(random.sample(POOL, 6)):
        strip.paste(load(p, (300, 300)), (i*300, 0))
    q = strip.quantize(colors=24)
    pal = q.getpalette(); counts = sorted(q.getcolors(), reverse=True)
    picked = []
    for _, idx in counts:
        r, g, b = pal[idx*3:idx*3+3]
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        if l < 0.12 or l > 0.96: continue
        if all(abs(r-pr)+abs(g-pg)+abs(b-pb) > 110 for pr, pg, pb in picked):
            picked.append((r, g, b))
        if len(picked) == n: break
    return picked

NAMES = [("Dusty Blue",(96,119,160)),("Deep Navy",(35,48,90)),("Coral",(214,116,98)),
         ("Blush",(226,180,170)),("Sage",(148,164,128)),("Antique Cream",(238,226,200)),
         ("Terracotta",(186,101,71)),("Plum",(112,72,110)),("Golden Ochre",(206,164,92)),
         ("Teal",(64,124,128)),("Rose",(196,123,123)),("Olive",(120,120,70))]
def name_of(c):
    return min(NAMES, key=lambda n: sum((a-b)**2 for a, b in zip(n[1], c)))[0]

# ═══ 1. Problem Solver ════════════════════════════════════════════════════════
def pin01():
    cv = canvas(PAPER); d = ImageDraw.Draw(cv)
    T(d, (W//2, 130), "Your journal", F(YESEVA, 96), NAVY)
    T(d, (W//2, 235), "feels flat?", F(YESEVA, 96), NAVY)
    T(d, (W//2, 330), "add watercolor mood & instant layers", F(GEO_I, 32), INK)
    hero = card(load(POOL[0], (560, 560)))
    shadow_paste(cv, hero, (210, 420))
    for (x, y, r), p in zip([(40, 470, -10), (700, 520, 9), (90, 800, 7), (680, 860, -8)], POOL[1:5]):
        c = card(load(p, (240, 240))).rotate(r, expand=True, resample=Image.BICUBIC)
        shadow_paste(cv, c, (x, y))
    d = ImageDraw.Draw(cv)
    cta(d, 1240, "Save this for your next spread »", w=640)
    wordmark(d, W//2, 1400)
    cv.convert("RGB").save(OUT/"pin01_problem_solver.png")

# ═══ 2. Stuck on what to create ═══════════════════════════════════════════════
def pin02():
    cv = canvas(NAVY); d = ImageDraw.Draw(cv)
    T(d, (W//2, 150), "Stuck on what", F(YESEVA, 92), CREAM)
    T(d, (W//2, 250), "to create?", F(YESEVA, 92), CREAM)
    T(d, (W//2, 470), "30", F(YESEVA, 260), (247, 205, 120))
    T(d, (W//2, 660), "journal theme ideas", F(GEO_B, 46), WHITE)
    T(d, (W//2, 718), "for every mood & season", F(GEO_I, 32), (200, 210, 240))
    for i, p in enumerate(POOL[5:9]):
        c = card(load(p, (210, 210)), border=8, radius=14)
        c = c.rotate((-7, 6, -5, 8)[i], expand=True, resample=Image.BICUBIC)
        shadow_paste(cv, c, (35 + i*242, 800), alpha=120)
    d = ImageDraw.Draw(cv)
    cta(d, 1150, "Pick one & start today »", fill=(247, 205, 120), tcol=NAVY, w=540)
    wordmark(d, W//2, 1330, color=CREAM)
    cv.convert("RGB").save(OUT/"pin02_stuck_ideas.png")

# ═══ 3. List / Ideas ═════════════════════════════════════════════════════════
def pin03():
    cv = canvas(CREAM); d = ImageDraw.Draw(cv)
    T(d, (W//2, 120), "25 Colorful", F(YESEVA, 88), NAVY)
    T(d, (W//2, 215), "Collage Ideas", F(YESEVA, 88), NAVY)
    T(d, (W//2, 300), "for bright, maximalist journal pages", F(GEO_I, 30), INK)
    items = ["rainbow paper mosaic strips", "one bold bird as the hero",
             "layered petals + tiny type", "a full-page pattern background",
             "frame a quote with florals", "…and 20 more ideas inside"]
    y = 400
    for i, t in enumerate(items, 1):
        d.ellipse([90, y-6, 134, y+38], fill=NAVY if i < 6 else ACCENT)
        T(d, (112, y+16), str(i) if i < 6 else "+", F(GEO_B, 26), WHITE)
        T(d, (160, y+16), t, F(GEO, 34) if i < 6 else F(GEO_I, 34),
          INK if i < 6 else ACCENT, anchor="lm")
        y += 78
    for (x, yy, r), p in zip([(640, 900, 8), (330, 940, -7), (60, 900, 5)], POOL[9:12]):
        c = card(load(p, (280, 280))).rotate(r, expand=True, resample=Image.BICUBIC)
        shadow_paste(cv, c, (x, yy))
    d = ImageDraw.Draw(cv)
    cta(d, 1270, "Save this idea list »", w=520)
    wordmark(d, W//2, 1410)
    cv.convert("RGB").save(OUT/"pin03_list_ideas.png")

# ═══ 4. Aesthetic Match ═══════════════════════════════════════════════════════
def pin04():
    cv = canvas(); hero = load(POOL[12], (W, 1000)); cv.paste(hero, (0, 0))
    grad = Image.new("L", (1, 260))
    for i in range(260): grad.putpixel((0, i), int(255 * i / 259))
    ov = Image.new("RGBA", (W, 260), CREAM + (255,))
    ov.putalpha(grad.resize((W, 260)))
    cv.alpha_composite(ov, (0, 740))
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 1000, W, H], fill=CREAM)
    T(d, (W//2, 1080), "For colorful", F(YESEVA, 92), NAVY)
    T(d, (W//2, 1180), "collage makers", F(YESEVA, 92), NAVY)
    T(d, (W//2, 1265), "vivid watercolor art in one pack", F(GEO_I, 32), INK)
    cta(d, 1310, "Try this mood »", w=440)
    wordmark(d, W//2, 1450)
    cv.convert("RGB").save(OUT/"pin04_aesthetic_match.png")

# ═══ 5. Color Palette ═════════════════════════════════════════════════════════
def pin05():
    cv = canvas(CREAM)
    bg = load(POOL[13], (W, 620)).filter(ImageFilter.GaussianBlur(2))
    bg = Image.blend(bg, Image.new("RGB", bg.size, CREAM), 0.35)
    cv.paste(bg, (0, 0))
    d = ImageDraw.Draw(cv)
    T(d, (W//2, 120), "Vivid Medley", F(YESEVA, 90), NAVY)
    T(d, (W//2, 210), "Color Palette", F(YESEVA, 90), NAVY)
    T(d, (W//2, 292), "for journals, cards & printables", F(GEO_I, 30), INK)
    pal = listing_palette(6)
    sw, gap, x0, y0 = 128, 24, (W - 6*128 - 5*24)//2, 400
    for i, c in enumerate(pal):
        x = x0 + i*(sw+gap)
        d.rounded_rectangle([x, y0, x+sw, y0+sw], 20, fill=c, outline=WHITE, width=5)
        T(d, (x+sw//2, y0+sw+34), name_of(c), F(GEO, 21), INK)
    for i, p in enumerate(POOL[14:18]):
        c = card(load(p, (208, 208)), border=8, radius=14)
        shadow_paste(cv, c, (28 + i*242, 660))
    d = ImageDraw.Draw(cv)
    T(d, (W//2, 960), "every shade pulled from the real pages", F(GEO_I, 28), ACCENT)
    cta(d, 1180, "Save this palette »", w=480)
    wordmark(d, W//2, 1340)
    cv.convert("RGB").save(OUT/"pin05_color_palette.png")

# ═══ 6. Theme Board ═══════════════════════════════════════════════════════════
def pin06():
    cv = canvas(PAPER); d = ImageDraw.Draw(cv)
    T(d, (W//2, 110), "Vivid Medley", F(YESEVA, 84), NAVY)
    T(d, (W//2, 190), "· journal theme board ·", F(GEO_I, 34), ACCENT)
    cells = [(40, 260, 440, 440), (500, 260, 460, 300), (500, 580, 220, 220),
             (740, 580, 220, 220), (40, 720, 210, 210), (270, 720, 210, 210)]
    for (x, y, w, h), p in zip(cells, POOL[18:24]):
        shadow_paste(cv, card(load(p, (w, h)), border=8, radius=14), (x, y), alpha=70)
    d = ImageDraw.Draw(cv)
    for i, kw in enumerate(["vivid", "playful", "maximalist", "bold", "joyful"]):
        x = 85 + i*175
        d.rounded_rectangle([x, 990, x+160, 1046], 28, outline=NAVY, width=3)
        T(d, (x+80, 1018), kw, F(GEO_I, 27), NAVY)
    pal = listing_palette(6)
    for i, c in enumerate(pal):
        d.rectangle([120 + i*128, 1090, 120 + i*128 + 118, 1150], fill=c)
    cta(d, 1220, "Use this theme next »", w=540)
    wordmark(d, W//2, 1380)
    cv.convert("RGB").save(OUT/"pin06_theme_board.png")

# ═══ 7. Collection Variety (chaos) ═══════════════════════════════════════════
def pin07():
    cv = canvas(PAPER)
    spots = [(50, 60, 300, 300, -11), (400, 30, 330, 330, 8), (140, 330, 340, 340, 6),
             (520, 350, 330, 330, -9), (60, 640, 300, 300, 10), (430, 680, 340, 340, -6)]
    for (x, y, w, h, r), p in zip(spots, POOL[24:30]):
        c = card(load(p, (w, h))).rotate(r, expand=True, resample=Image.BICUBIC)
        shadow_paste(cv, c, (x, y))
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 1040, W, 1240], fill=NAVY)
    T(d, (W//2, 1105), "One collection,", F(YESEVA, 72), WHITE)
    T(d, (W//2, 1185), "endless project ideas", F(YESEVA, 58), (247, 205, 120))
    cta(d, 1280, "Explore the collection »", w=580, fill=ACCENT)
    wordmark(d, W//2, 1430)
    cv.convert("RGB").save(OUT/"pin07_variety.png")

# ═══ 8. Close-Up Detail ═══════════════════════════════════════════════════════
def pin08():
    cv = canvas(CREAM); d = ImageDraw.Draw(cv)
    T(d, (W//2, 110), "Tiny details for", F(YESEVA, 80), NAVY)
    T(d, (W//2, 195), "beautiful projects", F(YESEVA, 80), NAVY)
    T(d, (W//2, 275), "watercolor textures, florals & art", F(GEO_I, 30), INK)
    for i, p in enumerate(POOL[30:34]):
        im = Image.open(p).convert("RGB")
        w2, h2 = im.size
        crop = im.crop((w2//4, h2//4, w2*3//4, h2*3//4)).resize((440, 440), Image.LANCZOS)
        x, y = 40 + (i % 2)*480, 350 + (i//2)*480
        shadow_paste(cv, card(crop, border=10, radius=16), (x, y), alpha=70)
    d = ImageDraw.Draw(cv)
    cta(d, 1330, "Save for detail inspiration »", w=640)
    wordmark(d, W//2, 1450)
    cv.convert("RGB").save(OUT/"pin08_closeup.png")

# ═══ 9. Etsy Seller Product Ideas ═════════════════════════════════════════════
def pin09():
    cv = canvas(CREAM); d = ImageDraw.Draw(cv)
    T(d, (W//2, 120), "Need art for your", F(YESEVA, 82), NAVY)
    T(d, (W//2, 208), "next Etsy product?", F(YESEVA, 82), NAVY)
    T(d, (W//2, 292), "commercial-use watercolor image pack", F(GEO_I, 30), INK)
    mock = [("wall art", POOL[34]), ("greeting card", POOL[35]),
            ("journal cover", POOL[36]), ("digital download", POOL[37])]
    for i, (label, p) in enumerate(mock):
        x, y = 60 + (i % 2)*450, 370 + (i//2)*430
        d.rounded_rectangle([x, y, x+430, y+360], 16, fill=WHITE, outline=(216, 203, 184), width=2)
        cv.alpha_composite(card(load(p, (330, 240)), border=6, radius=10).convert("RGBA"), (x+44, y+28))
        d = ImageDraw.Draw(cv)
        T(d, (x+215, y+320), label, F(GEO_B, 27), ACCENT)
    cta(d, 1280, "Create your next product faster »", w=720)
    wordmark(d, W//2, 1430)
    cv.convert("RGB").save(OUT/"pin09_etsy_seller.png")

# ═══ 10. Keyword SEO grid ═════════════════════════════════════════════════════
def pin10():
    cv = canvas(WHITE); d = ImageDraw.Draw(cv)
    T(d, (W//2, 105), "Colorful Watercolor", F(YESEVA, 76), NAVY)
    T(d, (W//2, 185), "Images for Creators", F(YESEVA, 76), NAVY)
    T(d, (W//2, 262), "commercial-use printable image pack", F(GEO_B, 30), ACCENT)
    for i, p in enumerate(POOL[2:11]):
        x, y = 45 + (i % 3)*310, 330 + (i//3)*310
        cv.alpha_composite(card(load(p, (280, 280)), border=6, radius=12).convert("RGBA"), (x, y))
    d = ImageDraw.Draw(cv)
    T(d, (W//2, 1310), "200+ images · print at home · use in your projects", F(GEO_I, 28), INK)
    cta(d, 1345, "View the full image pack »", w=620)
    wordmark(d, W//2, 1478)
    cv.convert("RGB").save(OUT/"pin10_seo_grid.png")

for fn in (pin01, pin02, pin03, pin04, pin05, pin06, pin07, pin08, pin09, pin10):
    fn()
print("rendered:", len(list(OUT.glob("pin*.png"))), "pins ->", OUT)
