# LVL 04 3D polish pass (owner, 2026-10-20: "real waterfall shape, better kids, particle splashes").
# Loads village3d.py, then replaces: the flat waterfall -> curved free-fall sheet (2 layers) + particle foam;
# blocky kids -> rounded kids (ellipsoid body parts, hands, feet, neck); cone splashes -> particle droplets + ripple rings.
# Live (MCP, each call re-loads):  exec(open(r'...\village3d_polish.py').read()); polish_waterfall() / polish_kids()
# Headless: blender -b village3d_live.blend --python village3d_polish.py -- --all [--test DIR] [--save]
import bpy, bmesh, math, os, sys
from mathutils import Vector
_argv_backup = sys.argv; sys.argv = ['blender']
exec(open(os.environ.get('VILLAGE3D', 'village3d.py')).read())   # path to village3d.py (same folder)
sys.argv = _argv_backup

def kill(names):
    for n in names:
        o = bpy.data.objects.get(n)
        if o:
            for c in list(o.children_recursive): bpy.data.objects.remove(c, do_unlink=True)
            bpy.data.objects.remove(o, do_unlink=True)

def droplet():
    o = bpy.data.objects.get('fx droplet')
    if o: return o
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.25)
    o = mesh_obj('fx droplet', bm, 'fx', flat('M_droplet', '#EAF6F3', 0.15, 0.15)); o.location = (0, 0, -60)   # parked under the ground
    return o

def particles(name, emitter, f0, f1, count, life, vel, rand, size, grav=1.0):
    ps = emitter.modifiers.new(name, 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = count; st.frame_start = f0; st.frame_end = f1; st.lifetime = life; st.lifetime_random = 0.4
    st.emit_from = 'FACE'; st.normal_factor = vel; st.factor_random = rand; st.effector_weights.gravity = grav
    st.render_type = 'OBJECT'; st.instance_object = droplet(); st.particle_size = size; st.size_random = 0.6
    st.display_method = 'DOT'
    return ps

# ------------------------------------------------------------------ waterfall
def fall_sheet(name, top, drop, w0, w1, reach, nu=10, nv=40, off=0.0):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap'); rows = []
    for j in range(nv + 1):
        v = j / nv; y = top.y - reach * math.sqrt(v) - off; z = top.z - drop * v
        hw = (w0 + (w1 - w0) * v) / 2
        rows.append([bm.verts.new((top.x + (i / nu * 2 - 1) * hw + 0.08 * math.sin(i * 1.7 + j * 0.9), y + 0.05 * math.sin(i * 2.3), z)) for i in range(nu + 1)])
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
            for l, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uv].uv = (a / nu, 1 - b / nv)
    return mesh_obj(name, bm, 'env')

