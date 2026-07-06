#!/usr/bin/env python3
"""Per-LISTING Pinterest bulk-upload CSV (a listing accumulates pins from ALL
its articles — spotlight, theme articles, idea articles).

Columns follow Pinterest's bulk template:
Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords

Usage:
  python3 tools/pin_csv.py add <NNN_Listing> --title T --media-url U --board B \
      --description D --link L --keywords "k1, k2" [--publish-date YYYY-MM-DD]
  python3 tools/pin_csv.py list <NNN_Listing>
Dedup: a (title, media-url) pair is only stored once.
"""
import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = REPO / "staging" / "pins"
FIELDS = ["Title", "Media URL", "Pinterest board", "Thumbnail",
          "Description", "Link", "Publish date", "Keywords"]


def path_for(listing):
    PINS.mkdir(parents=True, exist_ok=True)
    return PINS / f"{listing}.csv"


def read_rows(p):
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "list"])
    ap.add_argument("listing")
    ap.add_argument("--title")
    ap.add_argument("--media-url")
    ap.add_argument("--board", default="Junk Journal Printables")
    ap.add_argument("--thumbnail", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--publish-date", default="")
    args = ap.parse_args()

    p = path_for(args.listing)
    rows = read_rows(p)

    if args.cmd == "list":
        print(f"{p} — {len(rows)} pins")
        for r in rows:
            print(f"  [{r['Publish date'] or '—'}] {r['Title'][:60]} -> {r['Link'][:50]}")
        return

    if not args.title or not args.media_url:
        sys.exit("add requires --title and --media-url")
    if len(args.title) > 100:
        sys.exit(f"TITLE TOO LONG ({len(args.title)} > 100)")
    key = (args.title.strip(), args.media_url.strip())
    if any((r["Title"].strip(), r["Media URL"].strip()) == key for r in rows):
        print("duplicate — skipped")
        return
    rows.append({
        "Title": args.title.strip(), "Media URL": args.media_url.strip(),
        "Pinterest board": args.board, "Thumbnail": args.thumbnail,
        "Description": args.description.strip(), "Link": args.link.strip(),
        "Publish date": args.publish_date, "Keywords": args.keywords.strip(),
    })
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"✓ {p.name}: {len(rows)} pins")
    # Mirror to Google Drive so Ksenia gets the file automatically
    # (Drive Desktop syncs it; ready for Pinterest bulk upload).
    drive = Path("/Users/kseniateter/My Drive/Sentimentalica/Pinterest_CSV")
    try:
        drive.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(p, drive / p.name)
        print(f"→ Google Drive: Sentimentalica/Pinterest_CSV/{p.name}")
    except Exception as e:
        print(f"WARNING: Drive mirror failed ({e}) — CSV remains at {p}")


if __name__ == "__main__":
    main()
