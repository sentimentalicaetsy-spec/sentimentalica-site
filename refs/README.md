# Reference intake — Ksenia drops her real reference IMAGES here (as files)

These folders are the GROUND TRUTH. Every image the pipeline makes is judged
against the files here — not against words. Empty folder = the agent is blind
and falls back to my paraphrase (this is what caused "как об стенку горохом").

## refs/scenes/  — atmospheric scene references (the "gen3" bar)
The dreamy, save-worthy corners a girl wants to escape INTO. Golden light,
layered depth, mood. NOT bright sterile stock desks. Name them freely
(e.g. cozy-terracotta-corner.jpg). The image-critic compares every scene to
these; a scene that doesn't reach this bar = REGENERATE.

## refs/infographics/  — list/infographic layout references (the "50 things" bar)
The exact grid/table style you want copied 1:1: readable font WITHOUT zooming,
clear grid, real illustration. Drop the screenshot you keep sending.
render_list_infographic.py must reproduce THIS, not my interpretation.

## refs/50things/  — (optional) the specific 50-things reference
If the 50-things list has its own exact reference, put it here.
