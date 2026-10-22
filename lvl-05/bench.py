# GPU benchmark on the real shot: blender -b mecha_v7.blend --python bench.py -- OUT_DIR
#   EEVEE (64 / 128 TAA) vs Cycles CUDA (128 / 256 / 512, OIDN denoise, adaptive) on a wide frame (205) and a face frame (340), 1080p.
import bpy, sys, os, time, json
out = sys.argv[sys.argv.index('--') + 1]; scn = bpy.context.scene; res = []
scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = 1920, 1080, 100
scn.render.image_settings.file_format = 'PNG'
def warm(f):
    for k in range(1, f + 1, 3): scn.frame_set(k)                       # particles need sequential evaluation
    scn.frame_set(f)
def shot(tag, f):
    scn.render.filepath = os.path.join(out, f'{tag}_{f}.png'); t = time.time(); bpy.ops.render.render(write_still=True); dt = time.time() - t
    res.append({'tag': tag, 'frame': f, 'sec': round(dt, 1)}); print('[bench]', tag, f, round(dt, 1), 's', flush=True)
for f in (205, 340):
    warm(f)
    scn.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    for s in (64, 128):
        scn.eevee.taa_render_samples = s; shot(f'eevee{s}', f)
    scn.render.engine = 'CYCLES'; cp = bpy.context.preferences.addons['cycles'].preferences
    cp.compute_device_type = 'CUDA'; cp.get_devices()
    for d in cp.devices: d.use = (d.type == 'CUDA')
    c = scn.cycles; c.device = 'GPU'; c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 4; c.transmission_bounces = 4; c.volume_bounces = 0; c.transparent_max_bounces = 12
    c.volume_step_rate = 2.0; c.caustics_reflective = False; c.caustics_refractive = False; scn.render.use_persistent_data = True
    for s in (128, 256, 512):
        c.samples = s
        try: shot(f'cycles{s}', f)
        except Exception as e: res.append({'tag': f'cycles{s}', 'frame': f, 'error': str(e)}); print('[bench] FAIL', s, e, flush=True)
json.dump(res, open(os.path.join(out, 'bench.json'), 'w'), indent=1); print('[bench] done')
