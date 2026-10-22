# LVL 05 mecha dragon v2 — hard-surface detail pass (owner reference: Zoids-style mecha; our own design: black-cherry red
# candy paint, gold internals, gunmetal frame, cyan glows). Reuses skeleton/rig/set/animation from dragon.py.
# Live (each MCP call reloads this file): exec(open(r'...\mecha.py').read()); then call ONE step:
#   m_materials() · m_kit_demo() · m_body() · m_rig() · m_close_up(path)
# Headless: blender -b --factory-startup --python mecha.py -- --steps body [--close DIR] [--save F]
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Quaternion

_W = os.environ.get('LVL05_DIR') or os.path.dirname(os.path.abspath(__file__))   # folder with these scripts
exec(open(os.path.join(_W, 'dragon.py'), encoding='utf-8').read().split('ANGLES_RUN = False')[0])

def part(o, bone):
    o['bone'] = bone; PARTS.append((o.name, bone)); return o          # bone also stored on the object: each MCP call starts fresh
# ================================================================ materials
def m_materials():
    step_materials()                                   # stone, floor, dust, spark, ember channels from v1
    def base(name):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
        for n in [n for n in nt.nodes if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL')]: nt.nodes.remove(n)
        return m, nt, bsdf(m)
    def coat(p, w=1.0, r=0.05):
        for k, v in (('Coat Weight', w), ('Coat Roughness', r)):
            try: p.inputs[k].default_value = v
            except KeyError: pass
    # black-cherry candy paint: deep cavities, metal flake, clear coat, chipped edges to bare steel
    m, nt, p = base('M_paint')
    ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.12
    cav = nt.nodes.new('ShaderNodeMix'); cav.data_type = 'RGBA'; cav.inputs['A'].default_value = (*lin('#14020A'), 1); cav.inputs['B'].default_value = (*lin('#7A0F2E'), 1)
    nt.links.new(ao.outputs['AO'], cav.inputs['Factor'])
    fn = nt.nodes.new('ShaderNodeTexNoise'); fn.inputs['Scale'].default_value = 900
    fl = nt.nodes.new('ShaderNodeMix'); fl.data_type = 'RGBA'; fl.blend_type = 'OVERLAY'; fl.inputs['Factor'].default_value = 0.22; fl.inputs['B'].default_value = (*lin('#FF7FA0'), 1)
    nt.links.new(cav.outputs['Result'], fl.inputs['A']); nt.links.new(fn.outputs['Color'], fl.inputs['Factor'])
    # edge wear: convex edges (AO "inside" on a short distance) x scratchy noise -> bare steel, not metallic paint
    ai = nt.nodes.new('ShaderNodeAmbientOcclusion'); ai.inside = True; ai.inputs['Distance'].default_value = 0.025
    tc = nt.nodes.new('ShaderNodeTexCoord'); wn = nt.nodes.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 28; wn.inputs['Detail'].default_value = 10
    nt.links.new(tc.outputs['Object'], wn.inputs['Vector'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; nt.links.new(ai.outputs['AO'], inv.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; nt.links.new(inv.outputs[0], mul.inputs[0]); nt.links.new(wn.outputs['Fac'], mul.inputs[1])
    wr = nt.nodes.new('ShaderNodeMapRange'); wr.inputs['From Min'].default_value = 0.32; wr.inputs['From Max'].default_value = 0.4; nt.links.new(mul.outputs[0], wr.inputs['Value'])
    wear = nt.nodes.new('ShaderNodeMix'); wear.data_type = 'RGBA'; wear.inputs['B'].default_value = (*lin('#9A9AA0'), 1)
    nt.links.new(fl.outputs['Result'], wear.inputs['A']); nt.links.new(wr.outputs['Result'], wear.inputs['Factor'])
    nt.links.new(wear.outputs['Result'], p.inputs['Base Color'])
    rgh = nt.nodes.new('ShaderNodeMapRange'); rgh.inputs['To Min'].default_value = 0.26; rgh.inputs['To Max'].default_value = 0.45; nt.links.new(wr.outputs['Result'], rgh.inputs['Value']); nt.links.new(rgh.outputs['Result'], p.inputs['Roughness'])
    p.inputs['Metallic'].default_value = 0.75; coat(p)
    # thin parts (feathers, feet): same paint without edge wear (AO-inside reads thin plates as 'all edge' -> white)
    if 'M_paint_clean' in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials['M_paint_clean'])
    mc = bpy.data.materials['M_paint'].copy(); mc.name = 'M_paint_clean'; nt2 = mc.node_tree
    wnode = next(n for n in nt2.nodes if n.type == 'MIX' and n.inputs['B'].default_value[0] > 0.3 and n.inputs['B'].default_value[0] == n.inputs['B'].default_value[1])
    for l in list(wnode.inputs['Factor'].links): nt2.links.remove(l)
    wnode.inputs['Factor'].default_value = 0.0
    # gold internals (brushed), gunmetal frame, chrome rods, rubber hoses
    for name, hx, mt, rg in (('M_gold', '#E3A53A', 1.0, 0.24), ('M_frame', '#2B2B31', 0.95, 0.42), ('M_chrome', '#D8D8DE', 1.0, 0.08), ('M_rubber', '#141416', 0.0, 0.6)):
        m, nt, p = base(name); p.inputs['Base Color'].default_value = (*lin(hx), 1); p.inputs['Metallic'].default_value = mt; p.inputs['Roughness'].default_value = rg
        if name == 'M_gold':
            an = nt.nodes.new('ShaderNodeTexNoise'); an.inputs['Scale'].default_value = 600; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08
            nt.links.new(an.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], p.inputs['Normal'])
    # glows -> cyan (eyes/visor, seams, strips, core); keyed channels keep their names
    for name, hx in (('M_ember', '#46D9E6'), ('M_ember_edge', '#46D9E6'), ('M_core', '#9FF3FF'), ('M_spark', '#7FE9FF')):
        m = bpy.data.materials[name]; pp = bsdf(m); pp.inputs['Emission Color'].default_value = (*lin(hx), 1)
    m, nt, p = base('M_strip'); p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin('#46D9E6'), 1); p.inputs['Emission Strength'].default_value = 5.0
    return 'materials: black-cherry candy paint (cavity, flake, clear coat, edge wear), gold, gunmetal, chrome, rubber, cyan glows'

# ================================================================ kitbash library
def k_piston(name, length, r, cname='dragon'):
    """piston along local +Y from the origin: gunmetal sleeve (55 %), chrome rod, gold end caps + collars"""
    bm = bmesh.new()
    def seg(r0, y0, y1, n=16):
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r0, depth=y1 - y0)
        bmesh.ops.rotate(bm, verts=g['verts'], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, 'X'))
        bmesh.ops.translate(bm, verts=g['verts'], vec=(0, (y0 + y1) / 2, 0)); return g['verts']
    vs = seg(r, 0.0, length * 0.55); vr = seg(r * 0.45, length * 0.5, length * 0.98)
    o = mesh_obj(name, bm, 'M_frame', True, cname)
    me = o.data; me.materials.append(M('M_chrome'))
    for f in me.polygons:
        if f.center.y > length * 0.56 and math.hypot(f.center.x, f.center.z) < r * 0.6: f.material_index = 1
    bevel(o, r * 0.12, 2)
    for y in (0.0, length * 0.55, length):
        c = cyl(f'{name} collar', r * (1.15 if y < length else 0.75), r * 0.5, 'M_gold', 16); c.parent = o; c.location = (0, y, 0); c.rotation_euler = (math.radians(90), 0, 0)
    return o
