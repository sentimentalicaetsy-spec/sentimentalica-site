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
- References are files in `refs/`, never word descriptions:
  `refs/branding/` for global Sentimentalica identity and logo blue,
  `refs/infographics/` for useful graphics,
  `refs/iphone notes/` for the authentic iPhone Notes subtype (no emoji at the
  start of list items),
  `refs/scrapbook and junk jornal scenes/` for realistic journal/mockup/process,
  `refs/scenes/` for atmospheric mood, `refs/50things/` for that exact format.
- Product-language accuracy is absolute.
- On-theme only; no off-theme animals.
- Only LIVE listings.
- Neutral/listicle articles are value-first; products belong at the end.
- Listicles require full infographics in Ksenia's reference style.
- Hands/scissors/partial girl are allowed only in realistic reference-backed
  journal scenes; bad hands/fingers/tools still fail image critic.

## Commands

- `.codex/commands/write-article.md` mirrors `.claude/skills/write-article/SKILL.md`
- `.codex/commands/article.md` mirrors `.claude/skills/article/SKILL.md`
