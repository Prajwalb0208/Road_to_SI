# B-577 v4 character builder (role-based palette, two amber-iris eyes, no lids) + a palette study:
# 4 bright light palettes, one comp each, built live in EffectCraft over MCP, rendered side by side, saved.
#   python ec_char.py -> steps/ec_palette.json
import json, os
from ec_build import LIB, OUT

PALETTES = {   # roles: shell (head bezel), torso, screen, fin, limb (arms/legs), hand (hands/feet), accent (iris/tag/lit ticks), ink, line
 'P1 sunny':     dict(shell='#FFF8EC', torso='#FFF8EC', screen='#7FE3F0', fin='#FF8A5B', limb='#FFF8EC', hand='#FF8A5B', accent='#FFA448', ink='#4A3628', line='#E8D5BF'),
 'P2 mint pop':  dict(shell='#FFFFFF', torso='#FFE3C2', screen='#A8F0DC', fin='#FFB547', limb='#FFFFFF', hand='#FFB547', accent='#FF9F2E', ink='#3F3A36', line='#DCCFC0'),
 'P3 brand pop': dict(shell='#FFF3E0', torso='#FFF3E0', screen='#5FE0EA', fin='#FF5A8C', limb='#FFF3E0', hand='#FFA448', accent='#FFA448', ink='#3E2A20', line='#E6CFB6'),
 'P4 sky + tangerine': dict(shell='#FAFCFF', torso='#FF9F43', screen='#9AD8FF', fin='#9AD8FF', limb='#FAFCFF', hand='#FF9F43', accent='#FF8A1F', ink='#33333D', line='#D6DEE8'),
}

