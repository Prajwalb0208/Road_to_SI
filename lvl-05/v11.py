# LVL 05 v11 — owner: "we need more dust and natural burst of wall or rock"
#   wall stays whole until the hit, then a jagged hole; cubes -> irregular fractured rock (slabs, chunks, gravel);
#   rolling volumetric dust clouds + fine grit at the breach, dust plumes along the body when the stone shell bursts.
def _hull(name, size, seed, mat='M_stone', n=14):
    """irregular fractured rock: convex hull of jittered points in an ellipsoid, flat-shaded (fracture faces)"""
    rnd = random.Random(seed); bm = bmesh.new()
    for _ in range(n):
        v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
        if v.length > 1: v.normalize()
        bm.verts.new((v.x * size[0], v.y * size[1], v.z * size[2]))
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M(mat)); return me
def _dust_mat(name, hx='#6E655A'):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n_ in list(nt.nodes):
        if n_.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n_)
    out = next(n_ for n_ in nt.nodes if n_.type == 'OUTPUT_MATERIAL'); vol = nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value = (*lin(hx), 1); vol.inputs['Anisotropy'].default_value = 0.3
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.2; nz.inputs['Detail'].default_value = 6; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; nt.links.new(tc.outputs['Object'], gr.inputs['Vector'])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(nz.outputs['Fac'], m1.inputs[0]); nt.links.new(gr.outputs['Fac'], m1.inputs[1])
    cr = nt.nodes.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = 0.05; cr.inputs['From Max'].default_value = 0.35; nt.links.new(m1.outputs[0], cr.inputs['Value'])
    dn = nt.nodes.new('ShaderNodeMath'); dn.operation = 'MULTIPLY'; dn.name = 'density'; dn.inputs[1].default_value = 0.0; nt.links.new(cr.outputs['Result'], dn.inputs[0])
    nt.links.new(dn.outputs[0], vol.inputs['Density']); nt.links.new(vol.outputs[0], out.inputs['Volume']); return m, dn
def puff(name, loc, vel, t0, life, r0, r1, dens, hx='#6E655A', coll_name='fx'):
    """one rolling dust cloud: sphere volume that expands, drifts, sinks a little and thins out"""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    m, dn = _dust_mat(f'M_{name}', hx); me.materials.append(m); o = bpy.data.objects.new(name, me); coll(coll_name).objects.link(o)
    o.rotation_euler = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, 3))
    for f, k, d in ((t0 - 1, 0.0, 0.0), (t0, 0.05, dens), (t0 + life * 0.25, 0.45, dens * 0.9), (t0 + life * 0.6, 0.8, dens * 0.5), (t0 + life, 1.0, 0.0)):
        f = int(f); o.location = Vector(loc) + Vector(vel) * k * life / 24 + Vector((0, 0, -0.3 * k * k)); s = r0 + (r1 - r0) * k; o.scale = (s, s, s * 0.8)
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f); dn.inputs[1].default_value = d; dn.inputs[1].keyframe_insert('default_value', frame=f)
    return o

