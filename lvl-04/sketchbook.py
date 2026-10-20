# LVL 04 shared sketchbook: 6 storyboard panels of the village waterfall scene, drawn live in FigCraft with the Pencil over MCP.
# One board drives BOTH versions (2D EffectCraft + 3D Blender). Ends with a save.
#   python -I sketchbook.py -> steps/sketchbook.json
#   node ..\lvl-02-who-is-b577\mcp-drive.mjs "C:\Program Files\FigCraft\figcraft-cli.exe" "mcp --attach 7993" steps\sketchbook.json --log steps\sketchbook_log.json
import json, math, random, os

random.seed(1115)
W = os.path.dirname(os.path.abspath(__file__))
PW, PH, G, OX, OY = 560, 420, 60, 0, 0

def stroke(pts, pace=8, pr=0.6):
    S = [["pointer", {"tool": "pencil", "kind": "down", "x": round(pts[0][0], 1), "y": round(pts[0][1], 1), "pressure": pr}, pace]]
    S += [["pointer", {"kind": "move", "x": round(x, 1), "y": round(y, 1), "pressure": pr}, pace] for x, y in pts[1:]]
    S.append(["pointer", {"kind": "up", "x": round(pts[-1][0], 1), "y": round(pts[-1][1], 1)}, 80])
    return S
def jit(p, a=1.3): return [(x + random.uniform(-a, a), y + random.uniform(-a, a)) for x, y in p]
def ell(cx, cy, rx, ry, n=24, over=0.06, t0=-1.6):
    return [(cx + rx * math.cos(t0 + 2 * math.pi * (1 + over) * i / n), cy + ry * math.sin(t0 + 2 * math.pi * (1 + over) * i / n)) for i in range(n + 1)]
def line(x0, y0, x1, y1, n=6): return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n + 1)]
def arc(cx, cy, r, a0, a1, n=12, ry=None):
    ry = ry or r; return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def poly(*p): return list(p)
def wavy(x0, x1, y, amp=4, n=12): return [(x0 + (x1 - x0) * i / n, y + amp * math.sin(i * 1.7)) for i in range(n + 1)]

# ---------------- scene pieces (panel-local coords, 560 x 420) ----------------
def hills(): return [wavy(0, 560, 120, 10, 14)]
def sun(cx, cy, r=22): return [ell(cx, cy, r, r)] + [line(cx + (r + 6) * math.cos(a), cy + (r + 6) * math.sin(a), cx + (r + 18) * math.cos(a), cy + (r + 18) * math.sin(a), 2) for a in [i * math.pi / 4 for i in range(8)]]
def house(x, y, w=70, h=40):   # tiled roof (Western Ghats): low wide triangle + walls + door
    return [poly((x - 10, y), (x + w / 2, y - 30), (x + w + 10, y), (x - 10, y)), line(x - 4, y + 6, x + w + 4, y + 6, 3),
            poly((x, y), (x, y + h), (x + w, y + h), (x + w, y)), poly((x + w / 2 - 8, y + h), (x + w / 2 - 8, y + h - 22), (x + w / 2 + 8, y + h - 22), (x + w / 2 + 8, y + h))]
def palm(x, y, h=110, lean=12):
    top = (x + lean, y - h)
    S = [[(x + lean * (i / 6) ** 1.5 + random.uniform(-1, 1), y - h * i / 6) for i in range(7)]]
    for dx, up in ((-1, 0.2), (-0.7, -0.5), (0.7, -0.5), (1, 0.2), (-0.25, -0.9)):   # drooping fronds
        S.append([(top[0] + dx * 60 * t, top[1] + 60 * (up * t + 0.9 * t * t)) for t in (0, 0.25, 0.5, 0.75, 1)])
    return S
def fall(x, top, bot, w=60):    # waterfall: cliff lip + falling strokes + mist puffs
    S = [line(x - 30, top, x + w + 30, top, 4)]
    S += [line(x + k, top + 4, x + k + random.uniform(-3, 3), bot, 5) for k in range(6, w, 12)]
    S += [ell(x + k, bot + 4, 18, 9, 10) for k in (0, w / 2, w)]
    return S