def fall_material(name, alpha=0.95, speed=0.09):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = bsdf(m)
    for n in [n for n in nt.nodes if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL')]: nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (10, 0.9, 1)
    d = mp.inputs['Location'].driver_add('default_value', 1); d.driver.expression = f'frame*{speed}'      # streaks run down the sheet
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 5; nz.inputs['Detail'].default_value = 10; nz.inputs['Distortion'].default_value = 0.6
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.38; rp.color_ramp.elements[0].color = (0.42, 0.58, 0.56, 1)
    rp.color_ramp.elements[1].position = 0.66; rp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], p.inputs['Base Color']); nt.links.new(rp.outputs['Color'], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = 0.2; p.inputs['Roughness'].default_value = 0.15
    mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY_ADD'; mth.inputs[1].default_value = alpha * 0.6; mth.inputs[2].default_value = alpha * 0.4
    nt.links.new(nz.outputs['Fac'], mth.inputs[0]); nt.links.new(mth.outputs[0], p.inputs['Alpha'])
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

def polish_waterfall():
    kill(['waterfall', 'waterfall back', 'waterfall front', 'foam emitter'])
    top = Vector((0, 17.6, 10.9)); drop = 11.0
    a = fall_sheet('waterfall back', top, drop, 2.2, 3.6, 1.6, off=0.0); a.data.materials.append(fall_material('M_fall_back', 1.0, 0.09))
    b = fall_sheet('waterfall front', top + Vector((0, -0.12, 0.05)), drop, 2.0, 3.9, 1.75, off=0.05); b.data.materials.append(fall_material('M_fall_front', 0.55, 0.12))
    # foam: particle spray where the fall hits the pool
    em = grid('foam emitter', 2.2, 0.8, 4, 2, 'env', None, 0.05); em.location = (0, top.y - 1.7, 0); em.show_instancer_for_render = False; em.show_instancer_for_viewport = False
    particles('foam', em, 0, 480, 3200, 22, 3.4, 2.0, 0.09)
    O('mist').location = (0, top.y - 1.9, 0.8); O('mist').scale = (5.5, 2.8, 2.4)
    vol = next(n for n in O('mist').active_material.node_tree.nodes if n.type == 'PRINCIPLED_VOLUME'); vol.inputs['Density'].default_value = 0.22   # was a flat white blob
    try: bpy.context.scene.render.use_motion_blur = True
    except Exception: pass
    return 'waterfall: curved free-fall sheet x2 + particle foam'

# ------------------------------------------------------------------ kids (rounded)
def kid(k, tee, shorts, loc, s=1.0):
    root = bpy.data.objects.new(f'kid {k}', None); link(root, 'actors'); root.location = loc
    sk, tm, sm, hm = flat('M_skin', SKIN, 0.5), flat(f'M_tee {k}', tee, 0.8), flat(f'M_shorts {k}', shorts, 0.8), flat('M_hair', '#1E1612', 0.6)
    def ball(n, sc, at, m, parent=root):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
        o = mesh_obj(f'kid {k} {n}', bm, 'actors', m); o.scale = tuple(v * s for v in sc); o.location = tuple(v * s for v in at); o.parent = parent; return o
    for side, sx in (('L', -1), ('R', 1)):
        ball(f'thigh {side}', (0.065, 0.07, 0.17), (sx * 0.085, 0, 0.47), sk); ball(f'shin {side}', (0.055, 0.058, 0.17), (sx * 0.085, 0, 0.21), sk)
        ball(f'foot {side}', (0.05, 0.1, 0.035), (sx * 0.085, -0.04, 0.03), sk)
    ball('shorts', (0.165, 0.12, 0.13), (0, 0, 0.68), sm); ball('tee', (0.175, 0.12, 0.25), (0, 0, 0.98), tm)
    ball('neck', (0.045, 0.045, 0.06), (0, 0, 1.24), sk)
    for side, sx in (('L', -1), ('R', 1)):
        piv = bpy.data.objects.new(f'kid {k} shoulder {side}', None); link(piv, 'actors'); piv.parent = root; piv.location = (sx * 0.2 * s, 0, 1.17 * s)
        ball(f'arm {side}', (0.048, 0.05, 0.15), (sx * 0.02, 0, -0.14), sk, piv); ball(f'forearm {side}', (0.042, 0.044, 0.14), (sx * 0.025, 0, -0.4), sk, piv)
        ball(f'hand {side}', (0.04, 0.03, 0.05), (sx * 0.03, 0, -0.57), sk, piv)
    ball('head', (0.125, 0.135, 0.15), (0, 0, 1.42), sk); ball('hair', (0.132, 0.14, 0.09), (0, 0.015, 1.5), hm)
    for side, sx in (('L', -1), ('R', 1)): ball(f'ear {side}', (0.02, 0.03, 0.035), (sx * 0.125, 0, 1.42), sk)
    return root

# ------------------------------------------------------------------ splashes (particles + ripple)
def splash(name, at, f0, s=1.0):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=0.35 * s)
    em = mesh_obj(name, bm, 'actors'); em.location = (at[0], at[1], 0.03); em.show_instancer_for_render = False; em.show_instancer_for_viewport = False   # hiding the emitter would hide its particles
    particles(name + ' drops', em, f0, f0 + 3, int(500 * s), 24, 4.5 * s, 1.8, 0.12 * s)
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=32, radius=1.0)
    rg = mesh_obj(name + ' ripple', bm, 'actors', flat('M_ripple', '#EAF6F3', 0.2, 0.2)); rg.location = (at[0], at[1], 0.04)
    sk = rg.modifiers.new('w', 'SKIN') if False else None
    sol = rg.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = 0.05
    bm2 = bmesh.new(); bmesh.ops.create_circle(bm2, cap_ends=False, segments=32, radius=1.0); bm2.free()
    rg.data.vertices.foreach_get  # noop: keep simple ring (edges) -> give it width with a screw-less trick below
    for f, sc, hide in ((0, 0.01, True), (f0, 0.01, True), (f0 + 1, 0.2, False), (f0 + 24, 2.2 * s, False), (f0 + 25, 2.2 * s, True)):
        rg.scale = (sc, sc, 1); rg.keyframe_insert('scale', frame=f); rg.hide_render = hide; rg.keyframe_insert('hide_render', frame=f)
    return em

