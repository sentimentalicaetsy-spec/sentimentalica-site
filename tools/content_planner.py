#!/usr/bin/env python3
"""Deterministic slate allocator — the backbone that makes article DISTRIBUTION
non-guessed. Given N and today's date it decides, per Ksenia's approved rules:

  * 65% lead-magnet / 35% listing-bound   (axis 1: product tie)
  * seasonal slots are OPPORTUNISTIC — only for seasons whose creation window is
    open TODAY (Pinterest ~30-45d lead); the rest are eternal.   (axis 2: time)

It reads the Seasonal Calendar sheet (so Ksenia edits windows, not code) and
tells you exactly which seasons are live for content creation right now — so no
"swim in the sea" in October, and no Halloween in July.

Output: N slot specs the ideation funnel fills with real ideas. It does NOT
invent the ideas (that's the desire-scout agent) — it only allocates the mix.

Usage:  python tools/content_planner.py slate 20 [--date YYYY-MM-DD]
"""
import argparse
import re
from datetime import date, timedelta

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
     "nov", "dec"], start=1)}
LEAD_FRAC = 0.65        # lead-magnet share
SEASONAL_FRAC = 0.25    # max share given to seasonal when windows are open
SEASONAL_COOLDOWN_DAYS = 30  # rotate away after a recently published season


def _season_tokens(theme):
    """Distinctive words used to match a calendar season to recent plan rows."""
    generic = {"season", "peak", "planning", "content", "engagement"}
    return [w for w in re.findall(r"[a-z0-9]+", theme.lower())
            if len(w) >= 4 and w not in generic]


def season_on_cooldown(theme, plan_rows, today, days=SEASONAL_COOLDOWN_DAYS):
    """True when this season already produced a published article recently."""
    tokens = _season_tokens(theme)
    if not tokens:
        return False
    cutoff = today - timedelta(days=days)
    for row in plan_rows or []:
        if str(row.get("Status", "")).strip().lower() != "published":
            continue
        try:
            published = date.fromisoformat(str(row.get("Date", "")).strip())
        except ValueError:
            continue
        if published < cutoff or published > today:
            continue
        haystack = " ".join(str(row.get(k, "")) for k in
                            ("Title / angle", "Theme", "Notes")).lower()
        if any(token in haystack for token in tokens):
            return True
    return False


def _doy(month, day):
    from datetime import date as _d
    return _d(2001, month, day).timetuple().tm_yday


def _parse_md(tok):
    """'Aug 15' / '~Sep 1' / 'Oct 31' -> (month, day). None if unparseable."""
    tok = tok.strip().lstrip("~").strip()
    m = re.match(r"([A-Za-z]{3})[a-z]*\.?\s*(\d{1,2})?", tok)
    if not m or m.group(1).lower() not in MONTHS:
        return None
    mon = MONTHS[m.group(1).lower()]
    day = int(m.group(2)) if m.group(2) else 1
    return mon, day


def _window_end(window):
    """Live window 'Sep 1 - Oct 31' / 'May - Jul' -> end (month,day). Handles
    'year-round'/'ongoing'. Returns ('always') or (m,d) or None."""
    w = window.lower()
    if "year" in w or "round" in w or "ongoing" in w or "always" in w:
        return "always"
    parts = re.split(r"[-–—]", window)
    if not parts:
        return None
    end = _parse_md(parts[-1])
    if end and not re.search(r"\d", parts[-1]):
        # month only -> last day of that month
        import calendar
        end = (end[0], calendar.monthrange(2001, end[0])[1])
    return end


def open_seasons(today, calendar_rows):
    """Themes whose CREATION window (seed-start .. live-end) covers today.
    Excludes the year-round 'eternal' row (that's the eternal bucket)."""
    live = []
    tdoy = today.timetuple().tm_yday
    for r in calendar_rows:
        theme = str(r.get("Theme", "")).strip()
        if not theme or "eternal" in theme.lower():
            continue
        seed = str(r.get("Start seeding (Pinterest ~30-45d lead)", "")
                   or r.get("Start seeding", "")).strip().lower()
        end = _window_end(str(r.get("Window (content live)", "")
                              or r.get("Window", "")))
        if end == "always" or "ongoing" in seed or "always" in seed:
            live.append(theme)
            continue
        smd = _parse_md(seed)
        if not smd or not end or end == "always":
            continue
        s, e = _doy(*smd), _doy(*end)
        active = (s <= tdoy <= e) if s <= e else (tdoy >= s or tdoy <= e)
        if active:
            live.append(theme)
    return live


def slate(n, today, calendar_rows, plan_rows=None):
    """Return N slot dicts: {tie, time, season}. tie in lead|listing;
    time in eternal|seasonal; season = theme or ''."""
    n = max(1, int(n))
    n_lead = round(LEAD_FRAC * n)
    ties = ["lead"] * n_lead + ["listing"] * (n - n_lead)

    live = open_seasons(today, calendar_rows)
    eligible = [s for s in live
                if not season_on_cooldown(s, plan_rows or [], today)]
    n_season = min(round(SEASONAL_FRAC * n), len(eligible) * 3) if eligible else 0

    slots = []
    for i, tie in enumerate(ties):
        if i < n_season and eligible:
            slots.append({"tie": tie, "time": "seasonal",
                          "season": eligible[i % len(eligible)]})
        else:
            slots.append({"tie": tie, "time": "eternal", "season": ""})
    return slots, live


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["slate", "seasons"])
    ap.add_argument("n", nargs="?", type=int, default=1)
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()
    today = date.fromisoformat(args.date)
    try:
        import plan_io
        cal = plan_io.seasonal_calendar()
        plan = plan_io.sheet_rows("Plan")
    except Exception as e:
        print(f"(calendar unreadable: {e}) — using empty calendar"); cal = []; plan = []

    live = open_seasons(today, cal)
    print(f"Open seasonal windows on {today}: {live or '(none — all eternal)'}")
    if args.cmd == "seasons":
        return
    cooled = [s for s in live if season_on_cooldown(s, plan, today)]
    if cooled:
        print(f"Seasonal cooldown ({SEASONAL_COOLDOWN_DAYS}d): {cooled}"
              " — those slots rotate to eternal")
    slots, _ = slate(args.n, today, cal, plan)
    lead = sum(1 for s in slots if s['tie'] == 'lead')
    seas = sum(1 for s in slots if s['time'] == 'seasonal')
    print(f"\nSlate of {args.n}: {lead} lead-magnet / {args.n - lead} listing-bound"
          f" · {seas} seasonal / {args.n - seas} eternal\n")
    for i, s in enumerate(slots, 1):
        tag = f"{s['tie']:>7} · {s['time']}" + (f" · {s['season']}" if s['season'] else "")
        print(f"  {i:>2}. {tag}")


if __name__ == "__main__":
    main()
