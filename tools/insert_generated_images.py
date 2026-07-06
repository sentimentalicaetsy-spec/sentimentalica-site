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

DEFAULT_NEG = ("text, watermark, logo, low quality, blurry, cartoon, anime, "
               "oversaturated, scissors, hands, fingers, people, person, "
               "deformed objects")


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


def meld(image, prompt, denoise=0.32):
    """img2img pass: melt a composite into one photographic image —
    unifies light/shadow/texture so the pasted print looks photographed."""
    import base64 as _b64
    import io as _io
    import requests
    buf = _io.BytesIO()
    image.save(buf, "PNG")
    payload = {
        "init_images": [_b64.b64encode(buf.getvalue()).decode()],
        "prompt": prompt,
        "negative_prompt": DEFAULT_NEG,
        "denoising_strength": denoise,
        "width": image.width, "height": image.height,
        "steps": 30, "cfg_scale": 6.0, "sampler_name": "DPM++ 2M Karras",
    }
    r = requests.post(f"{A1111}/sdapi/v1/img2img", json=payload, timeout=900)
    r.raise_for_status()
    from PIL import Image as _Image
    return _Image.open(_io.BytesIO(_b64.b64decode(r.json()["images"][0]))).convert("RGB")


def _one_print(art_path, target_h, angle):
    from PIL import Image, ImageOps
    art = Image.open(art_path).convert("RGB")
    border = max(6, int(max(art.size) * 0.018))
    printed = ImageOps.expand(art, border=border, fill=(252, 250, 245))
    ratio = target_h / printed.height
    printed = printed.resize((int(printed.width * ratio), int(target_h)), Image.LANCZOS)
    return printed.convert("RGBA").rotate(angle, expand=True, resample=Image.BICUBIC)


def composite_print(scene_img, art_paths):
    """Lay 1-3 real listing pages onto the generated desk scene like scattered
    prints: paper borders, varied rotation, overlap, soft shadows."""
    from PIL import Image, ImageFilter
    if not isinstance(art_paths, (list, tuple)):
        art_paths = [art_paths]
    art_paths = list(art_paths)[:3]
    canvas = scene_img.convert("RGBA")
    n = len(art_paths)
    # organic layout: pages rest ON the open journal / among the ephemera,
    # varied sizes, overlapping — like work in progress, not a catalog.
    portrait = canvas.height >= canvas.width
    if portrait:
        specs = {1: [(0.42, -4, 0.50, 0.52)],
                 2: [(0.34, 8, 0.40, 0.34), (0.40, -5, 0.58, 0.60)],
                 3: [(0.30, 9, 0.34, 0.30), (0.32, -7, 0.70, 0.44),
                     (0.40, -2, 0.46, 0.66)]}[n]
    else:
        specs = {1: [(0.58, -3.5, 0.50, 0.52)],
                 2: [(0.46, 7, 0.36, 0.44), (0.52, -4, 0.63, 0.56)],
                 3: [(0.40, 9, 0.29, 0.40), (0.40, -8, 0.72, 0.42),
                     (0.50, -2, 0.50, 0.62)]}[n]
    for path, (hfrac, ang, cx, cy) in zip(art_paths, specs):
        printed = _one_print(path, canvas.height * hfrac, ang)
        x = int(canvas.width * cx - printed.width / 2)
        y = int(canvas.height * cy - printed.height / 2)
        a = printed.split()[3].point(lambda v: 110 if v > 0 else 0)
        sh = Image.new("RGBA", printed.size, (25, 18, 10, 0))
        sh.putalpha(a)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(sh, (x + 9, y + 13), sh)
        canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(9)))
        canvas.alpha_composite(printed, (x, y))
    return canvas.convert("RGB")



def inpaint_around(base_img, mask_img, prompt, denoise=0.85):
    """A1111 inpaint: regenerate everything EXCEPT the masked-out pages —
    the scene grows natively around the real prints."""
    import base64 as _b64
    import io as _io
    import requests
    def b64(im, fmt="PNG"):
        b = _io.BytesIO(); im.save(b, fmt); return _b64.b64encode(b.getvalue()).decode()
    payload = {
        "init_images": [b64(base_img)],
        "mask": b64(mask_img),
        "inpainting_mask_invert": 0,      # white = regenerate, black = keep pages
        "inpainting_fill": 2,              # latent noise -> rich fresh scene
        "inpaint_full_res": False,
        "mask_blur": 14,                   # feathered edges: soft, natural contact
        "prompt": prompt,
        "negative_prompt": DEFAULT_NEG,
        "denoising_strength": denoise,
        "width": base_img.width, "height": base_img.height,
        "steps": 32, "cfg_scale": 6.5, "sampler_name": "DPM++ 2M Karras",
    }
    r = requests.post(f"{A1111}/sdapi/v1/img2img", json=payload, timeout=900)
    r.raise_for_status()
    from PIL import Image as _Image
    return _Image.open(_io.BytesIO(_b64.b64decode(r.json()["images"][0]))).convert("RGB")


