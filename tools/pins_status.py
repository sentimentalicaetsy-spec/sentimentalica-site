#!/usr/bin/env python3
"""Compatibility entry point for the durable Pinterest article tracker.

Usage: python tools/pins_status.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import pinterest_tracker


def main():
    rows = pinterest_tracker.refresh_tracker()
    missing = [row for row in rows if int(row["Images with no CSV record"]) > 0]
    print(f"Pinterest CSV coverage for {len(rows)} published articles:\n")
    for row in rows:
        total = row["Total content images"]
        covered = row["Images with any CSV record"]
        provided = row["Images in a provided CSV"]
        uploaded = row["Images confirmed uploaded to Pinterest"]
        mark = "✓" if int(covered) == int(total) else "✗"
        print(f"  {mark} {row['Article slug']}: CSV {covered}/{total}; "
              f"provided {provided}; upload-confirmed {uploaded}")
    if missing:
        print(f"\n{len(missing)} article(s) still have current images without a "
              f"CSV record. See data/pinterest/PINTEREST_ARTICLE_TRACKER.csv.")
    else:
        print("\nEvery current article image has a CSV record. Upload confirmation "
              "is tracked separately.")
    return missing


if __name__ == "__main__":
    main()