def polish_kids():
    kill([o.name for o in bpy.data.objects if o.name.startswith(('kid ', 'splash '))])
    kids = [('#E04F3A', '#2F4A7A'), ('#F2C14E', '#3B6B3A'), ('#4FA3D9', '#5A3A2A')]
    jr = O('jump rock'); bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in jr.children_recursive if o.type == 'MESH' for c in o.bound_box]
    top = Vector((jr.location.x + 0.3, jr.location.y, max(zs) - 0.15))
    for k, (tee, sh) in enumerate(kids):
        xy = top + Vector((k * 0.7 - 0.7, 0, 0)); bpy.context.view_layer.update()
        hit = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector((xy.x, xy.y, 40)), Vector((0, 0, -1)))
        r = kid(k, tee, sh, Vector((xy.x, xy.y, (hit[1].z if hit[0] else xy.z) + 0.01)))
        start = r.location.copy(); land = Vector((-3 + k * 2.2, 3 + k * 1.5, -0.6)); t0 = 250 + k * 30
        for f in (0, t0): r.location = start; r.keyframe_insert('location', frame=f); r.rotation_euler = (0, 0, 0); r.keyframe_insert('rotation_euler', frame=f)
        for i in range(1, 9):
            u = i / 8; p = start.lerp(land, u); p.z = start.z + (land.z - start.z) * u + 3.0 * 4 * u * (1 - u)
            r.location = p; r.keyframe_insert('location', frame=t0 + i * 2.25)
        r.rotation_euler = (math.radians(70), 0, 0); r.keyframe_insert('rotation_euler', frame=t0 + 18)
        for side in 'LR':      # arms up for the jump
            sp = O(f'kid {k} shoulder {side}'); sp.rotation_euler = (0, 0, 0); sp.keyframe_insert('rotation_euler', frame=t0)
            sp.rotation_euler = (0, math.radians(165 if side == 'L' else -165), 0); sp.keyframe_insert('rotation_euler', frame=t0 + 4)
        for ch in r.children_recursive:
            ch.hide_render = False; ch.keyframe_insert('hide_render', frame=t0 + 18); ch.hide_render = True; ch.keyframe_insert('hide_render', frame=t0 + 19)
        splash(f'splash {k}', land, t0 + 18)
    sh = O('kid 1 shoulder R')
    for f, deg in ((168, 0), (175, -150), (186, -150), (190, -60), (197, -150), (208, -150), (212, -60), (219, -160), (248, -160)):
        sh.rotation_euler = (0, math.radians(deg), 0); sh.keyframe_insert('rotation_euler', frame=f)
    k5 = kid(5, '#E04F3A', '#2F4A7A', (2, -2, -1.8), 1.0)
    for f, z in ((0, -1.8), (352, -1.8), (366, -0.85), (374, -0.98)): k5.location.z = z; k5.keyframe_insert('location', frame=f, index=2)
    for side in 'LR': O(f'kid 5 shoulder {side}').rotation_euler = (0, math.radians(-160 if side == 'R' else 160), 0)
    splash('splash 5a', (1.4, -2.2), 360, 0.9); splash('splash 5b', (2.7, -1.8), 362, 0.7)
    for k, (x, y) in enumerate([(6.5, -2.8), (8.0, -4.2)]):
        h = kid(10 + k, '#E04F3A' if k else '#4FA3D9', '#2F4A7A', (x, y, -1.2), 1.0); d = h.driver_add('location', 2); d.driver.expression = f'-1.2+0.05*sin(frame/6+{k})'
    return 'kids: rounded bodies x6, jumps + particle splashes'

if __name__ == '__main__' and '--all' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]
    print('[pol]', polish_waterfall()); print('[pol]', polish_kids())
    if '--test' in argv:
        out = argv[argv.index('--test') + 1]; scn = bpy.context.scene
        scn.render.resolution_percentage = 40; scn.eevee.taa_render_samples = 16
        want = {132: 's2', 271: 's4', 286: 's4b', 366: 's5'}
        for f in range(0, 367):                     # particles only simulate when frames are evaluated in order
            scn.frame_set(f)
            if f in want: scn.render.filepath = os.path.join(out, f'p_{want[f]}_{f:03d}.png'); bpy.ops.render.render(write_still=True)
    if '--save' in argv: bpy.ops.wm.save_mainfile()
