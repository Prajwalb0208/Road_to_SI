# B-577 v2.1 fix pass ("rewind"): the eye never disappears, a small mouth shows the mood, lit level ticks are amber,
# waving arm shortened, run pose leans forward. Drawn live in FigCraft over MCP, below the v2 sheet; ends with a save.
#   python sketch3.py -> steps/fix.json
import json, math, os
from sketch import stroke, jit, ell, rrect, line, arc
from sketch2 import body, frame, text, draw, poly, FX

W = os.path.dirname(os.path.abspath(__file__))
OY = 2400                     # third row, under the v2 sheet
LIT = '#FFA448'

def head2(cx, cy, s=1.0, mood='idle'):
    S, dots = [], []
    hw, hh = 190 * s, 160 * s
    S += [rrect(cx - hw, cy - hh, 2 * hw, 2 * hh, 60 * s), rrect(cx - 150 * s, cy - 120 * s, 300 * s, 240 * s, 42 * s)]
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        x, y = cx + 175 * s * math.cos(a), cy + 145 * s * math.sin(a)
        if i < 2: dots.append((x, y))                       # LVL 02 = 2 lit ticks (filled amber dots)
        else: S.append(line(x - 8 * s * math.cos(a), y - 8 * s * math.sin(a), x + 8 * s * math.cos(a), y + 8 * s * math.sin(a), 2))
    eh = {'idle': 110, 'blink': 18, 'happy': 90, 'focused': 70, 'wow': 120}[mood] * s
    S.append(rrect(cx - 20 * s, cy - 20 * s - eh / 2, 40 * s, eh, min(20 * s, eh / 2), 4))   # the capsule eye, always there
    my = cy + 70 * s
    if mood == 'happy': S.append(arc(cx, my - 22 * s, 30 * s, math.pi * 0.15, math.pi * 0.85))    # ‿ smile (y down: 0..π is the lower half)
    elif mood == 'focused': S.append(line(cx - 22 * s, my, cx + 22 * s, my, 4))
    elif mood == 'wow': S.append(ell(cx, my, 12 * s, 14 * s, 14, 0.05))
    elif mood == 'idle': S.append(arc(cx, my - 14 * s, 18 * s, math.pi * 0.2, math.pi * 0.8))
    for d in (-1, 1):
        x0 = cx + d * hw
        S += [poly((x0, cy - 60 * s), (x0 + d * 55 * s, cy - 95 * s), (x0 + d * 55 * s, cy + 75 * s), (x0, cy + 50 * s)),
              line(x0 + d * 20 * s, cy - 40 * s, x0 + d * 20 * s, cy + 35 * s, 3)]
    S += [ell(cx, cy - hh - 6 * s, 9 * s, 9 * s, 12, 0.05), line(cx, cy - hh - 10 * s, cx - 35 * s, cy - hh - 70 * s, 4),
          line(cx, cy - hh - 10 * s, cx + 45 * s, cy - hh - 110 * s, 5)]
    return S, dots

def lit(S, dots, ox, oy, s=1.0):
    for x, y in dots:
        S.append(["create_node", {"type": "ellipse", "x": ox + x - 9 * s, "y": oy + y - 9 * s, "width": 18 * s, "height": 18 * s,
                                  "props": {"fill": LIT}}, 200])

S = [["create_node", {"type": "section", "name": "B-577 v2.1 · rewind + fixes", "x": FX - 60, "y": OY - 140, "width": 3720, "height": 1240}, 400]]
# 1 rewind note
frame(S, 'rewind', FX, OY, 800, 1000, '#FFF4E3')
text(S, FX + 40, OY + 40, '⟲ rewind', 56, 720, '#FF8A1F')
text(S, FX + 40, OY + 150, 'mistakes in v2:\n• "happy" came out as a frown — the arc was flipped (screen y points down)\n• the eye vanished in 2 expressions\n• waving hand landed on my own screen\n• lit level ticks looked like the rest\n• run pose: stiff', 32, 720)
text(S, FX + 40, OY + 640, 'fix: the eye never leaves.\na small mouth shows the mood.\nlit ticks = amber.', 34, 720, '#FF8A1F')
# 2 front v2.1 (shorter wave)
ox = FX + 920; frame(S, 'front v2.1', ox, OY, 800, 1000)
h, d = head2(400, 300, 1.0, 'happy'); b = body(400, 480, 'wave', 'stand'); draw(S, h + b[:9] + b[-4:], ox, OY)   # torso, tag, road, left arm, legs
draw(S, [poly((500, 520), (560, 480), (590, 420)), ell(598, 402, 22, 22, 14, 0.05)], ox, OY)         # shorter waving arm, clear of the head
lit(S, d, ox, OY); text(S, ox + 30, OY + 24, 'front · happy = eye + smile', 30)
# 3 run v2.1 (lean)
ox = FX + 1840; frame(S, 'run v2.1', ox, OY, 900, 1000)
h, d = head2(520, 290, 0.92, 'happy'); draw(S, h + body(470, 460, 'run', 'run'), ox, OY); lit(S, d, ox, OY, 0.92)
text(S, ox + 30, OY + 24, 'run · head leads, body follows', 30)
# 4 expressions v2.1 (eye always there)
ox = FX + 2760; frame(S, 'expressions v2.1', ox, OY, 900, 1000)
for k, m in enumerate(['idle', 'happy', 'focused', 'wow']):
    cx, cy = 230 + (k % 2) * 440, 260 + (k // 2) * 440
    h, d = head2(cx, cy, 0.62, m); draw(S, h, ox, OY); lit(S, d, ox, OY, 1.0)
    text(S, ox + cx - 50, OY + cy + 130, m, 30)
S.append(["select", {"ids": []}, 100]); S.append(["key", {"key": "1", "shift": True}, 1500])
S.append(["save_file", {"path": os.path.join(W, 'fig', 'b577_sketch.figcraft').replace(os.sep, '/')}, 300])
json.dump(S, open(os.path.join(W, 'steps', 'fix.json'), 'w'))
print(len(S), 'steps,', sum(1 for s in S if s[0] == 'pointer' and s[1].get('kind') == 'down'), 'strokes')
