#!/usr/bin/env python3
"""Durable Pinterest CSV and per-article coverage tracker.

The tracked files under data/pinterest/ are the source of truth. Files under
staging/pins/ are working copies and may be ignored by git.

Commands:
  refresh
      Rebuild the per-article tracker from published article HTML and the
      durable pin ledger.
  import-history
      Import every existing staging/pins CSV as a historical CSV record. This
      proves preparation, not delivery or successful Pinterest publication.
  record-batch PATH --status provided|uploaded [--date YYYY-MM-DD]
      Record every row in a handed-off or Pinterest-confirmed batch, archive an
      exact durable copy, and refresh the article tracker.
  record-report PATH [--date YYYY-MM-DD]
      Read Pinterest's downloaded result CSV. Blank error cells are recorded
      as accepted; nonblank errors remain unconfirmed for failed-row retries.
  check [SLUG ...]
      Refresh and report image coverage. With no slugs, report every article.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse


REPO = Path(__file__).resolve().parent.parent
PUBLIC_BLOG = REPO / "public" / "blog"
STAGING_PINS = REPO / "staging" / "pins"
DATA_DIR = REPO / "data" / "pinterest"
BATCH_ARCHIVE = DATA_DIR / "batches"
REPORT_ARCHIVE = DATA_DIR / "reports"
PIN_LEDGER = DATA_DIR / "PIN_MEDIA_LEDGER.csv"
BATCH_LEDGER = DATA_DIR / "PINTEREST_BATCH_LEDGER.csv"
ARTICLE_TRACKER = DATA_DIR / "PINTEREST_ARTICLE_TRACKER.csv"

PIN_FIELDS = [
    "Article slug",
    "Article URL",
    "Media URL",
    "First recorded batch",
    "All batch files",
    "CSV status",
    "CSV provided date",
    "Pinterest upload confirmed",
    "Pinterest uploaded date",
    "Last Pinterest result",
    "Last Pinterest error",
    "Scheduled publish dates",
    "Last updated",
]

BATCH_FIELDS = [
    "Batch file",
    "Row count",
    "Article count",
    "First publish date",
    "Last publish date",
    "Handoff status",
    "CSV provided date",
    "Pinterest upload confirmed date",
    "Pinterest accepted rows",
    "Pinterest rejected rows",
    "Pinterest report",
    "Durable archive",
    "Last updated",
    "Notes",
]

ARTICLE_FIELDS = [
    "Article date",
    "Article title",
    "Article slug",
    "Article URL",
    "Total content images",
    "Images with any CSV record",
    "Images in a provided CSV",
    "Images confirmed uploaded to Pinterest",
    "Images with no CSV record",
    "CSV coverage status",
    "Pinterest handoff / upload status",
    "Latest scheduled dates",
    "Batch file(s)",
    "Tracker updated",
]

STATUS_RANK = {
    "Historical CSV record; handoff status unknown": 1,
    "CSV provided to Ksenia; Pinterest upload not confirmed": 2,
    "Pinterest upload confirmed by Ksenia": 3,
}


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def clean_url(value: str) -> str:
    """Keep a direct URL exact apart from surrounding whitespace."""
    return (value or "").strip()


def canonical_article_url(slug: str) -> str:
    return f"https://sentimentalica.com/blog/{slug}.html"


def slug_from_row(row: dict[str, str]) -> str:
    link = clean_url(row.get("Link", ""))
    if link:
        stem = Path(urlparse(link).path).stem
        if stem and stem not in {"blog", "index"}:
            return stem
    media = clean_url(row.get("Media URL", ""))
    match = re.search(r"/blog/img/([^/]+)/", urlparse(media).path)
    return match.group(1) if match else ""


def split_values(value: str) -> set[str]:
    return {item.strip() for item in (value or "").split(" | ") if item.strip()}


def joined(values: set[str]) -> str:
    return " | ".join(sorted(values))


def valid_day(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise SystemExit(f"Invalid date {value!r}; expected YYYY-MM-DD")


class ContentImageParser(HTMLParser):
    def __init__(self, article_url: str):
        super().__init__(convert_charrefs=True)
        self.article_url = article_url
        self.body_depth = 0
        self.images: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = set((attrs_dict.get("class") or "").split())
        if tag == "div" and "post-body" in classes:
            self.body_depth = 1
            return
        if self.body_depth:
            if tag == "div":
                self.body_depth += 1
            if tag == "img":
                src = clean_url(attrs_dict.get("src") or "")
                if src and not src.startswith("data:"):
                    self.images.append(urljoin(self.article_url, src))

    def handle_endtag(self, tag: str) -> None:
        if self.body_depth and tag == "div":
            self.body_depth -= 1


def article_metadata(path: Path) -> dict[str, object] | None:
    text = path.read_text(encoding="utf-8")
    script_match = re.search(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    schema: dict[str, object] = {}
    if script_match:
        try:
            loaded = json.loads(html.unescape(script_match.group(1)).strip())
            if isinstance(loaded, dict):
                schema = loaded
        except json.JSONDecodeError:
            pass
    slug = path.stem
    article_url = str(schema.get("url") or canonical_article_url(slug))
    if urlparse(article_url).path.rstrip("/").endswith("/blog"):
        return None
    title = str(schema.get("headline") or "").strip()
    if not title:
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.DOTALL | re.IGNORECASE)
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else slug
    article_date = str(schema.get("datePublished") or "").strip()
    parser = ContentImageParser(article_url)
    parser.feed(text)
    images = list(dict.fromkeys(parser.images))
    return {
        "date": article_date,
        "title": html.unescape(title),
        "slug": slug,
        "url": article_url,
        "images": images,
    }


def published_articles() -> list[dict[str, object]]:
    articles: list[dict[str, object]] = []
    for path in sorted(PUBLIC_BLOG.glob("*.html")):
        meta = article_metadata(path)
        if meta and meta["images"]:
            articles.append(meta)
    return articles


def load_pin_ledger() -> dict[str, dict[str, str]]:
    return {
        clean_url(row.get("Media URL", "")): row
        for row in csv_rows(PIN_LEDGER)
        if clean_url(row.get("Media URL", ""))
    }


def load_batch_ledger() -> dict[str, dict[str, str]]:
    return {
        row.get("Batch file", "").strip(): row
        for row in csv_rows(BATCH_LEDGER)
        if row.get("Batch file", "").strip()
    }


def record_batch(
    path: Path,
    status: str,
    recorded_date: str,
    archive: bool = True,
    notes: str = "",
) -> tuple[int, int]:
    if not path.exists():
        raise SystemExit(f"CSV not found: {path}")
    rows = csv_rows(path)
    if not rows:
        raise SystemExit(f"CSV has no data rows: {path}")
    required = {"Media URL", "Link", "Publish date"}
    missing = required - set(rows[0])
    if missing:
        raise SystemExit(f"CSV lacks required tracker column(s): {', '.join(sorted(missing))}")

    status_text = {
        "historical": "Historical CSV record; handoff status unknown",
        "provided": "CSV provided to Ksenia; Pinterest upload not confirmed",
        "uploaded": "Pinterest upload confirmed by Ksenia",
    }[status]
    current_pins = load_pin_ledger()
    slugs: set[str] = set()

    for source in rows:
        media = clean_url(source.get("Media URL", ""))
        slug = slug_from_row(source)
        if not media or not slug:
            continue
        slugs.add(slug)
        existing = current_pins.get(media, {field: "" for field in PIN_FIELDS})
        batch_files = split_values(existing.get("All batch files", ""))
        batch_files.add(path.name)
        dates = split_values(existing.get("Scheduled publish dates", ""))
        publish_date = clean_url(source.get("Publish date", ""))
        if publish_date:
            dates.add(publish_date)
        previous_status = existing.get("CSV status", "")
        if STATUS_RANK.get(previous_status, 0) > STATUS_RANK[status_text]:
            status_text_for_row = previous_status
        else:
            status_text_for_row = status_text
        existing.update(
            {
                "Article slug": slug,
                "Article URL": canonical_article_url(slug),
                "Media URL": media,
                "First recorded batch": existing.get("First recorded batch", "") or path.name,
                "All batch files": joined(batch_files),
                "CSV status": status_text_for_row,
                "Scheduled publish dates": joined(dates),
                "Last updated": recorded_date,
            }
        )
        if status in {"provided", "uploaded"}:
            existing["CSV provided date"] = existing.get("CSV provided date", "") or recorded_date
        if status == "uploaded":
            existing["Pinterest upload confirmed"] = "Yes"
            existing["Pinterest uploaded date"] = recorded_date
        elif not existing.get("Pinterest upload confirmed"):
            existing["Pinterest upload confirmed"] = "No"
        current_pins[media] = existing

    write_csv(PIN_LEDGER, PIN_FIELDS, sorted(current_pins.values(), key=lambda r: (r["Article slug"], r["Media URL"])))

    archive_path = ""
    if archive:
        BATCH_ARCHIVE.mkdir(parents=True, exist_ok=True)
        target = BATCH_ARCHIVE / path.name
        if path.resolve() != target.resolve():
            # Preserve the exact batch rows/columns while normalizing line ends
            # so the durable git artifact remains portable and diffable.
            source_fields = list(rows[0])
            write_csv(target, source_fields, rows)
        archive_path = str(target.relative_to(REPO))

    publish_dates = sorted({clean_url(row.get("Publish date", "")) for row in rows if clean_url(row.get("Publish date", ""))})
    batches = load_batch_ledger()
    batch = batches.get(path.name, {field: "" for field in BATCH_FIELDS})
    if STATUS_RANK.get(batch.get("Handoff status", ""), 0) <= STATUS_RANK[status_text]:
        batch["Handoff status"] = status_text
    batch.update(
        {
            "Batch file": path.name,
            "Row count": str(len(rows)),
            "Article count": str(len(slugs)),
            "First publish date": publish_dates[0] if publish_dates else "",
            "Last publish date": publish_dates[-1] if publish_dates else "",
            "Durable archive": archive_path or batch.get("Durable archive", ""),
            "Last updated": recorded_date,
            "Notes": notes or batch.get("Notes", ""),
        }
    )
    if status in {"provided", "uploaded"}:
        batch["CSV provided date"] = batch.get("CSV provided date", "") or recorded_date
    if status == "uploaded":
        batch["Pinterest upload confirmed date"] = recorded_date
    batches[path.name] = batch
    write_csv(BATCH_LEDGER, BATCH_FIELDS, sorted(batches.values(), key=lambda r: r["Batch file"]))
    return len(rows), len(slugs)


def record_report(path: Path, recorded_date: str) -> tuple[int, int]:
    """Record Pinterest's row results without treating failures as uploads."""
    if not path.exists():
        raise SystemExit(f"Pinterest report not found: {path}")
    rows = csv_rows(path)
    if not rows or "error" not in rows[0]:
        raise SystemExit("Pinterest result CSV must contain an error column")
    current_pins = load_pin_ledger()
    accepted = 0
    rejected = 0
    errors: set[str] = set()
    for source in rows:
        media = clean_url(source.get("Media URL", ""))
        if not media:
            continue
        slug = slug_from_row(source)
        existing = current_pins.get(media, {field: "" for field in PIN_FIELDS})
        batch_files = split_values(existing.get("All batch files", ""))
        batch_files.add(path.name)
        existing.update({
            "Article slug": slug,
            "Article URL": canonical_article_url(slug),
            "Media URL": media,
            "First recorded batch": existing.get("First recorded batch", "") or path.name,
            "All batch files": joined(batch_files),
            "Last updated": recorded_date,
        })
        error = clean_url(source.get("error", ""))
        if error:
            rejected += 1
            errors.add(error)
            existing["Last Pinterest result"] = "Rejected"
            existing["Last Pinterest error"] = error
            if not existing.get("Pinterest upload confirmed"):
                existing["Pinterest upload confirmed"] = "No"
        else:
            accepted += 1
            existing["CSV status"] = "Pinterest upload confirmed by Ksenia"
            existing["CSV provided date"] = existing.get("CSV provided date", "") or recorded_date
            existing["Pinterest upload confirmed"] = "Yes"
            existing["Pinterest uploaded date"] = recorded_date
            existing["Last Pinterest result"] = "Accepted"
            existing["Last Pinterest error"] = ""
        current_pins[media] = existing
    write_csv(PIN_LEDGER, PIN_FIELDS, sorted(current_pins.values(), key=lambda r: (r["Article slug"], r["Media URL"])))

    REPORT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    report_target = REPORT_ARCHIVE / f"{path.stem}__pinterest-report_{recorded_date}.csv"
    write_csv(report_target, list(rows[0]), rows)

    batches = load_batch_ledger()
    batch = batches.get(path.name, {field: "" for field in BATCH_FIELDS})
    handoff = (f"Partial Pinterest result: {accepted} accepted, {rejected} rejected"
               if accepted and rejected else
               "Pinterest upload confirmed by report" if accepted else
               "Pinterest report rejected every row")
    batch.update({
        "Batch file": path.name,
        "Row count": str(len(rows)),
        "Handoff status": handoff,
        "Pinterest upload confirmed date": recorded_date if accepted else "",
        "Pinterest accepted rows": str(accepted),
        "Pinterest rejected rows": str(rejected),
        "Pinterest report": str(report_target.relative_to(REPO)),
        "Last updated": recorded_date,
        "Notes": "; ".join(sorted(errors)) or batch.get("Notes", ""),
    })
    batches[path.name] = batch
    write_csv(BATCH_LEDGER, BATCH_FIELDS, sorted(batches.values(), key=lambda r: r["Batch file"]))
    refresh_tracker(recorded_date)
    return accepted, rejected