def k_gear(name, r, teeth, thick, mat='M_gold', hole=0.35):
    bm = bmesh.new(); n = teeth * 4; vs_t, vs_b = [], []
    for k in range(n):
        a = 2 * math.pi * k / n; rr = r if (k % 4) in (1, 2) else r * 0.86
        vs_t.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), thick / 2))); vs_b.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), -thick / 2)))
    bm.faces.new(vs_t); bm.faces.new(vs_b[::-1])
    for k in range(n): bm.faces.new((vs_b[k], vs_b[(k + 1) % n], vs_t[(k + 1) % n], vs_t[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, mat, False); bevel(o, thick * 0.12, 2)
    hub = cyl(f'{name} hub', r * hole, thick * 1.6, 'M_frame', 20); hub.parent = o
    for k in range(6):
        a = 2 * math.pi * k / 6; b_ = ball(f'{name} bolt {k}', r * 0.05, 'M_chrome', (r * 0.55 * math.cos(a), r * 0.55 * math.sin(a), thick * 0.55)); b_.parent = o
    return o
def k_turbine(name, r, mat_ring='M_chrome'):
    """cowl ring + 14 angled blades + gold hub (blades spin in the animation)"""
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=48, radius1=r, radius2=r, depth=r * 0.35)   # a tube (an edge-only circle can't be solidified: live-take fail)
    ring = mesh_obj(f'{name} cowl', bm, mat_ring, True); s = ring.modifiers.new('s', 'SOLIDIFY'); s.thickness = r * 0.12; s.offset = 0
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=48, radius=r * 0.98)
    lip = mesh_obj(f'{name} lip', bm, 'M_gold', True); s2 = lip.modifiers.new('s', 'SOLIDIFY'); s2.thickness = 0.03; lip.parent = ring; lip.location = (0, 0, r * 0.18)
    fan = bpy.data.objects.new(f'{name} fan', None); coll('dragon').objects.link(fan); fan.parent = ring
    for k in range(14):
        bl = box(f'{name} blade {k}', (0.05, r * 0.85, 0.012), 'M_frame', bev=0.004); bl.parent = fan
        a = 2 * math.pi * k / 14; bl.location = (math.cos(a) * r * 0.48, math.sin(a) * r * 0.48, 0); bl.rotation_euler = (0, math.radians(30), a - math.pi / 2)
    hub = ball(f'{name} hub', r * 0.22, 'M_gold', (0, 0, 0), scale=(1, 1, 0.6)); hub.parent = fan
    return ring, fan
def k_vent(name, w, h, slats=5):
    fr = box(f'{name} frame', (w, h, 0.04), 'M_frame', bev=0.008)
    for k in range(slats):
        s = box(f'{name} slat {k}', (w * 0.9, h / slats * 0.5, 0.02), 'M_gold', bev=0.004); s.parent = fr
        s.location = (0, -h / 2 + h / slats * (k + 0.5), 0.02); s.rotation_euler = (math.radians(35), 0, 0)
    return fr
def k_ribs(name, a, b, r, n, mat='M_gold', squash=1.0):
    """stack of ribbed rings from a to b (gold internals like an exposed spine/belly)"""
    a, b = Vector(a), Vector(b); objs = []
    for k in range(n):
        t = (k + 0.5) / n; c = a.lerp(b, t)
        rg = cyl(f'{name} {k}', r * (1 - 0.15 * abs(t - 0.5)), (b - a).length / n * 0.55, mat, 20)
        rg.location = c; rg.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); rg.scale = (1, squash, 1); objs.append(rg)
    return objs
def panels(name, width, length, thick, angle, splits, mat='M_paint', gap=0.035):
    """curved armour split into separate chamfered panels with real gaps (= panel lines, dark frame shows through)"""
    out = []; ang = math.radians(angle); R = width / ang; pa = ang / splits
    for s_ in range(splits):
        a0 = -ang / 2 + s_ * pa + gap / R / 2; a1 = a0 + pa - gap / R
        bm = bmesh.new(); seg = 8
        for j in range(seg + 1):
            th = a0 + (a1 - a0) * j / seg
            for i in range(3): bm.verts.new((R * math.sin(th), (i / 2 - 0.5) * (length - gap), R * (math.cos(th) - 1)))
        bm.verts.ensure_lookup_table()
        for j in range(seg):
            for i in range(2):
                q = j * 3 + i; bm.faces.new((bm.verts[q], bm.verts[q + 3], bm.verts[q + 4], bm.verts[q + 1]))
        o = mesh_obj(f'{name} {s_}', bm, mat, True); so = o.modifiers.new('t', 'SOLIDIFY'); so.thickness = thick; so.offset = -1
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = thick * 0.45; bv.segments = 2; bv.limit_method = 'ANGLE'; o.modifiers.new('wn', 'WEIGHTED_NORMAL').keep_sharp = True
        out.append(o)
    return out
def group_place(objs, a, b, upv, off):
    """place a set of objects built around the origin (local Y = along, Z = up) on segment a->b"""
    root = bpy.data.objects.new('grp', None); coll('dragon').objects.link(root)
    for o in objs: o.parent = root
    orient_up(root, a, b, upv, off); bpy.context.view_layer.update()
    for o in objs:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    bpy.data.objects.remove(root, do_unlink=True); return objs

def m_kit_demo():
    """show the kitbash library on a shelf in front of the camera (take 1 receipt), then removed by m_body()"""
    x0 = -3
    p = k_piston('kit piston', 1.0, 0.07); p.location = (x0, -3, 0.8); p.rotation_euler = (0, 0, math.radians(90))
    g = k_gear('kit gear', 0.35, 14, 0.08); g.location = (x0 + 1.3, -3, 0.8); g.rotation_euler = (math.radians(90), 0, 0)
    t, f = k_turbine('kit turbine', 0.4); t.location = (x0 + 2.6, -3, 0.8); t.rotation_euler = (math.radians(90), 0, 0)
    v = k_vent('kit vent', 0.5, 0.4); v.location = (x0 + 3.9, -3, 0.8); v.rotation_euler = (math.radians(90), 0, 0)
    for o in k_ribs('kit ribs', (x0 + 5.0, -3, 0.45), (x0 + 5.0, -3, 1.15), 0.2, 7): pass
    for o in panels('kit panel', 1.0, 0.6, 0.05, 120, 3):
        o.location = (x0 + 6.4, -3, 1.05); o.rotation_euler = (math.radians(70), 0, 0)
    return 'kitbash: piston, gear, turbine, vent, ribs, split armour panels'

