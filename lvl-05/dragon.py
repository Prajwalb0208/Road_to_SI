# LVL 05 mechanical dragon — built from scratch in Blender over MCP, in steps (each step is one live MCP call):
#   step_materials() · step_body() · step_rig() · step_set() · step_light_camera() · step_animate()
# Headless: blender -b --factory-startup --python dragon.py -- --steps all [--angles DIR] [--test DIR f1,f2] [--save F] [--pct N]
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
PH = os.environ.get('POLYHAVEN_DIR') or os.path.join(HERE, 'polyhaven')
scn = bpy.context.scene
def O(n): return bpy.data.objects[n]
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scn.collection.children: scn.collection.children.link(c)
    return c
def bsdf(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

# ================================================================ materials
def step_materials():
    def base(name):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree, bsdf(m)
    # weathered bronze: metal + green patina in a noise mask + darker grime
    m, nt, p = base('M_bronze')
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 12; nz.inputs['Roughness'].default_value = 0.65
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.58; rp.color_ramp.elements[1].position = 0.7
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (*lin('#8A5A2E'), 1); mix.inputs['B'].default_value = (*lin('#3E6B5A'), 1)
    nt.links.new(rp.outputs['Color'], mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; nt.links.new(rp.outputs['Color'], inv.inputs[1])
    nt.links.new(inv.outputs[0], p.inputs['Metallic'])                      # patina is not metallic
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.28; rr.inputs['To Max'].default_value = 0.7
    nt.links.new(nz.outputs['Fac'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], p.inputs['Roughness'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25; nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 40
    nt.links.new(tc.outputs['Object'], nz2.inputs['Vector']); nt.links.new(nz2.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    # obsidian armour plates
    m, nt, p = base('M_obsidian'); p.inputs['Base Color'].default_value = (*lin('#16120F'), 1); p.inputs['Metallic'].default_value = 0.7; p.inputs['Roughness'].default_value = 0.22
    try: p.inputs['Coat Weight'].default_value = 0.4
    except KeyError: pass
    # dark joints / inner mechanics
    m, nt, p = base('M_joint'); p.inputs['Base Color'].default_value = (*lin('#2A2420'), 1); p.inputs['Metallic'].default_value = 0.9; p.inputs['Roughness'].default_value = 0.45
    # ember emission (eyes, seams) and the core — strength keyed by the animation
    for name, hx in (('M_ember', '#FF5A12'), ('M_core', '#FFB040')):
        m, nt, p = base(name); p.inputs['Base Color'].default_value = (0, 0, 0, 1)
        p.inputs['Emission Color'].default_value = (*lin(hx), 1); p.inputs['Emission Strength'].default_value = 0.0
    # stone (Poly Haven CC0)
    for name, folder, sc in (('M_stone', 'rock_face_03', 0.35), ('M_floor', 'aerial_grass_rock', 0.12)):
        m, nt, p = base(name); tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (sc, sc, sc)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); d = os.path.join(PH, folder)
        def tex(suf, nc=False):
            f = next((x for x in os.listdir(d) if suf in x), None)
            if not f: return None
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(d, f), check_existing=True); t.projection = 'BOX'; t.projection_blend = 0.3
            if nc: t.image.colorspace_settings.name = 'Non-Color'
            nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); return t
        td, tr, tn = tex('_diff_'), tex('_rough_', True), tex('_nor_gl_', True)
        if td: nt.links.new(td.outputs['Color'], p.inputs['Base Color'])
        if tr: nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
        if tn: nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    m, nt, p = base('M_ember_edge'); p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin('#FF5A12'), 1); p.inputs['Emission Strength'].default_value = 0.0
    m, nt, p = base('M_dust'); p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin('#FFE2B8'), 1); p.inputs['Emission Strength'].default_value = 1.5
    m, nt, p = base('M_spark'); p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin('#FF7A1A'), 1); p.inputs['Emission Strength'].default_value = 12
    return 'materials: bronze+patina, obsidian, joint, ember, core, stone, floor, dust, spark'

M = lambda n: bpy.data.materials[n]

# ================================================================ geometry helpers
def mesh_obj(name, bm, mat, smooth=True, cname='dragon'):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); coll(cname).objects.link(o)
    if mat: me.materials.append(M(mat))
    for f in me.polygons: f.use_smooth = smooth
    return o
def bevel(o, w=0.03, seg=3):
    b = o.modifiers.new('bevel', 'BEVEL'); b.width = w; b.segments = seg; b.limit_method = 'ANGLE'
    o.modifiers.new('wn', 'WEIGHTED_NORMAL').keep_sharp = True
    return o
def box(name, size, mat, loc=(0, 0, 0), rot=None, bev=0.03, taper=None, cname='dragon'):
    """bevelled box (size = full dims). taper=(sx, sz): scale of the +Y end face (tapered plates/wedges)"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        if taper and v.co.y > 0: v.co.x *= taper[0]; v.co.z *= taper[1]
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    o = mesh_obj(name, bm, mat, False, cname); o.location = loc
    if rot is not None: o.rotation_euler = rot
    return bevel(o, bev)
def cyl(name, r, depth, mat, seg=16, loc=(0, 0, 0), rot=None, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    o = mesh_obj(name, bm, mat, True); o.location = loc
    if rot is not None: o.rotation_euler = rot
    return bevel(o, min(r, depth) * 0.15, 2)
def ball(name, r, mat, loc, scale=(1, 1, 1), seg=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    o = mesh_obj(name, bm, mat, True); o.location = loc; o.scale = scale; return o
def along(o, a, b):
    """orient an object's local +Y from a to b, placed at the midpoint"""
    a, b = Vector(a), Vector(b); d = b - a
    o.location = (a + b) / 2; o.rotation_euler = d.to_track_quat('Y', 'Z').to_euler(); return o