def refresh_tracker(recorded_date: str | None = None) -> list[dict[str, object]]:
    recorded_date = recorded_date or date.today().isoformat()
    pins = load_pin_ledger()
    output: list[dict[str, object]] = []
    for article in published_articles():
        images = article["images"]
        records = [pins.get(url) for url in images]
        any_csv = sum(record is not None for record in records)
        provided = sum(
            bool(record) and STATUS_RANK.get(record.get("CSV status", ""), 0) >= 2
            for record in records
        )
        uploaded = sum(
            bool(record) and record.get("Pinterest upload confirmed", "") == "Yes"
            for record in records
        )
        missing = len(images) - any_csv
        if not images:
            coverage = "No article content images"
        elif missing == 0:
            coverage = "Complete: every current article image has a CSV record"
        elif any_csv == 0:
            coverage = "Not started: no current article image has a CSV record"
        else:
            coverage = f"Partial: {missing} current image(s) still need a CSV row"

        if uploaded == len(images) and images:
            handoff = "Pinterest upload confirmed for every current article image"
        elif uploaded:
            handoff = f"Pinterest upload confirmed for {uploaded} of {len(images)} current images"
        elif provided == len(images) and images:
            handoff = "CSV provided for every current image; Pinterest upload not confirmed"
        elif provided:
            handoff = f"CSV provided for {provided} of {len(images)} current images; upload not confirmed"
        elif any_csv:
            handoff = "Historical CSV record exists; delivery and Pinterest upload are not confirmed"
        else:
            handoff = "No CSV handoff recorded"

        schedules: set[str] = set()
        batch_files: set[str] = set()
        for record in records:
            if not record:
                continue
            schedules |= split_values(record.get("Scheduled publish dates", ""))
            batch_files |= split_values(record.get("All batch files", ""))
        output.append(
            {
                "Article date": article["date"],
                "Article title": article["title"],
                "Article slug": article["slug"],
                "Article URL": article["url"],
                "Total content images": len(images),
                "Images with any CSV record": any_csv,
                "Images in a provided CSV": provided,
                "Images confirmed uploaded to Pinterest": uploaded,
                "Images with no CSV record": missing,
                "CSV coverage status": coverage,
                "Pinterest handoff / upload status": handoff,
                "Latest scheduled dates": joined(schedules),
                "Batch file(s)": joined(batch_files),
                "Tracker updated": recorded_date,
            }
        )
    output.sort(key=lambda row: (row["Article date"], row["Article slug"]), reverse=True)
    write_csv(ARTICLE_TRACKER, ARTICLE_FIELDS, output)
    return output