def kid(x, y, s=1.0, pose='stand'):   # stylised kid: round head, body, limbs
    S = [ell(x, y - 46 * s, 9 * s, 10 * s, 12), line(x, y - 36 * s, x, y - 12 * s, 3)]
    if pose == 'stand':  S += [line(x, y - 30 * s, x - 12 * s, y - 18 * s, 2), line(x, y - 30 * s, x + 12 * s, y - 18 * s, 2)]
    if pose == 'count':  S += [line(x, y - 30 * s, x - 12 * s, y - 18 * s, 2), line(x, y - 30 * s, x + 10 * s, y - 56 * s, 2)]
    if pose == 'jump':   S += [line(x, y - 30 * s, x - 16 * s, y - 50 * s, 2), line(x, y - 30 * s, x + 16 * s, y - 50 * s, 2)]
    S += ([line(x, y - 12 * s, x - 8 * s, y + 6 * s, 2), line(x, y - 12 * s, x + 8 * s, y + 6 * s, 2)] if pose != 'jump'
          else [line(x, y - 12 * s, x - 14 * s, y, 2), line(x, y - 12 * s, x + 10 * s, y + 4 * s, 2)])
    return S
def splash(x, y, s=1.0): return [arc(x, y, 16 * s, math.pi * 1.1, math.pi * 1.9, 6), line(x - 10 * s, y - 6 * s, x - 18 * s, y - 22 * s, 2), line(x + 10 * s, y - 6 * s, x + 18 * s, y - 22 * s, 2), line(x, y - 10 * s, x, y - 28 * s, 2)]
def bot(cx, cy, s=0.16):   # tiny B-577 (v4), NEW wave: arm out to the side, hand clear of the head
    S = [poly((cx - 190 * s, cy - 160 * s), (cx + 190 * s, cy - 160 * s), (cx + 190 * s, cy + 160 * s), (cx - 190 * s, cy + 160 * s), (cx - 190 * s, cy - 160 * s)),
         ell(cx - 62 * s, cy - 20 * s, 36 * s, 50 * s, 10), ell(cx + 62 * s, cy - 20 * s, 36 * s, 50 * s, 10), arc(cx, cy + 45 * s, 40 * s, math.pi * 0.15, math.pi * 0.85, 6),
         line(cx, cy - 160 * s, cx + 45 * s, cy - 260 * s, 2)]
    by = cy + 175 * s
    S += [poly((cx - 100 * s, by), (cx + 100 * s, by), (cx + 100 * s, by + 180 * s), (cx - 100 * s, by + 180 * s), (cx - 100 * s, by)),
          line(cx - 100 * s, by + 40 * s, cx - 170 * s, by + 140 * s, 2), line(cx + 100 * s, by + 40 * s, cx + 250 * s, by - 10 * s, 2),
          ell(cx + 250 * s, by - 10 * s, 24 * s, 24 * s, 8), line(cx - 40 * s, by + 180 * s, cx - 45 * s, by + 280 * s, 2), line(cx + 40 * s, by + 180 * s, cx + 45 * s, by + 280 * s, 2)]
    return S

