# Collision audit: blender -b <file.blend> --python collide.py -- [step] [f0] [f1]
#   wing parts vs environment (pillars, chains, rocks, crystals, walls, blocks, props) and vs the dragon's own head/neck/legs/tail,
#   every `step` frames. AABB prefilter, then exact BVH overlap on evaluated meshes. Prints one line per (frame, wing part, hit).
import bpy, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
step = int(a[0]) if a else 4; f0 = int(a[1]) if len(a) > 1 else 124; f1 = int(a[2]) if len(a) > 2 else bpy.context.scene.frame_end
scn = bpy.context.scene
GROUND = ('ruin floor', 'flagstone', 'rune ', 'ground mist', 'hall haze', 'scorch', 'ridge', 'portal energy', 'wall breach cut', 'hall back hole', 'window cut', 'claw mark')
def is_wing(o): return o.name.startswith('wing ') and o.type == 'MESH' and any(k in o.name for k in ('feather', 'inner plate', 'heavy armour', ' bone ', 'arm shell', 'hook', 'claw', 'thruster'))
def body_part(o):
    b = o.get('bone') or (o.parent_bone if o.parent_type == 'BONE' else '')
    return b and (b.startswith(('neck', 'tail', 'leg')) or b in ('head', 'jaw')) and o.type == 'MESH'
def env(o):
    if o.type != 'MESH' or not o.visible_get() or o.hide_render: return False
    cs = [c.name for c in o.users_collection]
    return 'ruins' in cs and not o.name.startswith(GROUND) and o.location.x < 90
wings = [o for o in scn.objects if is_wing(o)]
others = [('env', o) for o in scn.objects if env(o)] + [('body', o) for o in scn.objects if body_part(o)]
print(f'[collide] {len(wings)} wing parts vs {len(others)} objects, frames {f0}-{f1} step {step}', flush=True)
def aabb(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))), Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
def ov(a, b): return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))
hits = []
for f in range(f0, f1 + 1, step):
    scn.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    WB = {o.name: aabb(o) for o in wings}; OB = {o.name: aabb(o) for _, o in others}
    bvh = {}
    def tree(o):
        if o.name not in bvh:
            oe = o.evaluated_get(dg); me = oe.to_mesh(); me.transform(o.matrix_world)
            bvh[o.name] = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [p.vertices[:] for p in me.polygons]) if len(me.polygons) else None
            oe.to_mesh_clear()
        return bvh[o.name]
    n = 0
    for w in wings:
        for kind, o in others:
            if not ov(WB[w.name], OB[o.name]): continue
            if kind == 'body' and w.name.split(' ')[1] in o.name: continue
            t1, t2 = tree(w), tree(o)
            if t1 and t2 and t1.overlap(t2):
                hits.append((f, kind, w.name, o.name)); n += 1
    if n: print(f'[collide] f{f}: {n} hits, e.g. ' + '; '.join(f'{h[2]} x {h[3]}' for h in hits[-min(n, 4):]), flush=True)
summary = {}
for f, k, w, o in hits: summary.setdefault((k, o.split(' drum')[0].split(' link')[0].split(' ')[0] if k == 'env' else o.split(' ')[0]), []).append(f)
print('[collide] SUMMARY', json.dumps({f'{k}:{n}': f'{min(v)}-{max(v)} ({len(v)} hits)' for (k, n), v in summary.items()}), flush=True)
print(f'[collide] total {len(hits)} hits', flush=True)