# ================================================================ skeleton layout (rest pose = standing, wings spread)
NECK = [(0, -0.85, 1.55), (0, -1.15, 1.9), (0, -1.38, 2.25), (0, -1.58, 2.55), (0, -1.82, 2.8), (0, -2.08, 2.95), (0, -2.32, 3.02)]
TAIL = [(0, 1.0, 1.28), (0, 1.55, 1.15), (0, 2.1, 1.0), (0, 2.65, 0.86), (0, 3.2, 0.72), (0, 3.75, 0.6), (0, 4.3, 0.5), (0, 4.8, 0.43), (0, 5.25, 0.38)]
LEGS = {'FL': [(-0.5, -0.55, 1.3), (-0.66, -0.78, 0.72), (-0.62, -0.62, 0.18), (-0.62, -0.95, 0.06)],
        'BL': [(-0.52, 0.85, 1.22), (-0.68, 0.5, 0.68), (-0.64, 0.95, 0.2), (-0.64, 0.62, 0.06)]}
for k in list(LEGS): LEGS[k.replace('L', 'R')] = [(-x, y, z) for x, y, z in LEGS[k]]
WING = {'L': [(-0.42, -0.35, 1.78), (-1.2, -0.1, 2.75), (-2.1, 0.35, 3.55)]}
def fan_dir(s, ang):
    """feather direction in a fan plane tilted up ~35 deg (V-shaped raised wings, never edge-on to a low camera)"""
    u = Vector((s * 0.82, 0.15, 0.55)).normalized(); w = Vector((s * 0.25, 0.45, -0.86)).normalized()
    return (math.cos(math.radians(ang)) * u + math.sin(math.radians(ang)) * w).normalized()
def fan_normal(s):
    u = Vector((s * 0.82, 0.15, 0.55)).normalized(); w = Vector((s * 0.25, 0.45, -0.86)).normalized(); n = u.cross(w).normalized()
    return n if n.y < 0 else -n          # blade faces forward (towards the camera side)
WING['R'] = [(-x, y, z) for x, y, z in WING['L']]
FEATHERS = [(8, 2.3), (24, 2.25), (40, 2.15), (56, 2.0), (72, 1.8), (88, 1.55), (104, 1.3), (120, 1.05)]   # (angle from outward, length)

PARTS = []      # (object, bone) — parented after the rig exists
def part(o, bone): PARTS.append((o.name, bone)); return o

def shell(name, width, length, thick, angle, mat, segs=28):
    """curved armour shell: a plate (width along local X, length along Y) bent around local Y (apex at the origin, arcs down)"""
    bm = bmesh.new(); ang = math.radians(angle); R = width / ang
    for j in range(segs + 1):
        th = (j / segs - 0.5) * ang                     # bend in the vertices (SimpleDeform barely bent this mesh)
        for i in range(5):
            bm.verts.new((R * math.sin(th), (i / 4 - 0.5) * length, R * (math.cos(th) - 1)))
    bm.verts.ensure_lookup_table()
    for j in range(segs):
        for i in range(4):
            a = j * 5 + i; bm.faces.new((bm.verts[a], bm.verts[a + 5], bm.verts[a + 6], bm.verts[a + 1]))
    o = mesh_obj(name, bm, mat, True)
    s = o.modifiers.new('thick', 'SOLIDIFY'); s.thickness = thick; s.offset = -1
    bv = o.modifiers.new('bevel', 'BEVEL'); bv.width = thick * 0.4; bv.segments = 2; bv.limit_method = 'ANGLE'
    o.modifiers.new('wn', 'WEIGHTED_NORMAL').keep_sharp = True
    return o
def orient(o, a, b, up_off=0.0):
    """local Y along a->b, local Z up; origin at the midpoint shifted up_off along local Z"""
    a, b = Vector(a), Vector(b); d = (b - a).normalized()
    q = d.to_track_quat('Y', 'Z'); o.rotation_euler = q.to_euler()
    o.location = (a + b) / 2 + (q @ Vector((0, 0, 1))) * up_off; return o
def orient_up(o, a, b, upv, off=0.0):
    """local Y along a->b, local Z towards upv (projected); origin at midpoint + off along local Z"""
    a, b = Vector(a), Vector(b); y = (b - a).normalized(); z = (Vector(upv) - Vector(upv).dot(y) * y).normalized(); x = y.cross(z)
    o.rotation_euler = Matrix((x, y, z)).transposed().to_euler(); o.location = (a + b) / 2 + z * off; return o
