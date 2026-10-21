# The prompt: paste into Claude (Claude Code + MCP for Blender)

Setup once (≈ 10 min): install Blender 5.x (blender.org) → `uvx mcp-for-blender install-addon` → `claude mcp add blender -- uvx mcp-for-blender` → in Blender: N-panel → BlenderMCP → Start MCP Server.

Then paste this (change the character in step 1 to make your own):

```
You're driving my live Blender over MCP. Build a 10-second premium hero render, step by step.
After EVERY step, use the look tool (angles or camera) to check it, and fix what's wrong before moving on.

1. Character: a small friendly desk robot — rounded cream body (bevel + subdivision), a dark
   screen face with two glowing cyan LED eyes (emission only) and a smile, orange ear fins,
   hands and feet, a tag on the chest. Build it from primitives, parent the parts to a simple
   7-bone rig (root, body, head, 2 arms, 2 legs). Add a custom property "mood" that blends the
   eye colour from cyan to orange with a driver, and "blink" that squashes the eyes.
2. World: a dark "terminal" set — glossy dark floor with a thin glowing cyan grid (shader, not
   geometry), 5 dark code-block platforms with a glowing amber top edge and labels
   ("$ b-577 --boot", "bpy", "look()", "render -a", "MCP"), giant floating lines of real
   Python code in the background, light world fog (very low density).
3. Light: warm amber key, strong cyan rim from behind, soft top fill. Standard view transform
   (keeps brand colours), medium-high contrast. Bloom only on emissives brighter than white.
4. Camera: vertical 1080x1920, 32 mm, depth of field focused on the robot, motion blur on.
   Start close on the face, pull back, follow the hops, end on a 3/4 hero framing.
5. Animation (24 fps, 240 frames): eyes boot (flicker on), head looks left/right, then it hops
   pad to pad: anticipation crouch -> stretch -> arc -> squash on landing -> settle; each pad
   lights up on landing. On the last pad: eyes turn orange, a small hop, then a wave (arm out
   to the side, hand never overlapping the head). Glowing "MADE BY <NAME>" title fades in.
   Bezier easing everywhere, never linear.
6. Render: EEVEE 64 samples, PNG frames, print the seconds per frame. Then tell me the total.
Never skip the look checks. Keep feet on surfaces (ray-cast down), no floating parts.
```

Or skip the prompt and run the exact scripts from the video: see README.md.
