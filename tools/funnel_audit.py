#!/usr/bin/env python3
"""Fail fast when an article package has no measurable next action or Pin layer."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "public/blog"


def audit(slug: str) -> list[str]:
    failures: list[str] = []
    article = BLOG / f"{slug}.html"
    if not article.exists():
        return ["article HTML is missing"]
    html = article.read_text(encoding="utf-8")
    body = html.split('<div class="post-body ql-content">', 1)[-1].split("</article>", 1)[0]
    if not re.search(r'<p class="lead">.{100,}?</p>', html, flags=re.S):
        failures.append("lead hook is missing or too vague")
    if html.count('class="post-freebie-cta"') != 1:
        failures.append("exactly one primary conversion block is required")
    if "utm_source=blog" not in html or f"utm_content={slug}" not in html:
        failures.append("tracked article CTA is missing")
    if html.count('class="post-disclosure"') != 1:
        failures.append("image disclosure must appear exactly once")
    for anchor in ("pin-guide", "pin-mood", "free-gift"):
        if f'id="{anchor}"' not in html:
            failures.append(f"missing unique Pin destination #{anchor}")
    for alt in re.findall(r'<img[^>]+alt="([^"]*)"', body):
        if len(alt.split()) < 7:
            failures.append(f"image alt text is too short: {alt!r}")
    pins = sorted((BLOG / "img" / slug / "pins").glob("*.jpg"))
    if len(pins) != 3:
        failures.append(f"expected 3 designed Pin assets, found {len(pins)}")
    for pin in pins:
        with Image.open(pin) as image:
            if image.size != (1000, 1500):
                failures.append(f"{pin.name} is {image.size}, expected 1000x1500")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--latest", type=int, default=0)
    args = parser.parse_args()
    slugs = args.slugs
    if args.latest:
        index = json.loads((BLOG / "index.json").read_text(encoding="utf-8"))["posts"]
        slugs = [post["slug"] for post in index[:args.latest]]
    if not slugs:
        raise SystemExit("Supply article slugs or --latest N")
    failed = False
    for slug in slugs:
        problems = audit(slug)
        if problems:
            failed = True
            print(f"FAIL {slug}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"PASS {slug}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
