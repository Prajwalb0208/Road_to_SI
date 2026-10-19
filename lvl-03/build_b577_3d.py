# B-577 in 3D — one-shot build of the Road to SI LVL 03 robot (final state of the live MCP session, fails already fixed).
# Run inside Blender (Text Editor > Run Script, or over MCP for Blender with execute_blender_code), or headless:
#   blender -b --factory-startup --python build_b577_3d.py -- [--out b577.blend] [--render still.png]
# Blender 5.x. Swap the shapes and colours to make your own character; keep the write -> look -> fix loop.
import bpy, bmesh, math, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
arg = lambda k: ARGS[ARGS.index(k) + 1] if k in ARGS else None
FONT = os.environ.get('B577_FONT', '')          # optional: path to JetBrainsMono-ExtraBold.ttf (OFL) for the tag text

def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def mat(name, hexcol, rough=0.45, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*lin(hexcol), 1); p.inputs['Roughness'].default_value = rough
    if emit: p.inputs['Emission Color'].default_value = (*lin(hexcol), 1); p.inputs['Emission Strength'].default_value = emit
    return m

def obj(o, m=None, smooth=True):
    if m: o.data.materials.append(m)
    if smooth and o.type == 'MESH':
        for f in o.data.polygons: f.use_smooth = True
    return o

def cube(name, loc, scale, m, bevel=0.0, seg=6, smooth=True):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; o.scale = scale
    if bevel: b = o.modifiers.new('Bevel', 'BEVEL'); b.width = bevel; b.segments = seg
    return obj(o, m, smooth)

def sphere(name, loc, r, m, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; o.scale = scale
    return obj(o, m)

def capsule(name, a, b, r, m):
    a, b = Vector(a), Vector(b)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=r, radius2=r, depth=(b - a).length); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = (a + b) / 2; o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = r * 0.9; bv.segments = 6
    return obj(o, m)

def parent_keep(child, parent):
    bpy.context.view_layer.update()       # matrix_world is stale until the depsgraph runs -> parenting would use identity
    mw = child.matrix_world.copy(); child.parent = parent; child.matrix_world = mw

# ---------- scene ----------
scn = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
w = scn.world or bpy.data.worlds.new('World'); scn.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (*lin('17110E'), 1); bg.inputs[1].default_value = 3.0
scn.view_settings.view_transform = 'Standard'     # AgX (default) desaturates brand colours: cream turns grey, orange muddy
scn.render.engine = scn.render.engine             # EEVEE by default in 5.x
scn.eevee.taa_render_samples = 32

M = dict(cream=mat('B577_cream', 'FFF3E0'), orange=mat('B577_orange', 'FFA448', 0.4), amber=mat('B577_amber', 'FFA448', 0.35),
         lit=mat('B577_level_lit', 'FFA448', 0.4, 1.5), off=mat('B577_level_off', 'E6CFB6'), ink=mat('B577_ink', '060504'),
         panel=mat('B577_panel', '6E4C30'), white=mat('B577_white', 'FFFFFF', emit=3.0), screen=mat('B577_screen', '120F0D', 0.15))
