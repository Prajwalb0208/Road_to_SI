# Build-reveal Short #1 — hero render "B-577 boots up and hops out" in a terminal world.
# Builds B-577 with build_b577_3d.py (LVL 03 kit), then the set, light, camera and a 10 s hero animation (240 f @ 24 fps, 1080x1920).
#   blender -b --factory-startup --python hero.py -- [--test DIR f1,f2,..] [--save FILE] [--pct 50]
import bpy, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
# JetBrains Mono (free, OFL: jetbrains.com/lp/mono) next to this script, or set B577_FONT_DIR. Missing -> Blender's default font.
_FD = os.environ.get('B577_FONT_DIR', HERE)
FONT = os.path.join(_FD, 'JetBrainsMono-ExtraBold.ttf')
FONT_R = os.path.join(_FD, 'JetBrainsMono-Medium.ttf')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []

# ---------------------------------------------------------------- 1. B-577 (full model + rig + face drivers)
os.environ['B577_FONT'] = FONT
_saved = sys.argv; sys.argv = ['blender']
exec(open(os.path.join(HERE, 'build_b577_3d.py'), encoding='utf-8').read())
sys.argv = _saved
O = bpy.data.objects; scn = bpy.context.scene
for n in ('Key', 'Fill', 'Rim', 'Cam_hero'):
    if n in O: bpy.data.objects.remove(O[n], do_unlink=True)
rig = O['B577_rig']; rig.animation_data_clear()
for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
rig['blink'] = 0.0; rig['mood'] = 0.0
led = bpy.data.materials['B577_led']; LP = next(n for n in led.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scn.collection.children: scn.collection.children.link(c)
    return c
def emat(name, hexc, strength, base='#0B0807', rough=0.4):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*lin(base), 1); p.inputs['Roughness'].default_value = rough
    p.inputs['Emission Color'].default_value = (*lin(hexc), 1); p.inputs['Emission Strength'].default_value = strength
    return m, p
def text(name, body, loc, size, mat, rot=(math.radians(90), 0, 0), extrude=0.02, font=FONT_R, align='LEFT', cname='set'):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align
    if os.path.exists(font): cu.font = bpy.data.fonts.load(font, check_existing=True)
    o = bpy.data.objects.new(name, cu); coll(cname).objects.link(o); o.location = loc; o.rotation_euler = rot; cu.materials.append(mat); return o
def rbox(name, loc, size, mat, bev=0.08):
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); coll('set').objects.link(o); o.location = loc; o.scale = size
    b = o.modifiers.new('bevel', 'BEVEL'); b.width = bev; b.segments = 4; b.affect = 'EDGES'
    me.materials.append(mat)
    for f in me.polygons: f.use_smooth = True
    return o

# ---------------------------------------------------------------- 2. look: colour, render
scn.render.fps = 24; scn.frame_start, scn.frame_end = 1, 240
scn.render.resolution_x, scn.render.resolution_y = 1080, 1920
scn.render.resolution_percentage = int(argv[argv.index('--pct') + 1]) if '--pct' in argv else 100
try: scn.view_settings.view_transform = 'Standard'   # AgX washed out brand cream/cyan (test 1)
except TypeError: pass
for lk in ('Medium High Contrast', 'High Contrast'):
    try: scn.view_settings.look = lk; break
    except TypeError: continue
scn.eevee.taa_render_samples = 64
for a, v in (('use_raytracing', True), ('use_shadows', True), ('volumetric_tile_size', '8')):
    try: setattr(scn.eevee, a, v)
    except Exception: pass
