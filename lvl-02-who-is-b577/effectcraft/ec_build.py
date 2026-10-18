# B-577 2D build in EffectCraft, live over MCP (effectcraft-cli mcp --bridge 9877): one run_script per body part so each
# step is visible in the window, then expressions (idle bob, blink, clock hands, wave, walk), a preview render and a save.
#   python sketch-free: python ec_build.py -> steps/ec_build.json
import json, os

W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, 'ec').replace(os.sep, '/')
os.makedirs(os.path.join(W, 'ec'), exist_ok=True)

PAL = dict(bg='#17110E', shell='#F4EBDF', glass='#CDEFF2', amber='#FFA448', line='#D9CBB8', ink='#5A4A3F', cyan='#46D9E6', pink='#FF5A8C')

LIB = """
var K=%s;
function col(h){return [parseInt(h.slice(1,3),16)/255,parseInt(h.slice(3,5),16)/255,parseInt(h.slice(5,7),16)/255];}
function comp(){var c=app.project.activeItem; if(!c||!(c instanceof CompItem)){for(var i=1;i<=app.project.numItems;i++){if(app.project.item(i).name=="B-577 rig")c=app.project.item(i);}} return c;}
function L(c,n){return c.layer(n);}
function T(l){return l.property("ADBE Transform Group");}
function grp(l){return l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group").property("ADBE Vectors Group");}
function paint(v,fill,stroke,sw){if(fill)v.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(col(fill));
  if(stroke){var s=v.addProperty("ADBE Vector Graphic - Stroke");s.property("ADBE Vector Stroke Color").setValue(col(stroke));s.property("ADBE Vector Stroke Width").setValue(sw||6);
  try{s.property("ADBE Vector Stroke Line Cap").setValue(2);s.property("ADBE Vector Stroke Line Join").setValue(2);}catch(e){}}}
function rect(l,w,h,r,x,y,fill,stroke,sw){var v=grp(l);var q=v.addProperty("ADBE Vector Shape - Rect");q.property("ADBE Vector Rect Size").setValue([w,h]);
  q.property("ADBE Vector Rect Roundness").setValue(r);q.property("ADBE Vector Rect Position").setValue([x||0,y||0]);paint(v,fill,stroke,sw);return v;}
function oval(l,w,h,x,y,fill,stroke,sw){var v=grp(l);var q=v.addProperty("ADBE Vector Shape - Ellipse");q.property("ADBE Vector Ellipse Size").setValue([w,h]);
  q.property("ADBE Vector Ellipse Position").setValue([x||0,y||0]);paint(v,fill,stroke,sw);return v;}
function path(l,pts,closed,fill,stroke,sw,ins,outs){var v=grp(l);var pg=v.addProperty("ADBE Vector Shape - Group");var sh=new Shape();sh.vertices=pts;sh.closed=closed;
  if(ins){sh.inTangents=ins;sh.outTangents=outs;}pg.property("ADBE Vector Shape").setValue(sh);paint(v,fill,stroke,sw);return v;}
function layer(c,name,x,y,parent){var l=c.layers.addShape();l.name=name;T(l).property("ADBE Anchor Point").setValue([0,0]);
  if(parent){l.parent=c.layer(parent);}T(l).property("ADBE Position").setValue([x,y]);return l;}
""" % json.dumps(PAL)

def js(code): return LIB + code

STEPS = []
def step(label, code, pause=1600):
    STEPS.append(["run_script", {"name": label, "code": js(code)}, pause])

