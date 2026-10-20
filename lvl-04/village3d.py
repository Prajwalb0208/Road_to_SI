# LVL 04 3D (realistic) village scene for Blender 5.x — same storyboard as the 2D version.
# Run step by step in the live Blender over MCP (execute_blender_code):
#   exec(open(r'...\village3d.py').read()); step_env()      # sky, terrain, cliff, waterfall, pool
#   ...; step_village()   # houses, palms, rocks, plants (Poly Haven CC0)
#   ...; step_actors()    # kids + jumps + splashes, B-577 cameo (appended from LVL 03)
#   ...; step_cameras()   # 6 shots = 6 cameras switched by timeline markers, 20 s @ 24 fps
# Headless dry run: blender -b --factory-startup --python village3d.py -- --all --test <dir>
import bpy, bmesh, math, os, random, sys
from mathutils import Vector

ASSETS = os.environ.get('POLYHAVEN_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polyhaven'))   # run get_polyhaven.py first
B577 = os.environ.get('B577_BLEND', 'b577_3d.blend')   # build it with ../lvl-03/build_b577_3d.py --out b577_3d.blend
FPS = 24
SHOTS = [('s1 village wide', 0, 96), ('s2 waterfall', 96, 168), ('s3 kids edge', 168, 240), ('s4 the jumps', 240, 348), ('s5 surface', 348, 408), ('s6 cameo', 408, 480)]
C = bpy.data.collections

def coll(name):
    c = C.get(name) or C.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c
