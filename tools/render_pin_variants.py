#!/usr/bin/env python3
"""Render three branded 2:3 Pinterest variants from an article's two visuals.

The article images stay editorial and unbranded where required. These derived
assets are the marketing layer: mobile-readable promise, restrained branding,
and a distinct composition for each pin.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SIZE = (1000, 1500)
NAVY = (22, 48, 135)
CREAM = (250, 243, 230)
INK = (43, 36, 22)
ROSE = (190, 122, 126)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
             "/System/Library/Fonts/Supplemental/Georgia.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS,
                        centering=(0.5, 0.5))


def contain(image: Image.Image, size: tuple[int, int], background=CREAM) -> Image.Image:
    canvas = Image.new("RGB", size, background)
    fitted = ImageOps.contain(image.convert("RGB"), size, Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    return canvas


def wrap(draw: ImageDraw.ImageDraw, text: str, text_font, max_width: int) -> list[str]:
    words = text.upper().split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


def centered_text(draw, box, text, text_font, fill, spacing=10):
    x0, y0, x1, y1 = box
    lines = wrap(draw, text, text_font, x1 - x0)
    heights = [draw.textbbox((0, 0), line, font=text_font)[3] for line in lines]
    total = sum(heights) + spacing * max(0, len(lines) - 1)
    y = y0 + ((y1 - y0) - total) // 2
    for line, height in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=text_font)[2]
        draw.text((x0 + ((x1 - x0) - width) // 2, y), line, font=text_font, fill=fill)
        y += height + spacing


def brand_footer(canvas: Image.Image, label: str = "sentimentalica.com") -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 1400, 1000, 1500), fill=(*NAVY, 255))
    fnt = font(30, bold=True)
    width = draw.textbbox((0, 0), label, font=fnt)[2]
    draw.text(((1000 - width) // 2, 1431), label, font=fnt, fill=CREAM)


def render_guide(primary: Image.Image, headline: str, overlay: bool = False,
                 detail: str = "") -> Image.Image:
    canvas = Image.new("RGB", SIZE, CREAM)
    if overlay:
        draw = ImageDraw.Draw(canvas)
        centered_text(draw, (65, 40, 935, 340), headline, font(62, bold=True), NAVY, 12)
        canvas.paste(contain(primary, (1000, 830 if detail else 1020), CREAM), (0, 370))
        if detail:
            centered_text(draw, (60, 1220, 940, 1380), detail, font(44, bold=True), NAVY, 8)
    else:
        return cover(primary, SIZE)
    brand_footer(canvas)
    return canvas


def render_mood(mood: Image.Image, headline: str) -> Image.Image:
    canvas = cover(mood, SIZE)
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((65, 860, 935, 1320), radius=28, fill=(18, 34, 78, 220))
    centered_text(draw, (115, 915, 885, 1265), headline, font(66, bold=True), CREAM, 14)
    brand_footer(canvas)
    return canvas


def render_split(primary: Image.Image, mood: Image.Image, headline: str,
                 label: str = "FREE PRACTICE PICTURES INSIDE") -> Image.Image:
    canvas = Image.new("RGB", SIZE, CREAM)
    canvas.paste(cover(mood, (1000, 960)), (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 960, 1000, 1500), fill=(*CREAM, 255))
    draw.rectangle((0, 960, 18, 1500), fill=(*ROSE, 255))
    centered_text(draw, (70, 985, 930, 1330), headline, font(62, bold=True), INK, 12)
    fnt = font(25, bold=True)
    width = draw.textbbox((0, 0), label, font=fnt)[2]
    draw.text(((1000 - width) // 2, 1355), label, font=fnt, fill=NAVY)
    brand_footer(canvas)
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--headline", required=True)
    parser.add_argument("--mood-headline", required=True)
    parser.add_argument("--cta-headline", default="TRY THIS WITH FREE FLORALS")
    parser.add_argument("--primary", type=Path, help="Explicit existing guide or palette source")
    parser.add_argument("--mood", type=Path, help="Explicit existing atmospheric source")
    parser.add_argument("--practice-source", type=Path,
                        help="Existing process photo for the practice variant")
    parser.add_argument("--guide-overlay", action="store_true",
                        help="Add the guide promise when the source has no title")
    parser.add_argument("--guide-detail", default="",
                        help="Short article-specific method beneath a photo guide")
    parser.add_argument("--cta-label", default="FREE PRACTICE PICTURES INSIDE")
    parser.add_argument("--filenames", choices=("legacy", "journal"), default="legacy",
                        help="Use neutral journal filenames for a new inventory")
    args = parser.parse_args()

    for label, value in (("mood headline", args.mood_headline),
                         ("CTA headline", args.cta_headline)):
        count = len(value.split())
        if not 4 <= count <= 9:
            raise SystemExit(f"{label} must contain 4-9 mobile-readable words; got {count}")

    article_dir = ROOT / "public/blog/img" / args.slug
    primary_candidates = [article_dir / "gen1.png", article_dir / "gen1.jpg"]
    primary_path = args.primary or next((p for p in primary_candidates if p.exists()), None)
    mood_path = args.mood or next((article_dir / name for name in ("gen2.jpg", "gen2.png")
                                  if (article_dir / name).exists()), None)
    if not primary_path or not primary_path.exists() or not mood_path or not mood_path.exists():
        raise SystemExit(f"Missing gen1/gen2 assets for {args.slug}")

    primary = Image.open(primary_path)
    mood = Image.open(mood_path)
    practice = Image.open(args.practice_source) if args.practice_source else mood
    output = article_dir / "pins"
    output.mkdir(exist_ok=True)
    outputs = [
        (output / f"{args.slug}-step-by-step-guide.jpg",
         render_guide(primary, args.headline, args.guide_overlay, args.guide_detail)),
        (output / f"{args.slug}-{'journal-inspiration' if args.filenames == 'journal' else 'cozy-seasonal-idea'}.jpg",
         render_mood(mood, args.mood_headline)),
        (output / f"{args.slug}-{'paper-practice-idea' if args.filenames == 'journal' else 'free-practice-idea'}.jpg",
         render_split(primary, practice, args.cta_headline, args.cta_label)),
    ]
    for path, image in outputs:
        image.save(path, "JPEG", quality=92, optimize=True, progressive=True)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
