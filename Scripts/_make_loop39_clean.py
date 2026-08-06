from pathlib import Path
# Rebuild L39 cleanly from L38 full file rewrite of densify loop body
src = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop38_marker_smoke_capture.py").read_text(encoding="utf-8")
for a,b in [("AAA_L38_","AAA_L39_"),("L38","L39"),("loop38","loop39"),("Loop38","Loop39"),("RT_AAA_L38","RT_AAA_L39")]:
    src = src.replace(a,b)

# Replace densify function entirely with a clean version
start = src.find("def densify():")
end = src.find("\ndef capture(")
assert start > 0 and end > start
densify = r'''
def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    mats = [m for m in [unlit_y, unlit_c, unlit_r, unlit_w, unlit_g] if m]

    stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, unlit_y),
        ("PropHub", (0.0, 200.0, 500.0), 120.0, unlit_c),
        ("PropNose", (0.0, -200.0, 500.0), 120.0, unlit_r),
        ("YakBeauty", (300.0, -250.0, 420.0), 150.0, unlit_w),
        ("Cockpit", (40.0, 120.0, 380.0), 80.0, unlit_y),
        ("ADS", (20.0, 150.0, 370.0), 70.0, unlit_c),
        ("City", (-1200.0, 0.0, 300.0), 140.0, unlit_r),
        ("Combat", (900.0, 0.0, 450.0), 140.0, unlit_g or unlit_y),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, unlit_w),
        ("Ocean", (900.0, -400.0, 140.0), 140.0, unlit_c),
        ("Wide", (200.0, -600.0, 420.0), 180.0, unlit_y),
    ]

    for i, (name, cam, dist, mat) in enumerate(stages):
        cx, cy, cz = cam
        bx = cx + dist
        m = mat or (mats[i % len(mats)] if mats else None)
        spawn_sm(sphere, (bx, cy, cz), (6.0 + i * 0.3, 6.0 + i * 0.3, 6.0 + i * 0.3), None, PREFIX + "Marker_%s" % name, m)
        for iy in range(-8, 9):
            for iz in range(-6, 7):
                mm = mats[(i + iy + iz) % len(mats)] if mats else m
                spawn_sm(cube, (bx + 2, cy + iy * 5.0, cz + iz * 5.0), (0.4, 0.7, 0.7), None, PREFIX + "Wall_%s_%d_%d" % (name, iy, iz), mm)
        for iy in range(-10, 11):
            spawn_sm(cube, (bx + 1, cy + iy * 4.0, cz), (0.25, 0.3, 8.0), None, PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i + iy) % len(mats)] if mats else m)
        if name.startswith("Prop"):
            for k, ang in enumerate(range(0, 180, 10)):
                spawn_sm(cube, (bx - 3, cy, cz), (0.2, 8.0, 0.18), unreal.Rotator(0, ang, 0), PREFIX + "Blade_%s_%d" % (name, k), mats[(i + k) % len(mats)] if mats else m)
            spawn_sm(sphere, (bx - 8, cy, cz), (2.0, 2.0, 2.0), None, PREFIX + "Hub_%s" % name, unlit_w or m)
            spawn_sm(cube, (bx + 8, cy, cz), (1.5, 1.5, 1.5), None, PREFIX + "Cowling_%s" % name, unlit_c or m)
        if name == "Cockpit":
            for k in range(24):
                spawn_sm(cyl, (bx - 2, cy - 18 + k * 1.5, cz), (0.45, 0.45, 0.1), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % k, unlit_y if k % 2 == 0 else unlit_c)
                spawn_sm(cube, (bx - 1.5, cy - 18 + k * 1.5, cz + 0.4), (0.06, 0.3, 0.05), None, PREFIX + "Needle_%d" % k, unlit_r)
        if name == "City":
            for k in range(30):
                h = 4 + (k % 7)
                spawn_sm(cube, (bx + 12, cy - 50 + k * 3.2, cz - 6 + h * 2), (1.6, 1.4, h), None, PREFIX + "Bldg_%d" % k, unlit_y if k % 3 == 0 else (unlit_c if k % 3 == 1 else unlit_w))
                spawn_sm(cube, (bx + 20, cy - 50 + k * 3.2, cz + 2), (0.15, 0.9, 0.4), None, PREFIX + "Win_%d" % k, unlit_r if k % 2 == 0 else unlit_y)
        if name == "Combat":
            for k in range(18):
                spawn_sm(sphere, (bx + k * 5, cy - 8 + (k % 4) * 5, cz + (k % 3) * 4), (1.3, 1.3, 1.3), None, PREFIX + "Burst_%d" % k, unlit_y if k % 2 == 0 else unlit_r)
                spawn_sm(cube, (bx + 15 + k * 2.5, cy, cz), (0.18, 0.18, 2.4), None, PREFIX + "Tracer_%d" % k, unlit_c if k % 2 == 0 else unlit_w)
        if name in ("Harbor", "Ocean"):
            for k in range(20):
                spawn_sm(plane, (bx + 5, cy - 40 + k * 4, cz - 15), (4.0, 4.0, 1), unreal.Rotator(90, 0, 0), PREFIX + "Wave_%s_%d" % (name, k), unlit_c if k % 2 == 0 else unlit_w)

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-30, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(20.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(4.0)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (name, cam, dist, mat) in enumerate(stages):
        cx, cy, cz = cam
        bx = cx + dist
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx, cy, cz + 20), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%s" % name)
            try:
                pl.set_actor_location(unreal.Vector(bx, cy, cz + 20), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(400000.0)
                    c.set_editor_property("attenuation_radius", 6000.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + "PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("loop39 densify done")
    return stages

'''
src = src[:start] + densify + src[end:]
src = src.replace("loop39 minimal unique-marker capture smoke probe start", "loop39 marker recipe + denser stage content start")
out = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop39_marker_plus_density_capture.py")
out.write_text(src, encoding="utf-8")
# syntax check without unreal
import ast
# can't compile due to unreal import; basic balance checks
print("wrote", out.stat().st_size)
print("parens", src.count("(")-src.count(")"))
print("Blade", "Blade_%s" in src)
print("starts densify ok", "def densify():" in src and "def capture(" in src)