def loft(name, sections, mat, n=10):
    """skull/jaw: loft of rounded-octagon cross sections [(y, half_w, top, bottom)] along -Y"""
    bm = bmesh.new(); rings = []
    for y, w, t, bo in sections:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n; cx, cz = math.cos(a), math.sin(a)
            z = (t if cz > 0 else -bo) * abs(cz) ** 0.8 * (1 if cz > 0 else -1) * -1 if False else (t * cz if cz > 0 else bo * cz)
            ring.append(bm.verts.new((w * (abs(cx) ** 0.75) * (1 if cx >= 0 else -1), y, z)))
        rings.append(ring)
    for r in range(len(rings) - 1):
        for k in range(n):
            bm.faces.new((rings[r][k], rings[r][(k + 1) % n], rings[r + 1][(k + 1) % n], rings[r + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, mat, True)
    sd = o.modifiers.new('sub', 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
    return o
def horn(name, base, direction, length, r, bend_deg, mat):
    o = cyl(name, r, length, mat, 12, r2=0.0)
    for m in list(o.modifiers): o.modifiers.remove(m)
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01], cuts=10); bm.to_mesh(me); bm.free()
    for v in me.vertices: v.co.z += length / 2
    b = o.modifiers.new('bend', 'SIMPLE_DEFORM'); b.deform_method = 'BEND'; b.deform_axis = 'X'; b.angle = math.radians(bend_deg)
    o.location = base; o.rotation_euler = Vector(direction).to_track_quat('Z', 'Y').to_euler()
    for f in me.polygons: f.use_smooth = True
    return o

def step_body():
    random.seed(5)
    # --- torso: ellipsoid core + bent dorsal shells + side armour + chest shell around a glowing core
    part(ball('torso core', 1.0, 'M_joint', (0, 0.15, 1.3), scale=(0.5, 1.12, 0.46)), 'spine.chest')
    for i in range(6):
        y = -0.72 + i * 0.36; w = 1.55 - abs(i - 2.2) * 0.12
        sh = shell(f'back shell {i}', w, 0.42, 0.06, 165, 'M_bronze' if i == 2 else 'M_obsidian')
        sh.location = (0, y, 1.3 + 0.48 - abs(i - 2.2) * 0.02); sh.rotation_euler = (math.radians(-5), 0, 0)
        part(sh, 'spine.chest' if i < 3 else 'spine.pelvis')
        sp = cyl(f'back spike {i}', 0.08, 0.36 - abs(i - 2) * 0.03, 'M_obsidian', 6, r2=0.0)
        sp.location = (0, y + 0.05, 1.86 - abs(i - 2.2) * 0.02); sp.rotation_euler = (math.radians(-35), 0, 0); part(sp, 'spine.chest' if i < 3 else 'spine.pelvis')
    chest = shell('chest shell', 1.25, 0.55, 0.07, 150, 'M_bronze'); chest.location = (0, -0.95, 1.2); chest.rotation_euler = (math.radians(-80), 0, 0); part(chest, 'spine.chest')
    part(ball('core', 0.17, 'M_core', (0, -1.0, 1.18)), 'spine.chest')
    for k, a in enumerate((-50, -25, 0, 25, 50)):
        rb = cyl(f'cage rib {k}', 0.022, 0.5, 'M_bronze', 8); rb.location = (math.sin(math.radians(a)) * 0.22, -1.12, 1.18); part(rb, 'spine.chest')
    belly = shell('belly shell', 0.9, 1.6, 0.05, 90, 'M_bronze'); belly.location = (0, 0.15, 0.88); belly.rotation_euler = (0, math.radians(180), 0); part(belly, 'spine.chest')
    # --- neck: joints + dorsal bent shells + side guards + ember seams + spikes (dorsal: +n)
    for i in range(len(NECK) - 1):
        a, b = Vector(NECK[i]), Vector(NECK[i + 1]); r = 0.27 - i * 0.02; L = (b - a).length
        j = cyl(f'neck joint {i}', r * 0.72, L * 0.92, 'M_joint', 16); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, f'neck.{i}')
        sh = shell(f'neck shell {i}', r * 3.2, L * 1.02, 0.045, 190, 'M_bronze' if i == 5 else 'M_obsidian'); orient(sh, a, b, r * 0.92); part(sh, f'neck.{i}')
        bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=24, radius=r * 0.8)
        seam = mesh_obj(f'neck seam {i}', bm, 'M_ember'); sol = seam.modifiers.new('w', 'SOLIDIFY'); sol.thickness = 0.035
        seam.location = a; seam.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(seam, f'neck.{i}')
        q = (b - a).normalized().to_track_quat('Y', 'Z'); up = q @ Vector((0, 0, 1))
        sp = cyl(f'neck spike {i}', 0.07 - i * 0.006, 0.34 - i * 0.025, 'M_obsidian', 6, r2=0.0)
        sp.location = (a + b) / 2 + up * (r * 0.95 + 0.14); sp.rotation_euler = (up + (b - a).normalized() * -0.6).normalized().to_track_quat('Z', 'Y').to_euler(); part(sp, f'neck.{i}')
    # --- head: lofted skull + jaw, brow shells, curved horns, ember eyes + mouth glow
    h0 = Vector(NECK[-1])
    skull = loft('skull', [(0.1, 0.27, 0.26, 0.2), (-0.2, 0.32, 0.3, 0.18), (-0.5, 0.25, 0.22, 0.12), (-0.85, 0.17, 0.14, 0.08), (-1.1, 0.1, 0.07, 0.05), (-1.18, 0.05, 0.03, 0.03)], 'M_bronze')
    skull.location = h0 + Vector((0, 0, 0.02)); part(skull, 'head')
    jaw = loft('jaw', [(0.0, 0.22, 0.05, 0.1), (-0.4, 0.2, 0.05, 0.09), (-0.8, 0.13, 0.04, 0.06), (-1.05, 0.07, 0.03, 0.03)], 'M_bronze')
    jaw.location = h0 + Vector((0, -0.05, -0.2)); part(jaw, 'jaw')
    for s in (-1, 1):
        S = 'LR'[s > 0]
        brow = shell(f'brow {S}', 0.32, 0.55, 0.035, 70, 'M_obsidian'); brow.location = h0 + Vector((s * 0.2, -0.38, 0.27)); brow.rotation_euler = (math.radians(-12), s * math.radians(25), 0); part(brow, 'head')
        cheek = shell(f'cheek {S}', 0.3, 0.5, 0.03, 60, 'M_obsidian'); cheek.location = h0 + Vector((s * 0.29, -0.2, 0.0)); cheek.rotation_euler = (0, s * math.radians(80), 0); part(cheek, 'head')
        part(ball(f'eye {S}', 0.06, 'M_ember', h0 + Vector((s * 0.235, -0.48, 0.17)), scale=(0.55, 1.7, 0.5)), 'head')
        part(horn(f'horn {S}', h0 + Vector((s * 0.17, 0.0, 0.3)), (s * 0.3, 1.0, 0.55), 0.95, 0.075, -55 * s * 0 - 55, 'M_obsidian'), 'head')
        part(horn(f'horn small {S}', h0 + Vector((s * 0.27, -0.1, 0.18)), (s * 0.75, 0.8, 0.25), 0.5, 0.045, -40, 'M_obsidian'), 'head')
        for t in range(4):
            tt = cyl(f'tooth {S}{t}', 0.024, 0.11, 'M_bronze', 6, r2=0.0); tt.location = h0 + Vector((s * (0.14 - t * 0.025), -0.45 - t * 0.17, -0.1)); tt.rotation_euler = (math.radians(180), 0, 0); part(tt, 'head')
    mouth = box('mouth glow', (0.16, 0.5, 0.02), 'M_ember', bev=0.01); mouth.location = h0 + Vector((0, -0.45, -0.15)); part(mouth, 'jaw')
    # --- tail: joints + dorsal shells + spikes + blade
    for i in range(len(TAIL) - 1):
        a, b = Vector(TAIL[i]), Vector(TAIL[i + 1]); r = 0.3 - i * 0.03; L = (b - a).length
        j = cyl(f'tail joint {i}', r * 0.7, L * 0.9, 'M_joint', 14); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, f'tail.{i}')
        sh = shell(f'tail shell {i}', r * 3.1, L * 1.0, 0.04, 185, 'M_obsidian'); orient(sh, a, b, r * 0.88); part(sh, f'tail.{i}')
        q = (b - a).normalized().to_track_quat('Y', 'Z'); up = q @ Vector((0, 0, 1))
        sp = cyl(f'tail spike {i}', 0.06 - i * 0.005, 0.28 - i * 0.022, 'M_obsidian', 6, r2=0.0); sp.location = (a + b) / 2 + up * (r * 0.9 + 0.12)
        sp.rotation_euler = (up + (b - a).normalized() * 0.6).normalized().to_track_quat('Z', 'Y').to_euler(); part(sp, f'tail.{i}')
    tip = Vector(TAIL[-1]); fin = box('tail blade', (0.05, 1.0, 0.65), 'M_obsidian', bev=0.02, taper=(0.5, 0.05)); fin.location = tip + Vector((0, 0.4, 0.06)); part(fin, f'tail.{len(TAIL) - 2}')
    # --- legs: bigger pistons, bent armour, foot plates, claws
    for leg, P in LEGS.items():
        s = -1 if 'L' in leg else 1
        for i in range(3):
            a, b = Vector(P[i]), Vector(P[i + 1]); r = (0.2, 0.14, 0.11)[i]
            j = cyl(f'{leg} seg {i}', r, (a - b).length * 0.95, 'M_joint' if i == 1 else 'M_bronze', 16); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, f'leg.{leg}.{i}')
            if i < 2:
                ar = shell(f'{leg} armour {i}', r * 3.0, (a - b).length * 0.8, 0.04, 170, 'M_obsidian'); orient_up(ar, a, b, (s, -0.4 if 'F' in leg else 0.4, 0), r * 1.02); part(ar, f'leg.{leg}.{i}')
            part(ball(f'{leg} knuckle {i}', r * 1.1, 'M_bronze', b), f'leg.{leg}.{i}')
        foot = Vector(P[3]); fp = box(f'{leg} foot', (0.32, 0.36, 0.1), 'M_obsidian', foot + Vector((0, -0.05, 0.03)), bev=0.03, taper=(0.8, 0.6)); fp.rotation_euler.z = math.radians(180); part(fp, f'leg.{leg}.2')
        for c, dx in enumerate((-0.11, 0, 0.11)):
            cl = horn(f'{leg} claw {c}', foot + Vector((dx, -0.2, 0.05)), (0, -1, -0.25), 0.28, 0.045, 40, 'M_obsidian'); part(cl, f'leg.{leg}.2')
    # --- wings: arm bones + 8 wide overlapping blade-feathers with ember trailing edges
    for side, P in WING.items():
        s = -1 if side == 'L' else 1
        for i in range(2):
            a, b = Vector(P[i]), Vector(P[i + 1])
            j = cyl(f'wing {side} arm {i}', 0.09 - i * 0.02, (b - a).length, 'M_bronze', 12); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, f'wing.{side}.{i}')
            ar = shell(f'wing {side} arm plate {i}', 0.32, (b - a).length * 0.9, 0.03, 120, 'M_obsidian'); orient(ar, a, b, 0.08); part(ar, f'wing.{side}.{i}')
            part(ball(f'wing {side} knuckle {i}', 0.11 - i * 0.02, 'M_joint', b), f'wing.{side}.{i}')
        tip = Vector(P[2])
        for k, (ang, ln) in enumerate(FEATHERS):
            d = fan_dir(s, ang); nrm = fan_normal(s)
            fb = box(f'wing {side} feather {k}', (0.5, ln, 0.03), 'M_bronze', bev=0.012, taper=(0.3, 1.0))
            orient_up(fb, tip + d * 0.05, tip + d * ln, nrm, 0.012 * k); part(fb, f'wing.{side}.f{k}')
            edge = box(f'wing {side} feather edge {k}', (0.016, ln * 0.6, 0.035), 'M_ember_edge', bev=0.006); orient_up(edge, tip + d * 0.15, tip + d * ln * 0.88, nrm, 0.012 * k + 0.012)
            edge.location += d.cross(nrm).normalized() * 0.2; part(edge, f'wing.{side}.f{k}')
    return f'body: {len(PARTS)} parts'

