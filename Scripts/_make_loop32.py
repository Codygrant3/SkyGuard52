from pathlib import Path
src = Path('build_skyguard_aaa_loop31_contrast_restore_capture.py')
t = src.read_text(encoding='utf-8')
for a,b in [('AAA_L31_','AAA_L32_'),('L31','L32'),('loop31','loop32'),('Loop31','Loop32'),('RT_AAA_L31','RT_AAA_L32')]:
    t = t.replace(a,b)
old_start = t.find('stages = [')
old_end = t.find('for name, cam, dist, ny, nz in stages:')
print('markers', old_start, old_end)
assert old_start > 0 and old_end > old_start
new_stages = '''stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, 14, 10),
        ("PropHub", (0.0, 220.0, 500.0), 110.0, 12, 9),
        ("PropNose", (0.0, -220.0, 500.0), 110.0, 12, 9),
        ("YakBeauty", (250.0, -200.0, 430.0), 150.0, 14, 10),
        ("Cockpit", (40.0, 110.0, 380.0), 55.0, 16, 12),
        ("ADS", (20.0, 150.0, 370.0), 55.0, 11, 8),
        ("City", (-850.0, -220.0, 280.0), 150.0, 14, 10),
        ("Combat", (720.0, 10.0, 450.0), 120.0, 12, 9),
        ("Harbor", (-220.0, -160.0, 160.0), 130.0, 11, 8),
        ("Ocean", (680.0, -20.0, 120.0), 150.0, 12, 8),
        ("Wide", (160.0, -400.0, 400.0), 180.0, 13, 9),
    ]

    '''
t = t[:old_start] + new_stages + t[old_end:]
boost = '''
        if name == "City":
            for i in range(28):
                h = 3 + (i % 7)
                matb = bright_brick if i % 2 == 0 else plaster
                spawn_sm(cube, (bx + 12, cy - 45 + i * 3.0, cz - 6 + h * 2), (1.2, 1.0, h), None, PREFIX + "CityBlk_%d" % i, matb)
                spawn_sm(cube, (bx + 18, cy - 45 + i * 3.0, cz + 2), (0.08, 0.7, 0.3), None, PREFIX + "CityWin_%d" % i, unlit_y if i % 2 == 0 else panel)
        if name == "Combat":
            for i in range(14):
                spawn_sm(sphere, (bx + i * 5, cy - 6 + (i % 3) * 5, cz + (i % 4) * 3), (1.0, 1.0, 1.0), None, PREFIX + "Burst2_%d" % i, boom or hi(i))
                spawn_sm(cube, (bx + 18 + i * 2.2, cy, cz), (0.12, 0.12, 1.6), None, PREFIX + "Tracer2_%d" % i, unlit_y or muzzle)
        if name == "Cockpit":
            for i in range(24):
                spawn_sm(sphere, (bx - 6 + (i % 6) * 1.3, cy - 14 + (i // 6) * 3.0, cz + (i % 5) * 1.0), (0.22, 0.22, 0.22), None, PREFIX + "CockFill2_%d" % i, hi(i))
                spawn_sm(cyl, (bx - 2, cy - 20 + i * 1.6, cz - 1), (0.34, 0.34, 0.07), unreal.Rotator(90, 0, 0), PREFIX + "Gauge2_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
'''
marker = '    meshes = list_static_meshes'
if marker in t and 'CockFill2_' not in t:
    t = t.replace(marker, boost + '\n' + marker, 1)
if 'set_actor_location' not in t:
    t = t.replace('a.set_actor_scale3d(unreal.Vector(*scale))', 'a.set_actor_scale3d(unreal.Vector(*scale))\n    try:\n        a.set_actor_location(unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), False, True)\n    except Exception:\n        pass')
if 'bright_brick' not in t:
    t = t.replace('unlit_w = load_mat(', 'bright_brick = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightBrick") or brick\n    unlit_w = load_mat(', 1)
if 'def hi(' not in t:
    key = 'unlit_g = load_mat('
    if key in t:
        i = t.find(key)
        j = t.find('\n', i)
        t = t[:j+1] + '\n    def hi(i):\n        pool = [m for m in [unlit_w, unlit_y, unlit_c, unlit_r, unlit_g, white, panel, boom, muzzle, air] if m]\n        return pool[i % len(pool)] if pool else panel\n' + t[j+1:]
extra = '''
    for i, (loc, intens) in enumerate([((95, 110, 380), 190000.0), ((-700, -220, 280), 180000.0), ((840, 10, 450), 160000.0)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "PtX_%d" % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", 4500.0)
            except Exception:
                pass
'''
if 'PtX_' not in t:
    for s in ['log("loop32 densify done")', "log('loop32 densify done')", 'log("loop31 densify done")']:
        if s in t:
            t = t.replace(s, extra + '    ' + s.replace('loop31','loop32'))
            break
t = t.replace('loop32 HF frustum boards + dual/triple capture start', 'loop32 multi-cam HF contrast lock start')
out = Path('build_skyguard_aaa_loop32_multicam_lock_capture.py')
out.write_text(t, encoding='utf-8')
print('wrote', out.stat().st_size)
print('City', '("City"' in t)
print('Combat', '("Combat"' in t)
print('CockFill', 'CockFill2_' in t)
print('PtX', 'PtX_' in t)
print('hi', 'def hi(' in t)
