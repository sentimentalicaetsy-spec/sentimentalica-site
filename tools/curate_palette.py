#!/usr/bin/env python3
"""Curate a Sentimentalica 4-color palette from one real listing page.

This is the pre-render palette layer:
- over-extract 10-15 candidates from the actual page image
- reject muddy/neon/near-duplicate candidates
- assign four design roles: Dark Anchor, Strict Light Neutral, Support Mid-tone, Hero Accent
- print JSON plus a render_palette_card.py-ready --palette string

This is intentionally not "dominant colors = palette". It is a taste filter
that prepares good candidates for the vision/LLM curation step, and provides a
solid heuristic fallback when no vision model is available.
"""
from __future__ import annotations

import colorsys
import json
import math
import sys
from pathlib import Path

from PIL import Image


ROLE_NAMES = {
    "anchor": ["Midnight Ink", "Pine Shadow", "Deep Leaf", "Forest Ink", "Barn Shadow"],
    "neutral": ["Paper Cream", "Parchment", "Soft Linen", "Rice Paper", "Warm Paper"],
    "support": ["Sage", "Olive Field", "Smoky Teal", "Mountain Blue", "Leaf Green", "Moss Green", "Roof Blue"],
    "accent": [
        "Rose Blush", "Dusty Rose", "Barn Red", "Candle Amber", "Trail Ochre",
        "Fan Red", "Dusty Blue", "Lavender", "Smoky Teal",
    ],
}

NAME_RGB = {
    "Midnight Ink": (16, 35, 63),
    "Pine Shadow": (53, 75, 54),
    "Deep Leaf": (79, 99, 59),
    "Roof Blue": (125, 156, 154),
    "Forest Ink": (61, 84, 58),
    "Barn Shadow": (105, 54, 42),
    "Paper Cream": (234, 221, 200),
    "Parchment": (230, 208, 168),
    "Soft Linen": (230, 210, 178),
    "Rice Paper": (233, 216, 195),
    "Warm Paper": (232, 216, 199),
    "Sage": (137, 151, 104),
    "Olive Field": (120, 128, 82),
    "Smoky Teal": (95, 143, 134),
    "Mountain Blue": (117, 143, 146),
    "Leaf Green": (86, 107, 66),
    "Moss Green": (82, 102, 64),
    "Roof Blue": (125, 156, 154),
    "Rose Blush": (211, 174, 176),
    "Dusty Rose": (195, 139, 145),
    "Barn Red": (160, 68, 48),
    "Candle Amber": (197, 138, 69),
    "Brass": (184, 135, 76),
    "Trail Ochre": (183, 133, 72),
    "Fan Red": (166, 83, 74),
    "Dusty Blue": (104, 132, 164),
    "Lavender": (168, 152, 190),
}


def rgb_to_hls(rgb):
    r, g, b = [v / 255 for v in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, l, s


def dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def hex_of(rgb):
    return "#%02x%02x%02x" % rgb


def nearest_role_name(role, rgb):
    names = ROLE_NAMES[role]
    return min(names, key=lambda n: dist(NAME_RGB[n], rgb))


def clean_rgb(rgb, role=None):
    """Nudge raw extracted colors into a vintage tonal range."""
    h, l, s = rgb_to_hls(rgb)
    if role == "neutral":
        s = min(max(s, 0.14), 0.34)
        l = max(l, 0.86)
    elif role == "anchor":
        s = min(max(s, 0.18), 0.50)
        l = min(max(l, 0.18), 0.34)
    elif role == "support":
        s = min(max(s, 0.18), 0.46)
        l = min(max(l, 0.38), 0.62)
    else:
        s = min(max(s, 0.24), 0.54)
        l = min(max(l, 0.42), 0.66)
    if 35 <= h <= 65:  # yellow gets cheap fast; soften it.
        s = min(s, 0.42)
        if role == "accent":
            l = min(l, 0.64)
    if 0 <= h <= 15 or h >= 345:  # red should feel vintage, not primary.
        s = min(s, 0.48)
        if role != "neutral":
            l = min(max(l, 0.42), 0.58)
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return tuple(int(v * 255) for v in (r, g, b))


def extract_candidates(path, n=15):
    img = Image.open(path).convert("RGB")
    img.thumbnail((360, 540), Image.Resampling.LANCZOS)
    q = img.quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors() or [], reverse=True)
    out = []
    total = sum(c for c, _ in counts) or 1
    for count, idx in counts:
        rgb = tuple(pal[idx * 3:idx * 3 + 3])
        h, l, s = rgb_to_hls(rgb)
        share = count / total
        # Reject pure shadows, muddy middle greys, and cheap neons. Keep clean
        # highlights because the neutral must be a true light canvas.
        if l < 0.10 or l > 0.985:
            continue
        if s < 0.12 and 0.25 < l < 0.80:
            continue
        if s > 0.78 and l > 0.62:
            continue
        if max(rgb) - min(rgb) < 18:
            continue
        if any(abs(h - x["h"]) < 11 and abs(l - x["l"]) < 0.11 for x in out):
            continue
        out.append({"rgb": rgb, "hex": hex_of(rgb), "h": h, "l": l, "s": s, "share": share})
        if len(out) == n:
            break
    return out


