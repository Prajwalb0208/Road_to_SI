# render chosen frames of the saved file: blender -b X.blend --python stills.py -- OUT f1 f2 ...
import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]; out = a[0]; scn = bpy.context.scene; scn.render.resolution_percentage = 50
for f in map(int, a[1:]):
    for k in range(max(1, f - 60), f + 1, 2): scn.frame_set(k)
    scn.frame_set(f); scn.render.filepath = os.path.join(out, f's_{f:03d}.png'); bpy.ops.render.render(write_still=True)
print('[stills] done')