step('comp', """
var c=app.project.items.addComp("B-577 rig",1080,1080,1,8,30); c.bgColor=col(K.bg); c.openInViewer(); "ok";
""", 1800)
step('body', """
var c=comp(); var b=layer(c,"body",540,640);
rect(b,210,190,56,0,0,K.shell,K.line,6);            // torso
rect(b,96,40,10,0,-22,K.amber);                       // tag plate
for(var i=0;i<5;i++) rect(b,22,12,6,-48+i*24,48,i<2?K.amber:K.line);   // level road: LVL 02 = 2 lit
var t=c.layers.addText("B-577"); t.name="tag text"; var d=t.property("ADBE Text Properties").property("ADBE Text Document").value;
d.font="JetBrainsMono-ExtraBold"; d.fontSize=24; d.fillColor=col(K.bg); d.justification=ParagraphJustification.CENTER_JUSTIFY; t.property("ADBE Text Properties").property("ADBE Text Document").setValue(d);
t.parent=b; T(t).property("ADBE Position").setValue([0,-14]); "ok";
""")
step('legs', """
var c=comp();
var ll=layer(c,"leg L",-48,88,"body"); rect(ll,34,96,17,0,48,K.shell,K.line,6); oval(ll,82,38,-10,104,K.shell,K.line,6);
var lr=layer(c,"leg R",48,88,"body");  rect(lr,34,96,17,0,48,K.shell,K.line,6); oval(lr,82,38,10,104,K.shell,K.line,6);
c.layer("leg L").moveAfter(c.layer("body")); c.layer("leg R").moveAfter(c.layer("body")); "ok";
""")
step('arms', """
var c=comp();
var al=layer(c,"arm L",-100,-56,"body"); rect(al,30,110,15,0,52,K.shell,K.line,6); oval(al,50,50,0,118,K.shell,K.line,6);
T(al).property("ADBE Rotate Z").setValue(28);
var ar=layer(c,"arm R",100,-56,"body"); rect(ar,30,110,15,0,52,K.shell,K.line,6); oval(ar,50,50,0,118,K.shell,K.line,6);
T(ar).property("ADBE Rotate Z").setValue(-150); "ok";
""")
step('head', """
var c=comp(); var h=layer(c,"head",0,-270,"body");
rect(h,400,330,70,0,0,K.shell,K.line,7);                              // TV bezel
path(h,[[-200,-70],[-262,-108],[-262,82],[-200,54]],true,K.shell,K.line,6);   // ear fin L
path(h,[[200,-70],[262,-108],[262,82],[200,54]],true,K.shell,K.line,6);       // ear fin R
path(h,[[-236,-50],[-236,40]],false,null,K.line,5); path(h,[[236,-50],[236,40]],false,null,K.line,5);
"ok";
""")
step('face', """
var c=comp(); var s=layer(c,"screen",0,0,"head"); rect(s,310,250,46,0,0,K.glass,K.line,5);
var e=layer(c,"eye",0,-18,"head"); rect(e,44,112,22,0,0,K.amber);
var m=layer(c,"mouth",0,72,"head"); path(m,[[-26,-6],[0,10],[26,-6]],false,null,K.ink,7,[[0,0],[-14,0],[0,0]],[[0,0],[14,0],[0,0]]);
c.layer("screen").moveAfter(c.layer("eye")); "ok";
""")
step('dial', """
var c=comp(); var d=layer(c,"dial",0,0,"head");
for(var i=0;i<12;i++){var a=-Math.PI/2+i*Math.PI/6, x=181*Math.cos(a), y=150*Math.sin(a);
  if(i<2) oval(d,20,20,x,y,K.amber); else path(d,[[x-7*Math.cos(a),y-7*Math.sin(a)],[x+7*Math.cos(a),y+7*Math.sin(a)]],false,null,K.line,5);}
var hh=layer(c,"hand hour",0,-172,"head"); path(hh,[[0,0],[0,-62]],false,null,K.ink,10);
var hm=layer(c,"hand minute",0,-172,"head"); path(hm,[[0,0],[0,-104]],false,null,K.amber,8);
T(hh).property("ADBE Rotate Z").setValue(-30); T(hm).property("ADBE Rotate Z").setValue(25);
var pv=layer(c,"pivot",0,-172,"head"); oval(pv,22,22,0,0,K.amber,K.ink,4); "ok";
""")
step('animate', """
var c=comp(); function ex(n,p,e){T(c.layer(n)).property(p).expression=e;}
ex("body","ADBE Position","[540, 640 + Math.sin(time*Math.PI*2*0.9)*10]");                       // idle bob
ex("head","ADBE Rotate Z","Math.sin(time*Math.PI*2*0.45)*3");                                      // gentle head sway
ex("eye","ADBE Scale","var t=time%%3; var k=(t>2.6&&t<2.78)?12:100; [100,k]");                     // blink every 3 s
ex("hand minute","ADBE Rotate Z","25 + time*90");                                                  // clock ticks round
ex("hand hour","ADBE Rotate Z","-30 + time*7.5");
ex("arm R","ADBE Rotate Z","-150 + Math.sin(time*Math.PI*2*1.6)*22");                              // wave
ex("arm L","ADBE Rotate Z","28 + Math.sin(time*Math.PI*2*0.9)*4");
"ok";
""".replace('%%', '%'), 1500)
STEPS.append(["render_frame", {"time": 1.0, "max_side": 720, "inline": False, "path": OUT + "/b577_v1_t1.png"}, 600])
STEPS.append(["render_frame", {"time": 2.7, "max_side": 720, "inline": False, "path": OUT + "/b577_v1_blink.png"}, 600])
STEPS.append(["ui_key", {"key": "Space"}, 6000])          # play it in the viewer
STEPS.append(["ui_key", {"key": "Space"}, 400])
STEPS.append(["save_project", {"path": OUT + "/b577_rig.ecproj"}, 600])
json.dump(STEPS, open(os.path.join(W, 'steps', 'ec_build.json'), 'w'))
print(len(STEPS), 'steps')

