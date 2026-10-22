# LVL 05 v10 — owner (2026-10-21): "make sure eyes are placed correctly… wings should follow physics… legs horizontal in flight…
# no objects should collide with wings or go through wings"
# ---------------------------------------------------------------- eyes: short almond slits seated in sockets under the brow, hot pupil
def v10_eyes():
    h0 = Vector(NECK[-1]); _emit('M_pupil', '#F2FFFF', 0.0)
    for nm in ('eye socket', 'eye slit', 'eye halo', 'eye pupil'):
        for S in 'LR':
            o = bpy.data.objects.get(f'{nm} {S}')
            if o: bpy.data.objects.remove(o, do_unlink=True)
    for s, S in ((-1, 'L'), (1, 'R')):
        along = (-s * 0.28, -1, -0.32); c = h0 + Vector((s * 0.305, -0.56, 0.155))
        part(aimed(box(f'eye socket {S}', (0.05, 0.32, 0.13), 'M_frame', bev=0.02, taper=(1, 0.45)), along, c + Vector((-s * 0.012, 0, 0))), 'head')
        part(aimed(box(f'eye slit {S}', (0.03, 0.25, 0.06), 'M_eye', bev=0.012, taper=(1, 0.3)), along, c + Vector((s * 0.012, 0, 0))), 'head')
        part(aimed(box(f'eye pupil {S}', (0.034, 0.024, 0.07), 'M_pupil', bev=0.006), along, c + Vector((s * 0.016, -0.02, 0.004))), 'head')     # vertical slit pupil
        part(aimed(box(f'eye halo {S}', (0.04, 0.28, 0.09), 'M_eye_halo', bev=0.02, taper=(1, 0.4)), along, c + Vector((s * 0.02, 0, 0))), 'head')
        lg = bpy.data.objects.get(f'eye glow {S}')
        if lg: lg.location = c + Vector((s * 0.14, -0.06, 0.0))
    return 'eyes: 25 cm almond slits seated in 32 cm sockets under the brow blades, vertical white-hot pupils, halos, socket lights moved'

# ---------------------------------------------------------------- flight physics
def _drop_keys(rig, pred, f_from):
    for fc in _curves(rig.animation_data.action):
        if fc.data_path.startswith('pose.bones["'):
            bn = fc.data_path.split('"')[1]
            if pred(bn):
                for kp in [kp for kp in fc.keyframe_points if kp.co.x >= f_from][::-1]: fc.keyframe_points.remove(kp)
