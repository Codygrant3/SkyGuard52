from pathlib import Path

src = Path("build_skyguard_aaa_loop33_prop_relock_capture.py")
t = src.read_text(encoding="utf-8")

# rename L33 -> L34
for a, b in [
    ("AAA_L33_", "AAA_L34_"),
    ("L33", "L34"),
    ("loop33", "loop34"),
    ("Loop33", "Loop34"),
    ("RT_AAA_L33", "RT_AAA_L34"),
]:
    t = t.replace(a, b)

# Force location write in spawn_sm
if "set_actor_location" not in t:
    needle = "a.set_actor_scale3d(unreal.Vector(*scale))"
    repl = """a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
    try:
        a.set_actor_location(unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), False, True)
    except Exception:
        pass"""
    if needle not in t:
        needle = "a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))"
    t = t.replace(
        "a = unreal.EditorLevelLibrary.spawn_actor_from_class(\n        unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator()\n    )",
        "a = unreal.EditorLevelLibrary.spawn_actor_from_class(\n        unreal.StaticMeshActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), rot or unreal.Rotator()\n    )",
        1,
    )
    t = t.replace(needle, repl, 1)

# Expand stages: KEEP Prop* and YakBeauty and ADS numbers from L33; densify Cockpit; ADD City/Combat/Harbor/Ocean/Wide as yaw0
old_start = t.find("stages = [")
old_end = t.find("for name, cam, dist, ny, nz in stages:")
assert old_start > 0 and old_end > old_start
new_stages = """stages = [
        # LOCKED Prop/Yak recipe from L31/L33 (do not change coords/dist)
        ("Prop", (0.0, 0.0, 500.0), 180.0, 14, 10),
        ("PropHub", (0.0, 200.0, 500.0), 160.0, 12, 9),
        ("PropNose", (0.0, -200.0, 500.0), 160.0, 12, 9),
        ("YakBeauty", (300.0, -250.0, 420.0), 220.0, 16, 10),
        # denser cockpit board, still yaw0 +X
        ("Cockpit", (40.0, 120.0, 380.0), 70.0, 14, 11),
        ("ADS", (20.0, 150.0, 370.0), 70.0, 10, 8),
        # additive weak-camera stages (separate world cells so they cannot steal Prop content)
        ("City", (-1200.0, 0.0, 300.0), 160.0, 14, 10),
        ("Combat", (900.0, 0.0, 450.0), 140.0, 12, 9),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, 11, 8),
        ("Ocean", (900.0, -400.0, 140.0), 160.0, 12, 8),
        ("Wide", (200.0, -600.0, 420.0), 200.0, 13, 9),
    ]

    """
t = t[:old_start] + new_stages + t[old_end:]

# Extra densify for City/Combat/Cockpit after existing Cockpit block, before world context
boost = '''
        if name == "Cockpit":
            # extra unlit fill so BASE cannot be flat; FINAL needs structure + lights
            for i in range(30):
                spawn_sm(sphere, (bx - 8 + (i % 6) * 1.5, cy - 16 + (i // 6) * 3.2, cz - 2 + (i % 5) * 1.2), (0.25, 0.25, 0.25), None, PREFIX + "CockFillX_%d" % i, hi(i) if "hi" in dir() else (unlit_y if i % 2 == 0 else unlit_w))
                spawn_sm(cyl, (bx - 3, cy - 18 + i * 1.4, cz - 1), (0.36, 0.36, 0.08), unreal.Rotator(90, 0, 0), PREFIX + "GaugeX_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
                spawn_sm(cube, (bx - 6, cy - 18 + i * 1.4, cz - 4), (0.25, 0.8, 0.08), None, PREFIX + "DashX_%d" % i, panel)
            # bright local key lights will be added globally for cockpit
        if name == "City":
            for i in range(36):
                h = 4 + (i % 8)
                matb = unlit_y if i % 3 == 0 else (unlit_c if i % 3 == 1 else unlit_w)
                # alternate facade colors for edge energy
                spawn_sm(cube, (bx + 10, cy - 55 + i * 3.0, cz - 8 + h * 2.2), (1.4, 1.2, h), None, PREFIX + "CityBlk_%d" % i, matb)
                spawn_sm(cube, (bx + 18, cy - 55 + i * 3.0, cz + 2), (0.1, 0.8, 0.35), None, PREFIX + "CityWin_%d" % i, unlit_r if i % 2 == 0 else unlit_y)
            for i in range(20):
                spawn_sm(cube, (bx + 2, cy - 40 + i * 4, cz - 18), (0.3, 2.4, 0.1), None, PREFIX + "CityRoad_%d" % i, unlit_w)
                spawn_sm(cube, (bx + 2, cy - 40 + i * 4, cz - 17.4), (0.1, 1.0, 0.05), None, PREFIX + "CityLane_%d" % i, unlit_y)
        if name == "Combat":
            for i in range(20):
                spawn_sm(sphere, (bx + i * 5, cy - 10 + (i % 4) * 5, cz + (i % 5) * 3), (1.1, 1.1, 1.1), None, PREFIX + "BurstX_%d" % i, unlit_y if i % 2 == 0 else unlit_r)
                spawn_sm(cube, (bx + 12 + i * 2.5, cy, cz), (0.15, 0.15, 2.0), None, PREFIX + "TracerX_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        if name in ("Harbor", "Ocean"):
            for i in range(24):
                spawn_sm(plane, (bx + 4, cy - 50 + i * 4, cz - 20), (3.5, 3.5, 1), unreal.Rotator(90, 0, 0), PREFIX + "WaveX_%s_%d" % (name, i), unlit_c if i % 2 == 0 else unlit_w)
                spawn_sm(cube, (bx + 8, cy - 50 + i * 4, cz - 18), (0.8, 1.6, 0.12), None, PREFIX + "FoamX_%s_%d" % (name, i), unlit_y if i % 2 == 0 else unlit_w)
'''

