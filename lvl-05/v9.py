# LVL 05 v9 — owner story (2026-10-21): stone statue -> eyes glow first -> cyan cracks race over it, the stone shell shatters off
# -> (existing awakening, shifted +120 f) -> turns, charges, smashes through the hall wall, flies up into a night storm. 640 f ≈ 26.7 s.
OFF = 120
def v9_offset():
    """push every existing animation 120 frames later so the stone reveal owns frames 1-120"""
    for a in bpy.data.actions:
        for fc in _curves(a):
            for kp in fc.keyframe_points: kp.co.x += OFF; kp.handle_left.x += OFF; kp.handle_right.x += OFF
    n = 0
    for idb in list(bpy.data.objects) + list(bpy.data.materials) + list(bpy.data.node_groups) + list(bpy.data.lights):
        tree = getattr(idb, 'node_tree', None)
        for holder in (idb, tree):
            ad = getattr(holder, 'animation_data', None) if holder else None
            if ad:
                for d in ad.drivers:
                    e = d.driver.expression
                    if 'frame' in e and 'frame - %d' % OFF not in e: d.driver.expression = e.replace('frame', f'(frame - {OFF})'); n += 1
    for ps in bpy.data.particles: ps.frame_start += OFF; ps.frame_end += OFF
    scn.frame_end = 640
    return f'offset: all keys/particles +{OFF} f, {n} frame drivers re-based; frame_end 640'

