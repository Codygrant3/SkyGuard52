from pathlib import Path
src = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop34_additive_yaw0_capture.py")
t = src.read_text(encoding="utf-8")
for a, b in [
    ("AAA_L34_", "AAA_L35_"),
    ("L34", "L35"),
    ("loop34", "loop35"),
    ("Loop34", "Loop35"),
    ("RT_AAA_L34", "RT_AAA_L35"),
]:
    t = t.replace(a, b)

# denser cockpit absolute densify: append after CockFillA block if present, else before densify done
extra = r'''
    # Loop35 mega cockpit/city voxels (Prop/Yak coords untouched)
    for ix in range(-8, 9):
        for iy in range(-10, 11):
            for iz in range(-6, 7):
                if (ix + iy + iz) % 2 == 0:
                    continue
                mat = unlit_y if (ix + iy) % 3 == 0 else (unlit_c if (iy + iz) % 3 == 0 else (unlit_w if (ix + iz) % 2 == 0 else unlit_r))
                spawn_sm(cube, (110 + ix * 2.2, 120 + iy * 2.0, 380 + iz * 2.0), (0.35, 0.35, 0.35), None, PREFIX + "CockVox_%d_%d_%d" % (ix, iy, iz), mat)
    for i in range(40):
        spawn_sm(cyl, (108, 100 + i * 1.1, 382), (0.42, 0.42, 0.09), unreal.Rotator(90, 0, 0), PREFIX + "CockGauge_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
        spawn_sm(cube, (108.3, 100 + i * 1.1, 382.5), (0.05, 0.28, 0.04), None, PREFIX + "CockNeedle_%d" % i, unlit_r)
        spawn_sm(cube, (105, 100 + i * 1.1, 378), (0.35, 1.0, 0.1), None, PREFIX + "CockDash_%d" % i, panel)
    for ix in range(0, 12):
        for iy in range(-18, 19):
            h = 3 + ((ix * 7 + iy) % 9)
            mat = unlit_y if (ix + iy) % 3 == 0 else (unlit_c if (ix + iy) % 3 == 1 else unlit_w)
            spawn_sm(cube, (-1040 + ix * 4.0, iy * 3.5, 300 - 10 + h * 2.0), (1.6, 1.4, h), None, PREFIX + "CityVox_%d_%d" % (ix, iy), mat)
            spawn_sm(cube, (-1036 + ix * 4.0, iy * 3.5, 300 + 2), (0.12, 0.9, 0.4), None, PREFIX + "CityWinB_%d_%d" % (ix, iy), unlit_r if (ix + iy) % 2 == 0 else unlit_y)
    for i in range(30):
        spawn_sm(cube, (-1045, -50 + i * 3.5, 288), (0.4, 2.8, 0.15), None, PREFIX + "CityRoadB_%d" % i, unlit_w)
        spawn_sm(cube, (-1045, -50 + i * 3.5, 288.5), (0.12, 1.1, 0.08), None, PREFIX + "CityLaneB_%d" % i, unlit_y)
    for i, loc in enumerate([(100, 120, 395), (120, 110, 385), (115, 130, 400), (-1030, 10, 320), (-1050, -10, 305), (-1020, 0, 340)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "PtKeyCockExtra_%d" % i)
            try:
                pl.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(280000.0)
                    c.set_editor_property("attenuation_radius", 3500.0)
            except Exception:
                pass
'''
if "CockVox_" not in t:
    if 'log("loop35 densify done")' in t:
        t = t.replace('log("loop35 densify done")', extra + '    log("loop35 densify done")')
    elif "log('loop35 densify done')" in t:
        t = t.replace("log('loop35 densify done')", extra + "    log('loop35 densify done')")
    else:
        # find densify done
        idx = t.find("densify done")
        print("densify done idx", idx)
        # insert before last log densify done line
        marker = '    log("'
        # safer: insert before PtKey block
        if "PtKey_" in t:
            t = t.replace("    # strong keys aimed at weak-camera stages", extra + "\n    # strong keys aimed at weak-camera stages", 1)
        else:
            t = t.replace("return stages", extra + "\n    return stages", 1) if "return stages" in t else t + "\n" + extra
    print("extra densify inserted")

t = t.replace("loop35 additive yaw0 multi-stage HF lock start", "loop35 cockpit city mega densify keep prop lock start")
t = t.replace("((110.0, 120.0, 390.0), 220000.0)", "((110.0, 120.0, 390.0), 350000.0)")
t = t.replace("((-1040.0, 0.0, 310.0), 200000.0)", "((-1040.0, 0.0, 310.0), 320000.0)")

out = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop35_cockpit_city_mega_capture.py")
out.write_text(t, encoding="utf-8")
print("wrote", out.stat().st_size)
print("CockVox", "CockVox_" in t)
print("CityVox", "CityVox_" in t)
print("Prop locked", '("Prop", (0.0, 0.0, 500.0), 180.0, 14, 10)' in t)
print("parens", t.count("(") - t.count(")"))
