# LVL 05 v7 — terrifying pass, exec'd after mecha.py (same namespace):
#   huge serrated wings, face internals under the plates, gearboxes/gearsets/cables/tools on the body,
#   ruins with dead terminals + robot husks + fire, laser breath that blasts a pillar. 420 frames.
PH = os.environ.get('POLYHAVEN_DIR') or os.path.join(_W, 'polyhaven')   # rock_moss_set_01 + boulder_01 (1k glTF) from polyhaven.com, CC0

# ---------------------------------------------------------------- wings: bigger skeleton (set before m_body / m_rig read them)
WING['L'] = [(-0.42, -0.35, 1.78), (-1.65, 0.0, 3.15), (-3.05, 0.6, 4.25)]
WING['R'] = [(-x, y, z) for x, y, z in WING['L']]
FEATHERS[:] = [(k * 11, 3.7 - k * 0.17) for k in range(12)]

def v7_materials():
    def mat(name):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
        for n in [n for n in nt.nodes if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL')]: nt.nodes.remove(n)
        return m, nt, bsdf(m)
    # burnt metal for dead robots / scorched wrecks: dark steel, rust patches from noise
    m, nt, p = mat('M_scorch'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 7; nz.inputs['Detail'].default_value = 8
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[0].color = (*lin('#141312'), 1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (*lin('#5A2E16'), 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Metallic'].default_value = 0.7; p.inputs['Roughness'].default_value = 0.7
    # fire: animated 4D noise -> orange/yellow emission, alpha cut-out at the edges
    m, nt, p = mat('M_fire'); m.surface_render_method = 'BLENDED'
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'); nt.nodes.remove(p)
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 3.5; nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    d = nz.inputs['W'].driver_add('default_value'); d.driver.expression = 'frame * 0.07'
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; nt.links.new(nz.outputs['Fac'], mul.inputs[0])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.15; nt.links.new(sep.outputs['Z'], inv.inputs[1]); nt.links.new(inv.outputs[0], mul.inputs[1])
    cr = nt.nodes.new('ShaderNodeValToRGB'); E = cr.color_ramp.elements
    E[0].position = 0.32; E[0].color = (*lin('#7A1400'), 0); E[1].position = 0.85; E[1].color = (*lin('#FFB020'), 1); e = E.new(0.5); e.color = (*lin('#E83A00'), 1)
    nt.links.new(mul.outputs[0], cr.inputs['Fac'])
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 2.2; nt.links.new(cr.outputs['Color'], em.inputs['Color'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(cr.outputs['Alpha'], mx.inputs['Fac']); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    # laser core + glow, terminal screen text, red alarm glass
    for name, hx, st in (('M_beam', '#E8FFFF', 60.0), ('M_beam_glow', '#46D9E6', 12.0), ('M_screen', '#5CFFB0', 4.0), ('M_screen_red', '#FF3B30', 5.0),
                         ('M_firelight', '#FF7A1A', 25.0)):
        m, nt, p = mat(name); p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin(hx), 1); p.inputs['Emission Strength'].default_value = st
    m = bpy.data.materials['M_beam_glow']; p = bsdf(m); p.inputs['Alpha'].default_value = 0.35
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    if 'M_paint_dark' in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials['M_paint_dark'])
    md = bpy.data.materials['M_paint_clean'].copy(); md.name = 'M_paint_dark'; tgt_ = lin('#7A0F2E')
    for n_ in md.node_tree.nodes:
        if n_.type == 'MIX' and n_.data_type == 'RGBA' and abs(n_.inputs['B'].default_value[0] - tgt_[0]) < 1e-3: n_.inputs['B'].default_value = (*lin('#36040F'), 1)
    m, nt, p = mat('M_crt'); p.inputs['Base Color'].default_value = (*lin('#0A0F0C'), 1); p.inputs['Roughness'].default_value = 0.08; p.inputs['Metallic'].default_value = 0.0
    m, nt, p = mat('M_plastic'); p.inputs['Base Color'].default_value = (*lin('#8C8577'), 1); p.inputs['Roughness'].default_value = 0.55
    return 'v7 materials: scorch, fire, laser, screens, CRT glass, plastic'

# ---------------------------------------------------------------- wings: serrated blades, hook claws, under-wing thrusters
def blade(name, base, dirv, ln, wd, nrm, off, bone, dark, lead=None):
    """one patterned wing blade: alternating red/dark-cherry body, pointed scallop tip, dark under-plate, centre spar with a cyan vein,
    gold chevron bands at fixed fractions (they line up into concentric arcs across the whole wing), optional gold leading edge"""
    mat = 'M_paint_dark' if dark else 'M_paint_clean'; L0 = ln * 0.84; tw = 0.55
    o = box(f'{name}', (wd, L0, 0.11), mat, bev=0.03, taper=(tw, 0.8)); orient_up(o, base, base + dirv * L0, nrm, off); part(o, bone)
    tp = box(f'{name} tip', (wd * tw * 0.98, ln * 0.22, 0.09), mat, bev=0.02, taper=(0.03, 0.5)); orient_up(tp, base + dirv * (L0 - 0.02), base + dirv * (ln * 1.04), nrm, off); part(tp, bone)
    ub = box(f'{name} under', (wd * 0.92, L0 * 0.95, 0.08), 'M_frame', bev=0.02, taper=(tw, 0.8)); orient_up(ub, base, base + dirv * L0 * 0.95, nrm, off - 0.075); part(ub, bone)
    sp = box(f'{name} spar', (0.12, ln * 0.9, 0.08), 'M_frame', bev=0.02, taper=(0.35, 0.6)); orient_up(sp, base, base + dirv * ln * 0.92, nrm, off + 0.09); part(sp, bone)
    vn = box(f'{name} vein', (0.026, ln * 0.82, 0.02), 'M_ember_edge', bev=0.005, taper=(0.3, 1)); orient_up(vn, base + dirv * 0.08, base + dirv * ln * 0.88, nrm, off + 0.14); part(vn, bone)
    for j, t in enumerate((0.3, 0.55, 0.78)):
        w_ = wd * (1 - (1 - tw) * min(1.0, ln * t / L0)) * 0.97
        rb = box(f'{name} band {j}', (w_, 0.06, 0.125), 'M_gold', bev=0.012); orient_up(rb, base + dirv * (ln * t - 0.03), base + dirv * (ln * t + 0.03), nrm, off); part(rb, bone)
    if lead is not None:
        le = box(f'{name} edge', (0.07, L0, 0.14), 'M_gold', bev=0.02, taper=(0.5, 0.6)); orient_up(le, base, base + dirv * L0, nrm, off); le.location += lead * wd * 0.45; part(le, bone)
    return o

def v7_wings():
    for o in [o for o in bpy.data.objects if o.name.startswith('wing ') and (' feather' in o.name or ' spar' in o.name)]: bpy.data.objects.remove(o, do_unlink=True)
    for side, P in WING.items():
        s = -1 if side == 'L' else 1; tip = Vector(P[2])
        for k, (ang, ln) in enumerate(FEATHERS):
            d = fan_dir(s, ang); nrm = fan_normal(s); bn = f'wing.{side}.f{k}'; back = d.cross(nrm).normalized()
            if back.dot(Vector((0, 0, -1))) < 0: back = -back                       # serrations on the trailing (lower) edge
            off = 0.045 * k; lead = -back
            blade(f'wing {side} feather {k}', tip + d * 0.05, d, ln, 1.05, nrm, off, bn, k % 2 == 1, lead)
            hk = horn(f'wing {side} hook {k}', tip + d * ln * 0.97, d + back * 0.35, 0.32, 0.045, -45, 'M_gold'); part(hk, bn)
        # big hook claw on the wrist + three on the elbow, thruster under the upper arm
        part(horn(f'wing {side} wrist claw', tip + Vector((0, -0.08, 0.1)), (s * 0.3, -0.6, 0.9), 0.75, 0.07, -55, 'M_gold'), f'wing.{side}.1')
        for j in range(3):
            part(horn(f'wing {side} elbow claw {j}', Vector(P[1]) + Vector((0, -0.05 - j * 0.06, -0.05)), (s * 0.2, -0.9, -0.3 - j * 0.25), 0.4 - j * 0.07, 0.04, -40, 'M_gold'), f'wing.{side}.0')
        # inner wing: overlapping plates hang from the whole arm (shoulder -> wrist) down-back to the body line, so the wing is a full
        # surface, not a fan stuck on top of a bare arm. Length = how far the arm sits above the back (bottom edge ~ z 1.7).
        w_dir = fan_dir(s, 100); nrm = fan_normal(s); m = 0
        for i in range(2):
            a_, b_ = Vector(P[i]), Vector(P[i + 1]); L_ = (b_ - a_).length; cnt = 7
            for j in range(cnt):
                t = (j + 0.5) / cnt; c = a_.lerp(b_, t); ln = max(0.45, (c.z - 1.7) / max(0.3, -w_dir.z)) * 1.05
                wdt = L_ / cnt * 1.6; off = 0.03 * (j % 2) - 0.05
                blade(f'wing {side} inner plate {i}{j}', c, w_dir, ln, wdt, nrm, off, f'wing.{side}.{i}', j % 2 == 1)
                m += 1
        for i in range(2):                                                                # heavy arm armour: wrap-around split shells + dorsal gold fins
            a_, b_ = Vector(P[i]), Vector(P[i + 1]); L_ = (b_ - a_).length
            for o in group_place(panels(f'wing {side} heavy armour {i}', 1.0 - i * 0.22, L_ * 0.82, 0.08, 200, 3), a_, b_, (0, 0, 1), 0.17 - i * 0.03): part(o, f'wing.{side}.{i}')
            for j in range(3):
                fin = box(f'wing {side} arm fin {i}{j}', (0.04, L_ * 0.18, 0.3 - j * 0.05), 'M_gold', bev=0.01, taper=(1, 0.15)); orient_up(fin, a_.lerp(b_, 0.2 + j * 0.28), a_.lerp(b_, 0.3 + j * 0.28), (0, 0, 1), 0.38 - i * 0.05); fin.rotation_euler.rotate_axis('X', math.radians(-25)); part(fin, f'wing.{side}.{i}')
        a, b = Vector(P[0]), Vector(P[1]); ring, fan = k_turbine(f'wing thruster {side}', 0.2)
        ring.location = a.lerp(b, 0.55) - Vector((0, 0, 0.2)); ring.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); part(ring, f'wing.{side}.0')
        glow = ball(f'wing thruster glow {side}', 0.13, 'M_ember', ring.location.copy(), scale=(1, 1, 0.25)); glow.rotation_euler = ring.rotation_euler; part(glow, f'wing.{side}.0')
    return f'wings: 2 x {len(FEATHERS)} heavy layered blades (1.05 m wide, 11 cm thick) up to {FEATHERS[0][1]:.1f} m, armoured arms, hooks, claws, thrusters'

# ---------------------------------------------------------------- face internals: what you see when the plates open
def v7_face_internals():
    h0 = Vector(NECK[-1]); n = 0
    for s in (-1, 1):
        S = 'LR'[s > 0]
        # temple sensor eye (under the skull guard): three lens rings + glowing iris
        for j, (r, dx) in enumerate(((0.07, 0.0), (0.055, 0.025), (0.04, 0.045))):
            ring = cyl(f'eye lens {S}{j}', r, 0.02, 'M_chrome' if j != 1 else 'M_gold', 24); ring.rotation_euler = (0, math.radians(90), 0)
            ring.location = h0 + Vector((s * (0.33 + dx), -0.22, 0.17)); part(ring, 'head'); n += 1
        iris = cyl(f'eye iris {S}', 0.03, 0.012, 'M_ember', 16); iris.rotation_euler = (0, math.radians(90), 0); iris.location = h0 + Vector((s * 0.385, -0.22, 0.17)); part(iris, 'head')
        # jaw hinge gearset + jaw hydraulics on the cheek
        g = k_gear(f'jaw hinge gear {S}', 0.11, 12, 0.04, 'M_gold'); g.rotation_euler = (0, math.radians(90), 0); g.location = h0 + Vector((s * 0.33, 0.02, -0.12)); part(g, 'head')
        g2 = k_gear(f'jaw idler gear {S}', 0.07, 9, 0.035, 'M_chrome'); g2.rotation_euler = (0, math.radians(90), 0); g2.location = h0 + Vector((s * 0.34, -0.14, -0.05)); part(g2, 'head')
        p = k_piston(f'jaw piston {S}', 0.42, 0.028); p.location = h0 + Vector((s * 0.3, 0.12, 0.05)); p.rotation_euler = Vector((0, -1, -0.55)).to_track_quat('Y', 'Z').to_euler(); part(p, 'head')
        for j in range(3):                                                              # wire bundle over the temple
            w = cyl(f'temple wire {S}{j}', 0.012, 0.7, ('M_rubber', 'M_frame', 'M_gold')[j], 8)
            w.location = h0 + Vector((s * (0.2 + j * 0.025), -0.15, 0.27 - j * 0.02)); w.rotation_euler = Vector((0, -1, -0.15)).to_track_quat('Z', 'Y').to_euler(); part(w, 'head')
        for j in range(4):                                                              # circuit traces on the bare skull
            t = box(f'skull trace {S}{j}', (0.012, 0.22 + j * 0.04, 0.008), 'M_strip', bev=0.002); t.location = h0 + Vector((s * (0.12 + j * 0.035), -0.25 - j * 0.06, 0.31 - j * 0.03)); part(t, 'head')
    for j, (y, r) in enumerate(((-0.05, 0.1), (-0.22, 0.08), (-0.36, 0.065))):          # crest gear train along the top of the skull
        g = k_gear(f'crest gear {j}', r, 10 + j * 2, 0.04, 'M_gold' if j % 2 == 0 else 'M_chrome'); g.rotation_euler = (0, math.radians(90), 0); g.location = h0 + Vector((0, y, 0.33)); part(g, 'head')
        d_ = g.driver_add('delta_rotation_euler', 2); d_.driver.expression = f'frame * {0.12 * (1 if j % 2 == 0 else -1) / r * 0.1:.4f}'
    for o in k_ribs('snout ribs', h0 + Vector((0, -0.55, 0.2)), h0 + Vector((0, -0.95, 0.12)), 0.06, 6): part(o, 'head')
    for j in range(2):
        p = k_piston(f'crest piston {j}', 0.4, 0.022); p.location = h0 + Vector(((j - 0.5) * 0.14, 0.15, 0.3)); p.rotation_euler = Vector((0, -1, -0.15)).to_track_quat('Y', 'Z').to_euler(); part(p, 'head')
    return 'face internals: lens-ring eyes, jaw hinge gearsets + hydraulics, crest gear train, wires, circuit traces, snout ribs'

# ---------------------------------------------------------------- body mechanics
def wrench(name, L=0.32):
    h = box(f'{name}', (0.035, L, 0.012), 'M_chrome', bev=0.004)
    for sgn in (-1, 1):
        j = box(f'{name} jaw', (0.03, 0.06, 0.012), 'M_chrome', bev=0.004); j.parent = h; j.location = (sgn * 0.03, L / 2 + 0.02, 0); j.rotation_euler = (0, 0, sgn * 0.35)
    r = cyl(f'{name} ring', 0.035, 0.012, 'M_chrome', 16); r.parent = h; r.location = (0, -L / 2, 0)
    return h
def v7_body_mech():
    n = 0
    for s in (-1, 1):
        S = 'LR'[s > 0]
        for nm, y, z, bone in (('hip', 0.95, 1.5, 'spine.pelvis'), ('rib', 0.2, 1.62, 'spine.chest')):     # open gearboxes with meshing gears
            hb = box(f'{nm} gearbox {S}', (0.08, 0.62, 0.42), 'M_frame', bev=0.015); hb.location = (s * 0.5, y, z); part(hb, bone)
            for j, (dy, dz, r, t) in enumerate(((-0.15, 0.06, 0.12, 14), (0.06, -0.06, 0.09, 10), (0.2, 0.08, 0.06, 8))):
                g = k_gear(f'{nm} gearbox {S} gear {j}', r, t, 0.035, 'M_gold' if j != 1 else 'M_chrome'); g.rotation_euler = (0, s * math.radians(90), 0)
                g.location = (s * 0.555, y + dy, z + dz); part(g, bone)
                d_ = g.driver_add('delta_rotation_euler', 2); d_.driver.expression = f'0 if frame < 60 else (frame - 60) * {0.6 / (r * 10) * (1 if j % 2 == 0 else -1):.4f}'; n += 1
            for k in range(4): part(ball(f'{nm} gearbox {S} bolt {k}', 0.016, 'M_chrome', (s * 0.545, y + (-0.27 if k < 2 else 0.27), z + (0.18 if k % 2 else -0.18))), bone)
        for leg in (f'F{S}', f'B{S}'):                                                  # gearsets on hips/shoulders and knees
            P = LEGS[leg]
            for i, (r, t) in enumerate(((0.2, 16), (0.13, 12))):
                g = k_gear(f'{leg} joint gear {i}', r, t, 0.045, 'M_gold'); g.rotation_euler = (0, s * math.radians(90), 0); g.location = Vector(P[i]) + Vector((s * (0.28 - i * 0.05), 0, 0)); part(g, f'leg.{leg}.{i}')
                g2 = k_gear(f'{leg} joint pinion {i}', r * 0.45, 8, 0.04, 'M_chrome'); g2.rotation_euler = g.rotation_euler; g2.location = g.location + Vector((s * 0.01, 0.0, r * 1.35)); part(g2, f'leg.{leg}.{i}')
                d_ = g2.driver_add('delta_rotation_euler', 2); d_.driver.expression = '0 if frame < 60 else (frame - 60) * 0.15'; n += 2
        # tools strapped to the hind thigh: two spanners + strap
        P = LEGS[f'B{S}']; a, b = Vector(P[0]), Vector(P[1])
        for j in range(2):
            wr = wrench(f'thigh spanner {S}{j}', 0.34 - j * 0.06); orient_up(wr, a.lerp(b, 0.25 + j * 0.05), a.lerp(b, 0.75 + j * 0.05), (s, 0, 0.1), 0.33 + j * 0.02); part(wr, f'leg.B{S}.0')
        st = box(f'thigh strap {S}', (0.05, 0.08, 0.5), 'M_rubber', bev=0.01); orient_up(st, a.lerp(b, 0.45), a.lerp(b, 0.55), (s, 0, 0.1), 0.3); st.rotation_euler.rotate_axis('Y', math.radians(90)); part(st, f'leg.B{S}.0')
    # sagging cable harnesses (bevelled curves) under the belly and along the neck base
    def cable(name, pts, r, mat, bone):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
        sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
        for p_, c in zip(sp.points, pts): p_.co = (*c, 1)
        sp.use_endpoint_u = True; sp.order_u = 3; cu.materials.append(M(mat))
        o = bpy.data.objects.new(name, cu); coll('dragon').objects.link(o); part(o, bone); return o
    for s in (-1, 1):
        for j in range(3):
            x = s * (0.22 + j * 0.06)
            cable(f'belly cable {s}{j}', [(x, -0.7, 1.0), (x * 1.1, -0.2, 0.86 - j * 0.03), (x * 1.15, 0.4, 0.84 - j * 0.04), (x, 0.95, 1.0)], 0.014 + j * 0.003, ('M_rubber', 'M_gold', 'M_frame')[j], 'spine.chest')
        cable(f'neck harness {s}', [(s * 0.3, -0.6, 1.5), (s * 0.36, -0.8, 1.42), (s * 0.3, -0.98, 1.62)], 0.022, 'M_rubber', 'spine.chest')
        for j in range(2):
            cable(f'tail harness {s}{j}', [(s * (0.2 + j * 0.05), 0.9, 1.25), (s * (0.26 + j * 0.05), 1.3, 1.08), (s * (0.2 + j * 0.05), 1.6, 1.18)], 0.016, ('M_rubber', 'M_gold')[j], 'spine.pelvis')
    return f'body mechanics: 4 open gearboxes, joint gearsets, spanners + strap, cable harnesses ({n} driven gears)'

# ---------------------------------------------------------------- environment: dead terminals, robot husks, fire, boulders, claw marks
def flicker(l, base, amp, phase):
    l.energy = base; l.keyframe_insert('energy', frame=1)
    fc = next(fc for fc in _curves(l.animation_data.action) if fc.data_path == 'energy')
    md = fc.modifiers.new('NOISE'); md.scale = 2.5; md.strength = amp; md.phase = phase
def v7_environment():
    random.seed(77); C = 'ruins'; n = {'terminal': 0, 'husk': 0, 'fire': 0, 'boulder': 0}
    def put(o):
        for c in list(o.users_collection): c.objects.unlink(o)
        coll(C).objects.link(o); return o
    # dead terminals: CRT consoles, some still printing, some smashed and dark
    LINES = [['> WAKE_SEQ.exe', '  core ......... ONLINE', '  servo grid ... 98%', '! CONTAINMENT FAIL', '> _'],
             ['ERR 0x05 SECTOR 7', 'ERR 0x05 SECTOR 7', 'unit LVL-05 :: ACTIVE', '  do not approach', '###########'],
             ['> ping core', '  reply 0ms', '  reply 0ms', '  reply ......', '!! SIGNAL LOST'],
             ['ROAD TO SI // node 05', '  status: AWAKE', '  threat: EXTREME', '> evacuate', '> _']]
    spots = [(-3.4, -1.6, 35, 0, True), (3.6, -0.8, -40, 1, True), (-5.6, 5.6, 80, 2, True), (5.8, 5.0, -95, 3, False), (-2.6, 9.2, 160, 1, False)]
    for i, (x, y, rz, li, live) in enumerate(spots):
        base = put(box(f'terminal {i} desk', (1.1, 0.7, 0.85), 'M_scorch', (x, y, 0.42), rot=(0, 0, math.radians(rz)), bev=0.03))
        crt = put(box(f'terminal {i} crt', (0.75, 0.6, 0.6), 'M_plastic', bev=0.05)); crt.parent = base; crt.location = (0, 0.08, 0.72); crt.rotation_euler = (math.radians(-8 if live else 18), 0, math.radians(random.uniform(-6, 6)))
        scr = put(box(f'terminal {i} screen', (0.6, 0.03, 0.44), 'M_crt', bev=0.02)); scr.parent = crt; scr.location = (0, -0.3, 0.0)
        kb = put(box(f'terminal {i} keys', (0.7, 0.22, 0.05), 'M_plastic', bev=0.01)); kb.parent = base; kb.location = (0, -0.28, 0.45); kb.rotation_euler = (math.radians(8), 0, 0)
        for r_ in range(3):
            for c_ in range(10): k_ = put(box(f'terminal {i} key {r_}{c_}', (0.05, 0.05, 0.02), 'M_frame', bev=0.004)); k_.parent = kb; k_.location = (-0.3 + c_ * 0.066, -0.06 + r_ * 0.06, 0.03)
        if live:
            for j, t in enumerate(LINES[li]):
                cu = bpy.data.curves.new(f'term {i} line {j}', 'FONT'); cu.body = t; cu.size = 0.045; cu.materials.append(M('M_screen_red' if t.startswith(('!', 'ERR')) else 'M_screen'))
                to = put(bpy.data.objects.new(f'terminal {i} text {j}', cu)); to.parent = scr; to.location = (-0.26, -0.02, 0.15 - j * 0.07); to.rotation_euler = (math.radians(90), 0, 0)
            gl = bpy.data.lights.new(f'terminal {i} glow', 'AREA'); gl.color = lin('#5CFFB0'); gl.size = 0.5; lo = put(bpy.data.objects.new(f'terminal {i} glow', gl))
            lo.parent = scr; lo.location = (0, -0.4, 0); lo.rotation_euler = (math.radians(90), 0, 0); flicker(gl, 40, 25, i * 7.0)
        else:
            for j in range(3):                                                         # smashed screen shards
                sh = put(box(f'terminal {i} shard {j}', (random.uniform(0.08, 0.2), 0.01, random.uniform(0.05, 0.15)), 'M_crt', bev=0.002)); sh.location = (x + random.uniform(-0.6, 0.6), y + random.uniform(-0.8, -0.3), 0.02); sh.rotation_euler = (math.radians(90), 0, random.uniform(0, 3))
        for j in range(2):                                                              # dead cables spilling out
            cu = bpy.data.curves.new(f'term {i} cable {j}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.018; sp = cu.splines.new('NURBS'); sp.points.add(3)
            for k, p_ in enumerate(sp.points): p_.co = (x + 0.3 * j + k * random.uniform(0.2, 0.5), y + 0.4 + k * random.uniform(0.1, 0.4), 0.02 if k else 0.4, 1)
            sp.use_endpoint_u = True; cu.materials.append(M('M_rubber')); put(bpy.data.objects.new(f'terminal {i} cable {j}', cu))
        n['terminal'] += 1
    # robot husks: slumped, scorched humanoid mechs (the dragon's last visitors)
    def husk(i, x, y, rz, pose):
        root = put(bpy.data.objects.new(f'husk {i}', None)); root.location = (x, y, 0); root.rotation_euler = (0, 0, math.radians(rz))
        def part_(nm, o, loc, rot=(0, 0, 0)):
            o = put(o); o.parent = root; o.location = loc; o.rotation_euler = rot; return o
        lean = math.radians(55 if pose == 'slump' else 85)
        part_('torso', box(f'husk {i} torso', (0.55, 0.36, 0.7), 'M_scorch', bev=0.04), (0, 0, 0.5), (lean * 0.6, 0, 0))
        part_('head', box(f'husk {i} head', (0.3, 0.3, 0.26), 'M_scorch', bev=0.05, taper=(0.8, 0.8)), (0, 0.42, 0.75 if pose == 'slump' else 0.25), (lean, 0.3, 0.2))
        part_('visor', box(f'husk {i} visor', (0.24, 0.04, 0.06), 'M_crt', bev=0.01), (0, 0.27, 0.72 if pose == 'slump' else 0.22), (lean, 0.3, 0.2))
        for s in (-1, 1):
            part_('arm', cyl(f'husk {i} arm {s}', 0.07, 0.62, 'M_scorch', 10), (s * 0.38, 0.15, 0.35), (math.radians(random.uniform(40, 110)), s * 0.4, 0))
            part_('leg', cyl(f'husk {i} leg {s}', 0.09, 0.75, 'M_scorch', 10), (s * 0.18, -0.35, 0.1), (math.radians(88), 0, s * 0.25))
            part_('hand', box(f'husk {i} hand {s}', (0.12, 0.14, 0.08), 'M_frame', bev=0.02), (s * 0.5, 0.5, 0.06), (0, 0, s * 0.5))
        part_('core', ball(f'husk {i} dead core', 0.07, 'M_crt', (0, 0, 0)), (0, 0.1, 0.62), (0, 0, 0))
        n['husk'] += 1
    for i, (x, y, rz, pose) in enumerate(((-5.4, -1.6, 30, 'slump'), (3.0, 1.8, -60, 'down'), (-1.2, 7.4, 190, 'down'), (-4.6, -5.6, -150, 'slump'))): husk(i, x, y, rz, pose)
    # braziers with fire, smoke-lit, flickering light, embers
    for i, (x, y) in enumerate(((-3.8, -3.2), (3.9, -3.0), (-4.0, 6.2), (4.4, 7.0))):
        bowl = put(cyl(f'brazier {i} bowl', 0.42, 0.3, 'M_stone', 20, r2=0.3)); bowl.location = (x, y, 1.0)
        put(cyl(f'brazier {i} stand', 0.12, 0.85, 'M_scorch', 10)).location = (x, y, 0.43)
        for j in range(6):                                                              # thin licking tongues, not one solid cone
            fl = put(cyl(f'brazier {i} flame {j}', random.uniform(0.07, 0.16), random.uniform(0.6, 1.3), 'M_fire', 12, r2=0.005)); fl.location = (x + random.uniform(-0.18, 0.18), y + random.uniform(-0.18, 0.18), 1.45 + random.uniform(0, 0.25)); fl.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), j)
        l = bpy.data.lights.new(f'brazier {i} light', 'POINT'); l.color = lin('#FF7A1A'); l.shadow_soft_size = 0.3; lo = put(bpy.data.objects.new(f'brazier {i} light', l)); lo.location = (x, y, 1.9); flicker(l, 900, 380, i * 13.0)
        em = put(cyl(f'brazier {i} embers emitter', 0.25, 0.02, 'M_fire', 12)); em.location = (x, y, 1.3); em.show_instancer_for_render = False
        ps = em.modifiers.new('embers', 'PARTICLE_SYSTEM').particle_system; st = ps.settings; st.count = 160; st.frame_start = -100; st.frame_end = 420; st.lifetime = 80
        st.normal_factor = 0.6; st.factor_random = 0.5; st.effector_weights.gravity = -0.12; st.brownian_factor = 0.4; st.render_type = 'OBJECT'
        st.instance_object = _droplet(f'fx ember {i}', 'M_firelight', 0.012); st.particle_size = 1.0; st.size_random = 0.7
        n['fire'] += 1
    # Poly Haven boulders (CC0) scattered around the base of the pillars
    for nm, cnt in (('rock_moss_set_01', 1), ('boulder_01', 3)):
        before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(PH, nm, f'{nm}_1k.gltf'))
        new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
        for o in new: put(o); o.location = (100, 100, 0)
        for k in range(cnt * 3):
            src = random.choice(new); c_ = src.copy(); put(c_)
            x = random.choice((-1, 1)) * random.uniform(3.2, 6.5); y = random.uniform(-3.5, 10)
            c_.location = (x, y, 0.0); c_.rotation_euler = (0, 0, random.uniform(0, 6.3)); sc = random.uniform(0.6, 1.6) if nm == 'boulder_01' else random.uniform(1.0, 2.2); c_.scale = (sc, sc, sc); n['boulder'] += 1
    # claw marks gouged into the back wall + scorch on the floor + tools left behind
    for j in range(4):
        cm = put(box(f'claw mark {j}', (0.09, 0.3, 2.6), 'M_joint', bev=0.03, taper=(0.3, 0.3))); cm.location = (-3.2 + j * 0.35, 13.35, 4.2 - j * 0.1); cm.rotation_euler = (0, math.radians(22), 0)
    for j in range(5):                                                                  # scorch patches, kept off the dragon's footprint (read as a platform)
        x_ = random.choice((-1, 1)) * random.uniform(3.0, 5.5); sc_ = put(cyl(f'scorch {j}', random.uniform(0.5, 1.1), 0.01, 'M_scorch', 9)); sc_.location = (x_, random.uniform(-3, 9), 0.13); sc_.scale = (1, random.uniform(0.4, 0.8), 1)
    for j in range(6):
        w = put(wrench(f'floor spanner {j}', random.uniform(0.25, 0.4))); w.location = (random.uniform(-4.5, 4.5), random.uniform(-3, 2), 0.14); w.rotation_euler = (0, 0, random.uniform(0, 6.3))
        for c_ in w.children: put(c_)
    return 'environment: ' + ', '.join(f'{v} {k}s' for k, v in n.items()) + ', claw marks, scorch, spanners'

# ---------------------------------------------------------------- terrifying light + laser breath that blasts a pillar (frames 362-420)
def v7_light():
    for nm, e in (('key', 1300), ('fill', 60), ('rim', 4200)):
        o = bpy.data.objects.get(nm)
        if o: o.data.energy = e
    rr = bpy.data.lights.new('red rim', 'SPOT'); rr.color = lin('#FF2A1A'); rr.energy = 5000; rr.spot_size = math.radians(30); rr.spot_blend = 0.5
    ro = bpy.data.objects.new('red rim', rr); coll('light').objects.link(ro); ro.location = (6.5, 7.5, 5.5); ro.rotation_euler = (Vector((0, -1, 2)) - ro.location).to_track_quat('-Z', 'Y').to_euler()
    w = scn.world; vol = next(n for n in w.node_tree.nodes if n.type == 'PRINCIPLED_VOLUME'); vol.inputs['Density'].default_value = 0.011
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (*lin('#04060A'), 1); bg.inputs['Strength'].default_value = 0.25
    return 'light: darker key, hotter rim, red spot rim from the back right, thinner haze, near-black world'
def v7_laser():
    rig = O('dragon_rig'); P = rig.pose.bones; scn.frame_end = 420
    target = Vector((9.4, 0.75, 3.2))                                                   # v13: the right hall wall it will smash through (terminals removed)
    # aim the head (and a bit of the neck) at the pillar, hold through the shot
    scn.frame_set(356); qn, qh = P['neck.5'].rotation_quaternion.copy(), P['head'].rotation_quaternion.copy()
    P['neck.5'].keyframe_insert('rotation_quaternion', frame=360); P['head'].keyframe_insert('rotation_quaternion', frame=360)
    scn.frame_set(360); hw = rig.matrix_world @ P['head'].head
    aim(P['neck.5'], ((rig.matrix_world.to_3x3() @ (P['neck.5'].tail - P['neck.5'].head)).normalized().lerp((target - hw).normalized(), 0.5)))
    aim(P['head'], (target - (rig.matrix_world @ P['head'].head)).normalized())
    for f in (370, 420): P['neck.5'].keyframe_insert('rotation_quaternion', frame=f); P['head'].keyframe_insert('rotation_quaternion', frame=f)
    for f, deg in ((360, 30), (368, 24), (420, 24)):
        P['jaw'].rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(deg)); P['jaw'].keyframe_insert('rotation_quaternion', frame=f)
    scn.frame_set(378); bpy.context.view_layer.update()
    hm = rig.matrix_world @ P['head'].matrix; fw = (hm.to_3x3() @ Vector((0, 1, 0))).normalized(); mouth = hm.translation + fw * 1.0 - (hm.to_3x3() @ Vector((0, 0, 1))).normalized() * 0.12
    dg = bpy.context.evaluated_depsgraph_get(); org = mouth + fw * 0.4
    for _ in range(8):                                                                  # skip volumes / fx (ground mist slab, energy discs)
        hit, loc, nrm, _i, ob, _m = scn.ray_cast(dg, org, fw)
        if not hit or not any(t in ob.name for t in ('mist', 'energy', 'rune', 'fx ')): break
        org = loc + fw * 0.01
    end = loc if hit else mouth + fw * 10; L = (end - mouth).length
    # beam = unit-length cylinders along +Z from the origin, scaled to the hit distance, parented to the head bone
    def beam(name, r, mat):
        bm = bmesh.new(); g = bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r * 0.8, depth=1.0); bmesh.ops.translate(bm, verts=g['verts'], vec=(0, 0, 0.5))
        o = mesh_obj(name, bm, mat, True, 'fx'); o.matrix_world = Matrix.Translation(mouth) @ fw.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'head'; o.matrix_world = mw
        for f, sz in ((371, 0.001), (374, L), (404, L), (410, 0.001)):
            o.scale = (1 if sz > 0.01 else 0.01, 1 if sz > 0.01 else 0.01, sz); o.keyframe_insert('scale', frame=f)
        return o
    beam('laser core', 0.035, 'M_beam'); beam('laser glow', 0.11, 'M_beam_glow')
    for f, v in ((360, 14), (368, 40), (404, 40), (412, 14)): emit_key('M_ember', f, v)
    # impact: white-hot flash light, fire + sparks at the hit, pillar top drum blown off
    fl = bpy.data.lights.new('impact flash', 'POINT'); fl.color = lin('#BFF8FF'); fl.shadow_soft_size = 0.4; fo = bpy.data.objects.new('impact flash', fl); coll('fx').objects.link(fo); fo.location = end - fw * 0.3
    for f, v in ((372, 0), (375, 30000), (380, 9000), (404, 12000), (414, 0)): fl.energy = v; fl.keyframe_insert('energy', frame=f)
    ml = bpy.data.lights.new('mouth glow light', 'POINT'); ml.color = lin('#46D9E6'); mo = bpy.data.objects.new('mouth glow light', ml); coll('fx').objects.link(mo); mo.location = mouth
    mw = mo.matrix_world.copy(); mo.parent = rig; mo.parent_type = 'BONE'; mo.parent_bone = 'head'; mo.matrix_world = mw
    for f, v in ((366, 0), (372, 4000), (404, 4000), (410, 0)): ml.energy = v; ml.keyframe_insert('energy', frame=f)
    for nm, cnt, life, spd, mat, sz, grav in (('impact sparks', 900, 26, 6.0, 'M_spark', 0.02, 1.0), ('impact fire', 260, 30, 1.6, 'M_firelight', 0.07, -0.3)):
        em = bpy.data.objects.new(nm, bpy.data.meshes.new(nm)); coll('fx').objects.link(em); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.25); bm.to_mesh(em.data); bm.free()
        em.location = end; em.show_instancer_for_render = False
        st = em.modifiers.new(nm, 'PARTICLE_SYSTEM').particle_system.settings; st.count = cnt; st.frame_start = 374; st.frame_end = 404; st.lifetime = life; st.lifetime_random = 0.5
        st.normal_factor = spd; st.factor_random = spd * 0.5; st.effector_weights.gravity = grav; st.render_type = 'OBJECT'; st.instance_object = _droplet(f'fx {nm}', mat, sz); st.particle_size = 1.0; st.size_random = 0.8
    tm = bpy.data.objects.get('terminal 1 desk')
    if tm:                                                                                 # blown backwards, tumbling (v13: terminals removed -> skipped)
        d0, r0 = tm.location.copy(), tm.rotation_euler.copy()
        for f, dl, rx in ((375, Vector(), 0), (381, Vector((1.0, -1.1, 1.1)), 1.2), (392, Vector((2.4, -4.4, -0.05)), 3.4), (398, Vector((2.6, -4.8, -0.1)), 3.6)):   # v10: lands off the charge path
            tm.location = d0 + dl; tm.rotation_euler = (r0.x + rx, r0.y + rx * 0.4, r0.z + rx * 0.3); tm.keyframe_insert('location', frame=f); tm.keyframe_insert('rotation_euler', frame=f)
    gl = bpy.data.objects.get('terminal 1 glow')
    if gl: gl.data.animation_data_clear(); [gl.data.keyframe_insert('energy', frame=f) for f, gl.data.energy in ((374, 40), (377, 0))]
    # camera: wide 3/4 so the beam crosses the frame, then a slow push
    cam, tgt = O('cam'), O('cam target')
    for f, c, t in ((362, (-6.5, -9.5, 3.0), (4.5, -0.5, 2.8)), (420, (-5.4, -8.2, 2.8), (5.2, -0.2, 2.9))):
        cam.location = c; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
    return f'laser: head turns to terminal 1 (360-370), beam {L:.1f} m fires 371-410, impact flash + sparks + fire, terminal blown away; 420 frames'

def v7_softer_split():
    """head split v6 threw plates 0.28-0.48 m: face read as empty. Re-key the 292-325 offsets to hinge closer (35-60 % of before)"""
    n = 0
    for o in [o for o in bpy.data.objects if 'd0' in o and o.parent_bone in ('head', 'jaw') and o.animation_data]:
        for fc in _curves(o.animation_data.action):
            for kp in fc.keyframe_points:
                if 290 < kp.co.x < 330: kp.co.y *= 0.45; kp.handle_left.y *= 0.45; kp.handle_right.y *= 0.45
        n += 1
    return f'head split softened on {n} plates'

def v7_head_paint():
    """bare black skull/jaw cores read as empty blobs in close-up: paint them, drop the snout vents (read as '11')"""
    for n in ('skull core', 'jaw core'): O(n).data.materials[0] = M('M_paint')
    for o in [o for o in bpy.data.objects if o.name.startswith('nose vent')]: bpy.data.objects.remove(o, do_unlink=True)
    return 'head: skull + jaw cores in candy paint, snout vents removed'