CHAR = r"""
function arcPts(cx,cy,rx,ry,a0,a1,n){var p=[];for(var i=0;i<=n;i++){var a=a0+(a1-a0)*i/n;p.push([cx+rx*Math.cos(a),cy+ry*Math.sin(a)]);}return p;}
function buildB577(c,P){
  var b=layer(c,"body",540,640);
  rect(b,96,40,10,0,-22,P.accent); for(var i=0;i<5;i++) rect(b,22,12,6,-48+i*24,48,i<2?P.accent:P.line);
  rect(b,210,190,56,0,0,P.torso,P.line,6);
  var t=c.layers.addText("B-577"); t.name="tag text"; var d=t.property("ADBE Text Properties").property("ADBE Text Document").value;
  d.font="JetBrainsMono-ExtraBold"; d.fontSize=24; d.fillColor=col(P.ink); d.justification=ParagraphJustification.CENTER_JUSTIFY;
  t.property("ADBE Text Properties").property("ADBE Text Document").setValue(d); t.parent=b; T(t).property("ADBE Position").setValue([0,-14]);
  var ll=layer(c,"leg L",-48,88,"body"); oval(ll,82,38,-10,104,P.hand,P.line,6); rect(ll,34,96,17,0,48,P.limb,P.line,6);
  var lr=layer(c,"leg R",48,88,"body");  oval(lr,82,38,10,104,P.hand,P.line,6);  rect(lr,34,96,17,0,48,P.limb,P.line,6);
  ll.moveAfter(b); lr.moveAfter(b);
  var al=layer(c,"arm L",-100,-56,"body"); oval(al,52,52,0,118,P.hand,P.line,6); rect(al,30,110,15,0,52,P.limb,P.line,6); T(al).property("ADBE Rotate Z").setValue(28);
  var ar=layer(c,"arm R",100,-56,"body");  oval(ar,52,52,0,118,P.hand,P.line,6); rect(ar,30,110,15,0,52,P.limb,P.line,6); T(ar).property("ADBE Rotate Z").setValue(-100);
  var h=layer(c,"head",0,-270,"body");
  path(h,[[-236,-50],[-236,40]],false,null,P.line,5); path(h,[[236,-50],[236,40]],false,null,P.line,5);
  path(h,[[-200,-70],[-262,-108],[-262,82],[-200,54]],true,P.fin,P.line,6); path(h,[[200,-70],[262,-108],[262,82],[200,54]],true,P.fin,P.line,6);
  rect(h,400,330,70,0,0,P.shell,P.line,7);
  var s=layer(c,"screen",0,0,"head"); rect(s,310,250,46,0,0,P.screen,P.line,5);
  var dl=layer(c,"dial",0,0,"head");
  for(var i=0;i<12;i++){var a=-Math.PI/2+i*Math.PI/6, x=181*Math.cos(a), y=150*Math.sin(a);
    if(i==1||i==2) oval(dl,20,20,x,y,P.accent); else path(dl,[[x-7*Math.cos(a),y-7*Math.sin(a)],[x+7*Math.cos(a),y+7*Math.sin(a)]],false,null,P.line,5);}
  var sides=[["L",-64],["R",64]];
  for(var k=0;k<2;k++){var sd=sides[k][0], ex=sides[k][1];
    var FI=P.faceInk||P.ink, mode=P.eyeMode||"white";
    var e=layer(c,"eye "+sd,ex,-20,"head");
    if(mode=="white"){ oval(e,84,116,0,0,"#FFFFFF",P.ink,5);
      var ir=layer(c,"iris "+sd,0,6,"eye "+sd); oval(ir,11,11,9,-9,"#FFFFFF"); oval(ir,6,6,-7,8,"#FFFFFF"); oval(ir,20,22,0,0,P.ink); oval(ir,44,48,0,0,P.accent); }
    else { // glowing LED eye on the dark screen: core + soft halo
      var ir=layer(c,"iris "+sd,0,0,"eye "+sd); oval(ir,14,14,10,-16,"#FFFFFF"); oval(ir,8,8,-8,-4,"#FFFFFF"); oval(ir,60,92,0,0,P.glow);
      oval(e,84,116,0,0,P.glow); T(e).property("ADBE Opacity").setValue(35); }
    var bw=layer(c,"brow "+sd,ex,-104,"head"); path(bw,sd=="L"?[[-28,6],[0,-6],[28,4]]:[[-28,4],[0,-6],[28,6]],false,null,FI,8);}
  var m=layer(c,"mouth",0,76,"head"); path(m,arcPts(0,-22,40,24,Math.PI*0.15,Math.PI*0.85,14),false,null,P.faceInk||P.ink,7);
  if(P.scan){ var sc=layer(c,"scanlines",0,0,"head"); for(var y=-118;y<120;y+=8) rect(sc,300,2,0,0,y,"#FFFFFF"); T(sc).property("ADBE Opacity").setValue(6); }
  if(P.cursor){ var cu=layer(c,"cursor",112,92,"head"); rect(cu,16,26,2,0,0,P.glow); T(cu).property("ADBE Opacity").expression="(Math.floor(time*2)%2)?0:100"; }
  var hh=layer(c,"hand hour",0,-172,"head"); path(hh,[[0,0],[0,-62]],false,null,P.ink,10); T(hh).property("ADBE Rotate Z").setValue(-30);
  var hm=layer(c,"hand minute",0,-172,"head"); path(hm,[[0,0],[0,-104]],false,null,P.accent,8); T(hm).property("ADBE Rotate Z").setValue(25);
  var pv=layer(c,"pivot",0,-172,"head"); oval(pv,22,22,0,0,P.accent,P.ink,4);
  function exn(n,p,e){T(c.layer(n)).property(p).expression=e;}
  exn("body","ADBE Position","[540, 640 + Math.sin(time*Math.PI*2*0.9)*10]");
  exn("head","ADBE Rotate Z","Math.sin(time*Math.PI*2*0.45)*3");
  var blink="var t=time%3.2; var k=(t>2.9&&t<3.05)?8:100; [100,k]"; exn("eye L","ADBE Scale",blink); exn("eye R","ADBE Scale",blink);
  var look="var t=time%4; var x=(t<1.5)?0:(t<2.6)?9:-7; [x, 6+((t>2.6)?-4:0)]"; exn("iris L","ADBE Position",look); exn("iris R","ADBE Position",look);
  exn("hand minute","ADBE Rotate Z","25 + Math.sin(time*Math.PI*2*0.6)*14"); exn("hand hour","ADBE Rotate Z","-30 + Math.sin(time*Math.PI*2*0.6+1)*8");
  exn("arm R","ADBE Rotate Z","-100 + Math.sin(time*Math.PI*2*1.6)*20"); exn("arm L","ADBE Rotate Z","28 + Math.sin(time*Math.PI*2*0.9)*4");
}
"""