def v11_breach():
    random.seed(1101); wall = O('hall wall 1'); bmod = wall.modifiers['breach']
    # 1) wall whole until the hit: boolean + blocks switched on at f588
    for f, on in ((1, False), (587, False), (588, True)):
        bmod.show_render = bmod.show_viewport = on; bmod.keyframe_insert('show_render', frame=f); bmod.keyframe_insert('show_viewport', frame=f)
    # 2) jagged hole: noise-displaced sphere cutter instead of a box
    cut = O('wall breach cut'); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in bm.verts:
        n = math.sin(v.co.x * 7.1 + v.co.y * 3.3) * 0.5 + math.sin(v.co.z * 9.7 + v.co.y * 5.9) * 0.5
        v.co *= 1.0 + 0.16 * n + random.uniform(-0.05, 0.05)
    me = bpy.data.meshes.new('breach cut jagged'); bm.to_mesh(me); bm.free(); old = cut.data; cut.data = me; bpy.data.meshes.remove(old)
    cut.scale = (2.4, 5.7, 5.5); cut.location = (10.5, 0.75, 4.7)
    # 3) blocks -> irregular fractured rock, varied sizes; hidden until the hit (they ARE the wall that breaks)
    blocks = [o for o in bpy.data.objects if o.name.startswith('breach block')]
    for i, b in enumerate(blocks):
        r = random.random(); sz = (0.42, 0.55, 0.5) if r < 0.25 else (0.3, 0.38, 0.32) if r < 0.7 else (0.2, 0.24, 0.2)       # slabs / chunks / small
        old = b.data; b.data = _hull(f'rock {i}', (sz[0] * random.uniform(0.8, 1.25), sz[1] * random.uniform(0.8, 1.25), sz[2] * random.uniform(0.8, 1.25)), 1100 + i)
        bpy.data.meshes.remove(old); b.modifiers.clear()
        for f, h in ((1, True), (587, True), (588, False)): b.hide_render = b.hide_viewport = h; b.keyframe_insert('hide_render', frame=f); b.keyframe_insert('hide_viewport', frame=f)
    # 4) gravel + grit: two particle bursts of small fractured stones from the breach face (sideways + outward, like the blocks)
    gravel = bpy.data.collections.new('fx gravel'); bpy.context.scene.collection.children.link(gravel); gravel.hide_render = False
    for k in range(6):
        g = bpy.data.objects.new(f'gravel {k}', _hull(f'gravel {k}', (0.07, 0.09, 0.06), 1200 + k)); gravel.objects.link(g); g.location = (200, 200, 0)
    lc = bpy.context.view_layer.layer_collection.children.get('fx gravel')
    for nm, cnt, spd, sz, t0, t1 in (('breach gravel', 900, 7.0, 1.0, 588, 598), ('breach grit', 2500, 4.0, 0.35, 588, 604)):
        em = bpy.data.objects.new(nm, bpy.data.meshes.new(nm)); coll('fx').objects.link(em); bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=6, y_segments=6, size=1.0); bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
        bm.to_mesh(em.data); bm.free(); em.location = (9.45, 0.75, 4.2); em.scale = (1, 4.4, 4.2); em.show_instancer_for_render = False; em.show_instancer_for_viewport = False
        st = em.modifiers.new(nm, 'PARTICLE_SYSTEM').particle_system.settings; st.count = cnt; st.frame_start = t0; st.frame_end = t1; st.lifetime = 70; st.lifetime_random = 0.4
        st.normal_factor = spd; st.factor_random = spd * 0.6; st.effector_weights.gravity = 1.0; st.render_type = 'COLLECTION'; st.instance_collection = gravel; st.use_collection_pick_random = True
        st.particle_size = sz; st.size_random = 0.8; st.use_rotations = True; st.rotation_factor_random = 1.0; st.angular_velocity_factor = 6.0
    # 5) dust: a rolling wall of volumetric clouds out of both faces of the wall + a slow pall that hangs after
    n = 0
    for k in range(14):
        y = random.uniform(-3.5, 5.0); z = random.uniform(0.6, 7.5); side = 1 if y >= 0.75 else -1
        puff(f'breach dust {k}', (10.5 + random.uniform(-0.8, 1.2), y, z), (random.uniform(1.5, 4.5), side * random.uniform(0.5, 2.5), random.uniform(-0.3, 0.6)),
             588 + random.randint(0, 6), random.randint(40, 52), random.uniform(0.4, 0.8), random.uniform(2.4, 3.8), random.uniform(1.2, 2.2)); n += 1
    for k in range(5):
        puff(f'breach pall {k}', (12.5 + k * 1.2, random.uniform(-3, 4), random.uniform(0.8, 3)), (0.6, random.uniform(-0.4, 0.4), 0.15), 596 + k * 3, 44, 1.0, 4.5, 0.6); n += 1
    for k in range(4):                                                                     # interior side too: dust blows back into the hall
        puff(f'breach back {k}', (9.0, random.uniform(-2.5, 3.5), random.uniform(1, 5)), (-1.8, random.uniform(-1, 1), 0.1), 590 + k * 2, 40, 0.5, 3.0, 1.0); n += 1
    return f'breach: wall whole until f588, jagged hole, {len(blocks)} fractured rocks (slab/chunk/small), 900 gravel + 2500 grit, {n} volumetric dust clouds'

def v11_shatter_dust():
    """the stone shell bursting off: dust plumes rise where the reveal front passes (times match v9's chunk bursts)"""
    rig = O('dragon_rig'); scn.frame_set(1); bpy.context.view_layer.update(); H = rig.matrix_world @ rig.pose.bones['head'].head; random.seed(1102); n = 0
    for nm in [o.name for o in coll('dragon').objects if o.type == 'MESH' and (o.name in ('torso frame', 'skull core') or o.name.startswith(('neck core', 'tail core')))]:
        o = O(nm); p = o.matrix_world.translation; d = (p - H).length; t0 = int(60 + max(0.0, d - 0.5) / 9.3 * 52)
        puff(f'shell dust {n}', p + Vector((random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 0.2)), (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 0.6),
             t0, 46, 0.3, 1.8 if nm == 'torso frame' else 1.3, 1.6, '#6A655C'); n += 1
    for k in range(6):                                                                     # low pall over the floor after the burst
        puff(f'shell pall {k}', (random.uniform(-2.5, 2.5), random.uniform(-2.5, 3.5), 0.4), (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0.05), 90 + k * 4, 60, 0.8, 3.4, 0.45, '#6A655C'); n += 1
    return f'shatter dust: {n} volumetric plumes along the body + floor pall'
