# B-577 signature moves, one comp each, built live in EffectCraft over MCP from the v4 rig (ec_char.FINAL):
# run · pull (an app out of its screen) · ask ([y/n] bubble) · rewind (dial spins back) · levelup (eyes turn orange) · talk.
#   python ec_moves.py -> steps/ec_moves.json  (renders a check frame per move; ends with a save)
import json, os
from ec_char import LIB, CHAR, FINAL, OUT

HELP = r"""
function walk(g,fn){for(var i=1;i<=g.numProperties;i++){var p=g.property(i);
  if(p.matchName=="ADBE Vector Fill Color"||p.matchName=="ADBE Vector Stroke Color"){fn(p);} else if(p.numProperties) walk(p,fn);}}
function near(a,b){return Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])<0.06;}
function recolor(c,names,fromHex,toHex,t0,t1){var A=col(fromHex),B=col(toHex);
  for(var n=0;n<names.length;n++){var l=c.layer(names[n]); if(!l)continue; walk(l.property("ADBE Root Vectors Group"),function(p){var v=p.value;
    if(near(v,A)){p.setValueAtTime(t0,A);p.setValueAtTime(t1,B);}});}}
var FACE=["eye L","eye R","iris L","iris R","brow L","brow R","mouth"];
function ex(c,n,p,e){T(c.layer(n)).property(p).expression=e;}
function txt(c,s,size,hex,parent,x,y){var t=c.layers.addText(s);var d=t.property("ADBE Text Properties").property("ADBE Text Document").value;
  d.font="JetBrainsMono-ExtraBold";d.fontSize=size;d.fillColor=col(hex);d.justification=ParagraphJustification.CENTER_JUSTIFY;
  t.property("ADBE Text Properties").property("ADBE Text Document").setValue(d);if(parent)t.parent=c.layer(parent);T(t).property("ADBE Position").setValue([x,y]);return t;}
function mk(name,dur){var c=app.project.items.addComp(name,1080,1080,1,dur,30);c.bgColor=col(K.bg);c.openInViewer();buildB577(c,P);return c;}
"""

MOVES = {
 'move run': ("""var c=mk("move run",3);
ex(c,"body","ADBE Position","[ -220 + (time%3)/3*1520, 640 - Math.abs(Math.sin(time*Math.PI*4))*26 ]");
ex(c,"body","ADBE Rotate Z","6");
ex(c,"leg L","ADBE Rotate Z","Math.sin(time*Math.PI*4)*38"); ex(c,"leg R","ADBE Rotate Z","-Math.sin(time*Math.PI*4)*38");
ex(c,"arm L","ADBE Rotate Z","28 - Math.sin(time*Math.PI*4)*40"); ex(c,"arm R","ADBE Rotate Z","-28 + Math.sin(time*Math.PI*4)*40");
ex(c,"head","ADBE Rotate Z","4 + Math.sin(time*Math.PI*8)*2");""", 1.2),
 'move pull': ("""var c=mk("move pull",4);
var r=T(c.layer("arm R")).property("ADBE Rotate Z"); r.expression="";
r.setValueAtTime(0,-100); r.setValueAtTime(0.8,-175); r.setValueAtTime(1.5,-175); r.setValueAtTime(2.3,-70);
var tile=layer(c,"app tile",0,118,"arm R"); rect(tile,120,90,14,0,-50,K.amber,P.ink,4); rect(tile,80,8,4,0,-70,P.ink); rect(tile,56,8,4,-12,-50,P.ink); rect(tile,70,8,4,-5,-30,P.ink);
var to=T(tile).property("ADBE Opacity"); to.setValueAtTime(1.4,0); to.setValueAtTime(1.5,100);
var ts=T(tile).property("ADBE Scale"); ts.setValueAtTime(1.5,[30,30]); ts.setValueAtTime(2.3,[100,100]);
recolor(c,FACE,P.glow,"#FFA448",2.2,2.4);""", 3.0),
 'move ask': ("""var c=mk("move ask",4);
var b=layer(c,"bubble",260,-330,"body"); rect(b,250,120,40,0,0,"#FFFFFF",P.ink,5); path(b,[[-60,55],[-110,95],[-30,58]],true,"#FFFFFF",P.ink,5);
var bt=txt(c,"[y/n]?",44,P.ink,"bubble",0,14);
var bs=T(b).property("ADBE Scale"); bs.setValueAtTime(0.3,[0,0]); bs.setValueAtTime(0.55,[115,115]); bs.setValueAtTime(0.7,[100,100]);
ex(c,"head","ADBE Rotate Z","8 + Math.sin(time*Math.PI*2*0.45)*2");
ex(c,"brow R","ADBE Position","[64, -118]");""", 1.5),
 'move rewind': ("""var c=mk("move rewind",3);
ex(c,"hand minute","ADBE Rotate Z","(time>0.5&&time<1.8) ? 25-(time-0.5)*1100 : 25");
ex(c,"hand hour","ADBE Rotate Z","(time>0.5&&time<1.8) ? -30-(time-0.5)*300 : -30");
ex(c,"scanlines","ADBE Opacity","(time>0.5&&time<1.8) ? 6+Math.abs(Math.sin(time*40))*30 : 6");
ex(c,"head","ADBE Position","(time>0.5&&time<1.8) ? [Math.sin(time*60)*3, -270] : [0,-270]");
var t=txt(c,"<< rewind",40,"#46D9E6","body",0,-520); var o=T(t).property("ADBE Opacity"); o.setValueAtTime(0.4,0); o.setValueAtTime(0.5,100); o.setValueAtTime(1.8,100); o.setValueAtTime(1.9,0);""", 1.0),
 'move levelup': ("""var c=mk("move levelup",3);
recolor(c,FACE,P.glow,"#FFA448",0.6,0.8);
var al=T(c.layer("arm L")).property("ADBE Rotate Z"), ar=T(c.layer("arm R")).property("ADBE Rotate Z"); al.expression=""; ar.expression="";
al.setValueAtTime(0.4,28); al.setValueAtTime(0.7,150); ar.setValueAtTime(0.4,-100); ar.setValueAtTime(0.7,-150);
ex(c,"body","ADBE Position","[540, 640 - ((time>0.6&&time<1.2) ? Math.sin((time-0.6)/0.6*Math.PI)*90 : 0)]");
var t=txt(c,"LVL 02",64,"#FFA448","body",0,-560); var o=T(t).property("ADBE Opacity"); o.setValueAtTime(0.7,0); o.setValueAtTime(0.85,100);""", 1.0),
 'move talk': ("""var c=mk("move talk",4);
ex(c,"mouth","ADBE Scale","[100, 50 + Math.abs(Math.sin(time*Math.PI*5.5))*90]");
ex(c,"brow L","ADBE Position","[-64, -104 - Math.abs(Math.sin(time*Math.PI*1.3))*6]"); ex(c,"brow R","ADBE Position","[64, -104 - Math.abs(Math.sin(time*Math.PI*1.3+0.6))*6]");""", 1.0),
}

S = []
for name, (code, t) in MOVES.items():
    S.append(["run_script", {"name": name, "code": LIB + CHAR + f"var P={json.dumps(FINAL)};" + HELP + code + ' "ok";'}, 1500])
    S.append(["render_frame", {"comp": name, "time": t, "max_side": 540, "inline": False, "path": OUT + f"/{name.replace(' ', '_')}.png"}, 300])
    S.append(["ui_key", {"key": "Space"}, 2500]); S.append(["ui_key", {"key": "Space"}, 300])
S.append(["save_project", {}, 500])
json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps', 'ec_moves.json'), 'w'))
print(len(S), 'steps')
