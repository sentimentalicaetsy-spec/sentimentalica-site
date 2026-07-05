# Sentimentalica Content Factory — runbook

One command runs a full content cycle:
```
/content-cycle <listing id / theme / "this week's push">
```
Creative Director (the skill) orchestrates: Scout → `copywriter` →
`visual-agent` → `qa-critic` → `publisher` (agents in `.claude/agents/`).
Spec: `~/sentimentalica-pipeline/PINTEREST_CONTENT_FACTORY_SPEC.md`.

## What ships per cycle
- **Blog post** — live on https://sentimentalica.com/blog/ (auto-deployed via
  `tools/publish_post.py --push`), with inline live Etsy product cards
  (`{{etsy:ID}}` shortcodes).
- **Pinterest pin** — 1000×1500 Canva design + copy, staged in
  `staging/pins/<slug>/` for manual posting (no Pinterest API exists; the pin
  links to the blog post, which converts to Etsy).

## Fixed infrastructure
| Piece | Where |
|---|---|
| Pin brand template (1000×1500) | Canva — ID recorded below |
| Brand kit | Canva `kAGBZKF98nk` |
| Blog publishing tool | `tools/publish_post.py` (this repo) |
| Product-card feed | `sentimentalica-etsy-feed` worker `?ids=` |
| Voice anchor | site copy (About/Freebie/existing posts) — no one-pager yet |
| QA text rules | `seo_rules.md` + PROMPT_CLEANING_CHECKLIST pattern |

**Pin template ID:** _pending — created by the one-time setup in
PINTEREST_CONTENT_FACTORY_SPEC.md §3c; record the ID here when done._

## Open decisions (Ksenia)
- Cadence: on-request vs weekly (`/schedule`) — currently on-request.
- Brand-voice one-pager: not written; Copywriter anchors to site copy.
- Pinterest posting: manual (staged packages) until an API/browser flow exists.