def hue_distance(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def hero_accent_score(c, used_candidates):
    h, l, s = c["h"], c["l"], c["s"]
    used_hues = [u["h"] for u in used_candidates]
    distinct = min([hue_distance(h, uh) for uh in used_hues] or [90])
    # The accent is the hero/focal contrast color, not necessarily warm. It can
    # be dusty pink, barn red, golden ochre, teal, blue, lavender, etc. Prefer
    # hue separation from the anchor/support, enough saturation to read, and
    # meaningful visual share. Avoid using another green/brown just because it
    # appears often.
    is_rose_red = h >= 300 or h <= 30
    is_cool_accent = 185 <= h <= 285 and s >= 0.16
    is_gold_or_ochre = 30 < h <= 50 and s >= 0.32
    is_support_like = 50 < h <= 135
    if is_rose_red:
        hero_family_penalty = 0
    elif is_cool_accent:
        hero_family_penalty = 0.25
    elif is_gold_or_ochre:
        hero_family_penalty = 0.8
    else:
        hero_family_penalty = 1.4
    support_like_penalty = 2 if is_support_like else 0
    contrast_score = 0 if distinct >= 38 else 1
    share_score = 0 if c["share"] >= 0.012 else 1
    return (hero_family_penalty, support_like_penalty, contrast_score, share_score, abs(l - 0.62), -s, -c["share"])


def clean_neutral_score(c):
    h, l, s = c["h"], c["l"], c["s"]
    warm_or_quiet = (18 <= h <= 58) or s < 0.18
    greenish_penalty = 1 if 70 <= h <= 145 and s > 0.10 else 0
    return (0 if l >= 0.80 else 2, greenish_penalty, 0 if warm_or_quiet else 1, s, -l, -c["share"])


def pick_role(candidates, role, used):
    pool = [c for c in candidates if c["hex"] not in used]
    used_candidates = [c for c in candidates if c["hex"] in used]
    if not pool:
        return None
    if role == "anchor":
        scored = sorted(pool, key=lambda c: (0 if c["l"] <= 0.36 else 1, abs(c["l"] - 0.27), -c["s"], -c["share"]))
    elif role == "neutral":
        scored = sorted(pool, key=clean_neutral_score)
    elif role == "support":
        scored = sorted(pool, key=lambda c: (0 if c["share"] >= 0.018 else 1,
                                             0 if 65 <= c["h"] <= 220 else 1,
                                             abs(c["l"] - 0.50), -c["share"]))
    else:
        scored = sorted(pool, key=lambda c: hero_accent_score(c, used_candidates))
    return scored[0]


def curate(path):
    candidates = extract_candidates(path)
    if len(candidates) < 4:
        raise SystemExit(f"Only {len(candidates)} clean candidates found in {path}")
    used = set()
    palette = []
    for role in ("anchor", "neutral", "support", "accent"):
        pick = pick_role(candidates, role, used)
        if not pick:
            continue
        adjusted = clean_rgb(pick["rgb"], role)
        name = nearest_role_name(role, adjusted)
        item = {
            "role": role,
            "name": name,
            "hex": hex_of(adjusted),
            "source_hex": pick["hex"],
            "source_rgb": pick["rgb"],
        }
        palette.append(item)
        used.add(pick["hex"])
    if len(palette) != 4:
        raise SystemExit("Could not curate all four palette roles.")
    return candidates, palette


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: tools/curate_palette.py <actual-listing-page.jpg>")
    path = Path(sys.argv[1])
    candidates, palette = curate(path)
    render_arg = ",".join(f"{p['name']}:{p['hex']}" for p in palette)
    print(json.dumps({
        "image": str(path),
        "candidates": [
            {"hex": c["hex"], "h": round(c["h"], 1), "l": round(c["l"], 3),
             "s": round(c["s"], 3), "share": round(c["share"], 4)}
            for c in candidates
        ],
        "palette": palette,
        "render_palette_arg": render_arg,
    }, indent=2))


if __name__ == "__main__":
    main()
