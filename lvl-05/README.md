# Road to SI · LVL 05 — mech dragon, built from code (free kit)

Everything B-577 used to build, rig, animate and render the mechanical dragon in the video: plain Python for Blender, no paid add-ons.
Do it yourself in about 10 minutes of setup (the render itself takes longer).

## What you need
- **Blender 5.2** (free, GPL) — https://www.blender.org
- Two free **Poly Haven** assets (CC0): `rock_moss_set_01` and `boulder_01`, 1k glTF — https://polyhaven.com/models
  Put them in a `polyhaven` folder next to these scripts (`polyhaven/rock_moss_set_01/rock_moss_set_01_1k.gltf`, `polyhaven/boulder_01/boulder_01_1k.gltf`), or set `POLYHAVEN_DIR`.
- Any GPU that runs EEVEE. The video's machine: a laptop with a GTX 1650 (4 GB).
- Optional, to drive Blender live from an AI like in the video: **MCP for Blender** by Siddharth Ahuja (MIT).

## Steps
1. Put all `.py` files from this folder in one folder.
2. Build the whole scene (dragon + rig + temple + 640-frame animation) and save it, rendering a few test frames:
   ```
   blender -b --factory-startup --python build_dragon.py -- out 30 300 600
   ```
   → `mech_dragon.blend` + `out/v7_030.png …`. A full build takes a few minutes.
3. Render the animation (EEVEE, half resolution preview; edit `render_preview.py` for full size/samples):
   ```
   blender -b mech_dragon.blend --python render_preview.py -- frames
   ```
   then `ffmpeg -framerate 24 -i frames/p_%04d.png -c:v libx264 -pix_fmt yuv420p dragon.mp4`
4. Check it like the video did:
   - `blender -b mech_dragon.blend --python collide.py -- 6 1 640` — every wing part vs every object, every 6th frame (the video went 4403 → 0 hits).
   - `blender -b mech_dragon.blend --python stills.py -- out 130 430 620` — single frames (particles evaluated in order).
   - `blender -b mech_dragon.blend --python bench.py -- bench` — EEVEE vs Cycles timing on your GPU.

## What each file does
| File | Builds |
|---|---|
| `dragon.py` | v1 base: skeleton layout, rig (51 bones), ruins set, light, camera, awakening animation |
| `mecha.py` | candy paint (cavity, flake, clear coat, edge wear), kitbash parts (piston, gear, turbine, vent, ribs, split panels), body, fierce face, micro details (rivets, codes, LEDs), transformer armour, bigger animation, pistons |
| `v7.py` | heavy patterned wings, face internals, gearboxes/gearsets/cables/tools, temple props, laser |
| `v8.py` | mystical temple (runes, portal, glyph pillars, floating rocks, crystals, chains, guardian head), dragon-tracking lights, eye/scale head pass, dark grade |
| `v9.py` | stone statue reveal, night storm sky, wall breach + flight |
| `v10.py` | eyes in sockets, flight physics (flap cycle, tuck), wing clearance zones, flight camera |
| `v11.py` | natural wall burst: jagged hole, fractured rocks, gravel, volumetric dust |
| `build_dragon.py` | runs all of the above in order |
| `BUILD_LOG.md` | every version, every note, every fail and fix |

Note: these are the scripts as they stood at the end of the video. They reproduce the dragon and the 640-frame shot; tiny details (exact props, the laser target) can differ from the rendered hero because fixes kept landing after it.

Made by B-577 (Claude Opus 5.5) for Road to SI. Scripts: MIT. Poly Haven assets: CC0. Blender: GPL.
