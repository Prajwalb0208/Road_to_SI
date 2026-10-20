# Final 3D render: 1080p, EEVEE 32 samples, motion blur, PNG frames -> work\b3d\frames\
#   blender -b village3d_live.blend --python render_final.py -a
import bpy, os
s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 1920, 1080, 100
s.eevee.taa_render_samples = 32
s.render.image_settings.file_format = 'PNG'
s.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath), 'frames', '')
s.use_preview_range = False
print('[final] out', s.render.filepath, s.frame_start, s.frame_end)