scn.render.use_motion_blur = True
w = scn.world; nt = w.node_tree; bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (*lin('#0A0706'), 1); bg.inputs['Strength'].default_value = 1.0
vol = nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value = 0.0035; vol.inputs['Color'].default_value = (*lin('#FFE6C8'), 1)
nt.links.new(vol.outputs[0], next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD').inputs['Volume'])

# soft glow only on emissives brighter than white (cream body stays clean: LVL 03 lesson)
try:
    ng = bpy.data.node_groups.new('hero_comp', 'CompositorNodeTree'); rl = ng.nodes.new('CompositorNodeRLayers'); gl = ng.nodes.new('CompositorNodeGlare')
    out = ng.nodes.new('NodeGroupOutput'); ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    gl.inputs['Type'].default_value = 'Bloom'; gl.inputs['Threshold'].default_value = 1.0; gl.inputs['Strength'].default_value = 0.45; gl.inputs['Size'].default_value = 0.6
    ng.links.new(rl.outputs['Image'], gl.inputs['Image']); ng.links.new(gl.outputs['Image'], out.inputs[0]); scn.compositing_node_group = ng
except Exception as e: print('[hero] glare skipped', e)
# ---------------------------------------------------------------- 3. terminal world set
# floor: dark gloss with a faint cyan grid
fm = bpy.data.materials.new('M_floor'); fm.use_nodes = True; nt = fm.node_tree; p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value = (*lin('#100B09'), 1); p.inputs['Roughness'].default_value = 0.18
tc = nt.nodes.new('ShaderNodeTexCoord'); gx = nt.nodes.new('ShaderNodeTexWave'); gy = nt.nodes.new('ShaderNodeTexWave')
for g, d in ((gx, 'X'), (gy, 'Y')):
    g.wave_type = 'BANDS'; g.bands_direction = d; g.inputs['Scale'].default_value = 0.9; g.inputs['Distortion'].default_value = 0
    nt.links.new(tc.outputs['Object'], g.inputs['Vector'])
mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'; nt.links.new(gx.outputs['Fac'], mx.inputs[0]); nt.links.new(gy.outputs['Fac'], mx.inputs[1])
rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.96; rp.color_ramp.elements[0].color = (0, 0, 0, 1)
rp.color_ramp.elements[1].position = 0.995; rp.color_ramp.elements[1].color = (*lin('#46D9E6'), 1)
nt.links.new(mx.outputs[0], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value = 0.6
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0)); fl = bpy.context.object; fl.name = 'floor'; fl.data.materials.append(fm)
for c in list(fl.users_collection): c.objects.unlink(fl)
coll('set').objects.link(fl)

# platforms: terminal code blocks; each lights up amber on landing
blk_m, _ = emat('M_block', '#FFA448', 0.0, base='#1A1311', rough=0.25)
PADS = [(0.0, 0.0, 0.6, 2.2, 'b-577 --boot'), (2.6, 1.4, 1.0, 1.5, 'bpy'), (4.9, 3.2, 1.45, 1.5, 'look()'),
        (6.9, 5.4, 1.9, 1.5, 'render -a'), (8.4, 8.0, 2.4, 2.4, 'MCP')]
pads = []
for k, (x, y, top, s, label) in enumerate(PADS):
    m, pp = emat(f'M_pad_glow_{k}', '#FFA448', 0.0, base='#1C1512', rough=0.22)
    b = rbox(f'pad {k}', (x, y, top / 2), (s, s, top), blk_m)
    lip = rbox(f'pad {k} lip', (x, y, top - 0.02), (s * 1.02, s * 1.02, 0.06), m, 0.02)      # glowing top edge strip
    t = text(f'pad {k} label', label if k else '$ ' + label, (x - s / 2 + 0.12, y - s / 2 - 0.012, top * 0.45), 0.22 if k else 0.2,
             emat(f'M_label_{k}', '#F4EBDF', 1.2)[0], extrude=0.005)
    pads.append((b, lip, pp, Vector((x, y, top))))
# background: giant floating code lines (the real script), dim cream + amber
code = ['import bpy', 'def hop(t, a, b):', '    u = ease(t)', '    rig.location = a.lerp(b, u)', '    rig.location.z += 4*u*(1-u)*H',
        "look(mode='camera')", "rig['mood'] = 1.0   # eyes -> orange", 'bpy.ops.render.render(animation=True)', '$ b-577 --level 05_']