def v10_flight():
    rig = O('dragon_rig'); P = rig.pose.bones; F0 = 541
    for fc in _curves(M('M_eye').node_tree.animation_data.action):                     # pupils ignite with the slits, hotter
        for kp in fc.keyframe_points: emit_key('M_pupil', kp.co.x, kp.co.y * 1.8)
    _drop_keys(rig, lambda b: b == 'root' or b.startswith(('wing.', 'leg.', 'tail.')), F0)
    def K(pb, f, q): pb.rotation_quaternion = q; pb.keyframe_insert('rotation_quaternion', frame=f)
    def ax_rest(pb, world_axis): return (pb.bone.matrix_local.to_3x3().inverted() @ Vector(world_axis)).normalized()
    I = Quaternion((1, 0, 0, 0)); wingbones = [pb for pb in P if pb.name.startswith('wing.')]
    # 1) root path (same beats as v9) + flight bob: body rises on each downstroke, dips on the upstroke, pitch breathes ±3°
    base = [(541, (0, 0, 0), 0, 0), (560, (0.3, 0.2, 0.0), 90, -4), (572, (2.0, 0.2, 0.35), 90, 4), (588, (6.9, 0.2, 0.9), 90, 2),
            (596, (10.5, 0.2, 1.6), 90, 10), (606, (15.0, 0.6, 4.0), 90, 24), (622, (22.0, 1.2, 11.0), 90, 38), (640, (29.0, 1.8, 20.0), 90, 44)]
    def lerp_path(f):
        for (fa, la, ya, pa), (fb, lb, yb, pb_) in zip(base, base[1:]):
            if fa <= f <= fb:
                t = (f - fa) / (fb - fa); t = t * t * (3 - 2 * t)
                return Vector(la).lerp(Vector(lb), t), ya + (yb - ya) * t, pa + (pb_ - pa) * t
        return Vector(base[-1][1]), base[-1][2], base[-1][3]
    PERIOD = 12; FLAP0 = 616                                                           # wings stay tucked until the body is ~6 m clear of the wall
    def flap_phase(f): return ((f - FLAP0) % PERIOD) / PERIOD if f >= FLAP0 else None
    for f in list(range(541, 600, 4)) + list(range(600, 641, 2)):
        loc, yaw, pit = lerp_path(f); ph = flap_phase(f)
        if ph is not None:
            loc = loc + Vector((0, 0, 0.28 * math.sin(2 * math.pi * (ph - 0.1)))); pit += 3 * math.sin(2 * math.pi * ph)
        P['root'].location = loc; P['root'].rotation_quaternion = Quaternion((0, -1, 0), math.radians(pit)) @ Quaternion((0, 0, 1), math.radians(yaw))
        P['root'].keyframe_insert('location', frame=f); P['root'].keyframe_insert('rotation_quaternion', frame=f)
    # 2) wings: tucked tight (sleep fold) for the turn + charge + breach so they never touch pillars, chains or the wall; open + flap outside
    scn.frame_set(F0)
    for pb in wingbones: pb.keyframe_insert('rotation_quaternion', frame=F0)
    for pb in wingbones:
        q = SLEEP[pb.name][0]
        for f, t in ((552, 0.9), (614, 0.9)): K(pb, f, _qt(q, t))
    for side, s in (('L', -1), ('R', 1)):
        p0, p1 = P[f'wing.{side}.0'], P[f'wing.{side}.1']; a0, a1 = ax_rest(p0, (0, 1, 0)), ax_rest(p1, (0, 1, 0))
        feathers = [P[f'wing.{side}.f{k}'] for k in range(len(FEATHERS))]
        K(p0, 620, Quaternion(a0, math.radians(-s * 40))); K(p1, 622, I)                 # unfold straight into the first upstroke
        for fb in feathers: K(fb, 622, I)
        for c in range(FLAP0 + 6, 641, PERIOD):                                           # each cycle: top -> fast downstroke (5 f) -> slow upstroke (7 f)
            top, bot = c, c + 5
            K(p0, top, Quaternion(a0, math.radians(-s * 42))); K(p0, bot, Quaternion(a0, math.radians(s * 32)))
            K(p1, top + 2, Quaternion(a1, math.radians(-s * 8))); K(p1, bot + 2, Quaternion(a1, math.radians(s * 20)))   # forearm lags 2 f, tip whips
            for k, fb in enumerate(feathers):
                lag = 3 + k // 4
                K(fb, bot + lag, I)                                                       # fully spread at the bottom (air pushes them open)
                K(fb, top + PERIOD - 3 + lag // 2, _qt(SLEEP[fb.name][0], 0.28))        # half-fold on the upstroke (less drag)
    # 3) legs: gallop on the charge, push at take-off, then trail straight back along the body (horizontal) for the whole flight
    for leg in LEGS:
        p0, p1 = P[f'leg.{leg}.0'], P[f'leg.{leg}.1']; ph0 = 0 if leg[0] == 'F' else 0.5; a0, a1 = ax_rest(p0, (1, 0, 0)), ax_rest(p1, (1, 0, 0))
        K(p0, F0, I); K(p1, F0, I)
        for f in range(562, 590, 4):
            w = math.sin(2 * math.pi * ((f - 562) / 10 + ph0))
            K(p0, f, Quaternion(a0, math.radians(24 * w))); K(p1, f, Quaternion(a1, math.radians(-30 * max(0, w))))
        K(P[f'leg.{leg}.2'], F0, I)
    for f in (598, 610, 624, 640):
        scn.frame_set(f); bpy.context.view_layer.update()
        back = (P['root'].matrix.to_3x3() @ Vector((0, 1, -0.06))).normalized()
        for leg in LEGS:
            for i in range(3):
                d = back if i < 2 else (back + (P['root'].matrix.to_3x3() @ Vector((0, 0, -0.35)))).normalized()   # feet angle slightly down, claws trailing
                aim(P[f'leg.{leg}.{i}'], d); P[f'leg.{leg}.{i}'].keyframe_insert('rotation_quaternion', frame=f)
    # 4) tail trails and sways a beat behind the flaps
    tails = [pb for pb in P if pb.name.startswith('tail.')]
    for pb in tails: K(pb, F0, I)
    for i, pb in enumerate(tails):
        ax = ax_rest(pb, (0, 0, 1))
        for f in range(600, 641, 6): K(pb, f, Quaternion(ax, math.radians(5 * math.sin(2 * math.pi * (f - 600 - i * 2) / 24))))
    for fc in _curves(rig.animation_data.action):
        for kp in fc.keyframe_points:
            if kp.co.x >= F0: kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    return 'flight: wings tucked 552-598 (turn/charge/breach), unfold 604, 12-f flap cycles (fast down / slow up, forearm lag 2 f, feathers spread on down + half-fold on up), body bob + pitch breathing, legs gallop then trail horizontal, tail sway'

# ---------------------------------------------------------------- sleep fold v10: wings folded high over the back, feathers fanned up and out
# (v9 fold sank the feathers into the floor and through the curled tail — collide.py: 1294 tail hits, 122 floor hits)
_capture_sleep_v1 = capture_sleep
def capture_sleep(rig):
    _capture_sleep_v1(rig); P = rig.pose.bones
    for side in 'LR':
        s = -1 if side == 'L' else 1
        aim(P[f'wing.{side}.0'], (s * 0.42, 0.62, 0.66)); aim(P[f'wing.{side}.1'], (s * 0.3, 0.95, 0.02))
        for k in range(len(FEATHERS)): aim(P[f'wing.{side}.f{k}'], (s * (0.22 + 0.045 * k), 1, 0.24 - 0.006 * k))
    for pb in P: SLEEP[pb.name] = (pb.rotation_quaternion.copy(), pb.location.copy())

# ---------------------------------------------------------------- wing clearance zone: nothing stands where the wings sweep
def v10_clear():
    KEEP = ('flagstone', 'rune', 'ruin floor', 'ground mist', 'hall', 'terminal', 'husk', 'brazier', 'scorch', 'claw', 'buttress', 'portal', 'ceiling', 'root ', 'guardian', 'ridge', 'breach', 'window', 'floor spanner', 'back wall', 'lintel')
    XMIN = 7.2; moved = {}
    def bbx(o):
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]; return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), max(c.z for c in cs)
    bpy.context.view_layer.update()
    groups = {}
    for o in coll('ruins').objects:
        if o.type not in ('MESH', 'CURVE') or o.name.startswith(KEEP) or o.parent is not None or o.location.x > 90: continue
        key = ' '.join(o.name.split(' ')[:2]) if o.name.startswith(('pillar', 'chain')) else o.name
        groups.setdefault(key, []).append(o)
    for key, objs in groups.items():
        xs = [bbx(o) for o in objs]; x0 = min(b[0] for b in xs); x1 = max(b[1] for b in xs); y0 = min(b[2] for b in xs); y1 = max(b[3] for b in xs); zt = max(b[4] for b in xs)
        if zt < 0.35 or y0 > 9.0 or y1 < -4.5: continue
        cx = (x0 + x1) / 2; sgn = 1 if cx >= 0 else -1; inner = x0 if sgn > 0 else -x1
        if inner >= XMIN: continue
        dx = sgn * (XMIN - inner)
        for o in objs:
            o.location.x += dx
            if o.animation_data and o.animation_data.action:
                for fc in _curves(o.animation_data.action):
                    if fc.data_path == 'location' and fc.array_index == 0:
                        for kp in fc.keyframe_points: kp.co.y += dx; kp.handle_left.y += dx; kp.handle_right.y += dx
        for o in coll('ruins').objects:                                                    # glyph bands ride with their pillar drums
            if key.startswith('pillar') and o.name.startswith(key + ' ') and o.name.endswith('glyphs') and o not in objs: o.location.x += dx
        moved[key] = round(dx, 2)
    for o in [o for o in coll('ruins').objects if o.name.startswith('floor spanner') and o.parent is None]:   # loose tools out from under the wings
        if abs(o.location.x) < XMIN and -4.5 < o.location.y < 9: o.location.x = (1 if o.location.x >= 0 else -1) * random.uniform(7.5, 8.6); moved[o.name] = 'out'
    # charge + breach + flight corridor (x > 1.5, y -4.5..6): props step aside in y (husks are empties with children)
    for o in coll('ruins').objects:
        if o.type == 'EMPTY' and o.name.startswith('husk') and o.parent is None: groups[o.name] = [o]
    for key, objs in groups.items():
        if key.startswith(('terminal', 'brazier')): continue
        pts = []
        for o in objs:
            for ch in [o] + list(o.children_recursive):
                if ch.type in ('MESH', 'CURVE'): pts += [ch.matrix_world @ Vector(c) for c in ch.bound_box]
        if not pts: continue
        x1 = max(p.x for p in pts); y0 = min(p.y for p in pts); y1 = max(p.y for p in pts); zt = max(p.z for p in pts)
        if x1 < 1.5 or y1 < -4.5 or y0 > 6.0 or zt < 0.35: continue
        dy = (6.0 - y0) if (y0 + y1) / 2 >= 0.7 else (-4.5 - y1)
        for o in objs:
            o.location.y += dy
            if o.animation_data and o.animation_data.action:
                for fc in _curves(o.animation_data.action):
                    if fc.data_path == 'location' and fc.array_index == 1:
                        for kp in fc.keyframe_points: kp.co.y += dy; kp.handle_left.y += dy; kp.handle_right.y += dy
        moved['corridor ' + key] = round(dy, 2)
    return f'clear zone |x|<{XMIN} m (y -4.5..9): moved {len(moved)} groups: ' + ', '.join(f'{k} {v:+}' for k, v in list(moved.items())[:12])