# ================================================================ body
def m_body():
    for o in [o for o in bpy.data.objects if o.name.startswith('kit ') or 'bone' in o or 'detail' in o]: bpy.data.objects.remove(o, do_unlink=True)
    PARTS.clear(); random.seed(5)
    # --- torso frame + gold belly + panelled back + shoulder turbines + vents + hoses
    part(ball('torso frame', 1.0, 'M_frame', (0, 0.15, 1.3), scale=(0.46, 1.08, 0.42)), 'spine.chest')
    for o in k_ribs('belly rib', (0, -0.75, 0.98), (0, 1.0, 0.98), 0.36, 14, squash=0.5):
        o.rotation_euler = (math.radians(90), 0, 0); o.scale = (1.0, 0.5, 1); part(o, 'spine.chest' if o.location.y < 0.2 else 'spine.pelvis')
    for i in range(5):
        y = -0.66 + i * 0.4; w = 1.6 - abs(i - 2) * 0.12
        for o in panels(f'back panel {i}', w, 0.4, 0.05, 168, 3):
            o.location = (0, y, 1.78 - abs(i - 2) * 0.02); o.rotation_euler = (math.radians(-4), 0, 0); part(o, 'spine.chest' if i < 3 else 'spine.pelvis')
        st = box(f'back strip {i}', (0.04, 0.3, 0.02), 'M_strip', (0, y, 1.795 - abs(i - 2) * 0.02), bev=0.005); part(st, 'spine.chest' if i < 3 else 'spine.pelvis')
        fin = box(f'back fin {i}', (0.03, 0.34, 0.28), 'M_gold', (0, y + 0.04, 1.93), rot=(math.radians(-25), 0, 0), bev=0.008, taper=(1, 0.2)); part(fin, 'spine.chest' if i < 3 else 'spine.pelvis')
    for s in (-1, 1):
        S = 'LR'[s > 0]
        ring, fan = k_turbine(f'shoulder turbine {S}', 0.36); ring.location = (s * 0.5, -0.42, 1.42); ring.rotation_euler = (0, s * math.radians(90), 0); part(ring, 'spine.chest')
        fan.animation_data_create(); d = fan.driver_add('rotation_euler', 2); d.driver.expression = 'frame * 0.35'
        g = k_gear(f'shoulder gear {S}', 0.3, 16, 0.06); g.location = (s * 0.44, -0.42, 1.42); g.rotation_euler = (0, s * math.radians(90), 0); part(g, 'spine.chest')
        for k in range(3):
            v = k_vent(f'flank vent {S}{k}', 0.32, 0.26); v.location = (s * 0.47, 0.25 + k * 0.32, 1.25); v.rotation_euler = (0, s * math.radians(90), 0); part(v, 'spine.pelvis' if k else 'spine.chest')
        for i in range(4):
            y = -0.55 + i * 0.42
            for o in panels(f'side panel {S}{i}', 0.62, 0.38, 0.045, 60, 2):
                o.location = (s * 0.5, y, 1.32); o.rotation_euler = (0, s * math.radians(95), 0); part(o, 'spine.chest' if i < 2 else 'spine.pelvis')
    chest = panels('chest plate', 1.0, 0.5, 0.06, 140, 3)
    for o in chest: o.location = (0, -1.0, 1.22); o.rotation_euler = (math.radians(-80), 0, 0); part(o, 'spine.chest')
    part(ball('core', 0.15, 'M_core', (0, -1.0, 1.16)), 'spine.chest')
    for k, a in enumerate((-45, -15, 15, 45)):
        rb = cyl(f'cage rib {k}', 0.02, 0.42, 'M_gold', 8); rb.location = (math.sin(math.radians(a)) * 0.18, -1.13, 1.16); part(rb, 'spine.chest')
    # --- neck: gunmetal core + gold ribbed throat + red dorsal panels + cables + gold crest fins + cyan seams
    for i in range(len(NECK) - 1):
        a, b = Vector(NECK[i]), Vector(NECK[i + 1]); r = 0.25 - i * 0.017; L = (b - a).length; bn = f'neck.{i}'
        q = (b - a).normalized().to_track_quat('Y', 'Z'); up = q @ Vector((0, 0, 1)); fw = (b - a).normalized()
        j = cyl(f'neck core {i}', r * 0.62, L * 0.95, 'M_frame', 16); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, bn)
        for o in k_ribs(f'neck throat {i}', a - up * r * 0.45, b - up * r * 0.45, r * 0.62, 4, squash=1.0): part(o, bn)
        for o in group_place(panels(f'neck panel {i}', r * 3.0, L * 0.98, 0.04, 175, 2), a, b, up, r * 0.9): part(o, bn)
        for s in (-1, 1):
            side = up.cross(fw).normalized() * s
            cb = cyl(f'neck cable {i}{"LR"[s > 0]}', r * 0.13, L * 1.02, 'M_rubber', 10); cb.location = (a + b) / 2 + side * r * 0.75; cb.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(cb, bn)
            cl = cyl(f'neck clamp {i}{"LR"[s > 0]}', r * 0.17, L * 0.12, 'M_gold', 10); cl.location = (a + b) / 2 + side * r * 0.75; cl.rotation_euler = cb.rotation_euler; part(cl, bn)
        fin = box(f'neck fin {i}', (0.03, L * 0.8, 0.26 - i * 0.02), 'M_gold', bev=0.006, taper=(1, 0.15)); orient_up(fin, a, b, up, r * 1.0 + 0.12); fin.rotation_euler.rotate_axis('X', math.radians(-20)); part(fin, bn)
        bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=24, radius=r * 0.66)
        seam = mesh_obj(f'neck seam {i}', bm, 'M_ember'); so = seam.modifiers.new('w', 'SOLIDIFY'); so.thickness = 0.03
        seam.location = a; seam.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(seam, bn)
    # --- head: gunmetal skull + layered red armour + cyan visor + gold teeth/horns/crest + nose vents
    h0 = Vector(NECK[-1])
    skull = loft('skull core', [(0.12, 0.3, 0.3, 0.2), (-0.2, 0.35, 0.34, 0.2), (-0.5, 0.29, 0.26, 0.15), (-0.8, 0.2, 0.17, 0.1), (-1.02, 0.11, 0.09, 0.06)], 'M_frame')   # v3: heavier, shorter snout
    skull.location = h0 + Vector((0, 0, 0.02)); part(skull, 'head')
    JAW = [(0.0, 0.26, 0.04, 0.14), (-0.4, 0.23, 0.08, 0.12), (-0.75, 0.15, 0.11, 0.07), (-0.95, 0.08, 0.1, 0.04)]   # v4: top follows the skull underside -> no gap when closed
    jawc = loft('jaw core', JAW, 'M_frame')
    jawc.location = h0 + Vector((0, -0.05, -0.17))
    def jaw_w(y):                                     # jaw half-width at head-local y
        y += 0.05
        for (y0, w0, *_), (y1, w1, *_) in zip(JAW, JAW[1:]):
            if y1 <= y <= y0: return w0 + (w1 - w0) * (y - y0) / (y1 - y0)
        return JAW[-1][1]
    part(jawc, 'jaw')
    # head armour: thin subdivided sheets SHRINKWRAPPED onto the skull/jaw so they hug the shape (v1: flat floating slabs)
    def hp(name, center, normal, along_, w, h, mat='M_paint', bone='head', target='skull core', off=0.012, thick=0.035, taper=0.75):
        bm = bmesh.new(); n = 10
        for j in range(n + 1):
            for i in range(n + 1):
                v = j / n - 0.5; k = 1 - (1 - taper) * (j / n)                     # taper towards the +along end
                bm.verts.new(((i / n - 0.5) * w * k, v * h, 0))
        bm.verts.ensure_lookup_table()
        for j in range(n):
            for i in range(n):
                q = j * (n + 1) + i; bm.faces.new((bm.verts[q], bm.verts[q + 1], bm.verts[q + n + 2], bm.verts[q + n + 1]))
        o = mesh_obj(name, bm, mat, True)
        z = Vector(normal).normalized(); y = (Vector(along_) - Vector(along_).dot(z) * z).normalized(); x = y.cross(z)
        o.rotation_euler = Matrix((x, y, z)).transposed().to_euler(); o.location = h0 + Vector(center)
        sw = o.modifiers.new('wrap', 'SHRINKWRAP'); sw.target = O(target); sw.wrap_method = 'NEAREST_SURFACEPOINT'; sw.wrap_mode = 'OUTSIDE_SURFACE'; sw.offset = off
        so = o.modifiers.new('t', 'SOLIDIFY'); so.thickness = thick; so.offset = 1
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = thick * 0.4; bv.segments = 2; bv.limit_method = 'ANGLE'
        part(o, bone); return o
    up, fwd = (0, 0, 1), (0, -1, 0)
    hp('snout plate', (0, -0.75, 0.15), up, fwd, 0.36, 0.5, thick=0.05, taper=0.55)
    hp('nose tip', (0, -1.0, 0.06), (0, -0.6, 0.8), fwd, 0.16, 0.16, taper=0.6)
    for k, (y, w) in enumerate(((-0.5, 0.42), (-0.22, 0.5), (0.05, 0.5), (0.3, 0.42))):
        hp(f'crest plate {k}', (0, y, 0.36), up, fwd, w * 1.2, 0.25, thick=0.05, taper=0.85)
    for s in (-1, 1):
        S = 'LR'[s > 0]; side = (s, 0, 0)
        hp(f'brow {S}', (s * 0.24, -0.45, 0.24), (s * 0.6, 0, 0.8), fwd, 0.2, 0.46, thick=0.07, taper=0.5)
        hp(f'skull guard {S}', (s * 0.32, 0.0, 0.15), (s * 0.8, 0, 0.5), fwd, 0.22, 0.42, thick=0.05, taper=0.8)
        hp(f'cheek {S}', (s * 0.36, -0.2, -0.03), side, fwd, 0.2, 0.55, thick=0.05, taper=0.7)
        hp(f'jaw plate {S}', (s * 0.26, -0.45, -0.28), (s, 0, -0.3), fwd, 0.15, 0.75, thick=0.05, bone='jaw', target='jaw core', taper=0.5)
        hp(f'visor {S}', (s * 0.3, -0.5, 0.13), (s, -0.25, 0.15), fwd, 0.085, 0.4, mat='M_ember', off=0.06, thick=0.025, taper=0.55)
        part(horn(f'horn {S}', h0 + Vector((s * 0.15, 0.05, 0.3)), (s * 0.28, 1.0, 0.5), 1.0, 0.075, -50, 'M_gold'), 'head')
        part(horn(f'horn small {S}', h0 + Vector((s * 0.25, -0.12, 0.2)), (s * 0.8, 0.7, 0.3), 0.45, 0.045, -35, 'M_gold'), 'head')
        v = k_vent(f'nose vent {S}', 0.14, 0.12, 3); v.location = h0 + Vector((s * 0.12, -0.88, 0.07)); v.rotation_euler = (0, s * math.radians(70), 0); part(v, 'head')
        for t in range(6):
            tt = cyl(f'tooth up {S}{t}', 0.02, 0.1, 'M_gold', 6, r2=0.0); y_ = -0.32 - t * 0.11; tt.location = h0 + Vector((s * (jaw_w(y_) + 0.02), y_, -0.15)); tt.rotation_euler = (math.radians(180), 0, 0); part(tt, 'head')
            tl = cyl(f'tooth lo {S}{t}', 0.018, 0.085, 'M_gold', 6, r2=0.0); y_ = -0.37 - t * 0.1; tl.location = h0 + Vector((s * jaw_w(y_) * 0.7, y_, -0.15)); part(tl, 'jaw')
    mouth = box('mouth glow', (0.12, 0.45, 0.015), 'M_ember', bev=0.005); mouth.location = h0 + Vector((0, -0.45, -0.13)); part(mouth, 'jaw')
    # --- tail
    for i in range(len(TAIL) - 1):
        a, b = Vector(TAIL[i]), Vector(TAIL[i + 1]); r = 0.27 - i * 0.026; L = (b - a).length; bn = f'tail.{i}'
        q = (b - a).normalized().to_track_quat('Y', 'Z'); up = q @ Vector((0, 0, 1))
        j = cyl(f'tail core {i}', r * 0.6, L * 0.95, 'M_frame', 14); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, bn)
        for o in group_place(panels(f'tail panel {i}', r * 3.0, L * 0.98, 0.035, 175, 2), a, b, up, r * 0.86): part(o, bn)
        for o in k_ribs(f'tail rib {i}', a - up * r * 0.4, b - up * r * 0.4, r * 0.58, 3): part(o, bn)
        fin = box(f'tail fin {i}', (0.025, L * 0.8, 0.22 - i * 0.018), 'M_gold', bev=0.006, taper=(1, 0.15)); orient_up(fin, a, b, up, r * 0.95 + 0.1); fin.rotation_euler.rotate_axis('X', math.radians(25)); part(fin, bn)
    tip = Vector(TAIL[-1])
    for s in (-1, 0, 1):
        bl = box(f'tail blade {s}', (0.04, 0.95, 0.5 if s == 0 else 0.3), 'M_paint' if s == 0 else 'M_gold', bev=0.01, taper=(0.5, 0.05))
        bl.location = tip + Vector((s * 0.12, 0.38, 0.05)); bl.rotation_euler = (0, s * math.radians(55), 0); part(bl, f'tail.{len(TAIL) - 2}')
    # --- legs: armour panels, gold knee caps, claws with 3 segments (pistons are added in m_rig with Stretch-To)
    for leg, P in LEGS.items():
        s = -1 if 'L' in leg else 1
        for i in range(3):
            a, b = Vector(P[i]), Vector(P[i + 1]); r = (0.26, 0.19, 0.13)[i]; bn = f'leg.{leg}.{i}'
            j = cyl(f'{leg} bone {i}', r * 0.7, (a - b).length * 0.96, 'M_frame', 14); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, bn)
            if i < 2:
                for o in group_place(panels(f'{leg} armour {i}', r * 3.4, (a - b).length * 0.85, 0.06, 200, 2), a, b, (s, -0.5 if 'F' in leg else 0.5, 0), r * 1.0): part(o, bn)
                # v3 bulk: outer thigh/shin shell + gold calf ribs
                sh = shell(f'{leg} outer shell {i}', r * 2.6, (a - b).length * 0.78, 0.05, 150, 'M_paint'); orient_up(sh, a, b, (s, 0, 0.2), r * 1.2); part(sh, bn)
                for o in k_ribs(f'{leg} calf rib {i}', a.lerp(b, 0.15) + Vector((0, 0.35 if 'F' in leg else -0.35, 0)) * r, a.lerp(b, 0.85) + Vector((0, 0.35 if 'F' in leg else -0.35, 0)) * r, r * 0.75, 4): part(o, bn)
            kn = ball(f'{leg} knee {i}', r * 0.95, 'M_gold', b); part(kn, bn)
            if i < 2:                                 # v4 knee guard: curved plate on the outside of the bend (v3 cap pointed the wrong way)
                c_ = Vector(P[i + 2]); nk = (b - (a + c_) / 2); nk = nk.normalized() if nk.length > 1e-4 else Vector((0, -1, 0))
                cap = shell(f'{leg} knee guard {i}', r * 2.1, r * 2.3, 0.05, 120, 'M_paint'); orient_up(cap, b - Vector((0, 0, r)), b + Vector((0, 0, r)), nk, r * 0.85); part(cap, bn)
                bolt = ball(f'{leg} knee bolt {i}', r * 0.22, 'M_gold', b + nk * (r * 0.85 + 0.06)); part(bolt, bn)
        foot = Vector(P[3])
        fp = box(f'{leg} foot', (0.44, 0.48, 0.14), 'M_paint_clean', foot + Vector((0, -0.05, 0.05)), rot=(0, 0, math.radians(180)), bev=0.02, taper=(0.75, 0.6)); part(fp, f'leg.{leg}.2')
        for c, dx in enumerate((-0.15, 0, 0.15)):
            base = foot + Vector((dx, -0.27, 0.06))
            for k in range(3):
                seg_ = box(f'{leg} claw {c}{k}', (0.06 - k * 0.012, 0.12, 0.06 - k * 0.012), 'M_frame' if k < 2 else 'M_gold', bev=0.01)
                seg_.location = base + Vector((0, -0.11 * k, -0.015 * k * k)); seg_.rotation_euler = (math.radians(-12 * k), 0, 0); part(seg_, f'leg.{leg}.2')
            tipc = horn(f'{leg} talon {c}', base + Vector((0, -0.25, -0.035)), (0, -1, -0.45), 0.18, 0.03, 35, 'M_gold'); part(tipc, f'leg.{leg}.2')
    # --- wings: red armoured arms, gold knuckles, red feather panels with gunmetal spars + cyan edge strips
    for side, P in WING.items():
        s = -1 if side == 'L' else 1
        for i in range(2):
            a, b = Vector(P[i]), Vector(P[i + 1]); bn = f'wing.{side}.{i}'
            j = cyl(f'wing {side} bone {i}', 0.11 - i * 0.02, (b - a).length, 'M_frame', 14); j.location = (a + b) / 2; j.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(j, bn)
            for o in group_place(panels(f'wing {side} arm armour {i}', 0.6 - i * 0.12, (b - a).length * 0.88, 0.05, 160, 3), a, b, (0, 0, 1), 0.12 - i * 0.02): part(o, bn)
            # v3: lower shell + gold ribbed underside + cyan strip -> reads as an armoured limb, not a stick
            sh = shell(f'wing {side} arm shell {i}', 0.42 - i * 0.08, (b - a).length * 0.8, 0.045, 150, 'M_paint'); orient_up(sh, a, b, (s, 0, -0.6), 0.12 - i * 0.02); part(sh, bn)
            for o in k_ribs(f'wing {side} arm rib {i}', a.lerp(b, 0.12) - Vector((0, 0, 0.06)), a.lerp(b, 0.88) - Vector((0, 0, 0.06)), 0.1 - i * 0.02, 6): part(o, bn)
            st = box(f'wing {side} arm strip {i}', (0.03, (b - a).length * 0.6, 0.02), 'M_strip', bev=0.005); orient_up(st, a, b, (0, 0, 1), 0.18 - i * 0.03); part(st, bn)
            part(ball(f'wing {side} knuckle {i}', 0.15 - i * 0.03, 'M_gold', b), bn)
        tip = Vector(P[2])
        for k, (ang, ln) in enumerate(FEATHERS):
            d = fan_dir(s, ang); nrm = fan_normal(s); bn = f'wing.{side}.f{k}'
            fb = box(f'wing {side} feather {k}', (0.48, ln, 0.03), 'M_paint_clean', bev=0.01, taper=(0.3, 1.0)); orient_up(fb, tip + d * 0.05, tip + d * ln, nrm, 0.012 * k); part(fb, bn)
            sp = box(f'wing {side} spar {k}', (0.05, ln * 0.92, 0.05), 'M_frame', bev=0.01); orient_up(sp, tip + d * 0.05, tip + d * ln * 0.95, nrm, 0.012 * k + 0.03); part(sp, bn)
            ed = box(f'wing {side} feather edge {k}', (0.016, ln * 0.6, 0.035), 'M_ember_edge', bev=0.006); orient_up(ed, tip + d * 0.15, tip + d * ln * 0.88, nrm, 0.012 * k + 0.012)
            ed.location += d.cross(nrm).normalized() * 0.2; part(ed, bn)
    return f'mecha body: {len(PARTS)} parts'

