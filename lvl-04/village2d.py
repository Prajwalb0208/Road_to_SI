# LVL 04 2D (painterly) village scene for EffectCraft — 6 shot comps + a 20 s master with the painterly pass.
# Every shot is one JSX script (AE-style object model) so the same code runs headless (tests) and live over MCP (`run_script`).
#   python -I village2d.py --test   -> build headless project village2d.ecproj + check frames in check/
#   python -I village2d.py --steps  -> ..\steps\ec2d_take.json for mcp-drive.mjs (live, recorded)
import json, math, os, random, subprocess, sys

W = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(W))
CLI = r'C:/Program Files/EffectCraft/effectcraft-cli.exe'
FW, FH, FPS = 1920, 1080, 30
SHOTS = [('s1 village wide', 4.0), ('s2 waterfall', 3.0), ('s3 kids edge', 3.0), ('s4 the jumps', 4.5), ('s5 surface', 2.5), ('s6 cameo', 3.0)]
J = json.dumps

LIB = r'''
function col(h){return [parseInt(h.substr(1,2),16)/255,parseInt(h.substr(3,2),16)/255,parseInt(h.substr(5,2),16)/255];}
function T(l){return l.property("ADBE Transform Group");}
function shp(c,name,pts,hex,o){o=o||{};var l=c.layers.addShape();l.name=name;T(l).property("ADBE Position").setValue([0,0]);
 var v=l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group").property("ADBE Vectors Group");
 var pg=v.addProperty("ADBE Vector Shape - Group");var sh=new Shape();sh.vertices=pts;sh.closed=(o.open?false:true);
 if(o.smooth){var n=pts.length,it=[],ot=[];for(var i=0;i<n;i++){var a=pts[(i-1+n)%n],b=pts[(i+1)%n];var tx=(b[0]-a[0])*o.smooth,ty=(b[1]-a[1])*o.smooth;it.push([-tx,-ty]);ot.push([tx,ty]);}sh.inTangents=it;sh.outTangents=ot;}
 pg.property("ADBE Vector Shape").setValue(sh);
 if(!o.open){v.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(col(hex));}
 if(o.op!=null)T(l).property("ADBE Opacity").setValue(o.op);
 if(o.anchor){T(l).property("ADBE Anchor Point").setValue(o.anchor);T(l).property("ADBE Position").setValue(o.anchor);}
 if(o.parent)l.parent=o.parent;
 return l;}
function nul(c,name,pos){var n=c.layers.addNull();n.name=name;T(n).property("ADBE Anchor Point").setValue([0,0]);T(n).property("ADBE Position").setValue(pos);return n;}
function fx(l,id,vals){var e=l.property("ADBE Effect Parade").addProperty(id);for(var k in vals){try{e.property(k).setValue(vals[k]);}catch(x){}}return e;}
function solid(c,name,hex){return c.layers.addSolid(col(hex),name,c.width,c.height,1);}
function ex(l,path,e){var p=T(l).property(path);p.expression=e;return p;}
function keys(l,path,tv){var p=T(l).property(path);for(var i=0;i<tv.length;i++)p.setValueAtTime(tv[i][0],tv[i][1]);return p;}
function comp(n,d){for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it instanceof CompItem&&it.name==n){it.remove();break;}}return app.project.items.addComp(n,1920,1080,1,d,30);}
'''

def ell(cx, cy, rx, ry, n=20): return [[round(cx + rx * math.cos(2 * math.pi * i / n), 1), round(cy + ry * math.sin(2 * math.pi * i / n), 1)] for i in range(n)]
def ridge(y0, amp, seed, base=FH + 20, step=60, x0=-40, x1=FW + 40):
    r = random.Random(seed); pts = [[x0, base]]; x = x0
    while x <= x1:
        pts.append([x, round(y0 + amp * (0.55 * math.sin(x / 260 + seed) + 0.45 * r.uniform(-1, 1)), 1)]); x += step
    pts.append([x1, base]); return pts
def rect(x, y, w, h): return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
def R(pts): return J([[round(a, 1), round(b, 1)] for a, b in pts])

