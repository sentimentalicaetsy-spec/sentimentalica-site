#!/usr/bin/env python3
"""Critic gate — makes the image-critic step IMPOSSIBLE to skip.

The failure of 2026-07-06 ("ты забыла про критика"): the critic was a step I
*invoked* by hand, so it could be forgotten. This turns it into a hard,
code-enforced gate: an article cannot be published until every generated image
(gen1..genN) has a recorded critic verdict, and every verdict is PASS.

Store: staging/overnight/critic/<slug>.json
  { "gen1": {"verdict": "PASS", "scores": "palette 5 · ...", "fix": "",
             "checked": "2026-07-07"} , ... }

The critic (image-critic agent, or me applying its rubric) LOOKS at each image
and calls record(). publish_post.py calls require_all_pass() and refuses to
write/push if anything is missing or REGENERATE. No verdict file => no publish.
"""
import json
import re
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CRITIC = REPO / "staging" / "overnight" / "critic"


def _path(slug):
    CRITIC.mkdir(parents=True, exist_ok=True)
    return CRITIC / f"{slug}.json"


def load(slug):
    p = _path(slug)
    return json.loads(p.read_text()) if p.exists() else {}


def record(slug, slot, verdict, scores="", fix=""):
    """Called by the critic after it LOOKS at an image."""
    verdict = verdict.upper()
    assert verdict in ("PASS", "REGENERATE"), verdict
    data = load(slug)
    data[slot] = {"verdict": verdict, "scores": scores, "fix": fix,
                  "checked": date.today().isoformat()}
    _path(slug).write_text(json.dumps(data, indent=2) + "\n")
    return data


def slots_in(body_html):
    """Every generated image the article actually uses (gen1, gen2, ...)."""
    return sorted(set(re.findall(r"\bgen(\d+)\.jpe?g\b", body_html)),
                  key=int)


def require_all_pass(slug, body_html):
    """Returns (ok, message). ok=False => publish must abort."""
    needed = slots_in(body_html)
    if not needed:
        return True, "no generated images in this article"
    data = load(slug)
    problems = []
    for n in needed:
        slot = f"gen{n}"
        v = data.get(slot)
        if not v:
            problems.append(f"  {slot}: NO CRITIC VERDICT — run image-critic, "
                            f"then critic_gate.record('{slug}','{slot}',...)")
        elif v["verdict"] != "PASS":
            problems.append(f"  {slot}: REGENERATE — {v.get('fix','(no fix noted)')}")
    if problems:
        msg = (f"CRITIC GATE BLOCKED publish of '{slug}':\n"
               + "\n".join(problems)
               + "\n\nThe critic step is mandatory and cannot be skipped. "
                 "Fix/regenerate the images above, record PASS verdicts, retry.")
        return False, msg
    return True, f"critic gate PASS — {len(needed)} images all verified"


if __name__ == "__main__":  # tiny CLI for manual recording
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("slug"); r.add_argument("slot")
    r.add_argument("verdict"); r.add_argument("--scores", default="")
    r.add_argument("--fix", default="")
    s = sub.add_parser("show"); s.add_argument("slug")
    a = ap.parse_args()
    if a.cmd == "record":
        record(a.slug, a.slot, a.verdict, a.scores, a.fix)
        print(f"recorded {a.slot}={a.verdict.upper()} for {a.slug}")
    else:
        print(json.dumps(load(a.slug), indent=2))
