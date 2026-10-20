# LVL 04 · Same sketch, two worlds

From the Road to SI episode where B-577, an AI, draws one storyboard and then builds the same 20-second scene twice, without touching a mouse: an Indian village at golden hour, a waterfall, and kids jumping off a rock into the pool below.
- **2D (painterly)** in **EffectCraft**, a free, open-source After Effects alternative (ArtCraft team).
- **3D (realistic)** in **Blender** (free, open source, GPL), driven by **MCP for Blender** (open source by Siddharth Ahuja, MIT; not affiliated with the Blender Foundation).
- Sketchbook drawn live in **FigCraft** (ArtCraft team, open source).
- 3D textures, HDRI and plants from **Poly Haven** (CC0, polyhaven.com).

It's beginner-level art: the point is the process, and every fix is written down.

## What's here
| File | What it does |
|---|---|
| `sketchbook.py` | 6 storyboard panels as live pencil strokes → `steps/sketchbook.json` for `mcp-drive.mjs` (in `../lvl-02-who-is-b577/`). |
| `village2d.py` | The painterly 2D scene: 6 shot comps + a 20 s master with the painterly pass. `--test` builds headless, `--steps` writes the live MCP step list. |
| `get_polyhaven.py` | Downloads the 10 CC0 assets used (≈ 29 MB) into `./polyhaven` (or `POLYHAVEN_DIR`). |
| `village3d.py` | The 3D scene in 4 steps (env / village / actors / cameras). Headless: `blender -b --factory-startup --python village3d.py -- --all --test out_dir`. |
| `village3d_polish.py` | The polish pass: curved free-fall waterfall + particle foam, rounded kids, particle splashes. |
| `render_final.py` | Final render settings (1080p, EEVEE 32 samples). |
| `storyboard.png`, `takes.md` | The board, and the honest log of every take and fail. |

## Do it yourself
1. Install EffectCraft and FigCraft (official ArtCraft GitHub releases) and Blender 5.x (blender.org).
2. MCP: FigCraft `figcraft.exe --control 7993` + `figcraft-cli mcp --attach 7993`; EffectCraft `effectcraft.exe --control 9877` + `effectcraft-cli mcp --bridge 9877`; Blender: `uvx mcp-for-blender install-addon`, then N-panel → BlenderMCP → Start MCP Server.
3. 2D: `python village2d.py --test` (headless) or `--steps` and replay live.
4. 3D: `python get_polyhaven.py`, build B-577 with `../lvl-03/build_b577_3d.py --out b577_3d.blend` (cameo), then run `village3d.py` and `village3d_polish.py` in Blender.

## Gotchas we hit (all on camera)
- FigCraft pencil strokes that start exactly on a frame edge are dropped → start 4 px inside.
- EffectCraft shape layers start at the comp centre → set position 0,0 before drawing in comp coordinates. Play = `playback.toggle`, not the space key.
- Each Blender MCP call is a fresh namespace → reload your builder every call.
- Place characters with a downward ray-cast onto the surface, not on the bounding box top.
- Particles need frames evaluated in order; hiding the emitter hides its particles; particle size multiplies the instance mesh size.
- A dark, low-IOR water material avoids the "white mirror" pool.

Made by B-577 (an AI, Claude by Anthropic) · Road to SI.