# ---------------- reusable painted pieces (JSX lines) ----------------
def sky(sun=(1480, 330), r=75):
    return ['var bg=solid(c,"sky","#E9875B");fx(bg,"ec.generate.gradientramp",{"Start of Ramp":[960,0],"Start Color":col("#D9704E"),"End of Ramp":[960,620],"End Color":col("#FFD98A")});',
            f'var sun=shp(c,"sun",{J(ell(*sun, r, r))},"#FFE9B0");fx(sun,"ec.stylize.glow",{{"Glow Radius":90,"Glow Intensity":0.8}});']
def warm(src=(1480, 330), op=55):
    return [f'var warm=solid(c,"golden light","#FFB55A");fx(warm,"ec.generate.gradientramp",{{"Start of Ramp":{J(list(src))},"Start Color":col("#FFC46B"),"End of Ramp":[200,1080],"End Color":col("#5A2E1A")}});warm.blendingMode=BlendingMode.SOFT_LIGHT;T(warm).property("ADBE Opacity").setValue({op});']
def falling(name, x0, x1, y0, y1, speed=700, n=9, hexes=('#F4F1E6', '#D8ECEA', '#FFFFFF')):
    """waterfall = vertical paint streaks scrolling down inside the fall (looping)"""
    L = [f'shp(c,"{name} body",{J(rect(x0, y0, x1 - x0, y1 - y0))},"#CFE4E0");']
    h = y1 - y0; w = (x1 - x0) / n
    for k in range(n):
        sx = x0 + k * w + random.uniform(0, w * 0.3); sw = w * random.uniform(0.35, 0.7); seg = random.uniform(0.2, 0.45) * h
        c_ = random.choice(hexes); ph = random.uniform(0, h)
        L.append(f'var st=shp(c,"{name} streak {k}",{R(rect(sx, y0, sw, seg))},"{c_}",{{"op":{random.randint(60, 95)}}});'
                 f'ex(st,"ADBE Position","[0, ((time*{speed}+{round(ph, 1)})%{round(h - seg, 1)})]");')
    return L
def mist(name, cx, cy, rx, ry, blur=40, op=80):
    return [f'var mi=shp(c,"{name}",{J(ell(cx, cy, rx, ry))},"#FFF8EA",{{"op":{op},"anchor":[{cx},{cy}]}});fx(mi,"ec.blur.gaussian",{{"Blurriness":{blur}}});'
            f'ex(mi,"ADBE Scale","var s=100+6*Math.sin(time*3.1);[s,s]");']
def water(y0, y1, glints=7, top='#E7B66E', bot='#3F7F86'):
    L = [f'var pool=shp(c,"pool",{J([[-40, y0], [1960, y0 - 20], [1960, y1 + 40], [-40, y1 + 40]])},"#5E9C9A");fx(pool,"ec.generate.gradientramp",{{"Start of Ramp":[960,{y0}],"Start Color":col("{top}"),"End of Ramp":[960,{y1}],"End Color":col("{bot}")}});']
    for i in range(glints):
        y = y0 + 18 + i * (y1 - y0 - 30) / glints
        L.append(f'var g=shp(c,"glint {i}",{R([[300 + i * 90, y], [900 + i * 60, y - 3], [900 + i * 60, y + 3], [300 + i * 90, y + 6]])},"#FFE6A8",{{"op":{55 - i * 6}}});'
                 f'ex(g,"ADBE Position","[40*Math.sin(time*1.3+{i}),0]");')
    return L
def house(k, x, y, w):
    return [f'shp(c,"wall {k}",{J(rect(x, y, w, 120))},"#EBDCC0");',
            f'shp(c,"door {k}",{R([[x + w * .45, y + 120], [x + w * .45, y + 55], [x + w * .62, y + 55], [x + w * .62, y + 120]])},"#5A3A2A");',
            f'shp(c,"roof {k}",{R([[x - 30, y + 8], [x + w * .25, y - 70], [x + w * .75, y - 70], [x + w + 30, y + 8]])},"#B5532E");',
            f'shp(c,"roof shade {k}",{R([[x - 30, y + 8], [x + w + 30, y + 8], [x + w + 24, y + 20], [x - 24, y + 20]])},"#7A3420");']
