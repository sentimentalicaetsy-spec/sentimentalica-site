#!/usr/bin/env python3
"""Pins completeness check — makes 'forgot the pins' VISIBLE, like the critic
gate makes 'forgot the critic' impossible. Lists every published article and
whether it has pin rows in a CSV yet. Run it any time to see what's missing.

Usage: python tools/pins_status.py
"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = REPO / "staging" / "pins"
sys.path.insert(0, str(REPO / "tools"))
import plan_io


def slug_covered(slug):
    """True if any CSV (active or uploaded) references this article slug."""
    files = list(PINS.glob("*.csv")) + list((PINS / "uploaded").glob("*.csv"))
    for f in files:
        try:
            with open(f, newline="", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    if slug in (r.get("Media URL", "") + r.get("Link", "")):
                        return True
        except Exception:
            pass
    return False


def main():
    published = [r for r in plan_io.sheet_rows("Plan")
                if str(r.get("Status", "")).strip() == "published"
                and str(r.get("Slug", "")).strip()]
    missing = []
    print(f"Pins status for {len(published)} published articles:\n")
    for r in published:
        slug = str(r["Slug"]).strip()
        ok = slug_covered(slug)
        print(f"  {'✓ pins' if ok else '✗ NO PINS'}  {slug}")
        if not ok:
            missing.append(slug)
    if missing:
        print(f"\n{len(missing)} article(s) have NO pins yet — run the "
              f"pinterest-seo agent on each to fill their CSVs "
              f"(auto-mirrors to Google Drive).")
    else:
        print("\nAll published articles have pins. ✓")
    return missing


if __name__ == "__main__":
    main()