# ================================================================ fierce face (v6): scowling slit eyes, brow blades, sabre fangs, cheek spikes, chin blade
def aimed(o, along, loc):
    """point an object's +Y along a direction (Z kept as up as far as possible) and place it"""
    o.rotation_euler = Vector(along).normalized().to_track_quat('Y', 'Z').to_euler(); o.location = loc; return o
def m_fierce():
    h0 = Vector(NECK[-1])
    for n in ('visor L', 'visor R'):
        if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    for s in (-1, 1):
        S = 'LR'[s > 0]
        # eye: dark recessed socket + narrow glowing slit, front end low and inboard -> a scowl, not a round 'friendly' visor
        part(aimed(box(f'eye socket {S}', (0.03, 0.5, 0.1), 'M_frame', bev=0.012, taper=(1, 0.45)), (-s * 0.2, -1, -0.3), h0 + Vector((s * 0.3, -0.47, 0.13))), 'head')
        part(aimed(box(f'eye slit {S}', (0.03, 0.42, 0.045), 'M_ember', bev=0.006, taper=(1, 0.35)), (-s * 0.2, -1, -0.3), h0 + Vector((s * 0.318, -0.47, 0.13))), 'head')
        # brow blade: heavy paint wedge overhanging the slit, angled down to the snout, gold edge on top
        part(aimed(box(f'brow blade {S}', (0.1, 0.56, 0.05), 'M_paint', bev=0.012, taper=(0.5, 0.6)), (-s * 0.25, -1, -0.42), h0 + Vector((s * 0.31, -0.42, 0.25))), 'head')
        part(aimed(box(f'brow edge {S}', (0.02, 0.5, 0.02), 'M_gold', bev=0.005, taper=(1, 0.5)), (-s * 0.25, -1, -0.42), h0 + Vector((s * 0.355, -0.41, 0.27))), 'head')
        # swept-back cheek spikes
        for k in range(3):
            part(horn(f'cheek spike {S}{k}', h0 + Vector((s * 0.36, -0.12 + k * 0.13, 0.02 - k * 0.05)), (s * 0.55, 1.0, 0.12 - k * 0.1), 0.36 - k * 0.07, 0.035 - k * 0.006, -28, 'M_gold'), 'head')
        # sabre fangs hang outside the closed jaw; lower tusks point up
        part(aimed(cyl(f'fang {S}', 0.034, 0.26, 'M_gold', 10, r2=0.0), (0, -0.25, -1), h0 + Vector((s * 0.21, -0.66, -0.2))), 'head')
        part(aimed(cyl(f'tusk {S}', 0.026, 0.15, 'M_gold', 10, r2=0.0), (0, -0.4, 1), h0 + Vector((s * 0.1, -0.86, -0.15))), 'jaw')
        part(aimed(box(f'jaw spike {S}', (0.03, 0.3, 0.08), 'M_frame', bev=0.008, taper=(0.4, 0.1)), (s * 0.5, 1, -0.4), h0 + Vector((s * 0.27, 0.05, -0.32))), 'jaw')
    part(aimed(box('nose blade', (0.035, 0.6, 0.1), 'M_gold', bev=0.008, taper=(0.5, 0.15)), (0, -1, -0.22), h0 + Vector((0, -0.6, 0.31))), 'head')
    part(aimed(box('chin blade', (0.04, 0.34, 0.12), 'M_paint', bev=0.01, taper=(0.5, 0.1)), (0, -1, -0.5), h0 + Vector((0, -0.78, -0.37))), 'jaw')
    part(ball('throat glow', 0.075, 'M_ember', h0 + Vector((0, -0.28, -0.1))), 'head')                       # lights the mouth when it opens
    return 'fierce face: scowling slit eyes in sockets, brow blades, cheek spikes, sabre fangs, tusks, nose + chin blades'

