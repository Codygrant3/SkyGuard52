from pathlib import Path
p = Path(r"D:/Skyguard52/Scripts/build_skyguard_aaa_loop32_multicam_lock_capture.py")
t = p.read_text(encoding="utf-8")
start = t.find("    # context cams")
end = t.find("    for name, loc, rot in cams:")
print("section", start, end)
if start > 0 and end > start:
    t = t[:start] + "    # context cams folded into yaw0 stages with HF boards\n" + t[end:]
    print("removed context cams")
if "c.set_actor_location" not in t:
    t = t.replace(
        "c.set_actor_label(name)",
        "c.set_actor_label(name)\n            try:\n                c.set_actor_location(unreal.Vector(*loc), False, True)\n            except Exception:\n                pass",
    )
    print("cam location force")
p.write_text(t, encoding="utf-8")
print("bytes", p.stat().st_size)
i = t.find("cams = []")
print(t[i:i+350])
