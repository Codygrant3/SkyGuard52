from pathlib import Path

p = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop34_additive_yaw0_capture.py")
t = p.read_text(encoding="utf-8")

# Extract and remove the misplaced boost (from first 'if name == "Cockpit":' after yak to just before City/ocean context)
start = t.find('        if name == "Cockpit":\n            # extra unlit fill')
if start < 0:
    raise SystemExit('misplaced boost start not found')
end = t.find('    # City / ocean / combat context', start)
if end < 0:
    end = t.find('    for i in range(70):', start)
if end < 0:
    raise SystemExit('misplaced boost end not found')
print('removing', start, end)
t = t[:start] + t[end:]

# Absolute densify for weak stages using locked coords
abs_block = '''
    # Absolute additive densify for weak stages (does not depend on stage loop vars)
    # Cockpit board center ~ (40+70, 120, 380) = (110,120,380)
    for i in range(36):
        spawn_sm(sphere, (102 + (i % 6) * 1.5, 104 + (i // 6) * 3.2, 378 + (i % 5) * 1.2), (0.28, 0.28, 0.28), None, PREFIX + "CockFillA_%d" % i, hi(i))
        spawn_sm(cyl, (107, 100 + i * 1.3, 379), (0.38, 0.38, 0.08), unreal.Rotator(90, 0, 0), PREFIX + "GaugeA_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
        spawn_sm(cube, (104, 100 + i * 1.3, 376), (0.28, 0.9, 0.08), None, PREFIX + "DashA_%d" % i, panel)
    # City board ~ (-1200+160, 0, 300) = (-1040,0,300)
    for i in range(40):
        h = 4 + (i % 8)
        matb = unlit_y if i % 3 == 0 else (unlit_c if i % 3 == 1 else unlit_w)
        spawn_sm(cube, (-1030, -60 + i * 3.0, 292 + h * 2.2), (1.5, 1.3, h), None, PREFIX + "CityBlkA_%d" % i, matb)
        spawn_sm(cube, (-1022, -60 + i * 3.0, 304), (0.12, 0.85, 0.4), None, PREFIX + "CityWinA_%d" % i, unlit_r if i % 2 == 0 else unlit_y)
    for i in range(22):
        spawn_sm(cube, (-1040, -45 + i * 4, 282), (0.35, 2.5, 0.12), None, PREFIX + "CityRoadA_%d" % i, unlit_w)
        spawn_sm(cube, (-1040, -45 + i * 4, 282.5), (0.12, 1.0, 0.06), None, PREFIX + "CityLaneA_%d" % i, unlit_y)
    # Combat board ~ (900+140, 0, 450) = (1040,0,450)
    for i in range(24):
        spawn_sm(sphere, (1040 + i * 5, -12 + (i % 4) * 5, 450 + (i % 5) * 3), (1.2, 1.2, 1.2), None, PREFIX + "BurstA_%d" % i, unlit_y if i % 2 == 0 else unlit_r)
        spawn_sm(cube, (1050 + i * 2.5, 0, 450), (0.16, 0.16, 2.2), None, PREFIX + "TracerA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
    # Harbor/Ocean boards
    for i in range(26):
        spawn_sm(plane, (-250, 350 + i * 4, 160), (3.8, 3.8, 1), unreal.Rotator(90, 0, 0), PREFIX + "WaveHA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        spawn_sm(cube, (-245, 350 + i * 4, 162), (0.9, 1.7, 0.12), None, PREFIX + "FoamHA_%d" % i, unlit_y if i % 2 == 0 else unlit_w)
        spawn_sm(plane, (1050, -450 + i * 4, 120), (3.8, 3.8, 1), unreal.Rotator(90, 0, 0), PREFIX + "WaveOA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        spawn_sm(cube, (1055, -450 + i * 4, 122), (0.9, 1.7, 0.12), None, PREFIX + "FoamOA_%d" % i, unlit_y if i % 2 == 0 else unlit_w)

'''

# Insert absolute densify before lights / densify done
if "CockFillA_" not in t:
    if "PtKey_" in t:
        t = t.replace("    # strong keys aimed at weak-camera stages", abs_block + "    # strong keys aimed at weak-camera stages", 1)
    else:
        t = t.replace('log("loop34 densify done")', abs_block + '    log("loop34 densify done")', 1)
    print("absolute densify inserted")

# Simplify hi() usage in remaining code
t = t.replace('hi(i) if "hi" in dir() else (unlit_y if i % 2 == 0 else unlit_w)', "hi(i)")

p.write_text(t, encoding="utf-8")
print("bytes", p.stat().st_size)
# verify boost no longer after yak with undefined bx
i = t.find("spawn_sm(mesh, origin")
print(t[i:i+350])
print("---abs---")
print("CockFillA", "CockFillA_" in t)
print("CityBlkA", "CityBlkA_" in t)
print("BurstA", "BurstA_" in t)
