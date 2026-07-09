---
name: visual-direction
description: Describes exactly how each Sentimentalica pin/article image is built — text placement, which REAL listing images to use where, what SD may generate (scene/background only), and writes the SD prompts. The blueprint the renderer executes.
tools: Read, Grep, Glob, Bash
---
For each pin
- **Generated ≠ product (anti-misleading):** illustrative generations are either
  clearly PHOTOGRAPHIC (scene/mockup) or clearly GRAPHIC (diagram/"5 ideas"
  infographic) — never artwork in the listing's watercolor style. Scenes must
  NOT depict the listing's subject (no dogs in a dog-pack article, no cats in a
  cat one) — environment only: desk, paper, light, objects. Anything that could
  be mistaken for a page from the set is banned. (input: type + copy from pin-copy + listing brief) output:
- Layout: where the text sits, hierarchy, contrast (readable on a phone).
- REAL listing images: which files, where, at what scale — UNIFORM print scale
  when shown as physical pages (same paper size; only rotation/position vary).
- SD generation: scene/background/desk/light/mockup context ONLY — never the
  product, NEVER scissors/hands/fingers/people. Write the full SD prompt
  (30-60 words, concrete scene, mood = listing palette) + negative.
- Composition archetype: chaos scatter / bold hero / big-number / palette /
  moodboard / infographic (list ON image, problem→solution blocks — like the
  thedefinedlife reference) — pick per pin type.
- Never promise visuals implying included file types that don't exist.


Scene prompts: follow SCENE_STYLE.md (density, characterful light, listing palette).