cm_dim, _ = emat('M_code_dim', '#A8978A', 0.9); cm_amb, _ = emat('M_code_amber', '#FFA448', 1.6)
for i, line in enumerate(code):
    z = 7.5 - i * 0.85; x = -6 + (i % 3) * 0.7
    text(f'code {i}', line, (x, 16 + (i % 2) * 3, z), 0.62, cm_amb if i in (5, 6, 8) else cm_dim, extrude=0.03)
# end title (appears at the end)
end_m, end_p = emat('M_endtitle', '#FFA448', 0.0)
et = text('end title', 'MADE BY B-577', (8.4, 9.6, 6.0), 0.55, end_m, font=FONT, align='CENTER', extrude=0.06)
et.rotation_euler = (math.radians(90), 0, math.radians(-25))

# ---------------------------------------------------------------- 4. light
def area(name, loc, target, energy, size, hexc):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = lin(hexc)
    o = bpy.data.objects.new(name, l); coll('light').objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
area('key amber', (1, -5, 5), (2, 2, 1.5), 700, 3, '#FFC890')
area('rim cyan', (-3, 6, 4), (2, 2, 2), 1400, 2, '#46D9E6')
area('top fill', (4, 3, 9), (4, 3, 0), 250, 8, '#F4EBDF')

# ---------------------------------------------------------------- 5. animation
def kf(o, path, f, val, idx=-1):
    setattr(o, path, val); o.keyframe_insert(path, frame=f, index=idx)
P = rig.pose.bones
def kb(b, path, f, val): setattr(P[b], path, val); P[b].keyframe_insert(path, frame=f)
def prop(n, f, v): rig[n] = v; rig.keyframe_insert(f'["{n}"]', frame=f)
start = pads[0][3]
kf(rig, 'location', 1, start); kf(rig, 'scale', 1, (1, 1, 1)); kf(rig, 'rotation_euler', 1, (0, 0, math.radians(-30)))
for b in ('head', 'arm.L', 'arm.R', 'leg.L', 'leg.R', 'body'): kb(b, 'rotation_euler', 1, (0, 0, 0))
prop('blink', 1, 0.0); prop('mood', 1, 0.0)
# boot: LEDs off -> flicker -> on (emission strength keyed)
for f, v in ((1, 0.0), (14, 0.0), (16, 1.6), (18, 0.1), (21, 1.8), (23, 0.4), (27, 1.4)):
    LP.inputs['Emission Strength'].default_value = v; LP.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
for f, v in ((1, 1.0), (12, 1.0), (30, 0.0)): prop('blink', f, v)           # eyes "open" as they boot
kb('head', 'rotation_euler', 30, (0, 0, 0)); kb('head', 'rotation_euler', 38, (0, 0, math.radians(14))); kb('head', 'rotation_euler', 46, (0, 0, math.radians(-12))); kb('head', 'rotation_euler', 52, (0, 0, 0))
f = 54; H = 1.4
for k in range(1, len(pads)):
    a = pads[k - 1][3]; b = pads[k][3]
    yaw = math.atan2(b.y - a.y, b.x - a.x) - math.pi / 2
    kf(rig, 'rotation_euler', f, (0, 0, yaw))
    kf(rig, 'scale', f, (1, 1, 1)); kf(rig, 'scale', f + 4, (1.06, 1.06, 0.86)); kf(rig, 'location', f + 4, a)        # anticipation
    for side, s in (('L', -1), ('R', 1)): kb(f'arm.{side}', 'rotation_euler', f + 4, (0, s * math.radians(30), 0))
    kf(rig, 'scale', f + 7, (0.95, 0.95, 1.1))                                                                     # stretch on take-off
    for i in range(1, 9):                                                                                          # arc
        u = i / 8; pnt = a.lerp(b, u); pnt.z = a.z + (b.z - a.z) * u + 4 * u * (1 - u) * H
        kf(rig, 'location', f + 4 + i * 1.75, pnt)
    for side, s in (('L', -1), ('R', 1)): kb(f'arm.{side}', 'rotation_euler', f + 10, (0, s * math.radians(-150), 0))
    land = f + 18
    kf(rig, 'scale', land, (1.1, 1.1, 0.82)); kf(rig, 'scale', land + 4, (0.98, 0.98, 1.03)); kf(rig, 'scale', land + 7, (1, 1, 1))
    for side in 'LR': kb(f'arm.{side}', 'rotation_euler', land + 4, (0, 0, 0))
    pp = pads[k][2]
    for ff, v in ((land - 1, 0.0), (land, 2.2), (land + 10, 0.7)):
        pp.inputs['Emission Strength'].default_value = v; pp.inputs['Emission Strength'].keyframe_insert('default_value', frame=ff)
    f = land + 6