# ================================================================ micro details (v5): rivets, panel codes, hazard tabs, LEDs, hydraulic lines
CORE = Vector((0, -1.0, 1.16))
def _detail_mats():
    def flat(name, hx, mt, rg):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; p = bsdf(m)
        p.inputs['Base Color'].default_value = (*lin(hx), 1); p.inputs['Metallic'].default_value = mt; p.inputs['Roughness'].default_value = rg; return m
    flat('M_decal', '#E8E2D6', 0.0, 0.5)
    m = flat('M_hazard', '#F2B705', 0.2, 0.45); nt = m.node_tree                   # black/yellow chevrons from a banded wave
    for n in [n for n in nt.nodes if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL')]: nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.bands_direction = 'DIAGONAL'; wv.inputs['Scale'].default_value = 9
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'; cr.color_ramp.elements[0].color = (0.01, 0.01, 0.01, 1); cr.color_ramp.elements[1].position = 0.5; cr.color_ramp.elements[1].color = (*lin('#F2B705'), 1)
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], bsdf(m).inputs['Base Color'])
def _shared(name, make):
    me = bpy.data.meshes.get(name)
    if me: return me
    bm = bmesh.new(); mat = make(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M(mat))
    for f in me.polygons: f.use_smooth = True
    return me
def _rivet(bm):
    g = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.013, radius2=0.011, depth=0.008)        # hex bolt head
    bmesh.ops.translate(bm, verts=g['verts'], vec=(0, 0, 0.004)); return 'M_chrome'