def mockup_v4(art_paths, prompt, width=832, height=1216):
    """Lay real pages on a neutral base, protect them with a mask, and let SD
    compose the whole dreamy scene AROUND them (native embedding)."""
    from PIL import Image, ImageDraw
    base = Image.new("RGB", (width, height), (233, 224, 208))  # warm linen tone
    mask = Image.new("L", (width, height), 255)                # 255 = regenerate
    n = min(3, len(art_paths))
    # UNIFORM SCALE (Ksenia 2026-07-06): all prints are the same paper size —
    # identical target height (±0 nothing), only rotation/position varies.
    if height >= width:
        H = 0.34
        specs = {1: [(0.42, -4, 0.50, 0.50)],
                 2: [(H, 6, 0.40, 0.34), (H, -5, 0.60, 0.62)],
                 3: [(H, 7, 0.33, 0.28), (H, -6, 0.68, 0.42),
                     (H, -2, 0.44, 0.68)]}[n]
    else:
        H = 0.46
        specs = {1: [(0.54, -3, 0.50, 0.50)],
                 2: [(H, 6, 0.35, 0.45), (H, -4, 0.65, 0.55)],
                 3: [(H, 7, 0.27, 0.40), (H, -6, 0.73, 0.42),
                     (H, -2, 0.50, 0.62)]}[n]
    canvas = base.convert("RGBA")
    for path, (hfrac, ang, cx, cy) in zip(art_paths[:3], specs):
        printed = _one_print(path, height * hfrac, ang)
        x = int(width * cx - printed.width / 2)
        y = int(height * cy - printed.height / 2)
        canvas.alpha_composite(printed, (x, y))
        # protect the page area (shrink a hair so feathering can kiss edges)
        a = printed.split()[3].point(lambda v: 255 if v > 8 else 0)
        mask.paste(0, (x, y), a)
    result = inpaint_around(canvas.convert("RGB"), mask, prompt)

    # ── Tone harmonization (Ksenia 2026-07-06: page contrast/saturation must
    # match the scene). Measure scene vs pages, nudge pages toward the scene.
    from PIL import ImageEnhance, ImageStat
    import numpy as _np
    m = _np.array(mask) < 128          # True where pages are
    arr = _np.array(result.convert("HSV")).astype(float)
    if m.any() and (~m).any():
        s_scene, v_scene = arr[..., 1][~m].mean(), arr[..., 2][~m].std()
        s_page, v_page = arr[..., 1][m].mean(), arr[..., 2][m].std()
        sat_f = 1 + 0.6 * ((s_scene / max(s_page, 1)) - 1)      # 60% toward scene
        con_f = 1 + 0.6 * ((v_scene / max(v_page, 1)) - 1)
        sat_f = min(max(sat_f, 0.6), 1.3)
        con_f = min(max(con_f, 0.6), 1.3)
        adjusted = ImageEnhance.Contrast(
            ImageEnhance.Color(result).enhance(sat_f)).enhance(con_f)
        from PIL import Image as _I
        page_mask = _I.fromarray((m * 255).astype("uint8")).convert("L")
        result = _I.composite(adjusted, result, page_mask)
    # whisper meld: unify grain without degrading the art
    result = meld(result, prompt, denoise=0.10)
    return result

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
                    prompt = MOCKUP_SCENE_PROMPT.format(
                        mood=slot.get("mood", "soft neutral tones"))
                    names = slot.get("insert_images") or [slot.get("insert_image", "img2.jpg")]
                    arts = [img_dir / n for n in names if (img_dir / n).exists()]
                    if not arts:
                        print(f"  SKIP mockup: none of {names} exist in {img_dir}")
                        continue
                    # v4: pages first, world generated AROUND them —
                    # occlusion of scene objects is impossible by construction.
                    im = mockup_v4(arts,
                                   prompt + ", printed watercolor art pages "
                                   "resting naturally among the layers, "
                                   "photorealistic, dreamy soft light",
                                   slot.get("width", 832),
                                   slot.get("height", 1216))
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
