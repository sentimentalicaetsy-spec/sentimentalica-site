# Codex setup prompt — mirror the Claude agents 1:1

Paste the block below to Codex (opened on `~/sentimentalica-site`) so it builds
the SAME agents for the SAME purposes. The `.claude/agents/*.md` files are the
source of truth; Codex agents must match their output contracts and call the
same shared tools (never reimplement them).

---

```
You are setting up Codex to run the Sentimentalica content system with the SAME
agents, for the SAME purposes, as the Claude Code setup already in this repo.
Both toolchains must behave identically. Do not invent — mirror what exists.

1) Read first (source of truth):
   - AGENTS.md  (project map + non-negotiable rules)
   - every file in .claude/agents/*.md  (the agent specs)
   - .claude/skills/write-article/SKILL.md  and  .claude/skills/article/
   - ARTICLE_FUNCTION.md, PIN_STRATEGY.md, SCENE_STYLE.md

2) For EACH file in .claude/agents/, create an equivalent Codex agent (in
   whatever form your version supports — custom prompt / agent definition),
   keeping IDENTICAL: name, purpose, inputs, the strict OUTPUT CONTRACT, the
   tools it uses, and the model intent. Parity is the goal: a Codex agent and
   its Claude twin must produce the same shape of output for the same input.
   Do not change the aims or the contracts.

3) Do NOT reimplement the tools. Agents are only orchestration; the real work
   and the GUARANTEES live in shared Python in tools/, which your agents must
   CALL exactly as the Claude agents do:
     - tools/content_planner.py   (65/35 mix + seasonal slate, windows open today)
     - tools/plan_io.py           (read/write content_plan.xlsx)
     - tools/critic_gate.py + tools/publish_post.py
                                  (publish is BLOCKED without every image PASS —
                                   this holds for Codex too; it is code, not an agent)
     - tools/insert_generated_images.py, tools/render_list_infographic.py (images)
     - tools/pin_csv.py + tools/pins_status.py  (Pinterest CSV + completeness)
     - tools/resolve_listing.py   (live-listing check)
   Use venv python: /Users/kseniateter/sentimentalica-pipeline/.venv/bin/python

4) Recreate the skills as Codex commands too:
   - write-article = the demand-first ideation funnel:
       marketing-director -> desire-scout -> audience-strategist ->
       product-bridge -> marketing-critic -> /article machinery -> pins->CSV
     Handles "напиши статью", "напиши N статей", "напиши статью под <listing>",
     and curated mode ("предложи идеи").
   - article = single listing -> full article.

5) Honor the non-negotiables (AGENTS.md): critic is a CODE gate; references are
   FILES in refs/ (never word-descriptions); product-language accuracy is
   absolute; on-theme only (no off-theme animals); only LIVE listings;
   neutral/listicle = value-first with product at the END; listicle -> full
   infographic in Ksenia's reference style.

6) When done: list every agent and skill you created; for each, name the Claude
   file it mirrors and confirm the output contract matches. Then, as a PARITY
   TEST, dry-run the funnel for "напиши 1 статью" WITHOUT publishing — show the
   slate (from content_planner.py) and the single idea it would produce.

Do not build or publish anything real yet. Set up the agents and prove parity first.
```
