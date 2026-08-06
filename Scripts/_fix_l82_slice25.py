from pathlib import Path
p = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop82_true_art_slice25_capture.py")
t = p.read_text(encoding="utf-8")
print("before", t.count("ensure_auth_niagara"))
t = t.replace("out[n] = ensure_auth_niagara(n)", "out[n] = ensure_authored_ns(n, deepen=True)")
old = "ensure_dir('/Game/Skyguard/VFX')\n    base = ensure_slice24_vfx_library()"
new = 'ensure_dir("/Game/Skyguard/VFX")\n    ensure_dir("/Game/Skyguard/VFX/Emitters")\n    base = ensure_slice24_vfx_library()'
if old in t:
    t = t.replace(old, new)
    print("dir ensure updated")
else:
    print("dir ensure pattern not found; continuing")
p.write_text(t, encoding="utf-8")
print("after", t.count("ensure_auth_niagara"))
print("has authored", "ensure_authored_ns(n, deepen=True)" in t)