# ---------------------------------------------------------------- stone statue + reveal wave (one node group inserted in front of every dragon material output)
def v9_stone():
    rig = O('dragon_rig'); scn.frame_set(1); bpy.context.view_layer.update()
    H = rig.matrix_world @ rig.pose.bones['head'].head
    ctrl = bpy.data.objects.new('reveal ctrl', None); coll('fx').objects.link(ctrl); ctrl['R'] = -1.0
    for f, r in ((1, -1.0), (52, -1.0), (60, 0.5), (112, 9.8), (120, 14.0), (124, 900.0)): ctrl['R'] = r; ctrl.keyframe_insert('["R"]', frame=f)
    for fc in _curves(ctrl.animation_data.action):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    g = bpy.data.node_groups.new('NG_reveal', 'ShaderNodeTree')
    g.interface.new_socket('Shader', in_out='INPUT', socket_type='NodeSocketShader'); g.interface.new_socket('Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
    N = g.nodes; L = g.links.new
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    geo = N.new('ShaderNodeNewGeometry'); dist = N.new('ShaderNodeVectorMath'); dist.operation = 'DISTANCE'; dist.inputs[1].default_value = H; L(geo.outputs['Position'], dist.inputs[0])
    rv = N.new('ShaderNodeValue'); rv.name = 'R'; dr = rv.outputs[0].driver_add('default_value'); v = dr.driver.variables.new(); v.name = 'r'
    v.targets[0].id_type = 'OBJECT'; v.targets[0].id = ctrl; v.targets[0].data_path = '["R"]'; dr.driver.expression = 'r'
    x = N.new('ShaderNodeMath'); x.operation = 'SUBTRACT'; L(rv.outputs[0], x.inputs[0]); L(dist.outputs['Value'], x.inputs[1])        # x > 0 : revealed
    fac = N.new('ShaderNodeMapRange'); fac.inputs['From Min'].default_value = -0.2; fac.inputs['From Max'].default_value = 0.05; L(x.outputs[0], fac.inputs['Value'])
    # weathered stone: two-tone noise, rough, chiselled bump
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; nz.inputs['Detail'].default_value = 10; L(geo.outputs['Position'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*lin('#2C2B28'), 1); cr.color_ramp.elements[1].color = (*lin('#5A5850'), 1); L(nz.outputs['Fac'], cr.inputs['Fac'])
    st = N.new('ShaderNodeBsdfPrincipled'); st.inputs['Roughness'].default_value = 0.93; L(cr.outputs['Color'], st.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; L(nz.outputs['Fac'], bp.inputs['Height']); L(bp.outputs['Normal'], st.inputs['Normal'])
    # cracks: Voronoi edges, glowing cyan only in a band around the wave front
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 4.5; L(geo.outputs['Position'], vo.inputs['Vector'])
    ck = N.new('ShaderNodeMapRange'); ck.inputs['From Min'].default_value = 0.0; ck.inputs['From Max'].default_value = 0.03; ck.inputs['To Min'].default_value = 1.0; ck.inputs['To Max'].default_value = 0.0; L(vo.outputs['Distance'], ck.inputs['Value'])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L(x.outputs[0], ab.inputs[0])
    band = N.new('ShaderNodeMapRange'); band.inputs['From Min'].default_value = 0.0; band.inputs['From Max'].default_value = 0.9; band.inputs['To Min'].default_value = 1.0; band.inputs['To Max'].default_value = 0.0; L(ab.outputs[0], band.inputs['Value'])
    mk = N.new('ShaderNodeMath'); mk.operation = 'MULTIPLY'; L(ck.outputs['Result'], mk.inputs[0]); L(band.outputs['Result'], mk.inputs[1])
    ks = N.new('ShaderNodeMath'); ks.operation = 'MULTIPLY'; ks.inputs[1].default_value = 30.0; L(mk.outputs[0], ks.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*lin('#46D9E6'), 1); L(ks.outputs[0], em.inputs['Strength'])
    mx = N.new('ShaderNodeMixShader'); L(fac.outputs['Result'], mx.inputs['Fac']); L(st.outputs[0], mx.inputs[1]); L(gi.outputs[0], mx.inputs[2])
    ad = N.new('ShaderNodeAddShader'); L(mx.outputs[0], ad.inputs[0]); L(em.outputs[0], ad.inputs[1]); L(ad.outputs[0], go.inputs[0])
    skip = {'M_eye', 'M_eye_halo', 'M_pupil', 'M_beam', 'M_beam_glow', 'M_spark', 'M_firelight', 'M_fire', 'M_dust'}
    mats = set()
    for o in coll('dragon').objects:
        for sl in getattr(o, 'material_slots', []):
            if sl.material and sl.material.name not in skip: mats.add(sl.material)
        if o.type == 'MESH' and o.data.materials:
            for m in o.data.materials:
                if m and m.name not in skip: mats.add(m)
    for m in mats:
        nt = m.node_tree; out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not out or not out.inputs['Surface'].links: continue
        src = out.inputs['Surface'].links[0].from_socket; gn = nt.nodes.new('ShaderNodeGroup'); gn.node_tree = g
        nt.links.new(src, gn.inputs[0]); nt.links.new(gn.outputs[0], out.inputs['Surface'])
    # eyes glow FIRST (inside the stone), everything else ignites later with the shifted timeline
    for idb in (M('M_eye').node_tree, M('M_eye_halo').node_tree):
        for fc in _curves(idb.animation_data.action):
            for kp in [kp for kp in fc.keyframe_points if kp.co.x < 70 + OFF][::-1]: fc.keyframe_points.remove(kp)
    for f, v in ((1, 0), (22, 0), (27, 6), (30, 0.8), (35, 10), (40, 3), (46, 9)): emit_key('M_eye', f, v); emit_key('M_eye_halo', f, v * 0.25)
    for S in 'LR':
        lg = O(f'eye glow {S}').data
        for fc in _curves(lg.animation_data.action):
            for kp in [kp for kp in fc.keyframe_points if kp.co.x < 70 + OFF][::-1]: fc.keyframe_points.remove(kp)
        for f, v in ((1, 0), (22, 0), (27, 24), (30, 3), (35, 40), (40, 12), (46, 36)): lg.energy = v; lg.keyframe_insert('energy', frame=f)
    # stone shell shatters off as the front passes: chunk bursts from the big core parts, timed by their distance to the head
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.07)
    for vv in bm.verts: vv.co *= random.uniform(0.6, 1.3)
    chunk = mesh_obj('fx stone chunk', bm, 'M_stone', False, 'fx'); chunk.location = (0, 0, -50)
    random.seed(9); n = 0
    names = [o.name for o in coll('dragon').objects if o.type == 'MESH' and (o.name in ('torso frame', 'skull core', 'jaw core') or
             o.name.startswith(('neck core', 'tail core', 'wing L bone', 'wing R bone')) or (' bone ' in o.name and o.name[:2] in LEGS))]
    for nm in names:
        o = O(nm); d = (o.matrix_world.translation - H).length; t0 = int(60 + max(0.0, d - 0.5) / 9.3 * 52)
        st_ = o.modifiers.new('stone shatter', 'PARTICLE_SYSTEM').particle_system.settings
        st_.count = 160 if nm == 'torso frame' else 50; st_.frame_start = t0; st_.frame_end = t0 + 4; st_.lifetime = 70; st_.emit_from = 'FACE'
        st_.normal_factor = 2.2; st_.factor_random = 1.2; st_.effector_weights.gravity = 1.0; st_.render_type = 'OBJECT'; st_.instance_object = chunk
        st_.particle_size = 1.0; st_.size_random = 0.8; st_.use_rotations = True; st_.rotation_factor_random = 1.0; st_.angular_velocity_factor = 4.0; n += 1
    # statue camera: slow push on the stone head, then pull back as the shell bursts
    cam, tgt = O('cam'), O('cam target')
    for f, c, t in ((1, (2.4, -6.4, 1.3), (0.9, -1.7, 0.45)), (48, (2.0, -5.3, 1.05), (0.95, -1.75, 0.4)), (100, (2.9, -7.4, 1.6), (0.6, -1.1, 0.6))):
        cam.location = c; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
    return f'stone: reveal group on {len(mats)} materials, wave 60-120 from the head, eyes glow 22-46, {n} shatter bursts'

# ---------------------------------------------------------------- night storm sky (world) + lightning
def v9_sky():
    w = scn.world.node_tree; out = next(n for n in w.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in w.nodes if n.type == 'BACKGROUND')
    tc = w.nodes.new('ShaderNodeTexCoord'); nz = w.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 2.2; nz.inputs['Detail'].default_value = 12; nz.inputs['Roughness'].default_value = 0.62
    w.links.new(tc.outputs['Generated'], nz.inputs['Vector']); d = nz.inputs['W'].driver_add('default_value'); d.driver.expression = 'frame * 0.003'
    cr = w.nodes.new('ShaderNodeValToRGB'); E = cr.color_ramp.elements; E[0].position = 0.35; E[0].color = (*lin('#020306'), 1); E[1].position = 0.75; E[1].color = (*lin('#8C9AAA'), 1)
    w.links.new(nz.outputs['Fac'], cr.inputs['Fac'])
    md = Vector((0.55, 0.35, 0.76)).normalized(); dp = w.nodes.new('ShaderNodeVectorMath'); dp.operation = 'DOT_PRODUCT'; dp.inputs[1].default_value = md; w.links.new(tc.outputs['Generated'], dp.inputs[0])
    pw = w.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 400; w.links.new(dp.outputs['Value'], pw.inputs[0])
    gl = w.nodes.new('ShaderNodeMath'); gl.operation = 'POWER'; gl.inputs[1].default_value = 12; w.links.new(dp.outputs['Value'], gl.inputs[0])
    sm = w.nodes.new('ShaderNodeMath'); sm.operation = 'MULTIPLY_ADD'; sm.inputs[1].default_value = 0.25; w.links.new(gl.outputs[0], sm.inputs[0]); w.links.new(pw.outputs[0], sm.inputs[2])
    mc = w.nodes.new('ShaderNodeMix'); mc.data_type = 'RGBA'; mc.blend_type = 'ADD'; mc.inputs['B'].default_value = (*lin('#C8D6E8'), 1)
    w.links.new(cr.outputs['Color'], mc.inputs['A']); w.links.new(sm.outputs[0], mc.inputs['Factor'])
    w.links.new(mc.outputs['Result'], bg.inputs['Color'])
    for f, v in ((1, 0.25), (586, 0.25), (594, 2.0), (595, 2.0), (596, 6.0), (599, 2.0), (611, 2.0), (612, 5.0), (615, 2.0), (629, 2.0), (630, 6.5), (634, 2.0)):           # lightning lights the clouds
        bg.inputs['Strength'].default_value = v; bg.inputs['Strength'].keyframe_insert('default_value', frame=f)
    l = bpy.data.lights.new('lightning', 'SUN'); l.color = lin('#C8DCFF'); l.angle = math.radians(4); o = bpy.data.objects.new('lightning', l); coll('light').objects.link(o)
    o.rotation_euler = (math.radians(35), math.radians(-20), math.radians(30))
    for f, v in ((1, 0), (595, 0), (596, 22), (598, 2), (599, 0), (611, 0), (612, 16), (614, 0), (629, 0), (630, 26), (633, 0)): l.energy = v; l.keyframe_insert('energy', frame=f)
    # EEVEE: a world volume absorbs the whole sky background -> move the haze into a box around the hall only
    vol = next(n for n in w.nodes if n.type == 'PRINCIPLED_VOLUME'); dens, col, an = vol.inputs['Density'].default_value, tuple(vol.inputs['Color'].default_value), vol.inputs['Anisotropy'].default_value
    for l_ in list(out.inputs['Volume'].links): w.links.remove(l_)
    hm = bpy.data.materials.new('M_hall_haze'); hm.use_nodes = True; hn = hm.node_tree
    for n_ in list(hn.nodes):
        if n_.type != 'OUTPUT_MATERIAL': hn.nodes.remove(n_)
    hv = hn.nodes.new('ShaderNodeVolumePrincipled'); hv.inputs['Density'].default_value = dens; hv.inputs['Color'].default_value = col; hv.inputs['Anisotropy'].default_value = an
    hn.links.new(hv.outputs[0], next(n_ for n_ in hn.nodes if n_.type == 'OUTPUT_MATERIAL').inputs['Volume'])
    hz = box('hall haze', (20.5, 26, 15), 'M_hall_haze', (0, 5, 7.4), bev=0.0, cname='ruins')
    ml = bpy.data.lights.new('moon sun', 'SUN'); ml.color = lin('#B4C2D4'); ml.angle = math.radians(1.5); mo = bpy.data.objects.new('moon sun', ml); coll('light').objects.link(mo)
    mo.rotation_euler = (Vector((0, 0, 0)) - Vector((0.55, 0.35, 0.76)) * 10).to_track_quat('-Z', 'Y').to_euler()   # from the moon in the sky dome
    for f, v in ((1, 0), (588, 0), (594, 9.0), (640, 9.0)): ml.energy = v; ml.keyframe_insert('energy', frame=f)
    for k in range(5):                                                                    # distant ridge silhouettes beyond the broken wall
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=40, y_segments=6, size=1)
        for vv in bm.verts:
            vv.co.x *= 40; vv.co.y *= 6; vv.co.z = max(0.0, (math.sin(vv.co.x * 0.21 + k) * 0.5 + 0.5) * random.uniform(6, 14) * (0.5 - vv.co.y / 12))
        rg = mesh_obj(f'ridge {k}', bm, 'M_stone', False, 'ruins'); rg.location = (45 + k * 12, 10 - k * 6, 0); rg.rotation_euler.z = math.radians(90 + k * 8)
        rg.hide_render = True                                                          # v10: low-poly ridges read cheap next to the breach; storm clouds alone
    return 'sky: storm-cloud world with moon + glow, lightning sun + cloud flashes at 596/612/630, ridge silhouettes'

# ---------------------------------------------------------------- finale: turn to the right wall, charge, smash through, fly up into the storm
def v9_finale():
    rig = O('dragon_rig'); P = rig.pose.bones; random.seed(66); scn.frame_set(556)
    for nm in ('buttress 10', 'buttress 11'):                                            # buttresses stand in the breach path
        if nm in bpy.data.objects: O(nm).hide_render = True; O(nm).hide_viewport = True
    # breakable section in the right hall wall: boolean hole filled with loose blocks
    wall = O('hall wall 1'); cut = box('wall breach cut', (3.0, 9.6, 9.4), 'M_stone', (10.5, 0.75, 4.5), bev=0.0, cname='ruins'); cut.hide_render = True; cut.hide_viewport = True
    b = wall.modifiers.new('breach', 'BOOLEAN'); b.operation = 'DIFFERENCE'; b.object = cut
    IMP = Vector((9.5, 0.3, 2.6)); bricks = []
    for layer, x in enumerate((9.9, 10.9)):
        for iy in range(9):
            for iz in range(10):
                br = box(f'breach block {layer}{iy}{iz}', (0.98, 1.04, 0.92), 'M_stone', bev=0.05, cname='ruins')
                br.location = (x + random.uniform(-0.03, 0.03), -3.49 + iy * 1.06, 0.46 + iz * 0.93); br.rotation_euler = (random.uniform(-0.02, 0.02), 0, random.uniform(-0.02, 0.02)); bricks.append(br)
    for br in bricks:
        p0 = br.location.copy(); r0 = br.rotation_euler.copy(); dist = (p0 - IMP).length
        side = 1 if p0.y >= 0.75 else -1                                                  # v10: blasted sideways OUT of the flight path, fast
        t0 = 588 + int(dist * 0.3); v = Vector((random.uniform(5, 9), side * random.uniform(6, 10), random.uniform(0.5, 3.0)))
        br.keyframe_insert('location', frame=t0); br.keyframe_insert('rotation_euler', frame=t0)
        for dtf in (6, 14, 26, 44):
            t = dtf / 24; p = p0 + v * t + Vector((0, 0, -4.9 * t * t)); p.z = max(0.4, p.z); br.location = p
            br.rotation_euler = (r0.x + random.uniform(-4, 4) * t, r0.y + random.uniform(-4, 4) * t, r0.z + random.uniform(-3, 3) * t)
            br.keyframe_insert('location', frame=t0 + dtf); br.keyframe_insert('rotation_euler', frame=t0 + dtf)
    # dust burst at the breach
    em = bpy.data.objects.new('breach dust', bpy.data.meshes.new('breach dust')); coll('fx').objects.link(em); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.8); bm.to_mesh(em.data); bm.free()
    em.location = IMP + Vector((0.6, 0, 0)); em.show_instancer_for_render = False
    st = em.modifiers.new('dust', 'PARTICLE_SYSTEM').particle_system.settings; st.count = 500; st.frame_start = 588; st.frame_end = 596; st.lifetime = 50; st.normal_factor = 3.5; st.factor_random = 2.0
    st.effector_weights.gravity = 0.4; st.render_type = 'OBJECT'; st.instance_object = O('fx stone chunk'); st.particle_size = 0.6; st.size_random = 0.9
    # body: neck/head back to rest, root yaw to face +X, charge, impact, burst through, climb + pitch up into the sky
    def key_root(f, loc, yaw, pitch):
        q = Quaternion((0, -1, 0), math.radians(pitch)) @ Quaternion((0, 0, 1), math.radians(yaw))
        P['root'].location = loc; P['root'].rotation_quaternion = q
        P['root'].keyframe_insert('location', frame=f); P['root'].keyframe_insert('rotation_quaternion', frame=f)
    for nm in ('neck.5', 'head', 'jaw'):
        P[nm].rotation_quaternion = (1, 0, 0, 0); P[nm].keyframe_insert('rotation_quaternion', frame=556)
    for f, loc, yaw, pitch in ((540, (0, 0, 0), 0, 0), (560, (0.3, 0.2, 0.0), 90, -4), (572, (2.0, 0.2, 0.35), 90, 4), (588, (6.9, 0.2, 0.9), 90, 2),
                               (596, (10.5, 0.2, 1.6), 90, 10), (606, (15.0, 0.6, 4.0), 90, 24), (622, (22.0, 1.2, 11.0), 90, 38), (640, (29.0, 1.8, 20.0), 90, 44)):
        key_root(f, Vector(loc), yaw, pitch)
    # wing beats from 562: up/down about the body axis (world Y in each wing bone's rest space); legs tuck after take-off
    for side, s in (('L', -1), ('R', 1)):
        pb = P[f'wing.{side}.0']; ax = (pb.bone.matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized()
        pb.keyframe_insert('rotation_quaternion', frame=556)
        for k, f in enumerate(range(562, 641, 7)):
            ang = (38 if k % 2 == 0 else -28) * -s; pb.rotation_quaternion = Quaternion(ax, math.radians(ang)); pb.keyframe_insert('rotation_quaternion', frame=f)
    scn.frame_set(594)
    for leg in LEGS:
        pb = P[f'leg.{leg}.0']; ax = (pb.bone.matrix_local.to_3x3().inverted() @ Vector((1, 0, 0))).normalized(); pb.keyframe_insert('rotation_quaternion', frame=594)
        pb.rotation_quaternion = Quaternion(ax, math.radians(-55 if 'F' in leg else 50)); pb.keyframe_insert('rotation_quaternion', frame=606)
    for f, deg in ((556, 0), (574, 0), (582, 30), (592, 30), (600, 8)):                        # roar into the charge
        P['jaw'].rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(deg)); P['jaw'].keyframe_insert('rotation_quaternion', frame=f)
    # camera: side-on charge, impact from inside, then outside looking up as it climbs into the storm
    cam, tgt = O('cam'), O('cam target')
    for f, c, t in ((544, (-3.0, -10.5, 3.2), (3.5, 0.0, 2.4)), (574, (3.0, -8.0, 2.2), (8.0, 0.2, 2.4)), (590, (5.6, -5.8, 1.9), (10.0, 0.2, 3.0)), (597, (6.2, -5.2, 2.0), (10.5, 0.2, 3.2)),
                    (598, (15.5, -7.5, 1.6), (11.5, 0.3, 2.6)), (610, (17.0, -7.0, 3.0), (16.0, 0.8, 5.5)), (624, (19.0, -6.5, 8.0), (23.0, 1.3, 12.5)), (640, (23.5, -6.0, 13.5), (29.5, 1.8, 20.5))):
        cam.location = c; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
    for fc in _curves(cam.animation_data.action) + _curves(tgt.animation_data.action):
        for kp in fc.keyframe_points:
            if kp.co.x >= 588: kp.interpolation = 'CONSTANT' if kp.co.x == 597 else 'BEZIER'   # hard cut to outside at the breach
    scn.render.motion_blur_shutter = 0.35
    # flight lights: they ride outside the hall and track the chest (the hall's hero spots can't reach out here)
    tc = O('aim chest')
    for nm, loc, e, hx in (('flight key', (24.0, -16.0, 9.0), 90000, '#D2DCE8'), ('flight rim', (34.0, 14.0, 30.0), 120000, '#46D9E6')):
        l = bpy.data.lights.new(nm, 'SPOT'); l.color = lin(hx); l.spot_size = math.radians(30); l.spot_blend = 0.4; o = bpy.data.objects.new(nm, l); coll('light').objects.link(o); o.location = loc
        c = o.constraints.new('TRACK_TO'); c.target = tc; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
        for f, v in ((1, 0), (592, 0), (598, e), (640, e)): l.energy = v; l.keyframe_insert('energy', frame=f)
    return f'finale: {len(bricks)} breach blocks blown out from frame 588, charge 560-588, flight out + climb to 640, wing beats, camera follows into the storm'
