from pathlib import Path
src = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop38_marker_smoke_capture.py")
t = src.read_text(encoding="utf-8")
for a, b in [
    ("AAA_L38_", "AAA_L39_"),
    ("L38", "L39"),
    ("loop38", "loop39"),
    ("Loop38", "Loop39"),
    ("RT_AAA_L38", "RT_AAA_L39"),
]:
    t = t.replace(a, b)

needle = 'PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i+iy) % len(mats)] if mats else m)'
idx = t.find(needle)
print("needle idx", idx)
if idx < 0:
    raise SystemExit("needle not found")
# insert after the full for-loop line
line_end = t.find("\n", idx)
extra = r'''
        # denser stage-specific content (keep marker/wall/stripe base)
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
'''
# Need plane mesh available - L38 densify only loads cube/sphere. Add plane load.
if 'plane = load_sm("/Engine/BasicShapes/Plane")' not in t:
    t = t.replace(
        'sphere = load_sm("/Engine/BasicShapes/Sphere")',
        'sphere = load_sm("/Engine/BasicShapes/Sphere")\n    plane = load_sm("/Engine/BasicShapes/Plane")\n    cyl = load_sm("/Engine/BasicShapes/Cylinder")',
        1,
    )
    print("added plane/cyl loads")
t = t[: line_end + 1] + extra + t[line_end + 1 :]
t = t.replace("loop39 minimal unique-marker capture smoke probe start", "loop39 marker recipe + denser stage content start")
t = t.replace("loop39 minimal marker densify done", "loop39 densify done")
out = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop39_marker_plus_density_capture.py")
out.write_text(t, encoding="utf-8")
print("wrote", out.stat().st_size)
print("Blade", "Blade_%s" in t)
print("Bldg", "Bldg_%d" in t)
print("parens", t.count("(") - t.count(")"))
