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

# Realistic scenes/mockups negative. CHANGED 2026-07-09 (see refs/README.md):
# the blanket ban on hands/fingers/scissors/people was REMOVED — cropped hands,
# a girl holding a journal, scissors and craft tools are now WANTED when natural.
# We keep photoreal pushers (no cartoon/anime/illustration) + AI hand-safety.
# NOTE: branded ILLUSTRATED infographics use a different negative (illustration is
# wanted there) — that path lives in the infographic renderer, not here.
DEFAULT_NEG = ("low quality, blurry, jpeg artifacts, watermark, signature, "
               "gibberish text, cartoon, anime, 3d render, oversaturated, "
               "deformed hands, extra fingers, mutated hands, missing fingers, "
               "disfigured face, ugly, extra limbs")


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
    "dreamy flat lay photograph of junk journaling in progress: an open "
    "vintage journal with blank cream pages in the center, surrounded by "
    "layers of torn aged papers, delicate lace and tulle fabric, dried "
    "lavender and garden flowers, scattered vintage ephemera and a wax-sealed "
    "envelope, warm golden window light, soft romantic shadows, shallow depth "
    "of field, photorealistic, ethereal cozy atmosphere, {mood}"
)


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
                    sys.exit(
                        "BANNED visual path: type=mockup embeds or implies real "
                        "listing pages inside a generated album/journal/desk "
                        "scene. Use a direct carousel/gallery for real pages, "
                        "2-3 max, or generate a process scene without product "
                        "pages."
                    )
                else:
                    if slot.get("type") == "thin-atmosphere":
                        slot.setdefault("width", 832)
                        slot.setdefault("height", 1216)
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
