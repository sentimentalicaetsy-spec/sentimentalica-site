#!/usr/bin/env python3
"""KILL SWITCH for the overnight article batch.

Reads staging/overnight/done.txt (one slug per line, written as each article
was published) and unpublishes them all: deletes the pages + their image
folders, rebuilds index.json + sitemap, commits and pushes.

Usage: python3 tools/unpublish_overnight.py [--yes]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG = REPO / "public" / "blog"
DONE = REPO / "staging" / "overnight" / "done.txt"

sys.path.insert(0, str(REPO / "tools"))
from publish_post import regenerate_sitemap  # noqa: E402


def main():
    if not DONE.exists():
        sys.exit("No overnight manifest — nothing to unpublish.")
    slugs = [s.strip() for s in DONE.read_text().splitlines() if s.strip()]
    print(f"{len(slugs)} overnight articles to remove.")
    if "--yes" not in sys.argv:
        if input("Remove them ALL from the live site? [yes/no] ") != "yes":
            sys.exit("aborted")

    idx_p = BLOG / "index.json"
    idx = json.loads(idx_p.read_text())
    for slug in slugs:
        (BLOG / f"{slug}.html").unlink(missing_ok=True)
        shutil.rmtree(BLOG / "img" / slug, ignore_errors=True)
    idx["posts"] = [p for p in idx["posts"] if p["slug"] not in set(slugs)]
    idx_p.write_text(json.dumps(idx, indent=2) + "\n")
    regenerate_sitemap()
    subprocess.run(["git", "-C", str(REPO), "add", "public"], check=True)
    subprocess.run(["git", "-C", str(REPO), "commit", "-m",
                    f"revert: unpublish {len(slugs)} overnight articles"], check=True)
    subprocess.run(["git", "-C", str(REPO), "push"], check=True)
    print("Done — live site clean again in ~1 minute.")


if __name__ == "__main__":
    main()
