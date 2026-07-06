#!/usr/bin/env python3
"""Insert SD-generated images into published articles (day-2 of the overnight plan).

Overnight, each article was published with invisible slot markers:
    <!-- genimg:gen1 -->
and a prompts file staging/overnight/prompts/<slug>.json:
    {"slug": ..., "slots": [{"id": "gen1", "prompt": ..., "negative": ...,
                             "width": 1216, "height": 832, "caption": ...}]}

This tool, for each prompts file:
  1. Generates each slot via local A1111 (http://127.0.0.1:7860) — SDXL.
  2. Saves to public/blog/img/<slug>/<id>.jpg (resized <=1200px, q80).
  3. Replaces the marker in public/blog/<slug>.html with an <img> tag.
Idempotent: slots whose image already exists are skipped. Run with --push
to commit+deploy at the end.

Usage: python3 tools/insert_generated_images.py [--slug one-slug] [--push] [--dry-run]
"""
import argparse
import base64
import io
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG = REPO / "public" / "blog"
PROMPTS = REPO / "staging" / "overnight" / "prompts"
A1111 = "http://127.0.0.1:7860"

DEFAULT_NEG = ("text, watermark, logo, low quality, blurry, deformed hands, "
               "extra fingers, cartoon, anime, oversaturated")


def generate(prompt, negative, width, height):
    import requests
    payload = {
        "prompt": prompt,
        "negative_prompt": negative or DEFAULT_NEG,
        "width": width, "height": height,
        "steps": 28, "cfg_scale": 6.5, "sampler_name": "DPM++ 2M Karras",
    }
    r = requests.post(f"{A1111}/sdapi/v1/txt2img", json=payload, timeout=600)
    r.raise_for_status()
    img_b64 = r.json()["images"][0]
    return base64.b64decode(img_b64)


MOCKUP_SCENE_PROMPT = (
    "top-down flat lay photograph of a cozy craft desk, warm natural window "
    "light, wooden surface with a linen cloth, scissors, washi tape, dried "
    "flowers and a cup of tea arranged around the EDGES of the frame, large "
    "EMPTY clear space in the center, soft shadows, photorealistic, {mood}"
)


def composite_print(scene_img, art_path):
    """Paste a real listing page onto the generated desk scene like a print:
    thin paper border, slight rotation, soft drop shadow, centered."""
    from PIL import Image, ImageFilter, ImageOps
    art = Image.open(art_path).convert("RGB")
    border = max(6, int(max(art.size) * 0.018))
    printed = ImageOps.expand(art, border=border, fill=(252, 250, 245))
    target_h = int(scene_img.height * 0.74)
    ratio = target_h / printed.height
    printed = printed.resize((int(printed.width * ratio), target_h), Image.LANCZOS)
    printed = printed.convert("RGBA").rotate(
        -3.5, expand=True, resample=Image.BICUBIC)
    # soft shadow from the print's silhouette
    a = printed.split()[3].point(lambda v: 110 if v > 0 else 0)
    sh = Image.new("RGBA", printed.size, (25, 18, 10, 0))
    sh.putalpha(a)
    canvas = scene_img.convert("RGBA")
    x = (canvas.width - printed.width) // 2
    y = (canvas.height - printed.height) // 2
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer.paste(sh, (x + 10, y + 14), sh)
    canvas.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(10)))
    canvas.alpha_composite(printed, (x, y))
    return canvas.convert("RGB")


def main():
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--remake", help="slug:slotid — regenerate one slot even if "
                                     "its image already exists (html untouched)")
    args = ap.parse_args()

    files = sorted(PROMPTS.glob("*.json"))
    if args.slug:
        files = [f for f in files if f.stem == args.slug]
    if not files:
        sys.exit("no prompt files found")

    changed = []
    for pf in files:
        spec = json.loads(pf.read_text())
        slug = spec["slug"]
        page = BLOG / f"{slug}.html"
        if not page.exists():
            print(f"SKIP {slug}: page missing")
            continue
        html = page.read_text()
        img_dir = BLOG / "img" / slug
        page_changed = False
        for slot in spec.get("slots", []):
            marker = f"<!-- genimg:{slot['id']} -->"
            remake = args.remake == f"{slug}:{slot['id']}"
            if marker not in html and not remake:
                continue
            target = img_dir / f"{slot['id']}.jpg"
            if not target.exists() or remake:
                if args.dry_run:
                    print(f"[dry] would generate {slug}/{slot['id']}")
                    continue
                print(f"generating {slug}/{slot['id']}"
                      f"{' (mockup)' if slot.get('type') == 'mockup' else ''} ...")
                if slot.get("type") == "mockup":
                    # SD scene with an empty center + the REAL listing page
                    # composited in as a physical print.
                    prompt = MOCKUP_SCENE_PROMPT.format(
                        mood=slot.get("mood", "soft neutral tones"))
                    raw = generate(prompt, slot.get("negative"),
                                   slot.get("width", 1216), slot.get("height", 832))
                    scene = Image.open(io.BytesIO(raw)).convert("RGB")
                    art = img_dir / slot.get("insert_image", "img2.jpg")
                    if not art.exists():
                        print(f"  SKIP mockup: {art} missing")
                        continue
                    im = composite_print(scene, art)
                else:
                    raw = generate(slot["prompt"], slot.get("negative"),
                                   slot.get("width", 1216), slot.get("height", 832))
                    im = Image.open(io.BytesIO(raw)).convert("RGB")
                im.thumbnail((1200, 1200))
                img_dir.mkdir(parents=True, exist_ok=True)
                im.save(target, "JPEG", quality=80, optimize=True)
            if remake and marker not in html:
                changed.append(slug)  # file replaced in place; page already refs it
                print(f"✓ {slug}/{slot['id']} remade")
                continue
            cap = slot.get("caption", "")
            tag = (f'<img src="img/{slug}/{slot["id"]}.jpg" '
                   f'alt="{cap or "junk journal inspiration"}" loading="lazy">')
            html = html.replace(marker, tag)
            page_changed = True
        if page_changed and not args.dry_run:
            page.write_text(html)
            changed.append(slug)
            print(f"✓ {slug}")

    print(f"\nupdated {len(changed)} articles")
    if args.push and changed:
        subprocess.run(["git", "-C", str(REPO), "add", "public"], check=True)
        subprocess.run(["git", "-C", str(REPO), "commit", "-m",
                        f"feat(blog): insert generated images into {len(changed)} articles"],
                       check=True)
        subprocess.run(["git", "-C", str(REPO), "push"], check=True)


if __name__ == "__main__":
    main()
