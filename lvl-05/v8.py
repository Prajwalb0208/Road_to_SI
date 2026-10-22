# LVL 05 v8 — mystical ancient environment, exec'd after mecha.py + v7.py:
#   flagstone floor, summoning rune circle that ignites with the dragon, colossal portal ring, glyph-banded pillars,
#   levitating rocks, crystal clusters, hanging chains + roots, colossal stone guardian head, ground mist, purple/teal moon.
def _emit(name, hx, st, alpha=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; p = bsdf(m)
    p.inputs['Base Color'].default_value = (0, 0, 0, 1); p.inputs['Emission Color'].default_value = (*lin(hx), 1); p.inputs['Emission Strength'].default_value = st
    if alpha is not None:
        p.inputs['Alpha'].default_value = alpha; m.surface_render_method = 'BLENDED'
    return m
def v8_materials():
    _emit('M_rune', '#46D9E6', 0.0); _emit('M_glyph', '#7A45FF', 0.9); _emit('M_portal_rim', '#7FE9FF', 6.0)
    m = bpy.data.materials.get('M_crystal') or bpy.data.materials.new('M_crystal'); m.use_nodes = True; p = bsdf(m)
    p.inputs['Base Color'].default_value = (*lin('#6A3CFF'), 1); p.inputs['Roughness'].default_value = 0.05; p.inputs['Transmission Weight'].default_value = 0.6
    p.inputs['Emission Color'].default_value = (*lin('#5A2BFF'), 1); p.inputs['Emission Strength'].default_value = 0.8
    m = bpy.data.materials.get('M_root') or bpy.data.materials.new('M_root'); m.use_nodes = True; p = bsdf(m)
    p.inputs['Base Color'].default_value = (*lin('#1F2416'), 1); p.inputs['Roughness'].default_value = 0.85
    m = bpy.data.materials.get('M_iron') or bpy.data.materials.new('M_iron'); m.use_nodes = True; p = bsdf(m)
    p.inputs['Base Color'].default_value = (*lin('#2E2A27'), 1); p.inputs['Metallic'].default_value = 1.0; p.inputs['Roughness'].default_value = 0.55
    # swirling portal energy: animated 4D noise -> purple/cyan, alpha from the noise
    m = bpy.data.materials.get('M_portal') or bpy.data.materials.new('M_portal'); m.use_nodes = True; nt = m.node_tree; m.surface_render_method = 'BLENDED'
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.voronoi_dimensions = '4D'; vo.inputs['Scale'].default_value = 3.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector']); d = vo.inputs['W'].driver_add('default_value'); d.driver.expression = 'frame * 0.02'
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 0.9; nz.inputs['Detail'].default_value = 10; nz.inputs['Distortion'].default_value = 2.5
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); d = nz.inputs['W'].driver_add('default_value'); d.driver.expression = 'frame * 0.015'
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; mx.inputs[1].default_value = 1.0; nt.links.new(nz.outputs['Fac'], mx.inputs[0])
    cr = nt.nodes.new('ShaderNodeValToRGB'); E = cr.color_ramp.elements; E[0].position = 0.38; E[0].color = (*lin('#12052E'), 0); E[1].position = 0.72; E[1].color = (*lin('#7FE9FF'), 0.9)
    e = E.new(0.55); e.color = (*lin('#6A2BFF'), 0.55); nt.links.new(mx.outputs[0], cr.inputs['Fac'])
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 2.0; nt.links.new(cr.outputs['Color'], em.inputs['Color'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); ms = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(cr.outputs['Alpha'], ms.inputs['Fac'])
    nt.links.new(tr.outputs[0], ms.inputs[1]); nt.links.new(em.outputs[0], ms.inputs[2]); nt.links.new(ms.outputs[0], out.inputs['Surface'])
    # low ground mist: a volume slab, density noise
    m = bpy.data.materials.get('M_mist') or bpy.data.materials.new('M_mist'); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'); vol = nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value = (*lin('#8C7CC8'), 1)
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 0.6; nz.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); d = nz.inputs['W'].driver_add('default_value'); d.driver.expression = 'frame * 0.004'
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    fall = nt.nodes.new('ShaderNodeMapRange'); fall.inputs['From Min'].default_value = 0.0; fall.inputs['From Max'].default_value = 1.0; fall.inputs['To Min'].default_value = 1.0; fall.inputs['To Max'].default_value = 0.0
    nt.links.new(sep.outputs['Z'], fall.inputs['Value'])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(nz.outputs['Fac'], m1.inputs[0]); nt.links.new(fall.outputs['Result'], m1.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 0.55; nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(m2.outputs[0], vol.inputs['Density'])
    nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return 'v8 materials: runes, glyphs, crystal, portal energy, ground mist, roots, iron'

def v8_environment():
    random.seed(808); C = 'ruins'; n = {}
    def put(o):
        for c in list(o.users_collection): c.objects.unlink(o)
        coll(C).objects.link(o); return o
    def cnt(k): n[k] = n.get(k, 0) + 1
    for nm in ('back wall', 'lintel'):                                                  # the plain wall + lintel go: replaced by the gateway hall
        if nm in bpy.data.objects: bpy.data.objects[nm].hide_render = True; bpy.data.objects[nm].hide_viewport = True
    # cracked flagstones under the dragon (ancient temple floor)
    for i in range(-5, 6):
        for j in range(-3, 8):
            if random.random() < 0.12: continue
            t = put(box(f'flagstone {i} {j}', (1.42, 1.42, 0.16), 'M_stone', bev=0.04)); t.location = (i * 1.5 + random.uniform(-0.04, 0.04), j * 1.5 + random.uniform(-0.04, 0.04), 0.0 + random.uniform(-0.03, 0.01))
            t.rotation_euler = (random.uniform(-0.03, 0.03), random.uniform(-0.03, 0.03), random.uniform(-0.03, 0.03)); cnt('flagstone')
    # summoning rune circle: 3 rings + 24 glyph ticks + 6 spokes, ignites with the core (M_rune keyed)
    for r, w in ((3.2, 0.06), (2.6, 0.04), (1.4, 0.05)):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=96, radius1=r, radius2=r, depth=0.012)
        o = put(mesh_obj(f'rune ring {r}', bm, 'M_rune', False, C)); o.location = (0, 0.6, 0.09); s_ = o.modifiers.new('s', 'SOLIDIFY'); s_.thickness = w; cnt('rune ring')
    for k in range(24):
        a = 2 * math.pi * k / 24; g = put(box(f'rune glyph {k}', (0.08, 0.36 if k % 3 else 0.5, 0.01), 'M_rune', bev=0.004)); g.location = (math.sin(a) * 2.9, 0.6 + math.cos(a) * 2.9, 0.09); g.rotation_euler.z = -a; cnt('glyph')
        if k % 2 == 0:
            g2 = put(box(f'rune mark {k}', (0.18, 0.05, 0.01), 'M_rune', bev=0.004)); g2.location = (math.sin(a + 0.13) * 2.0, 0.6 + math.cos(a + 0.13) * 2.0, 0.09); g2.rotation_euler.z = -a + 0.6
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.26; sp = put(box(f'rune spoke {k}', (0.04, 1.2, 0.01), 'M_rune', bev=0.004)); sp.location = (math.sin(a) * 2.0, 0.6 + math.cos(a) * 2.0, 0.09); sp.rotation_euler.z = -a
    for f, v in ((1, 0.0), (58, 0.0), (64, 1.2), (67, 0.2), (72, 2.2), (300, 2.2), (306, 5.0), (330, 2.8), (372, 2.8), (378, 6.0), (420, 3.0)): emit_key('M_rune', f, v)
    # colossal portal ring behind the dragon: segmented stone ring, glowing rim runes, swirling energy disc
    R = 4.6; cz = 5.6; cy = 12.2
    for k in range(20):
        a0 = 2 * math.pi * k / 20; seg_ = put(box(f'portal block {k}', (1.35, 1.1, 1.0), 'M_stone', bev=0.06, taper=(0.82, 1))); seg_.location = (math.cos(a0) * R, cy, cz + math.sin(a0) * R)
        seg_.rotation_euler = (0, -a0 + math.pi / 2, 0); seg_.rotation_euler.rotate_axis('X', math.radians(90)); cnt('portal block')
        gl = put(box(f'portal rune {k}', (0.32, 0.06, 0.32), 'M_portal_rim', bev=0.02)); gl.location = (math.cos(a0) * (R - 0.62), cy - 0.56, cz + math.sin(a0) * (R - 0.62)); gl.rotation_euler = (0, -a0, 0)
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=R - 0.55); disc = put(mesh_obj('portal energy', bm, 'M_portal', False, C)); disc.location = (0, cy, cz); disc.rotation_euler = (math.radians(90), 0, 0)
    d_ = disc.driver_add('rotation_euler', 1); d_.driver.expression = 'frame * 0.004'
    pl = bpy.data.lights.new('portal light', 'AREA'); pl.color = lin('#8A5CFF'); pl.energy = 3500; pl.size = 6; po = put(bpy.data.objects.new('portal light', pl)); po.location = (0, cy - 0.8, cz); po.rotation_euler = (math.radians(90), 0, 0)
    for f, v in ((1, 1200), (60, 1200), (74, 4200), (300, 4200), (306, 9000), (330, 4200)): pl.energy = v; pl.keyframe_insert('energy', frame=f)
    # gateway hall: massive side walls + broken colossal arches far back, all one dark stone mass
    for s in (-1, 1):
        w = put(box(f'hall wall {s}', (2.0, 18, 14), 'M_stone', bev=0.2)); w.location = (s * 10.5, 6, 7); cnt('hall wall')
        for j in range(4):
            bt = put(box(f'buttress {s}{j}', (1.4, 1.6, 12 - j * 1.5), 'M_stone', bev=0.15, taper=(0.8, 1))); bt.location = (s * 9.2, -2 + j * 4.4, (12 - j * 1.5) / 2)
    bk = put(box('hall back', (24, 2, 16), 'M_stone', bev=0.2)); bk.location = (0, 15.5, 8)
    bk2 = bk.modifiers.new('hole', 'BOOLEAN'); cut = put(cyl('hall back hole', R + 0.6, 4, 'M_stone', 48)); cut.location = (0, 15.5, cz); cut.rotation_euler = (math.radians(90), 0, 0); cut.hide_render = True; cut.hide_viewport = True; bk2.object = cut
    for k in range(7):                                                                     # collapsed ceiling ribs (silhouettes against the moon)
        rb = put(box(f'ceiling rib {k}', (22 if k % 3 else 13, 0.9, 1.1), 'M_stone', bev=0.08)); rb.location = ((0 if k % 3 else random.choice((-5, 5))), -3 + k * 3.0, 13.5 + random.uniform(-0.4, 0.4)); rb.rotation_euler = (0, random.uniform(-0.08, 0.08), 0)
    # glyph bands on every pillar drum (violet, faint) + pillars taller
    for o in [o for o in bpy.data.objects if o.name.startswith('pillar') and ' drum ' in o.name]:
        if random.random() < 0.55:
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=40, radius1=0.56, radius2=0.56, depth=0.07); g = put(mesh_obj(f'{o.name} glyphs', bm, 'M_glyph', False, C))
            g.location = o.location + Vector((0, 0, random.uniform(-0.25, 0.25))); cnt('glyph band')
    # levitating rocks: chunks hovering + slowly bobbing/rotating (bob is keyed, rotation driven)
    src = [o for o in bpy.data.objects if o.type == 'MESH' and o.location.x > 90]
    for k in range(16):
        r = random.choice(src).copy(); put(r); sc = random.uniform(0.25, 0.9); r.scale = (sc, sc, sc)
        x = random.choice((-1, 1)) * random.uniform(2.5, 8); y = random.uniform(-1, 12); z = random.uniform(3.0, 9.5)
        for f, dz in ((1, 0), (140, random.uniform(0.2, 0.5)), (280, -random.uniform(0.1, 0.3)), (420, 0.2)):
            r.location = (x, y, z + dz); r.keyframe_insert('location', frame=f)
        for ax in range(3): d_ = r.driver_add('rotation_euler', ax); d_.driver.expression = f'frame * {random.uniform(-0.006, 0.006):.4f} + {random.uniform(0, 6):.2f}'
        cnt('floating rock')
    # crystal clusters at pillar bases + rubble, each with a soft violet light
    for k, (x, y) in enumerate(((-4.0, 3.8), (5.2, 4.2), (-5.8, 8.6), (6.0, 9.4), (-2.4, 11.6), (2.8, 12.0), (-7.0, 1.0), (7.4, -1.0))):
        for j in range(random.randint(5, 9)):
            h = random.uniform(0.5, 1.9); c = put(cyl(f'crystal {k}{j}', random.uniform(0.07, 0.16), h, 'M_crystal', 6, r2=0.01)); c.location = (x + random.uniform(-0.4, 0.4), y + random.uniform(-0.4, 0.4), h * 0.4)
            c.rotation_euler = (random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6), random.uniform(0, 3)); cnt('crystal')
        cl = bpy.data.lights.new(f'crystal light {k}', 'POINT'); cl.color = lin('#8A5CFF'); cl.energy = 160; cl.shadow_soft_size = 0.4; put(bpy.data.objects.new(f'crystal light {k}', cl)).location = (x, y, 0.9)
    # hanging chains (alternating links) + dead roots from the ceiling
    link_me = None
    for k, (x, y, top, bot) in enumerate(((-3.5, 2, 13, 5.5), (3.8, 4, 13, 6.5), (-6.0, 7, 13, 4.2), (6.5, 6, 13, 7.0), (-1.5, 9.5, 13, 8.0), (1.8, -1.5, 13, 7.5))):
        nlinks = int((top - bot) / 0.16)
        for j in range(nlinks):
            link_me = link_me or _chain_link(); lk = put(bpy.data.objects.new(f'chain {k} link {j}', link_me))
            lk.location = (x, y, top - j * 0.16); lk.rotation_euler = (math.radians(90), 0, math.radians(90 * (j % 2)))
        cnt('chain')
    for k in range(10):
        cu = bpy.data.curves.new(f'root {k}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = random.uniform(0.02, 0.06); cu.bevel_resolution = 2; sp = cu.splines.new('NURBS'); sp.points.add(4)
        x = random.uniform(-8, 8); y = random.uniform(-2, 13); z0 = 13.2
        for j, p_ in enumerate(sp.points): p_.co = (x + random.uniform(-0.4, 0.4), y + random.uniform(-0.4, 0.4), z0 - j * random.uniform(0.8, 1.6), 1)
        sp.use_endpoint_u = True; cu.taper_radius_mode = 'MULTIPLY'; cu.materials.append(M('M_root')); put(bpy.data.objects.new(f'root {k}', cu)); cnt('root')
    # colossal guardian head carved into the left wall, faint violet eyes
    gh = put(loft('guardian skull', [(1.2, 1.6, 1.5, 1.0), (-0.4, 1.8, 1.7, 1.0), (-2.2, 1.3, 1.1, 0.7), (-4.0, 0.7, 0.6, 0.4)], 'M_stone'))
    gh.location = (-8.6, 9.5, 5.0); gh.rotation_euler = (0, math.radians(8), math.radians(-70))
    for s in (-1, 1):
        hn = put(horn(f'guardian horn {s}', Vector((-8.6, 9.5, 6.3)) + Vector((0.4, s * 1.0, 0.4)), (0.4, s * 0.6 + 0.6, 0.9), 4.0, 0.45, -60, 'M_stone'))
        ey = put(ball(f'guardian eye {s}', 0.32, 'M_glyph', (-7.3 + 0.2 * s, 9.5 - 1.7 + s * 0.9, 5.6))); cnt('guardian part')
    jw = put(loft('guardian jaw', [(0.8, 1.4, 0.4, 0.6), (-1.2, 1.2, 0.3, 0.5), (-3.2, 0.6, 0.2, 0.3)], 'M_stone')); jw.location = (-8.6, 9.5, 3.4); jw.rotation_euler = (math.radians(-12), math.radians(8), math.radians(-70))
    # low ground mist slab
    mist = put(box('ground mist', (26, 26, 1.6), 'M_mist', bev=0.0)); mist.location = (0, 4, 0.8)
    return 'v8 environment: ' + ', '.join(f'{v} {k}s' for k, v in n.items()) + ', portal energy, ground mist'
def _chain_link():
    bm = bmesh.new(); g = bmesh.ops.create_circle(bm, cap_ends=False, segments=14, radius=0.1)
    for v in bm.verts: v.co.y *= 1.6
    me = bpy.data.meshes.new('chain link'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('_tmp link', me); coll('ruins').objects.link(o); s = o.modifiers.new('s', 'SKIN')
    for v in me.skin_vertices[0].data: v.radius = (0.022, 0.022)
    dg = bpy.context.evaluated_depsgraph_get(); me2 = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); bpy.data.objects.remove(o, do_unlink=True)
    me2.materials.append(M('M_iron'))
    for f in me2.polygons: f.use_smooth = True
    return me2
def v8_light():
    w = scn.world; nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (*lin('#0A0718'), 1); bg.inputs['Strength'].default_value = 0.35
    vol = next(n for n in nt.nodes if n.type == 'PRINCIPLED_VOLUME'); vol.inputs['Color'].default_value = (*lin('#9C8CE0'), 1); vol.inputs['Density'].default_value = 0.014
    mo = bpy.data.objects.get('moon')
    if mo: mo.data.color = lin('#8F9CFF'); mo.data.energy = 90000; mo.location = (2.0, 6.0, 30); mo.rotation_euler = (Vector((0, 1, 0)) - mo.location).to_track_quat('-Z', 'Y').to_euler(); mo.data.spot_size = math.radians(22)
    for nm, e, hx in (('key', 900, '#B8C4FF'), ('rim', 4500, '#46D9E6'), ('red rim', 4000, '#FF2A1A')):
        o = bpy.data.objects.get(nm)
        if o: o.data.energy = e; o.data.color = lin(hx)
    rl = bpy.data.lights.new('rune light', 'AREA'); rl.color = lin('#46D9E6'); rl.size = 5; ro = bpy.data.objects.new('rune light', rl); coll('light').objects.link(ro); ro.location = (0, 0.6, 0.25)
    ro.rotation_euler = (math.radians(180), 0, 0)
    for f, v in ((1, 0), (58, 0), (72, 450), (300, 450), (306, 1100), (330, 550)): rl.energy = v; rl.keyframe_insert('energy', frame=f)
    for l in bpy.data.lights:                                                          # small accent lights cast no shadows (EEVEE shadow buffer overflowed)
        if any(t in l.name for t in ('crystal', 'terminal', 'rune', 'portal', 'mouth', 'brazier')): l.use_shadow = False
    return 'v8 light: violet moon shaft from the broken roof, cyan rim, red rim, rune uplight, violet haze'

def v8_dragon_light():
    """environment got rich, dragon got lost: dedicated spots that TRACK the dragon (chest + head targets ride the bones),
    environment accents pulled down so the cherry paint + gold pop against a darker violet hall"""
    rig = O('dragon_rig')
    def target(name, bone, loc):
        t = bpy.data.objects.new(name, None); coll('light').objects.link(t); t.location = loc; bpy.context.view_layer.update()
        mw = t.matrix_world.copy(); t.parent = rig; t.parent_type = 'BONE'; t.parent_bone = bone; t.matrix_world = mw; return t
    scn.frame_set(1); tc = target('aim chest', 'spine.chest', (0, -0.6, 1.4)); th = target('aim head', 'head', Vector(NECK[-1]) + Vector((0, -0.5, 0)))
    def spot(name, loc, tgt, e, hx, size_deg, blend=0.35, soft=0.6):
        l = bpy.data.lights.new(name, 'SPOT'); l.energy = e; l.color = lin(hx); l.spot_size = math.radians(size_deg); l.spot_blend = blend; l.shadow_soft_size = soft
        o = bpy.data.objects.new(name, l); coll('light').objects.link(o); o.location = loc
        c = o.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; return o
    spot('hero key', (-5.5, -8.0, 7.5), tc, 14000, '#FFE2C2', 38)                        # warm key from front-left-high
    spot('hero rim cyan', (-6.5, 7.5, 6.0), tc, 7000, '#46D9E6', 34, soft=0.3)            # hard cyan edge from back-left
    spot('hero rim red', (6.5, 7.0, 5.0), tc, 14000, '#FF2A1A', 34, soft=0.3)              # hot red edge from back-right
    spot('hero head', (3.5, -7.5, 5.5), th, 5000, '#FFF1E0', 16, soft=0.2)                 # face catch light
    spot('hero under', (0.0, -5.0, 0.4), tc, 900, '#FF7A1A', 45)                          # warm bounce from below (fire-lit belly)
    for nm in ('red rim', 'rim'):                                                          # the old static rims fought the new ones
        o = bpy.data.objects.get(nm)
        if o: o.data.energy *= 0.3
    for l in bpy.data.lights:                                                              # environment accents down
        if l.name.startswith('crystal light'): l.energy *= 0.45
        if l.name == 'portal light':
            for fc in _curves(l.animation_data.action):
                for kp in fc.keyframe_points: kp.co.y *= 0.45; kp.handle_left.y *= 0.45; kp.handle_right.y *= 0.45
    mo = bpy.data.objects.get('moon')
    if mo: mo.data.energy *= 0.7
    vol = next(n for n in scn.world.node_tree.nodes if n.type == 'PRINCIPLED_VOLUME'); vol.inputs['Density'].default_value = 0.011
    for l in bpy.data.lights:
        if l.name.startswith('brazier') and l.animation_data:
            for fc in _curves(l.animation_data.action):
                for kp in fc.keyframe_points: kp.co.y *= 0.55
    return 'dragon light: tracking warm key, cyan + red rims, head catch light, warm under-bounce; env accents dimmed'

# ---------------------------------------------------------------- head pass: hot eyes + gold-edged scales (owner: "head not visible correctly… eyes and scales highlighted")
def v8_head():
    # eye material: own channel (hotter than the seams), soft halo shell, small cyan light in each socket
    _emit('M_eye', '#5FE6F2', 0.0); _emit('M_eye_halo', '#46D9E6', 0.0, alpha=0.18)
    for s, S in ((-1, 'L'), (1, 'R')):
        sl = O(f'eye slit {S}'); sl.data.materials[0] = M('M_eye'); sl.scale = (1.0, 1.12, 1.7)
        h = box(f'eye halo {S}', (0.05, 0.52, 0.12), 'M_eye_halo', bev=0.02, taper=(1, 0.4)); h.matrix_world = sl.matrix_world.copy(); h.scale = (1.4, 1.15, 1.6); part(h, 'head')
        l = bpy.data.lights.new(f'eye glow {S}', 'POINT'); l.color = lin('#7FF3FF'); l.energy = 0; l.shadow_soft_size = 0.05; l.use_shadow = False
        o = bpy.data.objects.new(f'eye glow {S}', l); coll('dragon').objects.link(o); o.location = sl.location + Vector((s * 0.12, -0.05, 0)); part(o, 'head')
    # scale material: same candy paint, stronger flake, edge wear swapped to GOLD on a tight AO radius -> every scale gets a gold rim
    if 'M_scale' in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials['M_scale'])
    ms = M('M_paint').copy(); ms.name = 'M_scale'; nt = ms.node_tree
    for n_ in nt.nodes:
        if n_.type == 'AMBIENT_OCCLUSION' and n_.inside: n_.inputs['Distance'].default_value = 0.012
        if n_.type == 'MAP_RANGE' and abs(n_.inputs['From Min'].default_value - 0.32) < 1e-3: n_.inputs['From Min'].default_value = 0.16; n_.inputs['From Max'].default_value = 0.24
        if n_.type == 'MIX' and n_.data_type == 'RGBA' and n_.blend_type == 'MIX' and n_.inputs['B'].default_value[0] > 0.3 and abs(n_.inputs['B'].default_value[0] - n_.inputs['B'].default_value[1]) < 1e-3:
            n_.inputs['B'].default_value = (*lin('#E3A53A'), 1)
        if n_.type == 'MIX' and n_.blend_type == 'OVERLAY': n_.inputs['Factor'].default_value = 0.35
    # procedural scales (geometry studs read as a pineapple): Voronoi cells -> domed bump + gold seams, flush on the plates
    p = bsdf(ms); base_link = p.inputs['Base Color'].links[0].from_socket
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 0.7, 1.0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    ve = nt.nodes.new('ShaderNodeTexVoronoi'); ve.feature = 'DISTANCE_TO_EDGE'; ve.inputs['Scale'].default_value = 26; nt.links.new(mp.outputs['Vector'], ve.inputs['Vector'])
    vf = nt.nodes.new('ShaderNodeTexVoronoi'); vf.inputs['Scale'].default_value = 26; nt.links.new(mp.outputs['Vector'], vf.inputs['Vector'])
    seam = nt.nodes.new('ShaderNodeMapRange'); seam.inputs['From Min'].default_value = 0.0; seam.inputs['From Max'].default_value = 0.07; seam.inputs['To Min'].default_value = 1.0; seam.inputs['To Max'].default_value = 0.0
    nt.links.new(ve.outputs['Distance'], seam.inputs['Value'])
    mixg = nt.nodes.new('ShaderNodeMix'); mixg.data_type = 'RGBA'; mixg.inputs['B'].default_value = (*lin('#E3A53A'), 1)
    nt.links.new(base_link, mixg.inputs['A']); nt.links.new(seam.outputs['Result'], mixg.inputs['Factor']); nt.links.new(mixg.outputs['Result'], p.inputs['Base Color'])
    dome = nt.nodes.new('ShaderNodeMath'); dome.operation = 'SUBTRACT'; dome.inputs[0].default_value = 1.0; nt.links.new(vf.outputs['Distance'], dome.inputs[1])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.45; bp.inputs['Distance'].default_value = 0.02; nt.links.new(dome.outputs[0], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], p.inputs['Normal']); cnt = 0
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.material_slots and o.material_slots[0].material and o.material_slots[0].material.name == 'M_paint' and            any(o.name.startswith(pf) for pf in ('crest plate', 'snout plate', 'brow ', 'skull guard', 'cheek ', 'nose tip', 'jaw plate', 'neck panel', 'skull core', 'jaw core')):
            o.material_slots[0].material = ms; cnt += 1
    return f'head: hot eye slits + halos + socket lights, procedural gold-seamed scales on {cnt} head/neck plates'