final = f                                                                                                         # ~174
kf(rig, 'rotation_euler', final + 4, (0, 0, math.radians(-28)))                                                  # turn to camera
prop('mood', final, 0.0); prop('mood', final + 6, 1.0)                                                            # eyes -> orange
kf(rig, 'location', final + 6, pads[-1][3]); kf(rig, 'location', final + 12, pads[-1][3] + Vector((0, 0, 0.35))); kf(rig, 'location', final + 18, pads[-1][3])
for i, fw in enumerate(range(final + 14, 241, 7)):                                                                # new wave (hand clear of the head)
    kb('arm.R', 'rotation_euler', fw, (0, 0, math.radians(15 if i % 2 else -15)))
    kb('head', 'rotation_euler', fw, (0, 0, math.radians(5 if i % 2 else -3)))
for ff, v in ((1, 0.0), (final + 20, 0.0), (final + 32, 2.2)):
    end_p.inputs['Emission Strength'].default_value = v; end_p.inputs['Emission Strength'].keyframe_insert('default_value', frame=ff)
for ff, v in ((80, 0.0), (83, 1.0), (86, 0.0), (190, 0.0), (193, 1.0), (196, 0.0)): prop('blink', ff, v)
# ease every curve
def curves(a):
    if hasattr(a, 'fcurves') and len(a.fcurves): return list(a.fcurves)
    out = []
    for layer in getattr(a, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
for fc in curves(rig.animation_data.action):
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'

# ---------------------------------------------------------------- 6. camera: follows a smoothed target, push in at start, hero framing at end
tgt = bpy.data.objects.new('cam target', None); coll('camera').objects.link(tgt)
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); coll('camera').objects.link(cam); scn.camera = cam
cd.lens = 32; cd.dof.use_dof = True; cd.dof.focus_object = tgt; cd.dof.aperture_fstop = 2.8; cd.sensor_fit = 'VERTICAL'
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
CAM = [(1, (-1.25, -2.35, start.z + 1.85), start + Vector((0, 0, 1.7))),           # close on the face (boot)
       (46, (-1.0, -5.4, start.z + 2.2), start + Vector((0, 0, 1.3))),           # pull back
       (110, (3.2, -6.5, 3.6), pads[2][3] + Vector((0, 0, 1.2))),               # follow the hops
       (170, (6.8, -3.4, 4.4), pads[4][3] + Vector((0, 0, 1.3))),
       (240, (7.2, 1.6, 4.0), pads[4][3] + Vector((0, 0, 1.45)))]               # hero 3/4, end title behind
for ff, cl, tl in CAM:
    cam.location = cl; cam.keyframe_insert('location', frame=ff); tgt.location = tl; tgt.keyframe_insert('location', frame=ff)

if '--save' in argv: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(argv[argv.index('--save') + 1]))
if '--test' in argv:
    out = argv[argv.index('--test') + 1]; frames = [int(x) for x in argv[argv.index('--test') + 2].split(',')]
    for ff in frames:
        scn.frame_set(ff); scn.render.filepath = os.path.join(out, f't_{ff:03d}.png'); bpy.ops.render.render(write_still=True)
print('[hero] built; final landing frame', final)
