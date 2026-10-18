# B-577 v2 character sheet (concept C: clockface TV + cursor eye), drawn live in FigCraft over MCP.
#   python -I sketch2.py -> steps/sheet.json
import json, math, os
from sketch import stroke, jit, ell, rrect, line, arc

W = os.path.dirname(os.path.abspath(__file__))
FX, FY = 3000, 0           # sheet starts right of the v1 board

def poly(*p): return list(p)

def head(cx, cy, s=1.0, eye='cursor', lit=2):
    """TV head centred at (cx, cy): bezel, screen, 12 dial ticks (lit ones drawn bold), eye, fins, clock hands."""
    S = []
    hw, hh = 190 * s, 160 * s
    S.append(rrect(cx - hw, cy - hh, 2 * hw, 2 * hh, 60 * s))
    S.append(rrect(cx - 150 * s, cy - 120 * s, 300 * s, 240 * s, 42 * s))
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        r0, r1 = (1.0, 1.12) if i >= lit else (0.98, 1.16)
        S.append(line(cx + 165 * s * r0 * math.cos(a), cy + 136 * s * r0 * math.sin(a),
                      cx + 165 * s * r1 * math.cos(a), cy + 136 * s * r1 * math.sin(a), 2))
    if eye == 'cursor': S.append(rrect(cx - 20 * s, cy - 55 * s, 40 * s, 110 * s, 20 * s, 4))
    elif eye == 'blink': S.append(line(cx - 30 * s, cy, cx + 30 * s, cy, 4))
    elif eye == 'happy': S.append(arc(cx, cy + 25 * s, 40 * s, math.pi * 1.1, math.pi * 1.9))
    elif eye == 'squint': S.append(poly((cx - 35 * s, cy - 20 * s), (cx + 30 * s, cy), (cx - 35 * s, cy + 20 * s)))
    for d in (-1, 1):   # speaker ear fins
        x0 = cx + d * hw
        S.append(poly((x0, cy - 60 * s), (x0 + d * 55 * s, cy - 95 * s), (x0 + d * 55 * s, cy + 75 * s), (x0, cy + 50 * s)))
        S.append(line(x0 + d * 20 * s, cy - 40 * s, x0 + d * 20 * s, cy + 35 * s, 3))
    S.append(ell(cx, cy - hh - 6 * s, 9 * s, 9 * s, 12, 0.05))                      # clock-hand pivot
    S.append(line(cx, cy - hh - 10 * s, cx - 35 * s, cy - hh - 70 * s, 4))         # hour hand
    S.append(line(cx, cy - hh - 10 * s, cx + 45 * s, cy - hh - 110 * s, 5))        # minute hand
    return S

def body(cx, top, arms='wave', legs='stand'):
    S = [rrect(cx - 100, top, 200, 190, 50), rrect(cx - 45, top + 60, 90, 40, 10)]
    for x in range(-30, 31, 15): S.append(line(cx + x - 5, top + 140, cx + x + 5, top + 140, 1))   # level road dots
    if arms == 'wave':
        S += [poly((cx - 100, top + 40), (cx - 160, top + 110), (cx - 175, top + 170)), ell(cx - 178, top + 192, 22, 22, 14, 0.05),
              poly((cx + 100, top + 40), (cx + 170, top - 20), (cx + 200, top - 90)), ell(cx + 205, top - 112, 22, 22, 14, 0.05)]
    elif arms == 'run':
        S += [poly((cx - 100, top + 40), (cx - 170, top + 20), (cx - 220, top + 70)), ell(cx - 236, top + 88, 22, 22, 14, 0.05),
              poly((cx + 100, top + 40), (cx + 150, top + 120), (cx + 215, top + 140)), ell(cx + 238, top + 142, 22, 22, 14, 0.05)]
    if legs == 'stand':
        S += [line(cx - 40, top + 190, cx - 45, top + 290, 4), ell(cx - 55, top + 308, 38, 18, 16, 0.05),
              line(cx + 40, top + 190, cx + 45, top + 290, 4), ell(cx + 55, top + 308, 38, 18, 16, 0.05)]
    else:   # mid-stride
        S += [poly((cx - 40, top + 190), (cx - 110, top + 250), (cx - 170, top + 230)), ell(cx - 192, top + 236, 34, 16, 16, 0.05),
              poly((cx + 40, top + 190), (cx + 70, top + 270), (cx + 60, top + 330)), ell(cx + 80, top + 345, 34, 16, 16, 0.05),
              line(cx - 330, top + 60, cx - 260, top + 60, 3), line(cx - 350, top + 110, cx - 270, top + 110, 3), line(cx - 320, top + 160, cx - 255, top + 160, 3)]
    return S

def frame(S, name, x, y, w, h, fill='#F4EBDF'):
    S.append(["create_node", {"type": "frame", "name": name, "x": x, "y": y, "width": w, "height": h, "props": {"fill": fill}}, 300])
    S.append(["key", {"key": "2", "shift": True}, 450]); S.append(["select", {"ids": []}, 80])

