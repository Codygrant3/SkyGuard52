from pathlib import Path
p = Path(r"D:\Skyguard52\Scripts\host_audit_loop66.py")
t = p.read_text(encoding="utf-8")
# stills exported under AAA_Cam_L65_ names into AAA_L66 folder due generator incomplete camera rename
t = t.replace("AAA_Cam_L66_", "AAA_Cam_L65_")
# keep docs/path on L66
# already uses AAA_L66 for BASE; restore if damaged
t = t.replace(r"D:\Skyguard52\Saved\Screenshots\AAA_L65", r"D:\Skyguard52\Saved\Screenshots\AAA_L66")
t = t.replace("CRITIC_FAIL_loop65.md", "CRITIC_FAIL_loop66.md")
t = t.replace("Loop 65", "Loop 66")
t = t.replace("Loop65", "Loop66")
t = t.replace("loop65", "loop66")
p.write_text(t, encoding="utf-8")
print("patched bytes", p.stat().st_size)
print("has L66 base", "AAA_L66" in t)
print("has cam L65", "AAA_Cam_L65_" in t)
