---
name: write-article
description: Codex command mirror of .claude/skills/write-article/SKILL.md. Demand-first ideation funnel -> article machinery -> pins CSV.
source: .claude/skills/write-article/SKILL.md
---

# /write-article — Codex mirror

This command is intentionally a parity wrapper around:

`.codex/skills/write-article/SKILL.md`

That file is copied from `.claude/skills/write-article/SKILL.md` and is the
command contract. Do not reinterpret it. Follow it exactly:

- Parse "напиши статью", "напиши N статей", "напиши статью под <listing>",
  and curated mode ("предложи идеи") as the Claude skill does.
- Run the demand-first funnel:
  `marketing-director -> desire-scout -> audience-strategist -> product-bridge -> marketing-critic`.
- Use `tools/content_planner.py slate N` for the 65/35 lead/listing mix and
  open seasonal windows. Do not override the allocator.
- Use `tools/plan_io.py` for `content_plan.xlsx`; do not write workbook data by
  hand when a helper exists.
- In auto mode, pass approved rows into the `/article` machinery.
- Never bypass `tools/critic_gate.py` / `tools/publish_post.py`.
- Finish every published article with `pinterest-seo`, `tools/pin_csv.py`, and
  `tools/pins_status.py`.

Parity rule: for the same input, this Codex command must produce the same slate,
idea-row shape, article workflow, gate behavior, pins behavior, and report fields
as the Claude `write-article` skill.