# ---- fix pass (after looking at the first render) ----
FIX = []
def fix(label, code, pause=1500):
    FIX.append(["run_script", {"name": label, "code": js(code)}, pause])
fix('fix: tag + level road on top of the torso', """
var c=comp(); var root=c.layer("body").property("ADBE Root Vectors Group"); root.property(1).moveTo(root.numProperties); "ok";
""")
fix('fix: lit ticks at 1 and 2 o\'clock', """
var c=comp(); c.layer("dial").remove(); var d=layer(c,"dial",0,0,"head");
for(var i=0;i<12;i++){var a=-Math.PI/2+i*Math.PI/6, x=181*Math.cos(a), y=150*Math.sin(a);
  if(i==1||i==2) oval(d,20,20,x,y,K.amber); else path(d,[[x-7*Math.cos(a),y-7*Math.sin(a)],[x+7*Math.cos(a),y+7*Math.sin(a)]],false,null,K.line,5);}
d.moveAfter(c.layer("hand hour")); "ok";
""")
fix('fix: calm clock hands + wave clear of the head', """
var c=comp(); function ex(n,p,e){T(c.layer(n)).property(p).expression=e;}
ex("hand minute","ADBE Rotate Z","25 + Math.sin(time*Math.PI*2*0.6)*14");
ex("hand hour","ADBE Rotate Z","-30 + Math.sin(time*Math.PI*2*0.6+1)*8");
ex("arm R","ADBE Rotate Z","-100 + Math.sin(time*Math.PI*2*1.6)*20"); "ok";
""")
FIX.append(["render_frame", {"time": 1.0, "max_side": 720, "inline": False, "path": OUT + "/b577_v1fix_t1.png"}, 600])
FIX.append(["ui_key", {"key": "Space"}, 7000]); FIX.append(["ui_key", {"key": "Space"}, 400])
FIX.append(["save_project", {"path": OUT + "/b577_rig.ecproj"}, 600])
TAKE = [["open_project", {"new": True}, 1200]] + [s for s in STEPS if s[0] not in ('ui_key', 'save_project')] + FIX
json.dump(TAKE, open(os.path.join(W, 'steps', 'ec_take.json'), 'w'))
print(len(TAKE), 'take steps')
