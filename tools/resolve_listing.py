#!/usr/bin/env python3
"""Resolve a listing name to the article-pipeline input line.

Usage: python3 tools/resolve_listing.py "064_Poison_Bloom"   (or fuzzy: "poison")
Prints: NNN_Theme|etsy_id|/path/to/revised thumbnails
Exits non-zero with a clear reason if the listing can't be used.
"""
import sys
from pathlib import Path

VAULT = Path("/Users/kseniateter/Tower media/Listings")
DRIVE = Path("/Users/kseniateter/My Drive/Sentimentalica/Sentimentalica_01")
ORGS = ["00_LISTED", "00_DRAFT", "00_RENUMBERED", "00_PLANNED", "00_ongoing"]


def main():
    query = sys.argv[1].strip().lower().replace(" ", "_")
    notes = sorted(VAULT.glob("*.md"))
    hit = None
    for n in notes:  # exact stem first, then substring
        if n.stem.lower() == query:
            hit = n
            break
    if not hit:
        matches = [n for n in notes if query in n.stem.lower()]
        if len(matches) > 1:
            sys.exit("AMBIGUOUS: " + ", ".join(m.stem for m in matches[:6]))
        hit = matches[0] if matches else None
    if not hit:
        sys.exit(f"NOT FOUND: no vault note matches '{sys.argv[1]}'")

    etsy_id = None
    for line in hit.read_text().splitlines():
        if line.strip().startswith("etsy_id:"):
            digits = "".join(c for c in line if c.isdigit())
            etsy_id = digits or None
            break
    if not etsy_id:
        sys.exit(f"NO ETSY_ID: {hit.stem} has no etsy_id in its vault note — "
                 "run update_vault.py or add it manually.")

    # RULE (Ksenia 2026-07-06): articles only for LIVE listings — links must work.
    import json as _json
    import urllib.request as _rq
    try:
        feed = _json.load(_rq.urlopen(
            f"https://sentimentalica-etsy-feed.teter-album.workers.dev/?ids={etsy_id}",
            timeout=20))
        if feed.get("count", 0) < 1:
            sys.exit(f"NOT LIVE: {hit.stem} (etsy_id {etsy_id}) is not an active "
                     "Etsy listing (draft/inactive). Publish it on Etsy first — "
                     "article links must work for buyers.")
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"LIVE-CHECK FAILED: could not verify listing {etsy_id} is active "
                 f"({e}) — refusing to publish an article with possibly dead links.")

    for org in ORGS:
        d = DRIVE / org / hit.stem / "revised thumbnails"
        if d.is_dir():
            imgs = [p for p in d.iterdir()
                    if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
            if len(imgs) >= 3:
                print(f"{hit.stem}|{etsy_id}|{d}")
                return
    sys.exit(f"NO IMAGES: {hit.stem} has no local 'revised thumbnails' with >=3 "
             "images in any org folder (Drive mirror may not be synced).")


if __name__ == "__main__":
    main()
