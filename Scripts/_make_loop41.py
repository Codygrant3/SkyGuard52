from pathlib import Path

src = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop38_marker_smoke_capture.py").read_text(encoding="utf-8")
for a, b in [
    ("AAA_L38_", "AAA_L41_"),
    ("L38", "L41"),
    ("loop38", "loop41"),
    ("Loop38", "Loop41"),
    ("RT_AAA_L38", "RT_AAA_L41"),
]:
    src = src.replace(a, b)

old_log = 'log("SPAWN %s target=(%.1f,%.1f,%.1f) got=%s" % (label, x,y,z, got))'
new_log = '''if got and (abs(got[0]-x)+abs(got[1]-y)+abs(got[2]-z) > 1.0):
        log("SPAWN_MISMATCH %s target=(%.1f,%.1f,%.1f) got=%s" % (label, x,y,z, got))'''
if old_log in src:
    src = src.replace(old_log, new_log)
    print("spawn log quieted")

needle = 'for iy in range(-10, 11):\n            spawn_sm(cube, (bx + 1, cy + iy * 4.0, cz), (0.25, 0.3, 8.0), None, PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i+iy) % len(mats)] if mats else m)'
extra = '''
        # PropNose unique denser wall only (no mid-FOV densify)
        if name == "PropNose":
            for iy in range(-12, 13):
                for iz in range(-9, 10):
                    mm = mats[(iy * 7 + iz * 3) % len(mats)] if mats else m
                    spawn_sm(cube, (bx + 2, cy + iy * 3.2, cz + iz * 3.2), (0.3, 0.55, 0.55), None, PREFIX + "NoseWall_%d_%d" % (iy, iz), mm)
'''
if needle in src and "NoseWall_" not in src:
    src = src.replace(needle, needle + "\n" + extra)
    print("PropNose uniqueness added")
else:
    print("needle found?", needle in src, "already?", "NoseWall_" in src)

src = src.replace(
    "loop41 minimal unique-marker capture smoke probe start",
    "loop41 pure L38 freeze + PropNose wall uniqueness start",
)
src = src.replace("loop41 minimal marker densify done", "loop41 densify done")

out = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop41_l38_freeze_propnose_capture.py")
out.write_text(src, encoding="utf-8")
print("wrote", out.stat().st_size)
compile(src.replace("import unreal", "unreal=None"), "l41", "exec")
print("syntax ok")
print("NoseWall", "NoseWall_" in src)
