# B-577 storyboard (v4 look: two LED eyes, dark screen) — 6 panels drawn live in FigCraft over MCP; ends with a save.
#   python sketch4.py -> steps/storyboard.json
import json, math, os
from sketch import stroke, jit, ell, rrect, line, arc
from sketch2 import frame, text, draw, poly, FX

W = os.path.dirname(os.path.abspath(__file__))
OY = 3800                      # fourth row, under the v2.1 fixes
PW, PH, G = 560, 420, 60       # panel size

def bot(cx, cy, s=0.32, mood='smile', arm=None, legs='stand'):
    """small v4 B-577: TV head (two eyes, smile), fins, clock hands, body, arms, legs"""
    S = [rrect(cx - 190 * s, cy - 160 * s, 380 * s, 320 * s, 60 * s), rrect(cx - 150 * s, cy - 120 * s, 300 * s, 240 * s, 42 * s)]
    for d in (-1, 1):
        S.append(ell(cx + d * 62 * s, cy - 20 * s, 40 * s, 56 * s, 14, 0.05))
        S.append(poly((cx + d * 190 * s, cy - 60 * s), (cx + d * 245 * s, cy - 95 * s), (cx + d * 245 * s, cy + 75 * s), (cx + d * 190 * s, cy + 50 * s)))
    S.append(arc(cx, cy + 45 * s, 40 * s, math.pi * 0.15, math.pi * 0.85) if mood == 'smile' else ell(cx, cy + 70 * s, 14 * s, 16 * s, 10, 0.05))
    S += [line(cx, cy - 160 * s, cx - 35 * s, cy - 220 * s, 3), line(cx, cy - 160 * s, cx + 45 * s, cy - 260 * s, 3)]
    by = cy + 175 * s
    S.append(rrect(cx - 100 * s, by, 200 * s, 180 * s, 50 * s))
    arms = arm or [((-100, 40), (-170, 140)), ((100, 40), (170, 140))]
    for (x0, y0), (x1, y1) in arms:
        S += [line(cx + x0 * s, by + y0 * s, cx + x1 * s, by + y1 * s, 4), ell(cx + x1 * s, by + y1 * s, 22 * s, 22 * s, 10, 0.05)]
    if legs == 'run':
        S += [poly((cx - 40 * s, by + 180 * s), (cx - 110 * s, by + 240 * s), (cx - 170 * s, by + 220 * s)),
              poly((cx + 40 * s, by + 180 * s), (cx + 70 * s, by + 260 * s), (cx + 60 * s, by + 320 * s))]
    else:
        S += [line(cx - 40 * s, by + 180 * s, cx - 45 * s, by + 280 * s, 3), line(cx + 40 * s, by + 180 * s, cx + 45 * s, by + 280 * s, 3)]
    return S

PANELS = [
 ("1 · runs onto the terminal", lambda: bot(330, 170, legs='run', arm=[((-100, 40), (-180, 10)), ((100, 40), (170, 130))]) +
     [line(40, 330, 520, 330, 12), line(380, 165, 440, 165, 3), line(390, 190, 460, 190, 3)], "$ b577 --run"),
 ("2 · pulls the app out of its screen", lambda: bot(240, 170, arm=[((-100, 40), (-170, 140)), ((100, 40), (150, -80))]) +
     [rrect(330, 70, 140, 100, 14), line(345, 95, 455, 95, 3), line(345, 120, 420, 120, 3)], "→ FigCraft"),
 ("3 · asks you a question", lambda: bot(200, 190, mood='o') + [rrect(300, 50, 220, 120, 30), line(330, 170, 300, 200, 3)], "[y/n]?"),
 ("4 · rewinds a mistake", lambda: bot(280, 200) + [arc(280, 120, 150, math.pi * 1.1, math.pi * 1.9, 18), line(158, 32, 140, 70, 3), line(158, 32, 195, 45, 3)], "⟲ rewind"),
 ("5 · levels up", lambda: bot(280, 200, arm=[((-100, 40), (-150, -60)), ((100, 40), (150, -60))]) +
     [line(150, 60, 175, 30, 3), line(410, 60, 385, 30, 3), line(280, 20, 280, 0, 3)], "LVL 02 ✓"),
 ("6 · waves goodbye", lambda: bot(280, 190, arm=[((-100, 40), (-170, 140)), ((100, 40), (180, -40))]) +
     [arc(470, 80, 30, -0.6, 0.6), arc(470, 80, 50, -0.6, 0.6)], "see you next level"),
]

S = [["create_node", {"type": "section", "name": "B-577 v4 · storyboard", "x": FX - 60, "y": OY - 140, "width": 3 * (PW + G) + 60, "height": 2 * (PH + G) + 200}, 400]]
for k, (title, strokes, note) in enumerate(PANELS):
    ox, oy = FX + (k % 3) * (PW + G), OY + (k // 3) * (PH + G)
    frame(S, f"panel {k + 1}", ox, oy, PW, PH, '#F4EBDF')
    S.append(["pointer", {"tool": "pencil", "kind": "hover", "x": ox + 10, "y": oy + 10}, 50])
    draw(S, strokes(), ox, oy)
    text(S, ox + 16, oy + 12, title, 22, None, '#C25E00')
    text(S, ox + PW - 200, oy + PH - 46, note, 24, 190, '#0E8A96')
S.append(["select", {"ids": []}, 100]); S.append(["key", {"key": "1", "shift": True}, 1500])
S.append(["save_file", {"path": os.path.join(W, 'fig', 'b577_sketch.figcraft').replace(os.sep, '/')}, 300])
json.dump(S, open(os.path.join(W, 'steps', 'storyboard.json'), 'w'))
print(len(S), 'steps')