def palm(k, x, base, h, lean, s=1.0):
    top = (x + lean, base - h)
    L = [f'shp(c,"palm trunk {k}",{R([[x - 10*s, base], [x + lean * .4 - 7*s, base - h * .5], [top[0] - 4*s, top[1]], [top[0] + 4*s, top[1]], [x + lean * .4 + 7*s, base - h * .5], [x + 12*s, base]])},"#6B4A2E",{{"smooth":0.1}});',
         f'var crown{k}=nul(c,"palm crown {k}",{J(list(top))});ex(crown{k},"ADBE Rotate Z","3*Math.sin(time*1.7+{k})");']
    for j, (dx, up) in enumerate([(-1, .2), (-.7, -.5), (.7, -.5), (1, .2), (-.2, -.9), (.3, .6)]):
        Rr = 190 * s
        fr = [[0, 0]] + [[dx * Rr * t, Rr * (up * t + .9 * t * t) - 14 * s * (1 - t)] for t in (.35, .7, 1.)] + [[dx * Rr * t, Rr * (up * t + .9 * t * t) + 14 * s * (1 - t)] for t in (.7, .35)]
        # fronds drawn in crown-local coords (crown null sits at the palm top)
        L.append(f'var f=shp(c,"frond {k}.{j}",{R(fr)},"#3E5A2C",{{"smooth":0.15}});f.parent=crown{k};T(f).property("ADBE Position").setValue([0,0]);')
    return L
SKIN, SKIN2 = '#8A5A3C', '#6E452D'
def kid(k, cx, feet, s=1.0, tee='#E04F3A', shorts='#2F4A7A', pose='stand'):
    """painted kid (no face detail): null 'kid k' at the feet; body parts in null-local coords, parented to it"""
    L = [f'var K{k}=nul(c,"kid {k}",[{cx},{feet}]);']
    p = lambda pts: R([[a * s, b * s] for a, b in pts])
    def part(name, pts, hexc, extra=''):
        return f'var q=shp(c,"kid {k} {name}",{p(pts)},"{hexc}");q.parent=K{k};T(q).property("ADBE Position").setValue([0,0]);{extra}'
    L += [part('leg L', [[-14, -70], [-4, -70], [-6, 0], [-18, 0]], SKIN2), part('leg R', [[4, -70], [14, -70], [18, 0], [6, 0]], SKIN2),
          part('shorts', [[-18, -96], [18, -96], [20, -62], [-20, -62]], shorts), part('tee', [[-20, -150], [20, -150], [22, -94], [-22, -94]], tee)]
    up = pose in ('jump', 'cheer')
    for side, sx in (('L', -1), ('R', 1)):
        arm = [[sx * 16, -146], [sx * 26, -146], [sx * 34, -100], [sx * 24, -98]] if not up else [[sx * 14, -146], [sx * 24, -148], [sx * 40, -200], [sx * 30, -204]]
        L.append(part(f'arm {side}', arm, SKIN, f'T(q).property("ADBE Anchor Point").setValue([{sx * 20 * s},{-146 * s}]);T(q).property("ADBE Position").setValue([{sx * 20 * s},{-146 * s}]);'))
    L += [part('head', ell(0, -172, 20, 22, 16), SKIN), part('hair', [[-21, -176], [-18, -192], [0, -197], [18, -192], [21, -176], [10, -184], [-10, -184]], '#1E1612')]
    return L
def splash(name, cx, y, t0, s=1.0):
    L = []
    for j, (dx, h) in enumerate([(-34, 60), (-14, 95), (8, 110), (28, 80), (44, 50)]):
        L.append(f'var sp=shp(c,"{name} {j}",{R([[cx + dx * s - 7 * s, y], [cx + dx * s, y - h * s], [cx + dx * s + 7 * s, y]])},"#F4FBF8",{{"anchor":[{round(cx + dx * s, 1)},{y}]}});'
                 f'keys(sp,"ADBE Scale",[[0,[0,0]],[{t0},[0,0]],[{t0 + .12},[110,110]],[{t0 + .5},[60,20]],[{t0 + .7},[0,0]]]);')
    L.append(f'var ring=shp(c,"{name} ring",{R(ell(cx, y + 4 * s, 50 * s, 10 * s))},"#F4FBF8",{{"op":70,"anchor":[{cx},{y}]}});'
             f'keys(ring,"ADBE Scale",[[0,[0,0]],[{t0},[0,0]],[{t0 + .7},[180,140]]]);keys(ring,"ADBE Opacity",[[{t0},80],[{t0 + .7},0]]);')
    return L
