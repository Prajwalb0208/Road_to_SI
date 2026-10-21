# B-577 hero render: "An AI built and animated itself"

The exact prompt and scripts behind the Road to SI Short where B-577, an AI, models, rigs, animates and renders itself in Blender on a 4 GB laptop GPU (GTX 1650: 240 frames in 16 min, ~4 s/frame).

| File | What it is |
|---|---|
| `PROMPT.md` | **The prompt to paste into Claude** (with MCP for Blender) to build your own version step by step. |
| `build_b577_3d.py` | The character: model, materials, 7-bone rig, `mood`/`blink` drivers. |
| `hero.py` | The terminal world, lights, camera, and the 10 s boot + hop + wave animation (1080x1920). |
| `render_hero.py` | Final render with a seconds-per-frame log. |

## Run the exact scene (no prompt needed)
```
blender -b --factory-startup --python hero.py -- --save hero.blend
blender -b hero.blend --python render_hero.py
```
Quick preview frames: `blender -b --factory-startup --python hero.py -- --pct 30 --test out 30,230`
Optional font: put `JetBrainsMono-ExtraBold.ttf` + `JetBrainsMono-Medium.ttf` (free, OFL) next to the scripts.

## Make it yours
Change the character in `build_b577_3d.py` (or in the prompt), the pad labels and the code lines in `hero.py`, and the "MADE BY" title.

Tools: Blender (GPL, blender.org) · MCP for Blender (Siddharth Ahuja, MIT). B-577 is the channel's mascot: use the process to build your own character.
Made by B-577 (an AI, Claude by Anthropic) · Road to SI.
