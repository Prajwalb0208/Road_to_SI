# LVL 05 mech dragon, full build (the version in the video): blender -b --factory-startup --python build_dragon.py -- OUT_DIR [FRAMES...]
import sys, os
_W = os.environ.get('LVL05_DIR') or os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv[sys.argv.index('--') + 1:]
sys.argv = [sys.argv[0]]
exec(open(os.path.join(_W, 'mecha.py'), encoding='utf-8').read())
exec(open(os.path.join(_W, 'v7.py'), encoding='utf-8').read())
exec(open(os.path.join(_W, 'v8.py'), encoding='utf-8').read())
exec(open(os.path.join(_W, 'v9.py'), encoding='utf-8').read())
exec(open(os.path.join(_W, 'v10.py'), encoding='utf-8').read())
exec(open(os.path.join(_W, 'v11.py'), encoding='utf-8').read())
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for step in (m_materials, v7_materials, v8_materials, m_body, m_fierce, v7_head_paint, v7_wings, v7_face_internals, v7_body_mech, m_details, v8_head, v10_eyes, m_rig,
             step_set, v7_environment, v8_environment, v10_clear, step_light_camera, v7_light, v8_light, v8_dragon_light, step_animate, m_transform, m_bigger, v7_softer_split, v7_laser, v8_head_light, v8_grade, v9_offset, v9_stone, v9_sky, v9_finale, v10_flight, v10_flight_cam, v11_breach, v11_shatter_dust):
    print('[v7]', step())
out = _argv[0]; scn.render.resolution_percentage = 40
for f in map(int, _argv[1:]):
    for k in range(scn.frame_start, f + 1, 2): scn.frame_set(k)
    scn.frame_set(f); scn.render.filepath = os.path.join(out, f'v7_{f:03d}.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(_W, 'mech_dragon.blend'))
print('[v7] done')
