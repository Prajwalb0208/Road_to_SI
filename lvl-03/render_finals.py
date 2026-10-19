# Background final renders for LVL 03 (run after the recorded takes):
#   blender.exe -b work\b577_3d.blend --python work\render_finals.py
# Outputs (transparent PNG, 1920x1080, EEVEE 32 samples) in work\render\{anim,land,turn,stills}
import bpy, math, os, time

ROOT = os.path.join(os.path.dirname(bpy.data.filepath), 'render')
scn = bpy.context.scene
scn.render.film_transparent = True
scn.render.image_settings.file_format = 'PNG'
scn.render.image_settings.color_mode = 'RGBA'
scn.render.resolution_x, scn.render.resolution_y, scn.render.resolution_percentage = 1920, 1080, 100
scn.eevee.taa_render_samples = 32
scn.render.use_compositing = False
O = bpy.data.objects
for n in ('B577_ref_2D', 'B577_tag_cutter', 'B577_rig'):
    if n in O: O[n].hide_render = True
log = {}


def seq(name, cam, a, b):
    t = time.time()
    scn.camera = O[cam]
    scn.frame_start, scn.frame_end = a, b
    scn.render.filepath = os.path.join(ROOT, name, '')
    bpy.ops.render.render(animation=True)
    log[name] = (b - a + 1, round(time.time() - t, 1))


def still(name, cam, frame, w=1920, h=1080):
    scn.camera = O[cam]; scn.frame_set(frame)
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.filepath = os.path.join(ROOT, 'stills', name + '.png')
    bpy.ops.render.render(write_still=True)
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080


seq('anim', 'Cam_hero', 1, 240)
seq('land', 'Cam_hero', 241, 330)
# turntable: pose at frame 1, camera pivot spins 360 deg over 144 frames
t = time.time(); scn.camera = O['Cam_turn']; scn.frame_set(1)
piv = O['Turn_pivot']
for i in range(144):
    piv.rotation_euler.z = 2 * math.pi * i / 144
    scn.render.filepath = os.path.join(ROOT, 'turn', f'{i:04d}.png')
    bpy.ops.render.render(write_still=True)
log['turn'] = (144, round(time.time() - t, 1))
piv.rotation_euler.z = 0
still('hero_wave', 'Cam_hero', 95)
still('hero_happy', 'Cam_hero', 200)
still('hero_wave_sq', 'Cam_hero', 95, 2000, 2000)
with open(os.path.join(ROOT, 'render_log.txt'), 'w') as f:
    for k, (n, s) in log.items():
        f.write(f'{k}: {n} frames in {s} s ({s / n:.2f} s/frame)\n')
print('[finals] done', log)
