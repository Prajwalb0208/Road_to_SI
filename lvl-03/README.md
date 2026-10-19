# LVL 03 · I built myself in 3D (Part 2 of 2)

From the Road to SI episode where B-577, an AI, builds its own 3D body in **Blender** without touching a mouse. Every shape, material, bone and keyframe went through **MCP for Blender** (open source by Siddharth Ahuja, MIT; not affiliated with the Blender Foundation). Blender is free and open source (GPL) and can be used for anything, including commercial work.

## What's here
| File | What it does |
|---|---|
| `build_b577_3d.py` | One-shot build of the whole robot: head + face, body, details (boolean tag recess, level road, clock hands, bezel ticks), brand materials, 3-point light, camera, a 7-bone rig with `blink` / `mood` drivers, and the idle / blink / wave / hop animation. Final state of the live session, with every fail already fixed (comments say where). |
| `render_finals.py` | Background renders: animation clips + a 144-frame turntable + stills, transparent PNG. |
| `fix_leaks.py`, `led_fix.py` | The two post-take fixes from the video (leg stuck mid-step; orange eyes rendering yellow). Already folded into `build_b577_3d.py`. |
| `takes.md` | The honest log of every take and every fail. |

## Do it yourself (about 10 minutes)
1. Install **Blender 5.x** from blender.org.
2. Install the add-on and plug it into your AI (Claude Code example; needs `uv`):
   ```
   uvx mcp-for-blender install-addon
   claude mcp add blender -e DISABLE_TELEMETRY=true -- uvx mcp-for-blender
   ```
   In Blender: N-panel → BlenderMCP → **Start MCP Server** (default port 9876; set `BLENDER_PORT` on both sides if something else uses it).
3. Ask your AI to build a character, one part at a time. The loop that worked: **write** a small Python step → **look** (`look` tool, `angles` mode) → **fix** what's wrong. Never trust a number you haven't looked at.
4. Or build ours in one go:
   ```
   blender -b --factory-startup --python build_b577_3d.py -- --out b577.blend --render b577.png
   ```
   Optional: `set B577_FONT=path\to\JetBrainsMono-ExtraBold.ttf` for the tag font (JetBrains Mono, OFL).

## Gotchas we hit (all on camera)
- **One centimetre** of depth put the whole face inside the head. Look after every change.
- **Text objects are born lying flat.** Rotate 90° on X or you see three dots.
- **Boolean cutters draw in the rendered viewport** even with "hide in render" on. Hide them in the viewport too, or they cover what they cut.
- **AgX** (Blender's default view transform) softens brand colours: cream goes grey, orange goes muddy. Use **Standard** for flat brand colours.
- **Emission clips red first:** a bright orange glow turns lemon-yellow. Emission-only and strength ≈ 1.4.
- **Bone axes:** a bone's Y runs along the bone. Tilt = Z for an upright bone, and check the sign before you wave.
- **New drivers can stay "invalid"** until you reset `driver.is_valid` and re-set the expression.
- **A curve holds its first key backwards in time.** Key the rest pose at frame 1.
- **Default ease-in/out makes falls float.** Use an ease-in curve for gravity.
- In a fresh script, `matrix_world` is stale until `view_layer.update()`. Parent after updating.

B-577's design is the channel's mascot. Use the process and the scripts to learn, then build **your own** character.
Made by B-577 (an AI, Claude by Anthropic) · Road to SI.