def import_history(recorded_date: str) -> tuple[int, int]:
    paths = sorted(STAGING_PINS.glob("*.csv")) + sorted((STAGING_PINS / "uploaded").glob("*.csv"))
    paths = [path for path in paths if "TRACKER" not in path.name.upper()]
    batches = 0
    rows = 0
    for path in paths:
        if not csv_rows(path):
            continue
        count, _ = record_batch(path, "historical", recorded_date, archive=False)
        batches += 1
        rows += count
    refresh_tracker(recorded_date)
    return batches, rows


def check(slugs: list[str]) -> int:
    rows = refresh_tracker()
    articles = {article["slug"]: article for article in published_articles()}
    pins = load_pin_ledger()
    wanted = set(slugs)
    selected = [row for row in rows if not wanted or row["Article slug"] in wanted]
    unknown = wanted - {row["Article slug"] for row in selected}
    for row in selected:
        print(
            f"{row['Article slug']}: {row['Images with any CSV record']}/"
            f"{row['Total content images']} current images have CSV records; "
            f"{row['Images in a provided CSV']} provided; "
            f"{row['Images confirmed uploaded to Pinterest']} upload-confirmed; "
            f"{row['Images with no CSV record']} missing"
        )
        if slugs and int(row["Images with no CSV record"]) > 0:
            for media in articles[row["Article slug"]]["images"]:
                if media not in pins:
                    print(f"  NEEDS CSV: {media}")
    for slug in sorted(unknown):
        print(f"UNKNOWN ARTICLE: {slug}", file=sys.stderr)
    return 1 if unknown else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("refresh")
    history = sub.add_parser("import-history")
    history.add_argument("--date", default=date.today().isoformat())
    record = sub.add_parser("record-batch")
    record.add_argument("path", type=Path)
    record.add_argument("--status", choices=["provided", "uploaded"], required=True)
    record.add_argument("--date", default=date.today().isoformat())
    record.add_argument("--notes", default="")
    report = sub.add_parser("record-report")
    report.add_argument("path", type=Path)
    report.add_argument("--date", default=date.today().isoformat())
    check_parser = sub.add_parser("check")
    check_parser.add_argument("slugs", nargs="*")
    args = parser.parse_args()

    if args.command == "refresh":
        rows = refresh_tracker()
        print(f"Refreshed {ARTICLE_TRACKER.relative_to(REPO)} for {len(rows)} articles")
        return 0
    if args.command == "import-history":
        day = valid_day(args.date)
        batches, rows = import_history(day)
        print(f"Imported {rows} rows from {batches} historical CSV files")
        return 0
    if args.command == "record-batch":
        day = valid_day(args.date)
        rows, articles = record_batch(args.path, args.status, day, notes=args.notes)
        refresh_tracker(day)
        print(f"Recorded {rows} rows across {articles} articles as {args.status}")
        print(f"Tracker: {ARTICLE_TRACKER.relative_to(REPO)}")
        return 0
    if args.command == "record-report":
        day = valid_day(args.date)
        accepted, rejected = record_report(args.path, day)
        print(f"Pinterest report recorded: {accepted} accepted, {rejected} rejected")
        print(f"Tracker: {ARTICLE_TRACKER.relative_to(REPO)}")
        return 0
    return check(args.slugs)


if __name__ == "__main__":
    raise SystemExit(main())