def _led(bm):
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.009); return 'M_ember'
def _tab(bm):
    g = bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(0.03, 0.11, 0.004), verts=g['verts']); bmesh.ops.translate(bm, verts=g['verts'], vec=(0, 0, 0.002)); return 'M_hazard'
def stick(src, name, data, loc, nrm, along=(0, 1, 0), s=1.0):
    """detail glued to src's surface (src-local point + normal), parented to src so it rides along when the armour opens"""
    mw = src.matrix_world; z = (mw.to_3x3().inverted().transposed() @ Vector(nrm)).normalized(); y = mw.to_3x3() @ Vector(along)
    y = (y - y.dot(z) * z).normalized() if (y - y.dot(z) * z).length > 1e-5 else z.orthogonal().normalized(); x = y.cross(z)
    o = bpy.data.objects.new(name, data); coll('dragon').objects.link(o); o['detail'] = 1
    o.parent = src; o.matrix_world = Matrix.Translation(mw @ Vector(loc)) @ Matrix((x, y, z)).transposed().to_4x4() @ Matrix.Scale(s, 4); return o
def m_details():
    _detail_mats(); random.seed(11)
    # bake the shrinkwrap into the head plates: a live shrinkwrap would pull a plate back onto the skull when it opens
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and 'wrap' in o.modifiers]:
        keep = [(md, md.show_viewport, md.show_render) for md in o.modifiers if md.name != 'wrap']
        for md, _, _ in keep: md.show_viewport = md.show_render = False
        dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data
        o.data = me; o.modifiers.remove(o.modifiers['wrap']); bpy.data.meshes.remove(old)
        for md, v, r in keep: md.show_viewport, md.show_render = v, r
    dg = bpy.context.evaluated_depsgraph_get()
    RIV, LED, TAB = _shared('rivet mesh', _rivet), _shared('led mesh', _led), _shared('hazard tab mesh', _tab)
    paint = [o for o in bpy.data.objects if 'bone' in o and o.type == 'MESH' and o.material_slots and o.material_slots[0].material
             and o.material_slots[0].material.name in ('M_paint', 'M_paint_clean') and not o.name.endswith(' core')]   # painted skull/jaw cores never open
    n = {'rivet': 0, 'code': 0, 'tab': 0, 'led': 0, 'line': 0}
    def hit(o, x, y):
        bb = [Vector(c) for c in o.bound_box]; zt = max(c.z for c in bb) + 0.5
        ok, loc, nrm, _ = o.ray_cast(Vector((x, y, zt)), Vector((0, 0, -1)), distance=2.0, depsgraph=dg)
        return (loc + nrm * 0.001, nrm) if ok and nrm.z > 0.2 else None
    for k, o in enumerate(paint):
        o['d0'] = (o.matrix_world.translation - CORE).length                       # rest distance from the chest core: lock order for the transform
        bb = [Vector(c) for c in o.bound_box]; x0, x1 = min(c.x for c in bb), max(c.x for c in bb); y0, y1 = min(c.y for c in bb), max(c.y for c in bb)
        w, l = x1 - x0, y1 - y0
        if w < 0.06 or l < 0.06: continue
        ix, iy = min(0.035, w * 0.18), min(0.035, l * 0.18)
        pts = [(x0 + ix, y0 + iy), (x1 - ix, y0 + iy), (x0 + ix, y1 - iy), (x1 - ix, y1 - iy)]
        if l > 2.5 * w: pts += [(x0 + ix, (y0 + y1) / 2), (x1 - ix, (y0 + y1) / 2)]
        for j, (x, y) in enumerate(pts):
            h = hit(o, x, y)
            if h: stick(o, f'{o.name} rivet {j}', RIV, h[0], h[1], s=0.8 if 'feather' in o.name else 1.0); n['rivet'] += 1
        if 'feather' in o.name: continue
        if k % 3 == 0 and w > 0.18 and l > 0.18 and o['bone'] not in ('head', 'jaw'):                                   # stencilled panel code
            h = hit(o, (x0 + x1) / 2 + w * 0.12, (y0 + y1) / 2)
            if h:
                cu = bpy.data.curves.new(f'code {k}', 'FONT'); cu.body = random.choice(('A', 'B', 'C', 'R', 'K')) + f'-{k:02d}'; cu.size = 0.05; cu.align_x = 'CENTER'; cu.extrude = 0.0006
                cu.materials.append(M('M_decal')); stick(o, f'{o.name} code', cu, h[0], h[1], along=(1, 0, 0)); n['code'] += 1
        if k % 5 == 1 and l > 0.2:                                                  # hazard tab near one edge
            h = hit(o, x0 + ix * 2.2, (y0 + y1) / 2)
            if h: stick(o, f'{o.name} hazard', TAB, h[0], h[1]); n['tab'] += 1
        if k % 4 == 2 and l > 0.22:                                                 # 3-LED status row (keyed with M_ember: off asleep, on at ignition)
            for j in range(3):
                h = hit(o, x1 - ix * 2.5, y0 + iy * 2 + j * 0.03)
                if h: stick(o, f'{o.name} led {j}', LED, h[0], h[1]); n['led'] += 1
    # hydraulic lines: thin chrome + rubber pairs behind each leg segment and along the wing arm
    for leg, P in LEGS.items():
        for i in range(3):
            a, b = Vector(P[i]), Vector(P[i + 1]); r = (0.26, 0.19, 0.13)[i]; back = Vector((0, 1 if 'F' in leg else -1, 0)) * r * 0.6   # v13: hug the leg
            for j, (dx, mat, rr) in enumerate(((-0.03, 'M_chrome', 0.009), (0.03, 'M_rubber', 0.012))):
                t = cyl(f'{leg} line {i}{j}', rr, (b - a).length * 0.78, mat, 8); t.location = (a + b) / 2 + back + Vector((dx, 0, 0))
                t.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(t, f'leg.{leg}.{i}'); n['line'] += 1
    return 'details: ' + ', '.join(f'{v} {k}s' for k, v in n.items())