# screen scanlines: wave bands on Z -> base colour
nt = M['screen'].node_tree; p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tc, wv, ramp = nt.nodes.new('ShaderNodeTexCoord'), nt.nodes.new('ShaderNodeTexWave'), nt.nodes.new('ShaderNodeValToRGB')
wv.wave_type = 'BANDS'; wv.bands_direction = 'Z'; wv.inputs['Scale'].default_value = 40.0
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.006, 0.005, 0.004, 1)
ramp.color_ramp.elements[1].position = 0.55; ramp.color_ramp.elements[1].color = (0.03, 0.03, 0.03, 1)
nt.links.new(tc.outputs['Object'], wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
# LED: emission only (base black), colour = mix(cyan, orange) driven by the rig's "mood"
led = bpy.data.materials.new('B577_led'); led.use_nodes = True; nt = led.node_tree
p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value = (0, 0, 0, 1)
p.inputs['Emission Strength'].default_value = 1.4      # 2.5+ clips red first -> orange turns lemon-yellow
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
mix.inputs['A'].default_value = (*lin('46D9E6'), 1); mix.inputs['B'].default_value = (*lin('FFA448'), 1)
nt.links.new(mix.outputs['Result'], p.inputs['Emission Color'])

# ---------- head + face (face built on the unscaled head, then the head is slimmed: the face follows) ----------
head = cube('B577_head', (0, 0, 1.6), (1.3, 1.0, 1.05), M['cream'], 0.22)
head.modifiers.new('Subsurf', 'SUBSURF').levels = 1
screen = cube('B577_screen', (0, -0.515, 1.6), (1.0, 0.04, 0.78), M['screen'], 0.12, 5)   # -0.49 put the face INSIDE the head
eyes = [sphere(f'B577_eye_{s}', (x, -0.545, 1.66), 0.11, led, (0.8, 0.35, 1.25)) for s, x in (('L', -0.24), ('R', 0.24))]
for o in [screen] + eyes: parent_keep(o, head)
head.location.z = 1.55; head.scale.y = 0.78          # 1 m deep read as a toaster from the side
bpy.context.view_layer.update()
front_y = min((screen.matrix_world @ v.co).y for v in screen.data.vertices) - 0.006
def tube(name, pts, r):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, (x, z) in enumerate(pts): sp.points[i].co = (x, front_y, z, 1)
    o = bpy.data.objects.new(name, cu); scn.collection.objects.link(o); o.data.materials.append(led); parent_keep(o, head); return o
for e in eyes:
    c = e.matrix_world.translation.copy(); s = e.name[-1]
    tube(f'B577_brow_{s}', [(c.x - 0.09, c.z + 0.18), (c.x - 0.02, c.z + 0.225), (c.x + 0.09, c.z + 0.195)], 0.016)
    g = sphere(f'B577_glint_{s}', (c.x + 0.03, front_y - 0.03, c.z + 0.05), 0.022, M['white']); parent_keep(g, head)
tube('B577_smile', [(0.11 * math.cos(math.radians(a)), eyes[0].matrix_world.translation.z - 0.17 + 0.05 * math.sin(math.radians(a))) for a in range(200, 341, 10)], 0.015)

# ---------- body ----------
torso = cube('B577_torso', (0, 0, 0.68), (0.69, 0.5, 0.62), M['cream'], 0.15)
for s, x in (('L', -0.155), ('R', 0.155)):
    capsule(f'B577_leg_{s}', (x, 0, 0.42), (x, 0, 0.10), 0.06, M['cream'])
    sphere(f'B577_foot_{s}', (x, -0.04, 0.065), 0.14, M['orange'], (1, 1.1, 0.46))
capsule('B577_arm_L', (-0.35, 0, 0.88), (-0.5, 0, 0.53), 0.055, M['cream']); sphere('B577_hand_L', (-0.5, 0, 0.53), 0.09, M['orange'])
capsule('B577_arm_R', (0.35, 0, 0.9), (0.8, -0.12, 1.16), 0.055, M['cream']); sphere('B577_hand_R', (0.8, -0.12, 1.16), 0.09, M['orange'])  # wave, clear of the head
for s, sx in (('L', -1), ('R', 1)):     # ear fins: trapezoid, tall at the head
    me = bpy.data.meshes.new(f'ear_{s}'); bm = bmesh.new(); pts = [(0, -0.30), (0, 0.30), (0.22, 0.20), (0.22, -0.20)]
    vs = [bm.verts.new((sx * (0.66 + x), -0.08, z)) for x, z in pts] + [bm.verts.new((sx * (0.66 + x), 0.08, z)) for x, z in pts]
    bm.faces.new(vs[:4]); bm.faces.new(vs[4:][::-1])
    for i in range(4): j = (i + 1) % 4; bm.faces.new((vs[i], vs[j], vs[4 + j], vs[4 + i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(f'B577_ear_{s}', me); scn.collection.objects.link(o); o.location = (0, 0, 1.55); o.data.materials.append(M['orange'])
    b = o.modifiers.new('Bevel', 'BEVEL'); b.width = 0.03; b.segments = 3

# ---------- details ----------
cut = cube('B577_tag_cutter', (0, -0.25, 0.80), (0.34, 0.06, 0.12), None, smooth=False)
cut.display_type = 'WIRE'; cut.hide_render = True; cut.hide_set(True)   # visible cutters draw OVER the tag in the rendered viewport
bo = torso.modifiers.new('TagRecess', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cut
cube('B577_tag', (0, -0.24, 0.80), (0.3, 0.03, 0.09), M['amber'], 0.02, 4)
cu = bpy.data.curves.new('B577_tag_text', 'FONT'); cu.body = 'B-577'; cu.align_x = 'CENTER'; cu.size = 0.075; cu.extrude = 0.004
if FONT and os.path.exists(FONT): cu.font = bpy.data.fonts.load(FONT, check_existing=True)
t = bpy.data.objects.new('B577_tag_text', cu); scn.collection.objects.link(t); t.data.materials.append(M['ink'])
t.location = (0, -0.259, 0.775); t.rotation_euler = (math.radians(90), 0, 0)   # text is born lying flat
for i in range(5):   # level road: LVL 03 = 3 lit
    cube(f'B577_level_{i + 1}', (-0.16 + i * 0.08, -0.25, 0.62), (0.065, 0.02, 0.028), M['lit'] if i < 3 else M['off'], 0.012, 3)
top = 1.55 + 0.525
sphere('B577_pivot', (0, -0.05, top + 0.02), 0.05, M['amber'])
for name, ang, ln, r, m in (('B577_minute_hand', 40, 0.42, 0.022, M['amber']), ('B577_hour_hand', -25, 0.24, 0.026, M['ink'])):
    d = Vector((math.sin(math.radians(ang)), 0, math.cos(math.radians(ang)))); a = Vector((0, -0.05, top + 0.02))
    capsule(name, a, a + d * ln, r, m)
for k in range(12):   # clock ticks on the bezel
    a = math.radians(k * 30)
    o = cube(f'B577_tick_{k:02d}', (0.565 * math.sin(a), -0.392, 1.55 + 0.455 * math.cos(a)), (0.014, 0.012, 0.04), M['panel'], smooth=False)
    o.rotation_euler = (0, a, 0)

# ---------- lights + cameras ----------
def area(name, loc, energy, size, rgb):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = rgb
    o = bpy.data.objects.new(name, l); o.location = loc; scn.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area('Key', (2.2, -3.0, 3.2), 260, 2.5, (1.0, 0.96, 0.9)); area('Fill', (-3.0, -2.2, 1.6), 90, 3.0, (0.9, 0.95, 1.0)); area('Rim', (0.5, 3.0, 3.0), 220, 1.5, (0.75, 0.9, 1.0))
cd = bpy.data.cameras.new('Cam_hero'); cam = bpy.data.objects.new('Cam_hero', cd); scn.collection.objects.link(cam); cd.lens = 50
cam.location = (3.3, -6.9, 1.55); cam.rotation_euler = (Vector((0, 0, 1.2)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); scn.camera = cam

# ---------- rig: rigid parts ride on bones (no weight painting) ----------
arm = bpy.data.armatures.new('B577_rig'); rig = bpy.data.objects.new('B577_rig', arm); scn.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
for n, h, tl, par in (('root', (0, 0, 0), (0, 0, 0.3), None), ('body', (0, 0, 0.4), (0, 0, 1.0), 'root'), ('head', (0, 0, 1.02), (0, 0, 1.6), 'body'),
                      ('arm.L', (-0.35, 0, 0.88), (-0.5, 0, 0.53), 'body'), ('arm.R', (0.35, 0, 0.9), (0.8, -0.12, 1.16), 'body'),
                      ('leg.L', (-0.155, 0, 0.42), (-0.155, 0, 0.1), 'root'), ('leg.R', (0.155, 0, 0.42), (0.155, 0, 0.1), 'root')):
    b = arm.edit_bones.new(n); b.head, b.tail = h, tl
    if par: b.parent = arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT')
O = bpy.data.objects
groups = {'body': ['B577_torso', 'B577_tag', 'B577_tag_text', 'B577_tag_cutter'] + [f'B577_level_{i}' for i in range(1, 6)],
          'head': ['B577_head', 'B577_ear_L', 'B577_ear_R', 'B577_pivot', 'B577_minute_hand', 'B577_hour_hand'] + [f'B577_tick_{k:02d}' for k in range(12)],
          'arm.L': ['B577_arm_L', 'B577_hand_L'], 'arm.R': ['B577_arm_R', 'B577_hand_R'], 'leg.L': ['B577_leg_L', 'B577_foot_L'], 'leg.R': ['B577_leg_R', 'B577_foot_R']}
for bn, names in groups.items():
    for nm in names:
        o = O[nm]; mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bn; o.matrix_world = mw
for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
# face controls: blink + mood (cyan -> orange). New drivers must be re-validated or they stay "invalid" and do nothing.
rig['blink'] = 0.0; rig['mood'] = 0.0
def drive(fc, expr):
    d = fc.driver; d.type = 'SCRIPTED'; v = d.variables.new(); v.name = 'x'; v.type = 'SINGLE_PROP'
    v.targets[0].id = rig; v.targets[0].data_path = '["%s"]' % ('mood' if expr == 'mood' else 'blink')
    d.expression = 'x' if expr == 'mood' else expr; d.is_valid = True
for n, base in (('B577_eye_L', 1.25), ('B577_eye_R', 1.25), ('B577_glint_L', 1.0), ('B577_glint_R', 1.0)):
    drive(O[n].driver_add('scale', 2), f'{base}*(1-0.92*x)')
drive(mix.inputs['Factor'].driver_add('default_value'), 'mood')

# ---------- animation: idle bob, blinks, wave, hop + eyes turn orange (24 fps, 1-240) ----------
scn.render.fps = 24; scn.frame_start, scn.frame_end = 1, 240
P = rig.pose.bones
def key(b, path, f, val): setattr(P[b], path, val); P[b].keyframe_insert(path, frame=f)
def prop(p, f, v): rig[p] = v; rig.keyframe_insert(f'["{p}"]', frame=f)
for b in ('leg.L', 'leg.R', 'arm.L'): key(b, 'rotation_euler', 1, (0, 0, 0))   # a curve holds its first key backwards in time
for f in range(1, 241, 12): key('body', 'location', f, (0, 0.03 if (f // 12) % 2 else 0.0, 0))
for f0 in (40, 150):
    for f, v in ((f0, 0.0), (f0 + 3, 1.0), (f0 + 6, 0.0)): prop('blink', f, v)
key('arm.R', 'rotation_euler', 1, (0, 0, 0)); key('head', 'rotation_euler', 1, (0, 0, 0))
for i, f in enumerate(range(60, 121, 10)):     # bone axes: +Z raises this arm; head tilt is Z (a bone's Y runs along it)
    key('arm.R', 'rotation_euler', f, (0, 0, math.radians(50 if i % 2 else 10))); key('head', 'rotation_euler', f, (0, 0, math.radians(6 if i % 2 else -4)))
key('arm.R', 'rotation_euler', 135, (0, 0, 0)); key('head', 'rotation_euler', 135, (0, 0, 0))
for f, z in ((1, 0.0), (165, 0.0), (172, -0.06), (180, 0.4), (188, 0.0), (192, -0.05), (198, 0.0)): key('root', 'location', f, (0, z, 0))
for f, v in ((1, 0.0), (186, 0.0), (190, 1.0), (235, 1.0)): prop('mood', f, v)
scn.frame_set(95)

if arg('--out'): bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(arg('--out')))
if arg('--render'):
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    scn.render.filepath = os.path.abspath(arg('--render')); bpy.ops.render.render(write_still=True)
print('[build_b577_3d] done:', len([o for o in O if o.name.startswith('B577')]), 'parts')
