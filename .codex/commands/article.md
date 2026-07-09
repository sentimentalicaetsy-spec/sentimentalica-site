---
name: article
description: Codex command mirror of .claude/skills/article/SKILL.md. Single listing -> full Sentimentalica article via shared tools; no publishing without critic PASS.
source: .claude/skills/article/SKILL.md
---

# /article — Codex mirror

This command is intentionally a parity wrapper around:

`.codex/skills/article/SKILL.md`

That file is copied from `.claude/skills/article/SKILL.md` and is the command
contract. Do not reinterpret it. Follow it exactly:

- Work from `/Users/kseniateter/sentimentalica-site`.
- Use `PY=/Users/kseniateter/sentimentalica-pipeline/.venv/bin/python`.
- Call shared tools in `tools/`; do not reimplement them.
- Use `tools/resolve_listing.py` for LIVE-listing checks.
- Use `tools/gen_article_assets.py`, `tools/insert_generated_images.py`,
  `tools/render_list_infographic.py`, and related image tools as specified.
- `tools/publish_post.py` calls `tools/critic_gate.py`; publish is blocked
  unless every generated image has a recorded PASS.
- Run `pinterest-seo` and `tools/pin_csv.py` for the mandatory pins finale.

Parity rule: for the same input, this Codex command must produce the same
workflow shape, artifacts, gate behavior, and report fields as the Claude
`article` skill.
