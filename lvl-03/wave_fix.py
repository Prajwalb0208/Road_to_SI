# Owner note (2026-10-20): the waving hand still reads as stuck in the head. New rest: arm out to the side and forward,
# hand clear of the head (x <= 0.65) and the ear fin (x <= 0.88); wave = +-15 deg swing around that.
#   blender -b work\b577_3d.blend --python work\wave_fix.py -- [--test out_prefix] [--save]
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
O = bpy.data.objects; rig = O['B577_rig']; scn = bpy.context.scene
SH, HAND = Vector((0.35, 0, 0.9)), Vector((0.84, -0.34, 1.06))
AX = 'Z' if '--axis' not in argv else argv[argv.index('--axis') + 1]
SIGN = float(argv[argv.index('--sign') + 1]) if '--sign' in argv else 1.0

scn.frame_set(1); bpy.context.view_layer.update()
arm, hand = O['B577_arm_R'], O['B577_hand_R']
for o in (arm, hand):
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
# rest bone -> new direction
bpy.context.view_layer.objects.active = rig; rig.hide_set(False); rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); eb = rig.data.edit_bones['arm.R']; eb.head = SH; eb.tail = HAND; eb.roll = 0
bpy.ops.object.mode_set(mode='OBJECT')
# rebuild the arm capsule along the new direction, hand at the tip
d = HAND - SH
arm.rotation_mode = 'XYZ'; arm.location = (SH + HAND) / 2; arm.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
bpy.context.view_layer.update(); arm.scale.z *= d.length / arm.dimensions.z
hand.location = HAND
# re-parent at rest (all pose channels zero at the rest frame)
pb = rig.pose.bones['arm.R']; saved = pb.rotation_euler.copy(); pb.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
for o in (arm, hand):
    mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'arm.R'; o.matrix_world = mw
# remap wave keys: old 0 -> rest (0), old 10..50 -> -15..+15, landing 40 -> +15, -20 -> -12
idx = {'X': 0, 'Y': 1, 'Z': 2}[AX]
def curves(a):
    if hasattr(a, 'fcurves') and len(a.fcurves): return list(a.fcurves)
    out = []
    for layer in getattr(a, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
remap = {0: 0, 10: -15, 50: 15, 40: 15, -20: -12}
for fc in curves(rig.animation_data.action):
    if fc.data_path == 'pose.bones["arm.R"].rotation_euler':
        for kp in fc.keyframe_points:
            old = round(math.degrees(kp.co.y))
            new = math.radians(remap.get(old, old) * SIGN) if fc.array_index == 2 else 0.0
            if fc.array_index == idx: kp.co.y = new
            elif fc.array_index == 2: kp.co.y = 0.0
            kp.handle_left.y = kp.handle_right.y = kp.co.y
        fc.update()
if '--test' in argv:
    pre = argv[argv.index('--test') + 1]
    scn.render.resolution_x, scn.render.resolution_y = 960, 540; scn.render.film_transparent = False; scn.camera = O['Cam_hero']
    for n in ('B577_ref_2D', 'B577_tag_cutter', 'B577_rig'): O[n].hide_render = True
    for f in ([int(x) for x in argv[argv.index('--frames') + 1].split(',')] if '--frames' in argv else (1, 70, 90, 309)):
        scn.frame_set(f); scn.render.filepath = f'{pre}_{f:04d}.png'; bpy.ops.render.render(write_still=True)
if '--save' in argv: bpy.ops.wm.save_mainfile()
print('[wave_fix] axis', AX, 'sign', SIGN, 'saved' if '--save' in argv else 'not saved')
