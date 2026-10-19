# Keys before the first keyframe hold its value: leg keys start at 268 and arm.L at 241, so frames 1..267 had a leg
# mid-step (and the turntable pose too). Pin neutral keys before them.
#   blender.exe -b work\b577_3d.blend --python work\fix_leaks.py
import bpy

pb = bpy.data.objects['B577_rig'].pose.bones
for b, frames in (('leg.L', (1, 241, 262)), ('leg.R', (1, 241, 262)), ('arm.L', (1, 240))):
    for f in frames:
        pb[b].rotation_euler = (0, 0, 0)
        pb[b].keyframe_insert('rotation_euler', frame=f)
bpy.ops.wm.save_mainfile()
print('[fix_leaks] neutral keys added + saved')