# ================================================================ transform (v5): armour unlocks, lifts, then cascades shut from the chest outwards
def m_transform():
    random.seed(23); n = 0
    for o in [o for o in bpy.data.objects if 'd0' in o and 'feather' not in o.name]:
        d0 = o['d0']; bb = [Vector(c) for c in o.bound_box]
        w, l = max(c.x for c in bb) - min(c.x for c in bb), max(c.y for c in bb) - min(c.y for c in bb)
        nrm = o.matrix_basis.to_3x3().normalized() @ Vector((0, 0, 1))             # outward, in parent (bone) space = delta_location space
        lift = 0.07 + 0.1 * random.random(); ang = math.radians(random.uniform(16, 42)) * random.choice((-1, 1)); ax = 1 if l > w else 0
        f0 = 52 + int(d0 * 3) + random.randint(0, 3); fl = min(178, 100 + int(d0 * 13) + random.randint(0, 2))
        def key(f, k_):
            o.delta_location = nrm * lift * k_; r = [0.0, 0.0, 0.0]; r[ax] = ang * k_; o.delta_rotation_euler = r
            o.keyframe_insert('delta_location', frame=f); o.keyframe_insert('delta_rotation_euler', frame=f)
        for f, k_ in ((f0, 0), (f0 + 5, 1.12), (f0 + 8, 1.0), (fl - 4, 1.0), (fl, -0.06), (fl + 3, 0.02), (fl + 5, 0)):
            key(f, k_)
        for fc in _curves(o.animation_data.action):                                  # unlock eases out; the lock is a hard linear slam
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR' if fl - 4 <= kp.co.x < fl else 'BEZIER'
        n += 1
    # turbines + shoulder gears spin up with the ignition instead of idling from frame 1
    for o in bpy.data.objects:
        if o.name.endswith(' fan') and o.animation_data:
            for d in o.animation_data.drivers: d.driver.expression = '0 if frame < 60 else ((frame - 60) ** 2 / 240 if frame < 120 else 15 + 0.5 * (frame - 120))'
        if o.name.startswith('shoulder gear') and 'hub' not in o.name and 'bolt' not in o.name:
            d = o.driver_add('delta_rotation_euler', 2); d.driver.expression = '0 if frame < 70 else -((frame - 70) ** 2 / 400 if frame < 130 else 9 + 0.3 * (frame - 130))'
    return f'transform: {n} armour plates unlock 52-90, slam shut chest-outwards 100-183; turbines/gears spin up'

# ================================================================ bigger (v6): 15 s — feathers deploy one by one, head splits open and re-locks, roar; push-in camera
def _qt(q, t):
    ax, an = q.to_axis_angle(); return Quaternion(ax, an * t)                    # t < 0 overshoots past rest
def _key_delta(o, f, loc, rot):
    o.delta_location = loc; o.delta_rotation_euler = rot
    o.keyframe_insert('delta_location', frame=f); o.keyframe_insert('delta_rotation_euler', frame=f)
