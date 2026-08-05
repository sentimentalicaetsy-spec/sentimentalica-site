#!/usr/bin/env python3
"""Track Etsy listing IDs already promoted in published blog articles.

Default article workflow rule: a listing used by any other published article is
not eligible for a new product bridge. Reuse is allowed only when Ksenia
explicitly requests that exact listing again.
"""
import argparse
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG = REPO / "public" / "blog"


def listing_ids(html):
    ids = []
    for raw in re.findall(r'data-ids="([^"]+)"', html):
        for listing_id in re.findall(r"\d+", raw):
            if listing_id not in ids:
                ids.append(listing_id)
    return ids


def usage_by_id(exclude_slug=""):
    usage = defaultdict(list)
    for post in sorted(BLOG.glob("*.html")):
        if post.stem == exclude_slug:
            continue
        for listing_id in listing_ids(post.read_text(errors="ignore")):
            usage[listing_id].append(post.stem)
    return dict(usage)


def repeated_usage(candidate_ids, exclude_slug=""):
    usage = usage_by_id(exclude_slug)
    return {listing_id: usage[listing_id]
            for listing_id in candidate_ids if listing_id in usage}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("summary", "check"))
    ap.add_argument("listing_ids", nargs="*")
    ap.add_argument("--exclude-slug", default="")
    args = ap.parse_args()

    usage = usage_by_id(args.exclude_slug)
    if args.command == "summary":
        placements = sum(len(slugs) for slugs in usage.values())
        print(f"{len(usage)} unique listing IDs · {placements} article placements")
        for listing_id, slugs in sorted(
                usage.items(), key=lambda item: (-len(item[1]), item[0])):
            print(f"{listing_id}: {len(slugs)} · {', '.join(slugs)}")
        return

    if not args.listing_ids:
        ap.error("check requires at least one Etsy listing ID")
    candidates = []
    for raw in args.listing_ids:
        candidates.extend(re.findall(r"\d+", raw))
    repeated = repeated_usage(candidates, args.exclude_slug)
    for listing_id in candidates:
        if listing_id in repeated:
            print(f"USED {listing_id}: {', '.join(repeated[listing_id])}")
        else:
            print(f"UNUSED {listing_id}")
    if repeated:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