# ================================================================ rig
def step_rig():
    arm = bpy.data.armatures.new('dragon_rig'); rig = bpy.data.objects.new('dragon_rig', arm); coll('dragon').objects.link(rig)
    rig.show_in_front = True; arm.display_type = 'OCTAHEDRAL'
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.selected_objects: o.select_set(False)
    rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
    def B(n, h, t, par=None, conn=False):
        b = eb.new(n); b.head = h; b.tail = t
        if par: b.parent = eb[par]; b.use_connect = conn
        return b
    B('root', (0, 0, 0), (0, 0.6, 0))
    B('spine.pelvis', (0, 1.0, 1.3), (0, 0.15, 1.35), 'root'); B('spine.chest', (0, 0.15, 1.35), NECK[0], 'spine.pelvis', True)
    prev = 'spine.chest'
    for i in range(len(NECK) - 1): B(f'neck.{i}', NECK[i], NECK[i + 1], prev, i > 0); prev = f'neck.{i}'
    B('head', NECK[-1], Vector(NECK[-1]) + Vector((0, -0.7, -0.05)), prev, True)
    B('jaw', Vector(NECK[-1]) + Vector((0, -0.08, -0.15)), Vector(NECK[-1]) + Vector((0, -0.75, -0.25)), 'head')
    prev = 'spine.pelvis'
    for i in range(len(TAIL) - 1): B(f'tail.{i}', TAIL[i], TAIL[i + 1], prev, i > 0); prev = f'tail.{i}'
    for leg, P in LEGS.items():
        par = 'spine.chest' if 'F' in leg else 'spine.pelvis'
        for i in range(3): B(f'leg.{leg}.{i}', P[i], P[i + 1], par if i == 0 else f'leg.{leg}.{i - 1}', i > 0)
    for side, P in WING.items():
        s = -1 if side == 'L' else 1
        B(f'wing.{side}.0', P[0], P[1], 'spine.chest'); B(f'wing.{side}.1', P[1], P[2], f'wing.{side}.0', True)
        for k, (ang, ln) in enumerate(FEATHERS):
            d = fan_dir(s, ang)
            B(f'wing.{side}.f{k}', P[2], Vector(P[2]) + d * ln * 0.5, f'wing.{side}.1')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    for name, bone in PARTS:
        o = O(name); mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bone; o.matrix_world = mw
    for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
    return f'rig: {len(arm.bones)} bones, {len(PARTS)} parts parented'