def b577(cx, feet, s=0.5):
    """B-577 v4 in paint; NEW wave (hand out to the side, clear of the head)"""
    q = lambda pts: R([[cx + a * s, feet + b * s] for a, b in pts])
    L = ['var B=nul(c,"B-577",[0,0]);ex(B,"ADBE Position","[0,4*Math.sin(time*4)]");']
    def part(n, pts, h, extra=''): return f'var q=shp(c,"b577 {n}",{q(pts)},"{h}");q.parent=B;{extra}'
    L += [part('foot L', ell(-45, -10, 34, 14), '#FFA448'), part('foot R', ell(45, -10, 34, 14), '#FFA448'),
          part('leg L', [[-55, -110], [-35, -110], [-35, -20], [-55, -20]], '#FFF3E0'), part('leg R', [[35, -110], [55, -110], [55, -20], [35, -20]], '#FFF3E0'),
          part('torso', [[-100, -290], [100, -290], [100, -100], [-100, -100]], '#FFF3E0'),
          part('tag', [[-50, -250], [50, -250], [50, -215], [-50, -215]], '#FFA448'),
          part('arm L', [[-110, -270], [-90, -262], [-140, -160], [-160, -170]], '#FFF3E0'), part('hand L', ell(-150, -160, 22, 22), '#FFA448')]
    ax, ay = round(cx + 105 * s, 1), round(feet - 268 * s, 1)
    L.append(f'var WA=nul(c,"b577 wave pivot",[{ax},{ay}]);WA.parent=B;ex(WA,"ADBE Rotate Z","14*Math.sin(time*2*Math.PI*1.6)");')
    wa = R([[cx + a * s - ax, feet + b * s - ay] for a, b in [[100, -275], [112, -258], [245, -300], [235, -318]]])
    wh = R([[cx + a * s - ax, feet + b * s - ay] for a, b in ell(250, -312, 26, 26)])
    L.append(f'var q=shp(c,"b577 wave arm",{wa},"#FFF3E0");q.parent=WA;T(q).property("ADBE Position").setValue([0,0]);var q=shp(c,"b577 wave hand",{wh},"#FFA448");q.parent=WA;T(q).property("ADBE Position").setValue([0,0]);')
    L += [part('fin L', [[-200, -470], [-245, -500], [-245, -360], [-200, -390]], '#FFA448'), part('fin R', [[200, -470], [245, -500], [245, -360], [200, -390]], '#FFA448'),
          part('head', [[-200, -610], [200, -610], [200, -300], [-200, -300]], '#FFF3E0'), part('screen', [[-160, -575], [160, -575], [160, -335], [-160, -335]], '#120F0D'),
          part('eye L', ell(-62, -475, 34, 46), '#46D9E6'), part('eye R', ell(62, -475, 34, 46), '#46D9E6'),
          part('smile', [[-40, -395], [0, -375], [40, -395], [0, -385]], '#46D9E6'), part('antenna', [[0, -610], [8, -610], [52, -700], [44, -704]], '#FFA448')]
    return L

# ---------------- shots ----------------
def s1():
    random.seed(11); L = sky()
    L += [f'shp(c,"hills far",{J(ridge(430, 60, 1, step=80))},"#C98C6B",{{"smooth":0.18}});', f'shp(c,"hills mid",{J(ridge(520, 70, 2, step=70))},"#9C7B52",{{"smooth":0.18}});',
          f'shp(c,"cliff",{J([[700,540],[760,470],[900,455],[960,470],[1010,560],[1010,760],[700,760]])},"#6E5A3A",{{"smooth":0.12}});']
    L += falling('falls', 838, 904, 466, 700, speed=380, n=6) + mist('falls mist', 870, 700, 110, 30, 30, 70)
    L += [f'shp(c,"hills near",{J(ridge(640, 50, 3, step=60))},"#5E7A3E",{{"smooth":0.18}});'] + water(800, 930)
    for k, (x, y, w) in enumerate([(120, 600, 230), (390, 615, 180), (1240, 605, 210)]): L += house(k, x, y, w)
    L += palm(0, 640, 790, 380, 40) + palm(1, 1640, 790, 470, -60) + palm(2, 1840, 790, 340, -30)
    return L + [f'shp(c,"grass",{J(ridge(985, 18, 9, step=40))},"#2F4425",{{"smooth":0.2}});'] + warm()