def v8_head_light():
    th = O('aim head')
    l = bpy.data.lights.new('head rim', 'SPOT'); l.energy = 9000; l.color = lin('#7FE9FF'); l.spot_size = math.radians(16); l.spot_blend = 0.3; l.shadow_soft_size = 0.2
    o = bpy.data.objects.new('head rim', l); coll('light').objects.link(o); o.location = (-2.5, 4.5, 8.0); c = o.constraints.new('TRACK_TO'); c.target = th; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    hh = bpy.data.objects.get('hero head')
    if hh: hh.data.energy = 9000; hh.data.spot_size = math.radians(20)
    # eye ignition follows the seams' timeline, hotter; socket lights follow
    E = [(1, 0), (50, 0), (54, 5), (57, 0.5), (61, 7), (64, 1.5), (70, 9), (296, 9), (300, 18), (326, 18), (332, 11), (368, 24), (404, 24), (412, 12), (420, 12)]
    for f, v in E: emit_key('M_eye', f, v); emit_key('M_eye_halo', f, v * 0.25)
    for S in 'LR':
        lg = O(f'eye glow {S}').data
        for f, v in E: lg.energy = v * 4; lg.keyframe_insert('energy', frame=f)
    return 'head light: tracking cyan head rim from above-behind, stronger face spot, eye ignition keyed (slits, halos, socket lights)'