# ================================================================ set: ruins
def step_set():
    random.seed(11)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=60, location=(0, 4, 0)); fl = bpy.context.object; fl.name = 'ruin floor'
    for c in list(fl.users_collection): c.objects.unlink(fl)
    coll('ruins').objects.link(fl); fl.data.materials.append(M('M_floor'))
    tx = bpy.data.textures.new('floor_noise', 'CLOUDS'); tx.noise_scale = 1.2
    dm = fl.modifiers.new('d', 'DISPLACE'); dm.texture = tx; dm.strength = 0.12; dm.mid_level = 0.7
    for f in fl.data.polygons: f.use_smooth = True
    def pillar(name, x, y, h, broken):
        drums = int(h / 0.9)
        for k in range(drums):
            r = 0.55 - k * 0.01
            o = cyl(f'{name} drum {k}', r, 0.86, 'M_stone', 20, loc=(x + random.uniform(-0.03, 0.03), y, 0.43 + k * 0.88)); o.rotation_euler.z = random.uniform(0, 3)
            for c in list(o.users_collection): c.objects.unlink(o)
            coll('ruins').objects.link(o)
            if broken and k == drums - 1:
                o.rotation_euler.x = math.radians(random.uniform(4, 12)); o.scale.z = random.uniform(0.4, 0.8)
        cap = box(f'{name} base', (1.4, 1.4, 0.3), 'M_stone', (x, y, 0.15), bev=0.04, cname='ruins')
    for i, (x, y, h, br) in enumerate([(-4.5, 3, 7.2, False), (4.6, 3.4, 5.4, True), (-5.2, 8, 6.3, True), (5.4, 8.5, 7.2, False), (-1.8, 11, 4.5, True), (2.6, 11.5, 7.2, False)]):
        pillar(f'pillar {i}', x, y, h, br)
    box('lintel', (5.0, 1.0, 0.8), 'M_stone', (4.0, 10, 7.6), rot=(0, math.radians(4), 0), bev=0.05, cname='ruins')
    box('back wall', (16, 1.2, 9), 'M_stone', (0, 14, 4.5), bev=0.1, cname='ruins')
    box('window cut', (2.4, 1.6, 4.0), 'M_joint', (1.0, 14, 5.5), bev=0.1, cname='ruins').hide_render = True
    for k in range(9):   # fallen blocks / rubble
        x = random.uniform(-6, 6); y = random.uniform(-3, 9)
        if abs(x) < 1.6 and -3 < y < 6: x += 3.2 * (1 if x >= 0 else -1)
        box(f'rubble {k}', (random.uniform(0.5, 1.4), random.uniform(0.5, 1.2), random.uniform(0.3, 0.7)), 'M_stone',
            (x, y, 0.2), rot=(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(0, 3)), bev=0.06, cname='ruins')
    # window hole: boolean the back wall so moonlight god-rays pour through
    bw = O('back wall'); b = bw.modifiers.new('window', 'BOOLEAN'); b.operation = 'DIFFERENCE'; b.object = O('window cut')
    return 'set: floor, 6 pillars, lintel, back wall + window, rubble'