def m_bigger():
    rig = O('dragon_rig'); P = rig.pose.bones; scn.frame_end = 360; random.seed(31)
    # feathers: stay stacked until 150, then fan out one after another with a click of overshoot
    for side in 'LR':
        for k in range(len(FEATHERS)):
            nm = f'wing.{side}.f{k}'; dp = f'pose.bones["{nm}"].rotation_quaternion'
            for fc in [fc for fc in _curves(rig.animation_data.action) if fc.data_path == dp]:
                for kp in [kp for kp in fc.keyframe_points if 104 <= kp.co.x <= 200][::-1]: fc.keyframe_points.remove(kp)
            q = SLEEP[nm][0]; f0 = 150 + k * 4
            for f, t in ((104, 1), (f0, 1), (f0 + 7, -0.12), (f0 + 11, 0.03), (f0 + 14, 0)):
                P[nm].rotation_quaternion = _qt(q, t); P[nm].keyframe_insert('rotation_quaternion', frame=f)
    # head split: every face plate blasts outwards and spins, the bare skull + slits flare, then everything slams back
    face = [o for o in bpy.data.objects if 'd0' in o and o.parent_bone in ('head', 'jaw')]
    for o in face:
        nrm = o.matrix_basis.to_3x3().normalized() @ Vector((0, 0, 1)); d = 0.28 + 0.2 * random.random()
        r = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * math.radians(55)
        f0 = 292 + random.randint(0, 4); fl = 322 + random.randint(0, 3)
        for f, k_ in ((288, 0), (f0, 0), (f0 + 6, 1.1), (f0 + 10, 1.0), (fl - 3, 1.04), (fl, -0.05), (fl + 3, 0)):
            _key_delta(o, f, nrm * d * k_, r * k_)
    for f, v in ((288, 8), (296, 8), (300, 24), (326, 24), (332, 12), (360, 14)): emit_key('M_ember', f, v)
    for f, v in ((288, 12), (300, 30), (326, 30), (332, 14), (360, 14)): emit_key('M_core', f, v)
    for f, v in ((288, 25), (300, 70), (326, 70), (334, 40), (360, 40)): light_key('eye light', f, v)
    # roar: head thrusts up/forward, jaw drops wide
    scn.frame_set(288); qh = P['head'].rotation_quaternion.copy()
    for f, deg in ((288, 0), (334, 0), (340, -12), (356, -10), (360, -10)):
        P['head'].rotation_quaternion = qh @ Quaternion(Vector((1, 0, 0)), math.radians(deg)); P['head'].keyframe_insert('rotation_quaternion', frame=f)
    for f, deg in ((288, 0), (334, 0), (339, 36), (355, 34), (360, 30)):
        P['jaw'].rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(deg)); P['jaw'].keyframe_insert('rotation_quaternion', frame=f)
    sp = bpy.data.objects.get('spark emitter')                                      # second spark burst on the roar
    if sp:
        s2 = sp.copy(); s2.name = 'spark emitter roar'; coll('fx').objects.link(s2)
        st = s2.particle_systems[0].settings.copy(); s2.particle_systems[0].settings = st; st.frame_start, st.frame_end, st.count = 338, 352, 700
    for fc in _curves(rig.animation_data.action):
        for kp in fc.keyframe_points:
            if kp.co.x > 288: kp.interpolation = 'BEZIER'
    for o in face:
        for fc in _curves(o.animation_data.action):
            for kp in fc.keyframe_points:
                if 288 < kp.co.x: kp.interpolation = 'LINEAR' if kp.co.x >= 318 and kp.co.x < 326 else 'BEZIER'
    # camera: push in on the unlock, wide for the wings, then face-on close-up for the split + roar
    cam, tgt = O('cam'), O('cam target'); cam.animation_data_clear(); tgt.animation_data_clear()
    scn.frame_set(300); hp_ = rig.matrix_world @ P['head'].head; fw = (rig.matrix_world.to_3x3() @ (P['head'].tail - P['head'].head)).normalized()
    side_ = fw.cross(Vector((0, 0, 1))).normalized()
    K = [(1, (2.6, -7.0, 1.3), (0.8, -1.3, 0.6)), (48, (2.2, -5.6, 1.1), (1.0, -1.4, 0.5)),     # v11: between the braziers (old path was blocked) (92, (3.4, -4.3, 1.35), (0.5, -0.9, 0.9)),
         (150, (6.4, -8.6, 2.2), (0.2, -0.6, 1.6)), (200, (10.2, -13.4, 4.6), (0, 0.6, 2.9)), (270, (6.4, -10.6, 3.9), (0, -1.4, 3.0)),
         (300, tuple(hp_ + fw * 2.6 + side_ * 2.0 + Vector((0, 0, 0.35)))), (326, tuple(hp_ + fw * 2.1 + side_ * 1.7 + Vector((0, 0, 0.2)))), (360, tuple(hp_ + fw * 2.3 + side_ * 2.1 - Vector((0, 0, 0.05))))]   # 3/4: head-on hides the scowl
    for e in K:
        f, c = e[0], e[1]; t = e[2] if len(e) > 2 else tuple(hp_ + fw * 0.55 - Vector((0, 0, 0.05)))
        cam.location = c; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
    return f'bigger: 15 s; feathers deploy 150-195; head split {len(face)} plates 292-325; roar 334-360; push-in camera'

# ================================================================ rig + pistons (Stretch-To between bones)
def m_rig():
    PARTS.clear(); PARTS.extend((o.name, o['bone']) for o in bpy.data.objects if 'bone' in o)
    msg = step_rig()
    rig = O('dragon_rig'); n = 0
    PIST = []
    for leg, P in LEGS.items():
        s = -1 if 'L' in leg else 1
        PIST.append((f'{leg} piston', f'leg.{leg}.0', f'leg.{leg}.1', Vector(P[0]).lerp(Vector(P[1]), 0.3) + Vector((s * 0.2, 0, 0)), Vector(P[1]).lerp(Vector(P[2]), 0.5) + Vector((s * 0.12, 0, 0))))
    for i in range(0, len(NECK) - 2, 2):
        a, b = Vector(NECK[i]).lerp(Vector(NECK[i + 1]), 0.4), Vector(NECK[i + 1]).lerp(Vector(NECK[i + 2]), 0.6)
        for s in (-1, 1): PIST.append((f'neck piston {i}{"LR"[s > 0]}', f'neck.{i}', f'neck.{i + 1}', a + Vector((s * 0.2, 0, 0)), b + Vector((s * 0.18, 0, 0))))
    for name, bA, bB, a, b in PIST:
        p = k_piston(name, (b - a).length, 0.045); p.location = a; p.rotation_euler = (b - a).to_track_quat('Y', 'Z').to_euler()
        tgt = bpy.data.objects.new(f'{name} target', None); coll('dragon').objects.link(tgt); tgt.location = b
        bpy.context.view_layer.update()
        for o, bone in ((p, bA), (tgt, bB)):
            mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bone; o.matrix_world = mw
        c = p.constraints.new('STRETCH_TO'); c.target = tgt; c.volume = 'NO_VOLUME'; c.keep_axis = 'PLANE_Z'; n += 1
    return msg + f'; {n} pistons (Stretch-To)'

def m_close_up(out):
    """studio close-up for the owner check: 3/4 head+chest and full side"""
    if not scn.camera:
        cd = bpy.data.cameras.new('cu'); c = bpy.data.objects.new('cu', cd); coll('camera').objects.link(c); scn.camera = c
    c = scn.camera; c.constraints.clear(); c.animation_data_clear(); h0 = Vector(NECK[-1])
    for n, v in (('M_ember', 6.0), ('M_core', 10.0), ('M_ember_edge', 2.5)):
        M_ = bpy.data.materials[n]; M_.animation_data_clear(); M_.node_tree.animation_data_clear(); bsdf(M_).inputs['Emission Strength'].default_value = v
    for n, v in (('core light', 180.0), ('eye light', 25.0)):
        l = bpy.data.objects.get(n)
        if l: l.data.animation_data_clear(); l.data.energy = v
    for nm, loc, tgt, lens in (('head', tuple(h0 + Vector((3.4, -3.3, 0.7))), tuple(h0 + Vector((0, -0.3, -0.25))), 45), ('full', (7.5, -8.5, 3.2), (0, 0.8, 1.7), 35)):
        c.location = loc; c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); c.data.lens = lens
        scn.render.filepath = os.path.join(out, f'close_{nm}.png'); bpy.ops.render.render(write_still=True)
    return 'close-ups rendered'

if __name__ == '__main__' and '--steps' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    print('[mecha]', m_materials()); print('[mecha]', m_body()); print('[mecha]', m_fierce()); print('[mecha]', m_details()); print('[mecha]', m_rig())
    if 'set' in argv: print('[mecha]', step_set()); print('[mecha]', step_light_camera())
    if '--close' in argv:
        if 'set' not in argv:
            step_light_camera()
        scn.render.resolution_percentage = 50; print('[mecha]', m_close_up(argv[argv.index('--close') + 1]))
    if '--save' in argv: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(argv[argv.index('--save') + 1]))
