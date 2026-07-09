# Sentimentalica Codex Mirror

This directory mirrors the Claude Code content system. Parity is the goal:
Codex agents and commands must behave like their Claude twins for the same
input, with the same output contracts.

## Source of Truth

Read these before any content work:

- `AGENTS.md`
- `.codex/agents/*.md` (copied from `.claude/agents/*.md`)
- `.codex/skills/write-article/SKILL.md`
- `.codex/skills/article/SKILL.md`
- `ARTICLE_FUNCTION.md`
- `PIN_STRATEGY.md`
- `SCENE_STYLE.md`

## Shared Tools

Do not reimplement the engine. Agents orchestrate; Python tools enforce.

Use:

`/Users/kseniateter/sentimentalica-pipeline/.venv/bin/python`

Required shared tools:

- `tools/content_planner.py`
- `tools/plan_io.py`
- `tools/critic_gate.py`
- `tools/publish_post.py`
- `tools/insert_generated_images.py`
- `tools/render_list_infographic.py`
- `tools/pin_csv.py`
- `tools/pins_status.py`
- `tools/resolve_listing.py`

## Non-Negotiables

- The critic is a code gate. `publish_post.py` blocks without every generated
  image PASS in `staging/overnight/critic/<slug>.json`.
- References are files in `refs/`, never word descriptions.
- Product-language accuracy is absolute.
- On-theme only; no off-theme animals.
- Only LIVE listings.
- Neutral/listicle articles are value-first; products belong at the end.
- Listicles require full infographics in Ksenia's reference style.

## Commands

- `.codex/commands/write-article.md` mirrors `.claude/skills/write-article/SKILL.md`
- `.codex/commands/article.md` mirrors `.claude/skills/article/SKILL.md`