# ================================================================ light, fog, camera
def step_light_camera():
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    try: scn.view_settings.view_transform = 'AgX'
    except TypeError: pass
    try: scn.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError: pass
    scn.eevee.taa_render_samples = 64; scn.render.use_motion_blur = True
    for a, v in (('use_raytracing', True), ('volumetric_tile_size', '4'), ('volumetric_samples', 96), ('volumetric_end', 60.0)):
        try: setattr(scn.eevee, a, v)
        except Exception: pass
    w = scn.world or bpy.data.worlds.new('World'); scn.world = w; w.use_nodes = True; nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (*lin('#0B1018'), 1); bg.inputs['Strength'].default_value = 0.6
    vol = nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value = 0.018; vol.inputs['Anisotropy'].default_value = 0.6
    vol.inputs['Color'].default_value = (*lin('#C9D6E8'), 1)
    nt.links.new(vol.outputs[0], next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD').inputs['Volume'])
    def light(name, kind, loc, target, energy, hexc, **kw):
        l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = lin(hexc)
        for k, v in kw.items(): setattr(l, k, v)
        o = bpy.data.objects.new(name, l); coll('light').objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
    light('moon', 'SPOT', (1.5, 22, 14), (0, 0, 0.5), 60000, '#9DB8E8', spot_size=math.radians(28), spot_blend=0.4, shadow_soft_size=0.3)
    light('rim', 'AREA', (-6, 6, 5), (0, 0, 2), 3500, '#8FB4E8', size=4)
    light('key', 'AREA', (-4.5, -6.5, 5.5), (0, -0.5, 1.6), 2600, '#FFD2A0', size=3)
    light('fill', 'AREA', (6, -8, 4), (0, 0, 1.5), 180, '#C8B8A0', size=6)
    core = light('core light', 'POINT', (0, -1.0, 1.15), (0, -2, 1.15), 0.0, '#FFA040', shadow_soft_size=0.15)
    core.parent = O('dragon_rig'); core.parent_type = 'BONE'; core.parent_bone = 'spine.chest'
    bpy.context.view_layer.update(); core.matrix_world = Matrix.Translation((0, -1.05, 1.15))
    eye = light('eye light', 'POINT', (0, -2.9, 3.1), (0, -3, 3.1), 0.0, '#FF6A20', shadow_soft_size=0.05)
    eye.parent = O('dragon_rig'); eye.parent_type = 'BONE'; eye.parent_bone = 'head'; bpy.context.view_layer.update(); eye.matrix_world = Matrix.Translation(Vector(NECK[-1]) + Vector((0, -0.75, 0.1)))
    # camera
    tgt = bpy.data.objects.new('cam target', None); coll('camera').objects.link(tgt)
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); coll('camera').objects.link(cam); scn.camera = cam
    cd.lens = 35; cd.dof.use_dof = True; cd.dof.focus_object = tgt; cd.dof.aperture_fstop = 2.2
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    cam.location = (5.5, -9.5, 2.2); tgt.location = (0, 0.5, 1.2)
    return 'light: moon god-rays + rim + fill + core/eye lights; fog; camera'

# ================================================================ animation: awakening (24 fps, 288 frames)
def _vl(): bpy.context.view_layer.update()
def aim(pb, d):
    """rotate a pose bone (armature space) so its Y axis points along world direction d"""
    Mx = pb.matrix.copy(); cur = (Mx.to_3x3() @ Vector((0, 1, 0))).normalized()
    R = cur.rotation_difference(Vector(d).normalized()).to_matrix()
    pb.matrix = Matrix.Translation(Mx.translation) @ (R @ Mx.to_3x3()).to_4x4(); _vl()
def chain_dirs(pts):
    return [(Vector(pts[i + 1]) - Vector(pts[i])) for i in range(len(pts) - 1)]