def link(o, cname): coll(cname).objects.link(o); return o
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1,)
def bsdf(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
def flat(name, hexc, rough=0.6, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; p = bsdf(m)
    p.inputs['Base Color'].default_value = lin(hexc); p.inputs['Roughness'].default_value = rough
    if emit: p.inputs['Emission Color'].default_value = lin(hexc); p.inputs['Emission Strength'].default_value = emit
    return m
def pbr(name, folder, scale=1.0, disp=False):
    """Poly Haven texture set (diff / nor_gl / rough) with box-projected object coords"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = bsdf(m)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    d = os.path.join(ASSETS, folder)
    def tex(suffix, non_color=False):
        f = next((x for x in os.listdir(d) if suffix in x), None)
        if not f: return None
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(d, f), check_existing=True); t.projection = 'BOX'; t.projection_blend = 0.3
        if non_color: t.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); return t
    td = tex('_diff_'); tr = tex('_rough_', True); tn = tex('_nor_gl_', True)
    if td: nt.links.new(td.outputs['Color'], p.inputs['Base Color'])
    if tr: nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
    if tn:
        nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    return m
def mesh_obj(name, bm, cname, mat=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); link(o, cname)
    if mat: me.materials.append(mat)
    if smooth:
        for f in me.polygons: f.use_smooth = True
    return o
def grid(name, sx, sy, nx, ny, cname, mat=None, z=0.0):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=1.0)
    for v in bm.verts: v.co.x *= sx; v.co.y *= sy; v.co.z = z
    return mesh_obj(name, bm, cname, mat)
def keyp(o, path, frame, val, idx=-1):
    setattr(o, path, val); o.keyframe_insert(path, frame=frame, index=idx)

# ------------------------------------------------------------------ 1. environment
def step_env():
    scn = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    scn.render.fps = FPS; scn.frame_start, scn.frame_end = 0, 479
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    try: scn.view_settings.view_transform = 'AgX'
    except TypeError: pass
    scn.eevee.taa_render_samples = 32
    # sky: Poly Haven HDRI (golden dawn), sun from back-right
    w = scn.world or bpy.data.worlds.new('World'); scn.world = w; w.use_nodes = True; nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND'); env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(os.path.join(ASSETS, 'kiara_1_dawn', 'kiara_1_dawn_2k.hdr'), check_existing=True)
    mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp.inputs['Rotation'].default_value[2] = math.radians(200)
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector']); tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'; tint.inputs['Factor'].default_value = 0.55; tint.inputs['B'].default_value = (1.0, 0.62, 0.32, 1)
    nt.links.new(env.outputs['Color'], tint.inputs['A']); nt.links.new(tint.outputs['Result'], bg.inputs['Color'])     # golden-hour tint over the dawn HDRI
    bg.inputs['Strength'].default_value = 0.55
    sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 5.0; sun.color = (1.0, 0.62, 0.32); sun.angle = math.radians(3)
    so = bpy.data.objects.new('Sun', sun); link(so, 'env'); so.rotation_euler = (math.radians(79), 0, math.radians(150))
    # terrain: big grid, raised banks around a pool hole, hills in the back
    t = grid('terrain', 90, 90, 120, 120, 'env', pbr('M_grass_rock', 'aerial_grass_rock', 0.08))
    rnd = random.Random(4)
    for v in t.data.vertices:
        x, y = v.co.x, v.co.y; r = math.hypot(x / 1.2, y - 4)
        bank = max(0.0, min(1.0, (r - 12) / 6)) * 2.2           # pool bowl (radius ~12) rising to banks
        hills = max(0.0, (y - 24) / 40) ** 1.5 * 9 * (0.7 + 0.3 * math.sin(x / 11 + 1.3))
        v.co.z = -2.5 + bank + 2.5 * (r > 12) + hills + rnd.uniform(-0.15, 0.15)
    t.data.update()
    # cliff + waterfall at the back of the pool
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    cl = mesh_obj('cliff', bm, 'env', pbr('M_rock_face', 'rock_face_03', 0.25)); cl.scale = (20, 6, 13); cl.location = (0, 20.5, 5.0)
    for mname, kw in (('Subsurf', {'levels': 2}),):
        m = cl.modifiers.new(mname, 'SUBSURF'); m.levels = 2; m.render_levels = 2
    tx = bpy.data.textures.new('cliff_noise', 'CLOUDS'); tx.noise_scale = 0.35
    dm = cl.modifiers.new('rough', 'DISPLACE'); dm.texture = tx; dm.strength = 0.6
    wf = grid('waterfall', 2.0, 6.0, 8, 40, 'env', None); wf.rotation_euler = (math.radians(90), 0, 0); wf.location = (0, 17.1, 5.6)
    wm = bpy.data.materials.new('M_waterfall'); wm.use_nodes = True; nt = wm.node_tree; p = bsdf(wm)
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 6; noise.inputs['Detail'].default_value = 8
    mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp.inputs['Scale'].default_value = (9, 0.45, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], noise.inputs['Vector'])
    d = mp.inputs['Location'].driver_add('default_value', 1); d.driver.expression = 'frame*0.09'      # streaks scroll down
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.62; ramp.color_ramp.elements[0].color = (0.55, 0.68, 0.66, 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color']); nt.links.new(ramp.outputs['Color'], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = 0.25; p.inputs['Roughness'].default_value = 0.2
    wf.data.materials.append(wm)
    # mist at the foot of the fall (volume)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
    mi = mesh_obj('mist', bm, 'env'); mi.scale = (5, 2.5, 2.2); mi.location = (0, 15.8, 0.6)
    mv = bpy.data.materials.new('M_mist'); mv.use_nodes = True; nt = mv.node_tree
    for n in list(nt.nodes):
        if n.type == 'BSDF_PRINCIPLED': nt.nodes.remove(n)
    vol = nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value = 0.8; vol.inputs['Color'].default_value = (1, 0.95, 0.88, 1)
    nt.links.new(vol.outputs[0], next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL').inputs['Volume']); mi.data.materials.append(mv)
    # pool water: ocean modifier + glossy teal
    wt = grid('pool', 16, 14, 2, 2, 'env', None, 0.0); wt.location = (0, 4, 0)
    oc = wt.modifiers.new('ocean', 'OCEAN'); oc.resolution = 7; oc.size = 0.6; oc.spatial_size = 30; oc.wave_scale = 0.25; oc.choppiness = 0.6
    oc.geometry_mode = 'DISPLACE'
    fd = oc.driver_add('time'); fd.driver.expression = 'frame/24'
    wmat = flat('M_water', '#163F3C', 0.18); bsdf(wmat).inputs['Specular IOR Level'].default_value = 0.08; bsdf(wmat).inputs['IOR'].default_value = 1.1; wt.data.materials.append(wmat)
    return 'env ok: terrain, cliff, waterfall, mist, pool'

# ------------------------------------------------------------------ 2. village
def palm(name, base, h=9.0, lean=1.5, rot=0.0):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.18; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    pts = [Vector(base), Vector(base) + Vector((lean * 0.3, 0, h * 0.5)), Vector(base) + Vector((lean, 0, h))]
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.bezier_points[0].radius = 1.3; sp.bezier_points[2].radius = 0.7
    tr = bpy.data.objects.new(name + ' trunk', cu); link(tr, 'village'); tr.data.materials.append(flat('M_palm_trunk', '#6B4A2E', 0.9))
    top = pts[-1]; fm = flat('M_frond', '#3E5A2C', 0.7)
    crown = bpy.data.objects.new(name + ' crown', None); link(crown, 'village'); crown.location = top
    for j in range(9):
        a = 2 * math.pi * j / 9 + rot; L = 3.6
        bm = bmesh.new(); vs = []
        for i in range(7):
            t = i / 6; r = L * t; droop = -1.8 * t * t + 0.5 * t; wdt = 0.55 * math.sin(math.pi * min(t * 1.2, 1))
            c = Vector((r * math.cos(a), r * math.sin(a), droop)); side = Vector((-math.sin(a), math.cos(a), 0)) * wdt
            vs.append((bm.verts.new(c - side), bm.verts.new(c + side)))
        for i in range(6): bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
        f = mesh_obj(f'{name} frond {j}', bm, 'village', fm); f.parent = crown
    d = crown.driver_add('rotation_euler', 1); d.driver.expression = f'0.04*sin(frame/14+{rot})'
    return crown
def house(k, x, y, w, d, rot):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    wl = mesh_obj(f'house {k} walls', bm, 'village', pbr('M_plaster', 'clay_plaster', 0.6), False); wl.scale = (w, d, 2.6); wl.location = (x, y, 1.3 + 0.4); wl.rotation_euler[2] = rot
    bm = bmesh.new()
    a, b, hgt = w / 2 + 0.6, d / 2 + 0.6, 1.8
    v = [bm.verts.new(p) for p in [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (-a * 0.55, 0, hgt), (a * 0.55, 0, hgt)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)]: bm.faces.new([v[i] for i in f])
    rf = mesh_obj(f'house {k} roof', bm, 'village', pbr('M_roof', 'clay_roof_tiles', 0.5), False); rf.location = (x, y, 2.6 + 0.4); rf.rotation_euler[2] = rot
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    dr = mesh_obj(f'house {k} door', bm, 'village', flat('M_door', '#5A3A2A', 0.8), False); dr.scale = (0.9, 0.1, 1.8); dr.location = (x - math.sin(rot) * (d / 2 + 0.02), y - math.cos(rot) * (d / 2 + 0.02), 1.3); dr.rotation_euler[2] = rot
def import_gltf(folder, name, loc, scale, rotz=0.0):
    f = next(x for x in os.listdir(os.path.join(ASSETS, folder)) if x.endswith('.gltf'))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, folder, f))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name, None); link(root, 'village')
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        link(o, 'village')
        if o.parent is None: o.parent = root
    root.location = loc; root.scale = (scale,) * 3; root.rotation_euler[2] = rotz
    return root
def step_village():
    for k, (x, y, w, d, rot) in enumerate([(-15, 12, 5, 4, 0.3), (-21, 6, 4, 3.5, -0.2), (15, 15, 4.5, 4, 0.4)]): house(k, x, y, w, d, rot)
    for k, (x, y, h, lean) in enumerate([(16, 2, 10, 1.8), (19, 12, 12, -1.5), (-18, 4, 9, 2.0), (-14, 14, 11, -1.0), (31, -6, 8, 1.2)]):
        palm(f'palm {k}', (x, y, 2.4), h, lean, k * 0.7)
    import_gltf('boulder_01', 'jump rock', (-9, 2, -1.0), 4.0, 0.6)
    import_gltf('rock_moss_set_01', 'rocks', (9, 15, 0.2), 1.1, 1.2)
    import_gltf('rock_moss_set_01', 'rocks b', (-5, 15, 0.0), 0.9, 2.4)
    for k, (x, y) in enumerate([(13, -3), (-12, 9), (10, 10), (24, 2), (-20, 0)]): import_gltf('fern_02', f'fern {k}', (x, y, 2.3), 2.0, k)
    for k, (x, y) in enumerate([(18, -6), (-16, -6), (26, -1), (14, 6)]): import_gltf('grass_bermuda_01', f'grass {k}', (x, y, 2.4), 3.0, k * 1.3)
    return 'village ok: 3 houses, 5 palms, rocks, ferns, grass'

# ------------------------------------------------------------------ 3. actors
SKIN = '#8A5A3C'
def kid(k, tee, shorts, loc, s=1.0):
    root = bpy.data.objects.new(f'kid {k}', None); link(root, 'actors'); root.location = loc
    def part(n, prim, sc, at, m):
        bm = bmesh.new()
        if prim == 'ball': bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
        else: bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=1.0, radius2=1.0, depth=2.0)
        o = mesh_obj(f'kid {k} {n}', bm, 'actors', m); o.scale = tuple(v * s for v in sc); o.location = tuple(v * s for v in at); o.parent = root; return o
    sk, tm, sm, hm = flat('M_skin', SKIN, 0.55), flat(f'M_tee {k}', tee, 0.8), flat(f'M_shorts {k}', shorts, 0.8), flat('M_hair', '#1E1612', 0.6)
    part('leg L', 'cyl', (0.07, 0.07, 0.3), (-0.09, 0, 0.3), sk); part('leg R', 'cyl', (0.07, 0.07, 0.3), (0.09, 0, 0.3), sk)
    part('shorts', 'cyl', (0.17, 0.12, 0.13), (0, 0, 0.66), sm); part('tee', 'cyl', (0.18, 0.12, 0.25), (0, 0, 1.0), tm)
    for side, sx in (('L', -1), ('R', 1)):
        piv = bpy.data.objects.new(f'kid {k} shoulder {side}', None); link(piv, 'actors'); piv.parent = root; piv.location = (sx * 0.23 * s, 0, 1.2 * s)
        a = part(f'arm {side}', 'cyl', (0.055, 0.055, 0.27), (0, 0, -0.27), sk); a.parent = piv
    part('head', 'ball', (0.15, 0.15, 0.17), (0, 0, 1.43), sk); part('hair', 'ball', (0.16, 0.16, 0.1), (0, 0.02, 1.53), hm)
    return root
def splash(name, at, f0, s=1.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.6, radius2=0.15, depth=1.4)
    o = mesh_obj(name, bm, 'actors', flat('M_splash', '#F4FBF8', 0.3, 0.3)); o.location = (at[0], at[1], 0.5 * s)
    for f, sc in ((0, 0.0), (f0, 0.0), (f0 + 3, 1.1), (f0 + 12, 0.7), (f0 + 18, 0.0)): o.scale = (sc * s, sc * s, sc * s * 1.2); o.keyframe_insert('scale', frame=f)
    return o
def step_actors():
    kids = [('#E04F3A', '#2F4A7A'), ('#F2C14E', '#3B6B3A'), ('#4FA3D9', '#5A3A2A')]
    # shot 3 (168-240) + 4 (240-348): three kids on the jump rock top (z ~ 3), jumps one after another into the pool
    jr = O('jump rock'); bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in jr.children_recursive if o.type == 'MESH' for c in o.bound_box]
    top = Vector((jr.location.x + 0.3, jr.location.y, max(zs) - 0.15))      # kids stand on the measured top of the boulder
    for k, (tee, sh) in enumerate(kids):
        xy = top + Vector((k * 0.7 - 0.7, 0, 0)); bpy.context.view_layer.update()
        hit = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((xy.x, xy.y, 40)), Vector((0, 0, -1)))
        r = kid(k, tee, sh, Vector((xy.x, xy.y, (hit[1].z if hit[0] else xy.z) + 0.01)))   # feet ON the rock surface
        start = r.location.copy(); land = Vector((-3 + k * 2.2, 3 + k * 1.5, -0.6)); t0 = 250 + k * 30
        for f in (0, t0): r.location = start; r.keyframe_insert('location', frame=f); r.rotation_euler = (0, 0, 0); r.keyframe_insert('rotation_euler', frame=f)
        for i in range(1, 9):   # parabola over 18 frames
            u = i / 8; p = start.lerp(land, u); p.z = start.z + (land.z - start.z) * u + 3.0 * 4 * u * (1 - u)
            r.location = p; r.keyframe_insert('location', frame=t0 + i * 2.25)
        r.rotation_euler = (math.radians(70), 0, 0); r.keyframe_insert('rotation_euler', frame=t0 + 18)
        r.hide_render = False; r.keyframe_insert('hide_render', frame=t0 + 18)
        for ch in r.children_recursive:
            ch.hide_render = False; ch.keyframe_insert('hide_render', frame=t0 + 18); ch.hide_render = True; ch.keyframe_insert('hide_render', frame=t0 + 19)
        splash(f'splash {k}', land, t0 + 18)
    # countdown arm (kid 1, shot 3)
    sh = O('kid 1 shoulder R')
    for f, deg in ((168, 0), (175, -150), (186, -150), (190, -60), (197, -150), (208, -150), (212, -60), (219, -160), (248, -160), (252, 0)):
        sh.rotation_euler = (0, math.radians(deg), 0); sh.keyframe_insert('rotation_euler', frame=f)
    # shot 5 (348-408): a kid surfaces, cheering, close to camera
    k5 = kid(5, '#E04F3A', '#2F4A7A', (2, -2, -1.6), 1.0)
    for f, z in ((0, -1.6), (352, -1.6), (366, -0.55), (374, -0.7)): k5.location.z = z; k5.keyframe_insert('location', frame=f, index=2)
    for side in 'LR': O(f'kid 5 shoulder {side}').rotation_euler = (0, math.radians(-160 if side == 'R' else 160), 0)
    splash('splash 5a', (1.6, -2.2), 362, 0.8); splash('splash 5b', (2.6, -1.8), 364, 0.6)
    # B-577 cameo on a rock (shot 6, 408-480): append LVL 03 model + rig, new wave plays from frame 60 of its action
    with bpy.data.libraries.load(B577, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith('B577') or n == 'B577_rig']
    rig = None
    for o in dst.objects:
        if o is None or o.name.startswith('B577_ref') or o.name == 'B577_tag_cutter' and False: continue
        link(o, 'actors')
        if o.type == 'ARMATURE': rig = o
    O('B577_ref_2D').hide_render = True; O('B577_ref_2D').hide_viewport = True
    O('B577_tag_cutter').hide_set(True); O('B577_tag_cutter').hide_render = True
    hit = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((13, -9, 50)), Vector((0, 0, -1)))
    rig.location = (13, -9, (hit[1].z if hit[0] else 1.8) + 0.02); rig.rotation_euler[2] = math.radians(-125); rig.scale = (0.55,) * 3
    for k, (x, y) in enumerate([(6.5, -2.8), (8.0, -4.2)]):   # two swimmers between camera and B-577
        h = kid(10 + k, '#E04F3A' if k else '#4FA3D9', '#2F4A7A', (x, y, -1.25), 1.0); d = h.driver_add('location', 2); d.driver.expression = f'-1.25+0.05*sin(frame/6+{k})'
    ad = rig.animation_data; act = ad.action
    tr = ad.nla_tracks.new(); st = tr.strips.new('wave', 408, act); st.action_frame_start, st.action_frame_end = 40, 120; ad.action = None
    for o in [rig] + list(rig.children_recursive):          # B-577 only appears in shot 6
        o.hide_render = True; o.keyframe_insert('hide_render', frame=0); o.hide_render = False; o.keyframe_insert('hide_render', frame=408)
    return 'actors ok: 4 kids, jumps + splashes, B-577 cameo'
def O(n): return bpy.data.objects[n]

# ------------------------------------------------------------------ 4. cameras
def cam(name, loc, target, lens=35):
    cd = bpy.data.cameras.new(name); cd.lens = lens; o = bpy.data.objects.new(name, cd); link(o, 'cameras'); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
def step_cameras():
    scn = bpy.context.scene
    cams = [cam('cam s1 wide', (6, -38, 9), (0, 10, 4), 30), cam('cam s2 falls', (2, 2, 3.5), (0, 16, 6), 32), cam('cam s3 edge', (-3.0, -5.0, 5.2), (-8.7, 2.0, 2.6), 35),
            cam('cam s4 jumps', (14, -16, 6), (-2, 6, 2), 32), cam('cam s5 surface', (2, -6.5, 0.6), (2, -2, 0.0), 40), cam('cam s6 cameo', (3, 1.5, 1.6), (11, -6.5, 1.5), 40)]
    c1 = cams[0]; c1.keyframe_insert('location', frame=0); c1.location = (5, -32, 8.5); c1.keyframe_insert('location', frame=95)   # slow push
    for m in list(scn.timeline_markers): scn.timeline_markers.remove(m)
    for (name, f0, f1), c in zip(SHOTS, cams): mk = scn.timeline_markers.new(name, frame=f0); mk.camera = c
    scn.camera = cams[0]
    return 'cameras ok: 6 shots, markers bound'

if __name__ == '__main__' and '--all' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]
    print('[v3d]', step_env()); print('[v3d]', step_village()); print('[v3d]', step_actors()); print('[v3d]', step_cameras())
    if '--test' in argv:
        out = argv[argv.index('--test') + 1]; scn = bpy.context.scene
        scn.render.resolution_percentage = 33; scn.eevee.taa_render_samples = 8
        for name, f0, f1 in SHOTS:
            f = (f0 + f1) // 2 if 's4' not in name else 262; scn.frame_set(f)
            scn.render.filepath = os.path.join(out, f'{name.split()[0]}_{f:03d}.png'); bpy.ops.render.render(write_still=True)
    if '--save' in argv: bpy.ops.wm.save_as_mainfile(filepath=argv[argv.index('--save') + 1])
