# LED eyes rendered lemon-yellow when orange: the mood mix fed Base Color AND Emission, so both added up and clipped.
# Make the LED emission-only (base black). --test renders frame 300 to render/led_test.png without saving.
#   blender.exe -b work\b577_3d.blend --python work\led_fix.py -- [--test] [--strength 1.4]
import bpy, sys, os

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
strength = float(argv[argv.index('--strength') + 1]) if '--strength' in argv else 1.4
m = bpy.data.materials['B577_led_cyan']; nt = m.node_tree
p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
for l in list(p.inputs['Base Color'].links): nt.links.remove(l)
p.inputs['Base Color'].default_value = (0, 0, 0, 1)
p.inputs['Emission Strength'].default_value = strength
if '--test' in argv:
    scn = bpy.context.scene; scn.frame_set(300); scn.camera = bpy.data.objects['Cam_hero']
    scn.render.film_transparent = False
    for n in ('B577_ref_2D', 'B577_tag_cutter'): bpy.data.objects[n].hide_render = True
    scn.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath), 'render', f'led_test_{strength}.png')
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.wm.save_mainfile()
print('[led_fix] emission-only, strength', strength, 'test' if '--test' in argv else 'saved')