SLEEP = {}
def capture_sleep(rig):
    P = rig.pose.bones
    for pb in P: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    _vl()
    P['root'].matrix = Matrix.Translation((0, 0, -0.74)) @ P['root'].matrix; _vl()
    aim(P['spine.pelvis'], (0, -1, 0.05)); aim(P['spine.chest'], (0, -1, -0.02))
    neck = [(0, -0.85, 0.82), (0.12, -1.27, 0.7), (0.38, -1.6, 0.56), (0.72, -1.82, 0.42), (1.08, -1.92, 0.32), (1.43, -1.88, 0.27), (1.75, -1.72, 0.25)]
    for i, d in enumerate(chain_dirs(neck)): aim(P[f'neck.{i}'], d)
    aim(P['head'], (0.55, 0.83, -0.08))                                   # head lies on the floor, looking back along its body
    for i in range(len(TAIL) - 1):
        a = math.radians(18 + i * 21); aim(P[f'tail.{i}'], (math.sin(a), math.cos(a), -0.03))
    for leg in LEGS:
        s = -1 if 'L' in leg else 1
        if 'F' in leg: dirs = [(s * 0.3, -0.75, -0.6), (0, 0.95, -0.3), (0, -1, 0)]
        else: dirs = [(s * 0.3, 0.6, -0.75), (0, -0.95, -0.3), (0, -1, 0)]
        for i, d in enumerate(dirs): aim(P[f'leg.{leg}.{i}'], d)
    for side in 'LR':
        s = -1 if side == 'L' else 1
        aim(P[f'wing.{side}.0'], (s * 0.55, 0.8, 0.12)); aim(P[f'wing.{side}.1'], (s * 0.15, 0.98, -0.18))
        for k in range(len(FEATHERS)): aim(P[f'wing.{side}.f{k}'], (s * (0.12 + 0.02 * k), 1, -0.06 - 0.01 * k))
    for pb in P: SLEEP[pb.name] = (pb.rotation_quaternion.copy(), pb.location.copy())
GROUP = lambda n: ('root' if n in ('root', 'spine.pelvis', 'spine.chest') or n.startswith('leg') else 'neck' if n.startswith('neck') else 'head' if n in ('head', 'jaw')
                   else 'tail' if n.startswith('tail') else 'wing')
def set_mix(rig, w, f):
    """w: group -> 1 (asleep) .. 0 (awake rest); keyframe at frame f"""
    for pb in rig.pose.bones:
        q, loc = SLEEP[pb.name]; t = w.get(GROUP(pb.name), 0.0)
        if t >= 0: pb.rotation_quaternion = Quaternion((1, 0, 0, 0)).slerp(q, t)
        else: ax, an = q.to_axis_angle(); pb.rotation_quaternion = Quaternion(ax, an * t)      # overshoot past rest
        pb.location = loc * max(t, 0)
        pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('location', frame=f)
def emit_key(mat, f, v):
    p = bsdf(M(mat)); p.inputs['Emission Strength'].default_value = v; p.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
def light_key(name, f, v):
    l = O(name).data; l.energy = v; l.keyframe_insert('energy', frame=f)

def step_animate():
    from mathutils import Quaternion as _Q
    globals()['Quaternion'] = _Q
    rig = O('dragon_rig'); scn.render.fps = 24; scn.frame_start, scn.frame_end = 1, 288
    capture_sleep(rig)
    KEYS = [(1, dict(root=1, neck=1, head=1, tail=1, wing=1)), (52, dict(root=1, neck=1, head=1, tail=1, wing=1)),
            (78, dict(root=1, neck=0.86, head=0.8, tail=1, wing=1)),
            (104, dict(root=0.55, neck=0.62, head=0.55, tail=0.85, wing=1)),
            (132, dict(root=0.0, neck=0.36, head=0.3, tail=0.55, wing=0.95)),
            (162, dict(root=0.0, neck=0.0, head=0.0, tail=0.25, wing=0.55)),
            (188, dict(root=0.0, neck=0.0, head=0.0, tail=0.0, wing=-0.06)),      # slight overshoot past full spread
            (200, dict(root=0.0, neck=0.0, head=0.0, tail=0.0, wing=0.0))]
    for f, w in KEYS: set_mix(rig, w, f)
    P = rig.pose.bones
    # turn to camera + lean in (frames 205-288): aim head/neck tip at the camera position
    cam_pos = Vector((3.4, -7.2, 3.0))
    for f, lean in ((212, 1.0), (288, 1.0)):
        set_mix(rig, dict(root=0, neck=0, head=0, tail=0, wing=0), f)
        aim(P['neck.5'], (Vector(NECK[-1]) - Vector(NECK[-2])).normalized().lerp((cam_pos - Vector(NECK[-2])).normalized(), 0.35 * lean))
        aim(P['head'], (cam_pos - P['head'].head).normalized())
        for n in ('neck.5', 'head'): P[n].keyframe_insert('rotation_quaternion', frame=f)
    # jaw opens for the exhale (220-236)
    for f, deg in ((214, 0), (220, 22), (232, 22), (240, 0)):
        P['jaw'].rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(deg)); P['jaw'].keyframe_insert('rotation_quaternion', frame=f)
    # breathing: chest swell every 2 s
    for k, f in enumerate(range(1, 289, 24)):
        s = 1.0 + (0.025 if k % 2 else 0.0); P['spine.chest'].scale = (s, 1, s); P['spine.chest'].keyframe_insert('scale', frame=f)
    # ignition: eyes + seams flicker on, core pulses, lights follow
    for f, v in ((1, 0.0), (50, 0.0), (54, 4.0), (57, 0.4), (61, 6.0), (64, 1.2), (70, 8.0), (288, 8.0)): emit_key('M_ember', f, v)
    for f, v in ((1, 0.0), (150, 0.0), (175, 2.5), (288, 2.5)): emit_key('M_ember_edge', f, v)
    for f, v in ((1, 0.15), (24, 0.5), (48, 0.15), (60, 3.0), (66, 1.0), (74, 12.0), (288, 12.0)): emit_key('M_core', f, v)
    for f, v in ((1, 0.0), (60, 0.0), (74, 180.0), (288, 180.0)): light_key('core light', f, v)
    for f, v in ((1, 0.0), (66, 0.0), (74, 25.0), (288, 25.0)): light_key('eye light', f, v)
    # Bezier ease everywhere
    for fc in _curves(rig.animation_data.action):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    _particles()
    _camera_keys()
    return 'animation: sleep -> ignite -> rise -> wings unfold -> turn to camera -> exhale; 288 frames'
