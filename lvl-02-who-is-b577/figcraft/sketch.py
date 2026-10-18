# B-577 sketch board for FigCraft: 6 silhouette options drawn live with the Pencil over MCP (pointer down/move/up).
#   python -I sketch.py  -> steps/sketch_board.json   (run with filmcraft\tools\mcp-drive.mjs … --log steps/sketch_board_log.json)
import json, math, random, os

random.seed(577)
W = os.path.dirname(os.path.abspath(__file__))
F, GAP = 800, 120                     # frame size, gap between frames

def stroke(pts, pace=10, pr=0.6):
    S = [["pointer", {"tool": "pencil", "kind": "down", "x": round(pts[0][0], 1), "y": round(pts[0][1], 1), "pressure": pr}, pace]]
    S += [["pointer", {"kind": "move", "x": round(x, 1), "y": round(y, 1), "pressure": pr}, pace] for x, y in pts[1:]]
    S.append(["pointer", {"kind": "up", "x": round(pts[-1][0], 1), "y": round(pts[-1][1], 1)}, 90])
    return S

def jit(p, a=1.5):
    return [(x + random.uniform(-a, a), y + random.uniform(-a, a)) for x, y in p]

def ell(cx, cy, rx, ry, n=34, over=0.08, t0=-1.6):
    return [(cx + rx * math.cos(t0 + 2 * math.pi * (1 + over) * i / n), cy + ry * math.sin(t0 + 2 * math.pi * (1 + over) * i / n)) for i in range(n + 1)]

def rrect(x, y, w, h, r, n=8):
    P = []
    for cx, cy, a in [(x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0), (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)]:
        P += [(cx + r * math.cos(a + math.pi / 2 * i / n), cy + r * math.sin(a + math.pi / 2 * i / n)) for i in range(n + 1)]
    return P + [P[0]]

def line(x0, y0, x1, y1, n=10):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n + 1)]

def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def eyes(cx, cy, dx, rx, ry):
    return [ell(cx - dx, cy, rx, ry, 22, 0.04), ell(cx + dx, cy, rx, ry, 22, 0.04)]

def level_road(x, y, n=5, w=36, g=10):
    return [rrect(x + i * (w + g), y, w, 18, 6, 3) for i in range(n)]

# each option: list of strokes in frame-local coords + label
OPTS = [
 ("01 · round head, wide visor",
  [rrect(200, 150, 400, 330, 110), rrect(250, 220, 300, 170, 70), *eyes(400, 305, 65, 28, 34), rrect(150, 540, 500, 190, 60)]),
 ("02 · helmet + ear fins",
  [rrect(230, 140, 340, 360, 140), line(230, 260, 160, 200), line(160, 200, 175, 330), line(175, 330, 230, 360),
   line(570, 260, 640, 200), line(640, 200, 625, 330), line(625, 330, 570, 360), rrect(270, 250, 260, 120, 55),
   *eyes(400, 310, 55, 24, 30), rrect(180, 540, 440, 190, 70)]),
 ("03 · screen head",
  [rrect(190, 150, 420, 320, 40), rrect(225, 185, 350, 250, 26), arc(340, 320, 30, 3.5, 5.9), arc(460, 320, 30, 3.5, 5.9),
   line(400, 470, 400, 530, 6), rrect(170, 530, 460, 200, 50)]),
 ("04 · capsule + lens eyes",
  [rrect(260, 120, 280, 390, 140), ell(400, 260, 62, 62), ell(400, 380, 50, 50), ell(230, 300, 26, 50, 20, 0.04), ell(570, 300, 26, 50, 20, 0.04),
   rrect(190, 545, 420, 185, 80)]),
 ("05 · shoulders + level road",
  [rrect(260, 120, 280, 260, 100), rrect(290, 175, 220, 110, 50), *eyes(400, 230, 50, 20, 26), rrect(110, 420, 580, 300, 120),
   ell(180, 470, 70, 50), ell(620, 470, 70, 50), rrect(330, 520, 140, 50, 12), *level_road(290, 620)]),
 ("06 · minimal: circle + visor slit",
  [ell(400, 300, 190, 190, 46, 0.05), rrect(250, 260, 300, 70, 35), *eyes(400, 295, 60, 14, 18), rrect(200, 540, 400, 190, 90),
   rrect(350, 590, 100, 40, 10)]),
]

S = [["create_node", {"type": "section", "name": "B-577 · sketch board", "x": -60, "y": -140, "width": 3 * F + 2 * GAP + 120, "height": 2 * F + GAP + 200}, 400]]
for k, (label, strokes) in enumerate(OPTS):
    ox, oy = (k % 3) * (F + GAP), (k // 3) * (F + GAP)
    S.append(["create_node", {"type": "frame", "name": f"sketch {label[:2]}", "x": ox, "y": oy, "width": F, "height": F, "props": {"fill": "#F4EBDF"}}, 300])
    S.append(["key", {"key": "2", "shift": True}, 500])           # zoom to the new frame (it is selected)
    S.append(["select", {"ids": []}, 100])
    for st in strokes:
        S += stroke([(ox + x, oy + y) for x, y in jit(st)])
    S.append(["create_node", {"type": "text", "name": f"label {label[:2]}", "x": ox + 30, "y": oy + 24, "text": label, "props": {"fontSize": 30, "fill": "#17110E"}}, 500])
S.append(["select", {"ids": []}, 100])
S.append(["key", {"key": "1", "shift": True}, 2500])               # zoom to fit: the whole board
json.dump(S, open(os.path.join(W, 'steps', 'sketch_board.json'), 'w'))
print(len(S), 'steps,', sum(1 for s in S if s[0] == 'pointer' and s[1].get('kind') == 'down'), 'strokes')
