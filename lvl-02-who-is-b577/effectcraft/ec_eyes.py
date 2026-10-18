# B-577 eye study (two eyes, cartoon expressions): 3 styles x 4 moods on TV-screen heads, built live in EffectCraft over MCP.
#   python ec_eyes.py -> steps/ec_eyes.json   (record with rec.sh; ends with render + save)
import json, os, math
from ec_build import js, OUT

ROWS = ['A', 'B', 'C']
MOODS = ['neutral', 'happy', 'surprised', 'asking']

FACE = r"""
function arcPts(cx,cy,rx,ry,a0,a1,n){var p=[];for(var i=0;i<=n;i++){var a=a0+(a1-a0)*i/n;p.push([cx+rx*Math.cos(a),cy+ry*Math.sin(a)]);}return p;}
function eye(l,style,mood,x,y,s,flip){
  var rx=34*s, ry=46*s; if(mood=="surprised"){rx*=1.12;ry*=1.12;}
  var pr=(style=="C")?0:(mood=="surprised"?11*s:17*s);
  var px=x, py=y+4*s; if(mood=="asking"){px+=10*s;py-=12*s;}
  if(mood=="happy"){ // smiling closed eye: thick upward arc
    path(l,arcPts(x,y+14*s,rx,ry*0.62,Math.PI*1.12,Math.PI*1.88,14),false,null,K.ink,8*s); return;}
  // groups draw in order (first = top): highlights, lid, pupil/iris, sclera
  if(style!="C"){ oval(l,9*s,9*s,px+7*s,py-8*s,"#FFFFFF"); oval(l,5*s,5*s,px-6*s,py+6*s,"#FFFFFF"); }
  if(mood=="neutral"||mood=="asking"){ // calm half-lid: top segment of the eye in shell colour
    var a=(mood=="asking"&&flip)?0.30:0.42; var lid=arcPts(x,y,rx,ry,Math.PI*(1+a),Math.PI*(2-a),12);
    path(l,lid.concat(arcPts(x,y,rx,ry,Math.PI*(2-a),Math.PI*(1+a),12).slice(0,1)),true,K.shell,K.ink,4*s);}
  if(style=="A") oval(l,pr*2,pr*2.2,px,py,K.ink);
  if(style=="B"){ oval(l,pr*1.0,pr*1.1,px,py,K.ink); oval(l,pr*2,pr*2.2,px,py,K.amber); }
  if(style=="C"){ // pie-eye: dark oval with a pie-cut highlight wedge
    var w=[[x+6*s,y-10*s]].concat(arcPts(x+6*s,y-10*s,rx*0.55,ry*0.55,Math.PI*1.25,Math.PI*1.65,6));
    path(l,w,true,"#FFFFFF"); oval(l,rx*1.5,ry*1.7,x+2*s,y+2*s,K.ink); return; }
  oval(l,rx*2,ry*2,x,y,"#FFFFFF",K.ink,4*s);
}
function brow(l,mood,x,y,s,side){
  var lift=(mood=="surprised")?-22*s:(mood=="asking"&&side>0)?-26*s:(mood=="happy")?-8*s:0;
  var tilt=(mood=="asking"&&side<0)?6*s:0;
  path(l,[[x-24*s,y+lift+tilt+4*s],[x,y+lift-6*s],[x+24*s,y+lift+tilt*0.3+4*s]],false,null,K.ink,7*s);
}
function mouth(l,mood,x,y,s){
  if(mood=="happy"){ path(l,arcPts(x,y-14*s,44*s,30*s,Math.PI*0.08,Math.PI*0.92,16).concat([[x+40*s,y-4*s]]),true,K.ink,K.ink,4*s); return;} // open grin
  if(mood=="surprised"){ oval(l,26*s,32*s,x,y,K.ink); return;}
  if(mood=="asking"){ path(l,arcPts(x+8*s,y-12*s,24*s,14*s,Math.PI*0.15,Math.PI*0.85,10),false,null,K.ink,6*s); return;}
  path(l,arcPts(x,y-20*s,36*s,22*s,Math.PI*0.15,Math.PI*0.85,12),false,null,K.ink,6*s);
}
function face(c,name,style,mood,cx,cy,s){
  var l=layer(c,name,cx,cy);
  brow(l,mood,-60*s,-82*s,s,-1); brow(l,mood,60*s,-82*s,s,1);
  eye(l,style,mood,-60*s,-20*s,s,false); eye(l,style,mood,60*s,-20*s,s,true);
  mouth(l,mood,0,70*s,s);
  rect(l,310*s,250*s,46*s,0,0,K.glass,K.line,5*s);      // screen
  rect(l,400*s,330*s,70*s,0,0,K.shell,K.line,7*s);      // bezel
  return l;
}
"""

S = [["run_script", {"name": "eye study comp", "code": js(FACE + """
var c=app.project.items.addComp("eye study",1920,1080,1,4,30); c.bgColor=col(K.bg); c.openInViewer(); "ok";""")}, 1500]]
for r, st in enumerate(ROWS):
    code = "var c=comp(); for(var i=0;i<app.project.numItems;i++){} "
    code = "var c=null; for(var i=1;i<=app.project.numItems;i++){if(app.project.item(i).name=='eye study')c=app.project.item(i);} c.openInViewer();\n"
    for k, m in enumerate(MOODS):
        code += f'face(c,"{st} {m}","{st}","{m}",{300 + k * 440},{190 + r * 345},0.78);\n'
    S.append(["run_script", {"name": f"style {st}: 4 moods", "code": js(FACE + code + '"ok";')}, 1600])
S.append(["run_script", {"name": "labels", "code": js(FACE + """
var c=null; for(var i=1;i<=app.project.numItems;i++){if(app.project.item(i).name=='eye study')c=app.project.item(i);}
var L2=["A classic","B amber iris","C retro pie-eye"]; for(var r=0;r<3;r++){var t=c.layers.addText(L2[r]);var d=t.property("ADBE Text Properties").property("ADBE Text Document").value;
d.font="JetBrainsMono-ExtraBold";d.fontSize=26;d.fillColor=col(K.amber);t.property("ADBE Text Properties").property("ADBE Text Document").setValue(d);T(t).property("ADBE Position").setValue([20,60+r*345]);}
var M=["neutral","happy","surprised","asking"]; for(var k=0;k<4;k++){var t=c.layers.addText(M[k]);var d=t.property("ADBE Text Properties").property("ADBE Text Document").value;
d.font="JetBrainsMono-Medium";d.fontSize=24;d.fillColor=col(K.shell);t.property("ADBE Text Properties").property("ADBE Text Document").setValue(d);T(t).property("ADBE Position").setValue([250+k*440,1065]);}
"ok";""")}, 1200])
S.append(["render_frame", {"comp": "eye study", "time": 0, "max_side": 1920, "inline": False, "path": OUT + "/eye_study.png"}, 500])
S.append(["save_project", {}, 500])
json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps', 'ec_eyes.json'), 'w'))
print(len(S), 'steps')