# ---------------------------------------------------------------- flight camera: keyed along the real (bobbing) path, side-rear-low, whole body in frame
def v10_flight_cam():
    rig = O('dragon_rig'); P = rig.pose.bones; cam, tgt = O('cam'), O('cam target')
    for ob in (cam, tgt):
        for fc in _curves(ob.animation_data.action):
            for kp in [kp for kp in fc.keyframe_points if kp.co.x >= 598][::-1]: fc.keyframe_points.remove(kp)
    for f in range(598, 641, 3):
        scn.frame_set(f); bpy.context.view_layer.update()
        chest = rig.matrix_world @ P['spine.chest'].head; fw = (rig.matrix_world.to_3x3() @ P['root'].matrix.to_3x3() @ Vector((0, -1, 0))).normalized()
        k = min(1.0, (f - 598) / 24)                                                       # starts tight on the breach, widens to show the full span
        tgt.location = chest + fw * 0.8; cam.location = chest + Vector((-3.5 - 3.5 * k, -7.0 - 5.0 * k, -0.6 - 1.4 * k)) - fw * (1.5 + 1.5 * k)
        cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f)
    for ob in (cam, tgt):
        for fc in _curves(ob.animation_data.action):
            for kp in fc.keyframe_points:
                if kp.co.x >= 598: kp.interpolation = 'BEZIER'
    return 'flight cam: keyed every 3 f on the real path, side-rear-low, widening 598-622'