FACES = {
 'F1 dark + white eyes': dict(PALETTES['P3 brand pop'], screen='#17110E', faceInk='#FFA448', eyeMode='white', scan=True),
 'F2 dark + cyan LED':   dict(PALETTES['P3 brand pop'], screen='#120F0D', faceInk='#46D9E6', eyeMode='glow', glow='#46D9E6', scan=True),
 'F3 dark + amber LED':  dict(PALETTES['P3 brand pop'], screen='#17110E', faceInk='#FFA448', eyeMode='glow', glow='#FFA448', scan=True, cursor=True),
}

def faces_steps():
    S = []
    for name, P in FACES.items():
        S.append(["run_script", {"name": f"face {name}", "code": LIB + CHAR + f"""
var c=app.project.items.addComp("{name}",1080,1080,1,8,30); c.bgColor=col(K.bg); c.openInViewer(); buildB577(c,{json.dumps(P)}); "ok";"""}, 1800])
        S.append(["render_frame", {"comp": name, "time": 0.5, "max_side": 540, "inline": False, "path": OUT + f"/face_{name.split()[0]}.png"}, 400])
    S.append(["save_project", {}, 500])
    json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps', 'ec_faces.json'), 'w'))

if __name__ == '__main__':
    faces_steps()
    S = []
    for name, P in PALETTES.items():
        S.append(["run_script", {"name": f"palette {name}", "code": LIB + CHAR + f"""
var c=app.project.items.addComp("{name}",1080,1080,1,8,30); c.bgColor=col(K.bg); c.openInViewer(); buildB577(c,{json.dumps(P)}); "ok";"""}, 1800])
        S.append(["render_frame", {"comp": name, "time": 0.5, "max_side": 540, "inline": False, "path": OUT + f"/pal_{name.split()[0]}.png"}, 400])
    S.append(["save_project", {}, 500])
    json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps', 'ec_palette.json'), 'w'))
    print(len(S), 'steps')

# ---- v4 final (owner, 2026-10-18): F2 cyan LED face on a dark screen, cream body, orange ears/hands/feet, no pink ----
FINAL = dict(PALETTES['P3 brand pop'], screen='#120F0D', faceInk='#46D9E6', eyeMode='glow', glow='#46D9E6', scan=True, fin='#FFA448')
ALT = dict(FINAL, fin='#46D9E6')

def final_steps():
    S = [["run_script", {"name": "final B-577 (v4)", "code": LIB + CHAR + f"""
var c=app.project.items.addComp("B-577",1080,1080,1,8,30); c.bgColor=col(K.bg); c.openInViewer(); buildB577(c,{json.dumps(FINAL)}); "ok";"""}, 2000],
         ["run_script", {"name": "alt: cyan ears", "code": LIB + CHAR + f"""
var c=app.project.items.addComp("B-577 alt cyan ears",1080,1080,1,8,30); c.bgColor=col(K.bg); buildB577(c,{json.dumps(ALT)}); "ok";"""}, 1200]]
    for t in (0.5, 3.0):
        S.append(["render_frame", {"comp": "B-577", "time": t, "max_side": 1080, "inline": False, "path": OUT + f"/b577_v4_t{t}.png"}, 400])
    S.append(["render_frame", {"comp": "B-577 alt cyan ears", "time": 0.5, "max_side": 1080, "inline": False, "path": OUT + "/b577_v4_alt.png"}, 400])
    S += [["ui_key", {"key": "Space"}, 6000], ["ui_key", {"key": "Space"}, 400], ["save_project", {}, 500]]
    json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps', 'ec_final.json'), 'w'))

if __name__ == '__main__':
    final_steps()