PANELS = [
 ("1 · village at golden hour (wide)", lambda: hills() + sun(470, 80) + fall(250, 95, 200, 50) + [wavy(0, 560, 300, 3)] +
     house(40, 255) + house(130, 265, 60, 34) + palm(300, 330) + palm(470, 340, 130, -10), "3–4 s · slow push"),
 ("2 · the waterfall, close", lambda: [line(60, 40, 120, 400, 6), line(500, 40, 440, 400, 6)] + fall(170, 50, 330, 220) +
     [line(330, 30, 430, 160, 3), line(360, 30, 470, 150, 3)], "3 s · mist + light rays"),
 ("3 · kids on the rock edge", lambda: [poly((0, 260), (230, 250), (300, 300), (300, 420)), wavy(300, 560, 360, 4)] +
     kid(110, 250) + kid(160, 248, 1, 'count') + kid(215, 252) + [line(150, 160, 175, 150, 2)], "3 s · \"3… 2… 1!\""),
 ("4 · long shot: the jumps", lambda: hills() + fall(420, 100, 260, 40) + [poly((0, 210), (150, 200), (190, 260), (190, 420)), wavy(190, 560, 300, 4)] +
     kid(160, 200, 0.8, 'jump') + [arc(250, 260, 80, math.pi * 1.25, math.pi * 1.85, 8)] + kid(290, 215, 0.8, 'jump') + splash(330, 300, 0.8) + splash(400, 305, 0.6), "4–5 s · one after another"),
 ("5 · a kid surfaces, laughing", lambda: [wavy(0, 560, 250, 5, 16)] + [ell(280, 228, 34, 36, 16), arc(280, 236, 16, math.pi * 0.15, math.pi * 0.85, 6),
     ell(268, 222, 3, 3, 6), ell(292, 222, 3, 3, 6)] + splash(200, 250) + splash(360, 250, 0.8) + [ell(250, 300, 70, 12, 14)], "2–3 s · splash beat"),
 ("6 · B-577 on a rock, waves", lambda: [wavy(0, 560, 300, 4), poly((330, 420), (360, 300), (470, 290), (520, 420))] + bot(420, 181, 0.24) +
     [ell(150, 296, 8, 9, 10)] + splash(185, 300, 0.6) + splash(240, 300, 0.5) + [arc(500, 150, 20, -0.6, 0.6, 5), arc(500, 150, 34, -0.6, 0.6, 5)], "2–3 s · cameo, end"),
]

S = [["create_node", {"type": "section", "name": "LVL 04 · sketchbook · same sketch, two worlds", "x": OX - 60, "y": OY - 140, "width": 3 * (PW + G) + 60, "height": 2 * (PH + G) + 200}, 400],
     ["create_node", {"type": "text", "x": OX, "y": OY - 110, "text": "one storyboard → 2D (EffectCraft, painterly) + 3D (Blender, realistic) · Indian village, golden hour · ≤ 20 s · 6 cuts",
                      "props": {"fontSize": 28, "fill": "#17110E"}}, 450]]
for k, (title, strokes, note) in enumerate(PANELS):
    ox, oy = OX + (k % 3) * (PW + G), OY + (k // 3) * (PH + G)
    S.append(["create_node", {"type": "frame", "name": f"panel {k + 1}", "x": ox, "y": oy, "width": PW, "height": PH, "props": {"fill": "#F4EBDF"}}, 300])
    S.append(["key", {"key": "2", "shift": True}, 450]); S.append(["select", {"ids": []}, 80])
    S.append(["pointer", {"tool": "pencil", "kind": "hover", "x": ox + 10, "y": oy + 10}, 50])
    for st in strokes():
        st = st if len(st) < 8 else st[::2] + [st[-1]]
        S += stroke([(ox + x, oy + y) for x, y in jit(st)])
    S.append(["create_node", {"type": "text", "x": ox + 16, "y": oy + 12, "text": title, "props": {"fontSize": 22, "fill": "#C25E00"}}, 450])
    S.append(["create_node", {"type": "text", "x": ox + PW - 230, "y": oy + PH - 40, "text": note, "width": 220, "props": {"fontSize": 20, "fill": "#0E8A96"}}, 450])
S.append(["select", {"ids": []}, 100]); S.append(["key", {"key": "1", "shift": True}, 1500])
S.append(["save_file", {"path": os.path.join(W, 'fig', 'lvl04_sketchbook.figcraft').replace(os.sep, '/')}, 300])
os.makedirs(os.path.join(W, 'steps'), exist_ok=True); os.makedirs(os.path.join(W, 'fig'), exist_ok=True)
json.dump(S, open(os.path.join(W, 'steps', 'sketchbook.json'), 'w'))
print(len(S), 'steps,', sum(1 for s in S if s[0] == 'pointer' and s[1].get('kind') == 'down'), 'strokes')