def _curves(a):
    if hasattr(a, 'fcurves') and len(a.fcurves): return list(a.fcurves)
    out = []
    for layer in getattr(a, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
def _droplet(name, mat, r):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    o = mesh_obj(name, bm, mat, True, 'fx'); o.location = (0, 0, -50); return o
def _particles():
    # dust motes drifting in the air (whole shot)
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 1, 0.3)); em = bpy.context.object; em.name = 'dust emitter'
    for c in list(em.users_collection): c.objects.unlink(em)
    coll('fx').objects.link(em); em.show_instancer_for_render = False; em.show_instancer_for_viewport = False
    ps = em.modifiers.new('dust', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = 900; st.frame_start = -200; st.frame_end = 288; st.lifetime = 600; st.normal_factor = 0.05; st.factor_random = 0.1
    st.effector_weights.gravity = -0.004; st.brownian_factor = 0.02; st.render_type = 'OBJECT'; st.instance_object = _droplet('fx dust', 'M_dust', 0.012)
    st.particle_size = 1.0; st.size_random = 0.7
    # exhale sparks from the mouth (frames 221-232)
    bpy.ops.mesh.primitive_circle_add(radius=0.08, fill_type='NGON', location=(0, 0, 0)); sp = bpy.context.object; sp.name = 'spark emitter'
    for c in list(sp.users_collection): c.objects.unlink(sp)
    coll('fx').objects.link(sp); sp.show_instancer_for_render = False; sp.show_instancer_for_viewport = False
    rig = O('dragon_rig'); sp.parent = rig; sp.parent_type = 'BONE'; sp.parent_bone = 'jaw'; _vl()
    sp.matrix_world = Matrix.Translation(Vector(NECK[-1]) + Vector((0, -1.12, -0.1))) @ Matrix.Rotation(math.radians(90), 4, 'X')
    ps = sp.modifiers.new('sparks', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = 420; st.frame_start = 221; st.frame_end = 232; st.lifetime = 30; st.lifetime_random = 0.6; st.normal_factor = 3.2; st.factor_random = 1.4
    st.effector_weights.gravity = 0.25; st.render_type = 'OBJECT'; st.instance_object = _droplet('fx spark', 'M_spark', 0.02); st.particle_size = 1.0; st.size_random = 0.8
def _camera_keys():
    cam, tgt = O('cam'), O('cam target')
    K = [(1, (4.4, -5.0, 0.75), (1.55, -1.75, 0.4)), (66, (3.9, -4.4, 0.7), (1.6, -1.8, 0.38)),        # low, on the sleeping head
         (130, (6.4, -8.6, 2.2), (0.2, -0.6, 1.6)), (195, (8.0, -10.2, 5.2), (0, 0.4, 2.4)),            # rise, then wide for the wings
         (288, (4.6, -8.4, 3.4), (0, -2.0, 2.7))]                                                         # push in on the head
    for f, c, t in K:
        cam.location = c; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)

ANGLES_RUN = False
if __name__ == '__main__' and '--steps' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    print('[dragon]', step_materials()); print('[dragon]', step_body()); print('[dragon]', step_rig())
    if 'all' in argv or 'set' in argv: print('[dragon]', step_set()); print('[dragon]', step_light_camera())
    if 'all' in argv: print('[dragon]', step_animate())
    if '--test' in argv:
        out = argv[argv.index('--test') + 1]; frames = [int(x) for x in argv[argv.index('--test') + 2].split(',')]
        for f in range(1, max(frames) + 1):
            scn.frame_set(f)
            if f in frames: scn.render.filepath = os.path.join(out, f't_{f:03d}.png'); bpy.ops.render.render(write_still=True)
    if '--pct' in argv: scn.render.resolution_percentage = int(argv[argv.index('--pct') + 1])
    if '--angles' in argv:
        out = argv[argv.index('--angles') + 1]
        if not scn.camera:
            cd = bpy.data.cameras.new('c'); c = bpy.data.objects.new('c', cd); scn.collection.objects.link(c); scn.camera = c
        l = bpy.data.lights.new('studio', 'SUN'); l.energy = 3; lo = bpy.data.objects.new('studio', l); scn.collection.objects.link(lo); lo.rotation_euler = (0.8, 0.2, 0.6)
        scn.render.resolution_x, scn.render.resolution_y = 1200, 800
        scn.world = scn.world or bpy.data.worlds.new('W'); scn.world.use_nodes = True
        next(n for n in scn.world.node_tree.nodes if n.type == 'BACKGROUND').inputs['Strength'].default_value = 0.4
        c = scn.camera
        for name, loc in (('front', (0, -9, 2.2)), ('side', (10, 1.2, 2.0)), ('threeq', (6.5, -7, 3.5)), ('top', (0.01, 1.2, 12))):
            c.location = loc; c.rotation_euler = (Vector((0, 1.2, 1.5)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); c.data.lens = 35
            scn.render.filepath = os.path.join(out, f'a_{name}.png'); bpy.ops.render.render(write_still=True)
    if '--save' in argv: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(argv[argv.index('--save') + 1]))
    print('[dragon] done')