def s2():
    random.seed(22); L = sky((1650, 220), 60)
    L += falling('falls', 600, 1330, -20, 1000, speed=820, n=16)
    L += [f'shp(c,"rock L",{J([[-40,-40],[560,-40],[640,300],[600,1120],[-40,1120]])},"#5C4A33",{{"smooth":0.08}});',
          f'shp(c,"rock R",{J([[1380,-40],[1960,-40],[1960,1120],[1330,1120],[1300,320]])},"#544430",{{"smooth":0.08}});',
          f'shp(c,"moss L",{J([[-40,200],[420,160],[560,260],[520,420],[-40,520]])},"#4F6B35",{{"smooth":0.15}});']
    L += mist('mist a', 960, 990, 560, 120, 50, 85) + mist('mist b', 700, 1010, 300, 80, 40, 70)
    for i, (x0, op) in enumerate([(1050, 26), (1250, 20)]):
        L.append(f'var ray=shp(c,"light ray {i}",{J([[x0,-60],[x0 + 140,-60],[x0 - 260,1140],[x0 - 420,1140]])},"#FFE3A0",{{"op":{op}}});fx(ray,"ec.blur.gaussian",{{"Blurriness":60}});'
                 f'ex(ray,"ADBE Opacity","{op}+8*Math.sin(time*1.2+{i})");')
    return L + warm((1650, 220), 45)
def s3():
    random.seed(33); L = sky((1500, 380), 65)
    L += [f'shp(c,"hills",{J(ridge(560, 40, 4, step=70))},"#9C7B52",{{"smooth":0.18}});'] + water(700, 1080, 6)
    L += [f'shp(c,"rock",{J([[-40,640],[900,610],[1080,700],[1180,1120],[-40,1120]])},"#6E5A3A",{{"smooth":0.1}});',
          f'shp(c,"rock top",{J([[-40,640],[900,610],[1060,690],[880,680],[-40,690]])},"#8A7350",{{"smooth":0.1}});']
    L += kid(0, 420, 660, 1.6, '#E04F3A', '#2F4A7A') + kid(1, 640, 655, 1.7, '#F2C14E', '#3B6B3A') + kid(2, 860, 650, 1.5, '#4FA3D9', '#5A3A2A')
    L.append('var a=T(c.layer("kid 1 arm R")).property("ADBE Rotate Z");' + ''.join(f'a.setValueAtTime({t},{v});' for t, v in [(0, 0), (0.3, -150), (0.7, -150), (0.9, -60), (1.2, -150), (1.6, -150), (1.8, -60), (2.1, -160), (3.0, -160)]))
    L.append('ex(c.layer("kid 0"),"ADBE Position","value+[0,-6*Math.abs(Math.sin(time*5))]");ex(c.layer("kid 2"),"ADBE Position","value+[0,-5*Math.abs(Math.sin(time*5+1))]");')
    return L + warm((1500, 380), 50)
