#!/usr/bin/env python3
"""Pinterest bulk-upload CSV writer for article or listing pin batches.

Columns follow Pinterest's bulk template:
Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords

Usage:
  python3 tools/pin_csv.py add <csv-name> --title T --media-url U --board B \
      --description D --link L --keywords "k1, k2" [--publish-date YYYY-MM-DD] \
      [--boards-file PINTEREST_BOARDS.txt]
  python3 tools/pin_csv.py list <csv-name>
Dedup: each media URL is stored only once per active/archive batch.
Funnel: --link must be the exact Sentimentalica article that owns the image
(Pinterest→relevant article→Etsy/freebie).

Pinterest limits enforced here (official bulk-upload help, checked 2026-08-05):
up to 200 rows; Title <= 100 characters; Description <= 500 characters;
public direct Media URL; exact required board; blank Thumbnail for images;
Publish date blank, YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SS (UTC when timed).
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
PINS = REPO / "staging" / "pins"
FIELDS = ["Title", "Media URL", "Pinterest board", "Thumbnail",
          "Description", "Link", "Publish date", "Keywords"]
MAX_ROWS = 200
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTS = {".mp4"}
DEFAULT_BOARDS_FILE = REPO / "PINTEREST_BOARDS.txt"
CTA_STARTS = ("See ", "Find ", "Get ", "Read ", "Explore ", "Try ",
              "Discover ", "Save ", "Start ", "Create ", "Learn ",
              "Use ", "Make ", "Build ", "Open ")


def path_for(listing):
    PINS.mkdir(parents=True, exist_ok=True)
    return PINS / f"{listing}.csv"


def read_rows(p):
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_boards(path):
    """One exact Pinterest board or board/section name per non-comment line."""
    p = Path(path)
    if not p.exists():
        sys.exit(f"BOARDS FILE NOT FOUND: {p}")
    boards = {line.strip() for line in p.read_text(encoding="utf-8").splitlines()
              if line.strip() and not line.lstrip().startswith("#")}
    if not boards:
        sys.exit(f"BOARDS FILE IS EMPTY: {p}")
    return boards


def validate_publish_date(value):
    if not value:
        return
    formats = ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S")
    if not any(_valid_date(value, fmt) for fmt in formats):
        sys.exit("PUBLISH DATE must be blank, YYYY-MM-DD, or "
                 "YYYY-MM-DDTHH:MM:SS (timed values are UTC)")


def _valid_date(value, fmt):
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False


def media_kind(value):
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        sys.exit("MEDIA URL must be a public http(s) link to the file itself")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        sys.exit("MEDIA URL must be public, not localhost")
    ext = Path(parsed.path).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    sys.exit("MEDIA URL must point directly to a JPG, JPEG, PNG, or MP4 file")


def normalize_keywords(value):
    terms = [term.strip() for term in value.split(",") if term.strip()]
    unique = {term.casefold() for term in terms}
    if not 5 <= len(terms) <= 10:
        sys.exit(f"KEYWORDS must contain 5–10 comma-separated relevant terms "
                 f"({len(terms)} supplied)")
    if len(unique) != len(terms):
        sys.exit("KEYWORDS must not contain duplicates")
    return ", ".join(terms)


def validate_pin_copy(title, description):
    """Keep Pinterest copy human and action-led: CTA first, keyword second."""
    if "—" in title or "–" in title or "—" in description or "–" in description:
        sys.exit("Do not use em dashes or en dashes in Pinterest titles/descriptions")
    if ":" not in title:
        sys.exit("TITLE must use CTA first: keyword phrase")
    cta, keyword = (part.strip() for part in title.split(":", 1))
    if not any(cta == start.strip() or cta.startswith(start) for start in CTA_STARTS):
        sys.exit("TITLE must begin with a clear action CTA, then a colon")
    if len(keyword.split()) < 2:
        sys.exit("TITLE must place a meaningful Pinterest keyword phrase after the CTA")


def validate_article_link(link, media_url):
    """Require the canonical article URL and its matching public image folder."""
    link_parts = urlparse(link.strip())
    if link_parts.scheme not in {"http", "https"} or not link_parts.netloc:
        sys.exit("LINK must be a public http(s) URL")
    host = (link_parts.hostname or "").lower()
    if host != "sentimentalica.com" and not host.endswith(".sentimentalica.com"):
        sys.exit("LINK must point to the relevant Sentimentalica article")
    path = link_parts.path.rstrip("/")
    if not path.startswith("/blog/") or not path.endswith(".html"):
        sys.exit("LINK must be the canonical relevant article URL ending in .html")
    slug = Path(path).stem
    if not slug or slug in {"blog", "index"}:
        sys.exit("LINK must identify one relevant article, not the blog index")
    media_parts = urlparse(media_url.strip())
    media_host = (media_parts.hostname or "").lower()
    expected = f"/blog/img/{slug}/"
    if (media_host != "sentimentalica.com"
            and not media_host.endswith(".sentimentalica.com")):
        sys.exit("MEDIA URL must use the public sentimentalica.com article image")
    if not media_parts.path.startswith(expected):
        sys.exit(f"MEDIA URL does not belong to the linked article; expected "
                 f"an image under {expected}")
    if link_parts.fragment:
        article = REPO / "public" / "blog" / f"{slug}.html"
        if article.exists():
            marker = f'id="{link_parts.fragment}"'
            if marker not in article.read_text(encoding="utf-8"):
                sys.exit(f"LINK fragment #{link_parts.fragment} does not exist "
                         f"in {article.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "list", "mark-uploaded"])
    ap.add_argument("listing", nargs="?", default="")
    ap.add_argument("--all", action="store_true", help="mark-uploaded: all listings")
    ap.add_argument("--title")
    ap.add_argument("--media-url")
    ap.add_argument("--board", default="")
    ap.add_argument("--boards-file", default=(str(DEFAULT_BOARDS_FILE)
                    if DEFAULT_BOARDS_FILE.exists() else ""),
                    help="optional exact board allowlist, one board or board/section per line")
    ap.add_argument("--thumbnail", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--publish-date", default="")
    ap.add_argument("--no-drive", action="store_true",
                    help="Keep the CSV local; do not mirror it to Google Drive.")
    args = ap.parse_args()

    if args.cmd == "mark-uploaded":
        # Ksenia's flow: she says "I uploaded the CSV" -> current rows are
        # archived with the date; the active file restarts empty. Archived
        # pins can never be re-added (dedup below reads archives too).
        from datetime import date
        targets = sorted(PINS.glob("*.csv")) if getattr(args, "all", False) else [path_for(args.listing)]
        arch_dir = PINS / "uploaded"
        drive_arch = Path("/Users/kseniateter/My Drive/Sentimentalica/Pinterest_CSV/uploaded")
        for tp in targets:
            rows = read_rows(tp)
            if not rows:
                continue
            arch_dir.mkdir(parents=True, exist_ok=True)
            name = f"{tp.stem}__uploaded_{date.today().isoformat()}.csv"
            import shutil
            shutil.move(str(tp), str(arch_dir / name))
            try:
                drive_arch.mkdir(parents=True, exist_ok=True)
                shutil.copy2(arch_dir / name, drive_arch / name)
                drive_active = Path("/Users/kseniateter/My Drive/Sentimentalica/Pinterest_CSV") / tp.name
                drive_active.unlink(missing_ok=True)
            except Exception as e:
                print(f"WARNING: drive archive failed ({e})")
            print(f"✓ {tp.stem}: {len(rows)} pins archived -> uploaded/{name}; active file fresh")
        return

    p = path_for(args.listing)
    rows = read_rows(p)

    if args.cmd == "list":
        print(f"{p} — {len(rows)} pins")
        for r in rows:
            print(f"  [{r['Publish date'] or '—'}] {r['Title'][:60]} -> {r['Link'][:50]}")
        return

    if not args.listing:
        sys.exit("add requires a CSV batch name (use the article slug)")
    if not args.title or not args.media_url or not args.board or not args.link:
        sys.exit("add requires --title, --media-url, --board, and --link")
    if not args.description or not args.keywords:
        sys.exit("Sentimentalica image rows require --description and --keywords")
    if not args.boards_file:
        sys.exit("add requires --boards-file with Ksenia's canonical board list")
    if len(args.title) > 100:
        sys.exit(f"TITLE TOO LONG ({len(args.title)} > 100)")
    if len(args.description) > 500:
        sys.exit(f"DESCRIPTION TOO LONG ({len(args.description)} > 500)")
    validate_pin_copy(args.title.strip(), args.description.strip())
    keywords = normalize_keywords(args.keywords)
    if len(rows) >= MAX_ROWS:
        sys.exit(f"CSV ROW LIMIT REACHED ({MAX_ROWS}); start another upload batch")
    kind = media_kind(args.media_url)
    if kind == "image" and args.thumbnail.strip():
        sys.exit("THUMBNAIL must be blank for image Pins")
    if kind == "video" and not args.thumbnail.strip():
        sys.exit("THUMBNAIL is required for video Pins")
    allowed = read_boards(args.boards_file)
    if args.board.strip() not in allowed:
        sys.exit(f"UNKNOWN BOARD: {args.board!r}. Use an exact name from "
                 f"{args.boards_file}; do not create boards by typo.")
    validate_publish_date(args.publish_date)
    validate_article_link(args.link, args.media_url)
    link_key = args.link.strip()
    seen_links = {r["Link"].strip() for r in rows}
    if link_key in seen_links:
        sys.exit("DUPLICATE PIN LINK: Pinterest accepts only the first identical "
                 "destination in one bulk CSV. Use a unique, real article "
                 "section anchor for each image.")
    media_key = args.media_url.strip()
    seen = {r["Media URL"].strip() for r in rows}
    for arch in (PINS / "uploaded").glob(f"{args.listing}__uploaded_*.csv"):
        seen |= {r["Media URL"].strip() for r in read_rows(arch)}
    if media_key in seen:
        print("duplicate media URL (incl. already-uploaded) — skipped")
        return
    rows.append({
        "Title": args.title.strip(), "Media URL": args.media_url.strip(),
        "Pinterest board": args.board, "Thumbnail": args.thumbnail,
        "Description": args.description.strip(), "Link": args.link.strip(),
        "Publish date": args.publish_date, "Keywords": keywords,
    })
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"✓ {p.name}: {len(rows)} pins")
    # Mirror to Google Drive so Ksenia gets the file automatically
    # (Drive Desktop syncs it; ready for Pinterest bulk upload).
    if args.no_drive:
        print("→ local only (--no-drive)")
        return
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