def text(S, x, y, t, size=30, w=None, fill='#17110E'):
    n = {"type": "text", "x": x, "y": y, "text": t, "props": {"fontSize": size, "fill": fill}}
    if w: n["width"] = w
    S.append(["create_node", n, 450])

def draw(S, strokes, ox, oy):
    for st in strokes:
        st = st if len(st) < 8 else st[::2] + [st[-1]]          # half the points: same look, half the take time
        S += stroke([(ox + x, oy + y) for x, y in jit(st, 1.3)], pace=8)

S = [["create_node", {"type": "section", "name": "B-577 v2 · character sheet", "x": FX - 60, "y": FY - 140, "width": 3720, "height": 2360}, 400]]
# 1 owner input (the lesson: ask first)
frame(S, 'owner input', FX, FY, 800, 1000, '#FFF4E3')
text(S, FX + 40, FY + 40, 'v1 mistake: I designed myself without asking how I should feel.', 34, 720)
text(S, FX + 40, FY + 200, 'owner input →', 40, 720, '#FF8A1F')
text(S, FX + 40, FY + 270, '• more energy: upbeat but calm\n• a full body, not just a face\n• runs around the terminal\n• asks you questions\n• clock + screen head\n• one capsule eye\n• works in 2D and 3D', 34, 720)
text(S, FX + 40, FY + 820, 'now I ask before I draw.', 34, 720, '#FF8A1F')
# 2 front
ox = FX + 920; frame(S, 'front', ox, FY, 800, 1000); draw(S, head(400, 300) + body(400, 480), ox, FY); text(S, ox + 30, FY + 24, 'front · waving', 30)
# 3 side
ox = FX + 1840; frame(S, 'side', ox, FY, 800, 1000)
side = [rrect(300, 140, 220, 320, 60), arc(520, 300, 120, -0.9, 0.9), poly((360, 230), (300, 200), (300, 370), (360, 340)),
        ell(410, 128, 9, 9, 12, 0.05), line(410, 124, 380, 60, 4), line(410, 124, 470, 20, 5),
        rrect(340, 480, 150, 190, 40), poly((380, 520), (420, 600), (470, 640)), ell(486, 652, 22, 22, 14, 0.05),
        line(390, 670, 385, 770, 4), ell(400, 788, 40, 18, 16, 0.05), line(440, 670, 445, 770, 4), ell(462, 788, 40, 18, 16, 0.05)]
draw(S, side, ox, FY); text(S, ox + 30, FY + 24, 'side · screen bulges like a CRT', 30)
# 4 run pose
ox = FX + 2760; frame(S, 'run', ox, FY, 900, 1000); draw(S, head(470, 280, 0.92, 'happy') + body(470, 450, 'run', 'run'), ox, FY)
text(S, ox + 30, FY + 24, 'run · along the command line', 30)
# 5 expressions
oy = FY + 1120; frame(S, 'expressions', FX, oy, 1720, 900)
for k, e in enumerate(['cursor', 'blink', 'happy', 'squint']):
    draw(S, head(215 + k * 430, 420, 0.8, e), FX, oy); text(S, FX + 120 + k * 430, oy + 700, ['idle ▮', 'blink', 'happy', 'focused'][k], 34)
text(S, FX + 30, oy + 24, 'the eye is a cursor · the dial lights one tick per level', 30)
# 6 ASCII form + palette
ox = FX + 1840; frame(S, 'terminal form', ox, oy, 1820, 900, '#17110E')
text(S, ox + 60, oy + 120, '    \\  /\n .-------.\n | ( ▮ ) |))\n \'-------\'\n   /| |\\\n    d b', 64, 700, '#F4EBDF')
text(S, ox + 60, oy + 40, '$ b577 --run', 34, None, '#FFA448')
for k, (c, n) in enumerate([('#F4EBDF', 'cream shell'), ('#CDEFF2', 'screen glass'), ('#FFA448', 'eye + tag'), ('#D9CBB8', 'panel lines')]):
    S.append(["create_node", {"type": "rectangle", "x": ox + 900 + k * 220, "y": oy + 160, "width": 180, "height": 180, "props": {"fill": c, "cornerRadius": 24}}, 250])
    text(S, ox + 900 + k * 220, oy + 360, n, 26, 190, '#F4EBDF')
text(S, ox + 900, oy + 520, 'light body · espresso stays the background', 30, 860, '#F4EBDF')
S.append(["select", {"ids": []}, 100]); S.append(["key", {"key": "1", "shift": True}, 2500])
json.dump(S, open(os.path.join(W, 'steps', 'sheet.json'), 'w'))
print(len(S), 'steps,', sum(1 for s in S if s[0] == 'pointer' and s[1].get('kind') == 'down'), 'strokes')