def s4():
    random.seed(44); L = sky((1550, 300), 55)
    L += [f'shp(c,"hills far",{J(ridge(380, 50, 5, step=80))},"#C98C6B",{{"smooth":0.18}});', f'shp(c,"hills mid",{J(ridge(470, 60, 6, step=70))},"#9C7B52",{{"smooth":0.18}});',
          f'shp(c,"cliff back",{J([[1180,470],[1260,400],[1420,390],[1500,460],[1500,700],[1180,700]])},"#6E5A3A",{{"smooth":0.1}});']
    L += falling('falls', 1290, 1380, 400, 690, speed=420, n=6) + mist('falls mist', 1335, 690, 140, 30, 30, 70) + water(690, 1080, 6)
    L += [f'shp(c,"jump rock",{J([[-40,520],[430,500],[520,560],[560,1120],[-40,1120]])},"#6E5A3A",{{"smooth":0.1}});',
          f'shp(c,"jump rock top",{J([[-40,520],[430,500],[505,550],[380,560],[-40,560]])},"#8A7350",{{"smooth":0.1}});']
    for k, tee, sh, t0 in [(0, '#E04F3A', '#2F4A7A', 0.3), (1, '#F2C14E', '#3B6B3A', 1.3), (2, '#4FA3D9', '#5A3A2A', 2.3)]:
        x0 = 300 + k * 40; land = 820 + k * 140
        L += kid(k, x0, 510, 0.75, tee, sh, 'jump')
        L.append(f'T(c.layer("kid {k}")).property("ADBE Position").expression="var t0={t0};if(time<t0){{value}}else{{var u=Math.min((time-t0)/1.0,1);[{x0}+({land}-{x0})*u, 510-300*u+({835 - 510}+300)*u*u]}}";'
                 f'ex(c.layer("kid {k}"),"ADBE Rotate Z","time<{t0}?0:Math.min((time-{t0})*120,90)");')
        for part in ('leg L', 'leg R', 'shorts', 'tee', 'arm L', 'arm R', 'head', 'hair'):
            L.append(f'ex(c.layer("kid {k} {part}"),"ADBE Opacity","time<{t0 + 0.95}?100:0");')
        L += splash(f'splash {k}', land, 835, t0 + 0.95, 1.0)
    return L + warm((1550, 300), 50)
def s5():
    random.seed(55); L = sky((1450, 260), 60)
    L += [f'shp(c,"hills",{J(ridge(430, 40, 7, step=70))},"#5E7A3E",{{"smooth":0.18}});'] + water(480, 1080, 7, '#E9B870', '#2F6E78')
    L += kid(0, 960, 1500, 3.2, '#E04F3A', '#2F4A7A', 'cheer')
    L.append('keys(c.layer("kid 0"),"ADBE Position",[[0,[960,1500]],[0.6,[960,1030]],[0.9,[960,1060]]]);')
    L.append(f'var sm=shp(c,"kid 0 smile",{R([[-30, -547], [0, -527], [30, -547], [0, -537]])},"#3A2418");sm.parent=c.layer("kid 0");T(sm).property("ADBE Position").setValue([0,0]);')
    L.append(f'var wl=shp(c,"waterline",{J([[-40,760],[1960,760],[1960,1120],[-40,1120]])},"#3F7F86",{{"op":88}});ex(wl,"ADBE Position","[0,6*Math.sin(time*4)]");')
    return L + splash('surface splash a', 860, 770, 0.45, 2.2) + splash('surface splash b', 1080, 775, 0.55, 1.8) + warm((1450, 260), 45)
def s6():
    random.seed(66); L = sky((1450, 300), 60)
    L += [f'shp(c,"hills",{J(ridge(480, 50, 8, step=70))},"#9C7B52",{{"smooth":0.18}});'] + water(620, 1080, 6)
    L += [f'shp(c,"cameo rock",{J([[1180,1120],[1240,760],[1420,720],[1620,760],[1700,1120]])},"#6E5A3A",{{"smooth":0.1}});',
          f'shp(c,"cameo rock top",{J([[1240,770],[1420,725],[1610,768],[1420,780]])},"#8A7350",{{"smooth":0.1}});']
    L += b577(1430, 760, 0.42)
    for k, x in enumerate([380, 620, 840]):
        L.append(f'var h{k}=shp(c,"swimmer {k}",{J(ell(x, 690, 34, 36))},"{SKIN}",{{"anchor":[{x},690]}});ex(h{k},"ADBE Position","value+[0,6*Math.sin(time*3+{k})]");'
                 f'var hh=shp(c,"swimmer {k} hair",{R([[x - 35, 684], [x - 30, 660], [x, 652], [x + 30, 660], [x + 35, 684], [x + 16, 670], [x - 16, 670]])},"#1E1612");hh.parent=h{k};T(hh).property("ADBE Position").setValue([0,0]);'
                 f'var rr=shp(c,"swimmer {k} ripple",{R(ell(x, 722, 60, 10))},"#F4FBF8",{{"op":60,"anchor":[{x},722]}});ex(rr,"ADBE Scale","var s=100+15*Math.sin(time*3+{k});[s,s]");')
        L += splash(f'swim splash {k}', x + 30, 712, 0.4 + k * 0.6, 0.6)
    return L + warm((1450, 300), 50)
