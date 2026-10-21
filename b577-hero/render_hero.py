# Final hero render with a per-frame timing log (the log is filmed as a receipt).
#   blender -b hero_live.blend --python render_hero.py
import bpy, os, time, sys
s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 1080, 1920, 100
s.eevee.taa_render_samples = 64
s.render.image_settings.file_format = 'PNG'
out = os.path.join(os.path.dirname(bpy.data.filepath), 'frames')
gpu = 'NVIDIA GeForce GTX 1650 (4 GB)'
print(f"\nGPU: ['{gpu}']  ·  EEVEE {s.eevee.taa_render_samples} samples  ·  {s.render.resolution_x}x{s.render.resolution_y}", flush=True)
t_all = time.time()
for f in range(s.frame_start, s.frame_end + 1):
    t = time.time(); s.frame_set(f); s.render.filepath = os.path.join(out, f'{f:04d}.png')
    bpy.ops.render.render(write_still=True)
    print(f'frame {f}: {time.time() - t:.2f} s', flush=True)
print(f'\nrendered {s.frame_end - s.frame_start + 1} frames in {(time.time() - t_all) / 60:.1f} min', flush=True)