# The boost uses hi() which may not exist in L33 - check
if "def hi(" not in t:
    # define simple hi after mats_hi
    if "mats_hi = [" in t:
        i = t.find("mats_hi = [")
        j = t.find("\n", i)
        # find end of mats_hi block roughly after next few lines
        k = t.find("\n\n", j)
        insert = "\n    def hi(i):\n        pool = [m for m in mats_hi if m]\n        return pool[i % len(pool)] if pool else panel\n"
        t = t[:k] + insert + t[k:]
        print("hi helper inserted")

# insert boost before world context or meshes
marker = "    # City / ocean / combat context"
if marker not in t:
    marker = "    meshes = list_static_meshes"
if "CockFillX_" not in t:
    t = t.replace(marker, boost + "\n" + marker, 1)
    print("boost inserted at", marker[:40])

# Extra strong point lights for weak cams
extra_lights = '''
    # strong keys aimed at weak-camera stages (cockpit/city/combat)
    for i, (loc, intens) in enumerate([
        ((110.0, 120.0, 390.0), 220000.0),   # cockpit
        ((-1040.0, 0.0, 310.0), 200000.0),  # city board
        ((1040.0, 0.0, 460.0), 200000.0),   # combat board
        ((-260.0, 400.0, 190.0), 160000.0), # harbor
        ((1060.0, -400.0, 150.0), 160000.0),# ocean
        ((400.0, -600.0, 430.0), 160000.0), # wide
        ((180.0, 0.0, 510.0), 180000.0),    # prop
        ((480.0, -250.0, 430.0), 180000.0), # yak
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "PtKey_%d" % i)
            try:
                pl.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", 5000.0)
            except Exception:
                pass
'''
if "PtKey_" not in t:
    for s in ['log("loop34 densify done")', "log('loop34 densify done')", 'log("loop33 densify done")', "log('loop33 densify done')"]:
        if s in t:
            t = t.replace(s, extra_lights + "    " + s.replace("loop33", "loop34"))
            print("lights inserted before", s)
            break
    else:
        # try generic densify done
        if 'densify done")' in t:
            t = t.replace('densify done")', 'densify done")', 1)
        # fallback append before return stages if any
        if "return stages" in t and "PtKey_" not in t:
            t = t.replace("return stages", extra_lights + "\n    return stages", 1)
            print("lights before return stages")

# Capture cams: ONLY stage yaw0 cams. Remove non-yaw0 context extend block.
start = t.find("    # context cams")
if start < 0:
    start = t.find("cams.extend([")
end = t.find("    for name, loc, rot in cams:")
if start > 0 and end > start:
    t = t[:start] + "    # context cams are yaw0 stages only (no rotated orphan cams)\n" + t[end:]
    print("removed non-yaw0 context cams")

# force camera actor location
if "c.set_actor_location" not in t:
    t = t.replace(
        "c.set_actor_label(name)",
        "c.set_actor_label(name)\n            try:\n                c.set_actor_location(unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), False, True)\n            except Exception:\n                pass",
    )
    print("cam location force")

# FOV 95 for weak cams too
t = t.replace(
    'fov = 95.0 if any(k in name for k in ["Prop", "Cockpit", "ADS", "YakBeauty"]) else 70.0',
    'fov = 95.0 if any(k in name for k in ["Prop", "Cockpit", "ADS", "YakBeauty", "City", "Combat", "Harbor", "Ocean", "Wide"]) else 70.0',
)

t = t.replace("loop34 HF frustum boards + dual/triple capture start", "loop34 additive yaw0 multi-stage HF lock start")
t = t.replace("loop33 HF frustum boards + dual/triple capture start", "loop34 additive yaw0 multi-stage HF lock start")

out = Path("build_skyguard_aaa_loop34_additive_yaw0_capture.py")
out.write_text(t, encoding="utf-8")
print("wrote", out.stat().st_size)
print("City stage", '("City"' in t)
print("Combat stage", '("Combat"' in t)
print("CockFillX", "CockFillX_" in t)
print("PtKey", "PtKey_" in t)
print("set_actor_location", t.count("set_actor_location"))
# show stages
i = t.find("stages = [")
print(t[i:i+700])
