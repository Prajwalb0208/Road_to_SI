# Full preview of the saved v7 file: blender -b mecha_v7.blend --python anim_v7_preview.py -- OUT_DIR
import bpy, sys, os
out = sys.argv[sys.argv.index('--') + 1]; scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = 1920, 804, 50
scn.eevee.taa_render_samples = 16; scn.render.image_settings.file_format = 'PNG'; scn.render.filepath = os.path.join(out, 'p_')
bpy.ops.render.render(animation=True); print('[preview] done')