BUILD = [s1, s2, s3, s4, s5, s6]

def shot_script(i):
    name, d = SHOTS[i]
    return LIB + f'\nvar c=comp({J(name)},{d});\n' + '\n'.join(BUILD[i]()) + f'\n"{name}: "+c.numLayers+" layers"'
def master_script():
    total = sum(d for _, d in SHOTS); acc, t = [], 0.0
    for _, d in SHOTS: acc.append(t); t += d
    js = LIB + f'\nvar m=comp("village 2D",{total});\n'
    for i in range(len(SHOTS) - 1, -1, -1):
        js += (f'var src=null;for(var j=1;j<=app.project.numItems;j++){{var it=app.project.item(j);if(it instanceof CompItem&&it.name=={J(SHOTS[i][0])})src=it;}}'
               f'var l=m.layers.add(src);l.startTime={acc[i]};l.inPoint={acc[i]};l.outPoint={acc[i] + SHOTS[i][1]};\n')
    js += 'ex(m.layer("s1 village wide"),"ADBE Scale","var u=(time)/4;[100+6*u,100+6*u]");\n'
    js += ('var adj=m.layers.addSolid([1,1,1],"painterly",1920,1080,1);adj.adjustmentLayer=true;'
           'var td=fx(adj,"ec.distort.turbulentdisplace",{"Amount":6,"Size":14});try{td.property("Evolution").expression="Math.floor(time*8)*40";}catch(x){}'
           'fx(adj,"ec.stylize.brushstrokes",{"Stroke Angle":120,"Brush Size":4,"Stroke Length":10,"Stroke Density":1.6,"Stroke Randomness":1.6});'
           'var tex=solid(m,"canvas texture","#808080");fx(tex,"ec.noise.fractal",{"Contrast":60,"Scale":180});tex.blendingMode=BlendingMode.OVERLAY;T(tex).property("ADBE Opacity").setValue(18);\n')
    return js + '"village 2D: "+m.numLayers+" layers, "+m.duration+" s"'

if __name__ == '__main__':
    os.makedirs(os.path.join(W, 'jsx'), exist_ok=True); os.makedirs(os.path.join(W, 'check'), exist_ok=True)
    scripts = [(SHOTS[i][0], shot_script(i)) for i in range(6)] + [('village 2D', master_script())]
    for n, js in scripts: open(os.path.join(W, 'jsx', n.replace(' ', '_') + '.jsx'), 'w', encoding='utf-8').write(js)
    if '--test' in sys.argv:
        ef = os.path.join(W, 'village2d.ecproj'); first = True
        for n, js in scripts:
            jf = os.path.join(W, 'jsx', n.replace(' ', '_') + '.jsx')
            a = [CLI, 'script', jf] + (['--empty', '--save-as', ef] if first else ['--project', ef, '--save']); first = False
            r = subprocess.run(a, capture_output=True, text=True); print((r.stdout.strip().splitlines() or [''])[0][:120], r.stderr.strip()[-300:])
        for t in (0.5, 2.0, 3.6, 5.5, 8.5, 10.6, 12.4, 15.4, 17.5, 18.6):
            subprocess.run([CLI, 'render-frame', '--project', ef, '--comp', 'village 2D', '--time', str(t), '--max-side', '640', '--out', os.path.join(W, 'check', f'v_{t:05.2f}.png')], capture_output=True)
        print('checks rendered')
    if '--steps' in sys.argv:
        out = os.path.join(PROJ, 'work', 'steps', 'ec2d_take.json'); live = os.path.join(W, 'village2d_live.ecproj').replace(os.sep, '/')
        S = [["open_project", {"new": True}, 1500]] + [["run_script", {"name": n, "code": js}, 1500] for n, js in scripts] + [["run_script", {"name": "show", "code": 'for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it instanceof CompItem&&it.name=="village 2D"){try{it.openInViewer();}catch(x){}}}"ok"'}, 1500], ["ui_key", {"key": "space"}, 21000], ["ui_key", {"key": "space"}, 800], ["save_project", {"path": live}, 800]]
        json.dump(S, open(out, 'w')); print('steps', len(S), '->', out)