# ---------------------------------------------------------------- dark grade (owner: "looks like a vomit of colours, keep it dark and mysterious")
# palette discipline: near-black hall, black-cherry body, antique bronze metal, ONE accent (cyan) for eyes/core/runes, warm fire only as tiny pools
def _scale_keys(idb, k):
    if idb and idb.animation_data and idb.animation_data.action:
        for fc in _curves(idb.animation_data.action):
            for kp in fc.keyframe_points: kp.co.y *= k; kp.handle_left.y *= k; kp.handle_right.y *= k
def v8_grade():
    def rgba_swap(mat, old, new, tol=2e-3):
        for n_ in M(mat).node_tree.nodes:
            for inp in n_.inputs:
                if inp.type == 'RGBA' and not inp.is_linked and all(abs(inp.default_value[i] - lin(old)[i]) < tol for i in range(3)): inp.default_value = (*lin(new), inp.default_value[3])
            if n_.type == 'VALTORGB':
                for e in n_.color_ramp.elements:
                    if all(abs(e.color[i] - lin(old)[i]) < tol for i in range(3)): e.color = (*lin(new), e.color[3])
    for m in ('M_paint', 'M_paint_clean', 'M_scale'): rgba_swap(m, '#7A0F2E', '#4A0818'); rgba_swap(m, '#FF7FA0', '#8A2A40')
    rgba_swap('M_paint_dark', '#36040F', '#1E0309'); rgba_swap('M_paint_dark', '#FF7FA0', '#5A1A28')
    rgba_swap('M_scale', '#E3A53A', '#7A5220')
    for m in ('M_paint', 'M_paint_clean', 'M_paint_dark', 'M_scale'):
        for n_ in M(m).node_tree.nodes:
            if n_.type == 'MIX' and n_.blend_type == 'OVERLAY': n_.inputs['Factor'].default_value = 0.1
    p = bsdf(M('M_gold')); p.inputs['Base Color'].default_value = (*lin('#7A4E1C'), 1); p.inputs['Roughness'].default_value = 0.4
    p = bsdf(M('M_chrome')); p.inputs['Base Color'].default_value = (*lin('#7C7C82'), 1); p.inputs['Roughness'].default_value = 0.22
    for m, st in (('M_strip', 0.9), ('M_ember_edge', 0.6), ('M_glyph', 0.12), ('M_portal_rim', 0.8), ('M_screen', 0.9), ('M_screen_red', 1.2), ('M_crystal', 0.12), ('M_firelight', 10)):
        bm_ = bsdf(M(m)); bm_.inputs['Emission Strength'].default_value = st
    bsdf(M('M_glyph')).inputs['Emission Color'].default_value = (*lin('#2A6F78'), 1)
    c = bsdf(M('M_crystal')); c.inputs['Base Color'].default_value = (*lin('#16242A'), 1); c.inputs['Emission Color'].default_value = (*lin('#2A8C99'), 1)
    for m, k in (('M_ember', 0.5), ('M_core', 0.5), ('M_rune', 0.4), ('M_ember_edge', 0.22)): _scale_keys(M(m).node_tree, k)
    # portal: deep teal, much dimmer, no purple
    pn = M('M_portal').node_tree
    for n_ in pn.nodes:
        if n_.type == 'VALTORGB':
            E = n_.color_ramp.elements; E[0].color = (*lin('#010306'), 0); E[-1].color = (*lin('#3FB8C4'), 0.75)
            for e in E[1:-1]: e.color = (*lin('#123A42'), 0.45)
        if n_.type == 'EMISSION': n_.inputs['Strength'].default_value = 0.7
    mv = M('M_mist').node_tree; next(n for n in mv.nodes if n.type == 'PRINCIPLED_VOLUME').inputs['Color'].default_value = (*lin('#4A5560'), 1)
    w = scn.world.node_tree
    bg = next(n for n in w.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (*lin('#020306'), 1); bg.inputs['Strength'].default_value = 0.15
    vol = next(n for n in w.nodes if n.type == 'PRINCIPLED_VOLUME'); vol.inputs['Color'].default_value = (*lin('#7C8896'), 1); vol.inputs['Density'].default_value = 0.012
    # lights: one cool key, cyan accent rim, red gone, fire pools small, environment glow way down
    for o in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        l = o.data; n = o.name
        if n in ('hero rim red', 'red rim'): l.energy = 0; _scale_keys(l, 0)
        elif n == 'hero key': l.color = lin('#D2DCE8'); l.energy *= 0.6
        elif n == 'hero head': l.color = lin('#E6ECF2'); l.energy *= 0.7
        elif n == 'hero under': l.energy *= 0.4
        elif n == 'moon': l.color = lin('#B4C2D4'); l.energy *= 0.8
        elif n == 'portal light': l.color = lin('#2E8C99'); _scale_keys(l, 0.35)
        elif n.startswith('crystal light'): l.color = lin('#2A8C99'); l.energy *= 0.3
        elif n == 'rune light': _scale_keys(l, 0.2)
        elif n in ('hero rim cyan', 'head rim'): l.energy *= 0.5
        elif n.startswith('terminal') : _scale_keys(l, 0.5)
        elif n.startswith('brazier'): _scale_keys(l, 0.6)
        elif n in ('key', 'fill', 'rim'): l.energy *= 0.5
    vs = scn.view_settings; vs.exposure = -0.35
    try: vs.look = 'AgX - High Contrast'
    except TypeError: pass
    return 'grade: black-cherry + antique bronze + cyan accent only; red/violet/purple removed; hall near-black; exposure -0.35, AgX high contrast'
