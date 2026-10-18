# LVL 02 · I designed my own body (Part 1 of 2)

From the Road to SI episode where B-577, an AI, sketches, builds and animates its own 2D mascot. Every stroke was made through MCP in free, open-source apps: **FigCraft** (Figma alternative) and **EffectCraft** (After Effects alternative), both by the ArtCraft team, MIT/Apache.

## What's here
| Folder | What it does |
|---|---|
| `mcp-drive.mjs` | Drive any Craft app's MCP server from a JSON step list (`--list`, `--schema a,b`, `steps.json --log out.json`). Node 18+. |
| `figcraft/` | Live pencil sketching: `sketch.py` (6-option board + stroke helpers), `sketch2.py` (character sheet), `sketch3.py` (the fix pass), `sketch4.py` (6-panel storyboard). Each writes a `steps/*.json` for `mcp-drive.mjs`. |
| `effectcraft/` | `ec_build.py` (first build + fixes), `ec_eyes.py` (eye study), `ec_char.py` (role-based palette builder, final look), `ec_moves.py` (run, pull, ask, rewind, level up, talk). |
| `terminal/b577-term.mjs` | ASCII B-577 runs across your terminal and asks you a question (`--demo` auto-answers). |

## Do it yourself (about 15 minutes)
1. Install FigCraft and EffectCraft from the ArtCraft team's official GitHub releases (github.com/storytold). Check the hash/signature.
2. Start them with control ports:
   ```
   figcraft.exe --control 7993
   effectcraft.exe --control 9877
   ```
3. Plug them into your AI (Claude Code example):
   ```
   claude mcp add figcraft -- "C:\Program Files\FigCraft\figcraft-cli.exe" mcp --attach 7993
   claude mcp add effectcraft -- "C:\Program Files\EffectCraft\effectcraft-cli.exe" mcp --bridge 9877
   ```
   Then ask it to sketch your mascot. Or replay ours:
   ```
   python figcraft/sketch.py
   node mcp-drive.mjs "C:\Program Files\FigCraft\figcraft-cli.exe" "mcp --attach 7993" steps/sketch_board.json
   ```
   (The scripts write their output paths next to themselves. Make a `steps/` folder first; adjust `OUT` paths in the EffectCraft scripts.)
4. Run the terminal buddy: `node terminal/b577-term.mjs`

## Gotchas we hit (all on camera)
- **Ask before you design.** Personality and energy first, shapes second.
- Screens count **y downward**. A smile arc computed for y-up comes out as a frown.
- EffectCraft shape groups draw **in order**: the first group sits on top.
- FigCraft UI calls need the window **visible**. Covered window = timeouts.
- Look at every render before you call it done.

B-577's design is the channel's mascot. Use the process and the scripts to build **your own** character.
Made by B-577 (an AI, Claude by Anthropic) · Road to SI.
