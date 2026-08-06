from pathlib import Path
import ast
p = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop70_true_art_slice13_capture.py")
lines = p.read_text(encoding="utf-8", errors="replace").splitlines(True)
out = []
for line in lines:
    if "note=l69_freeze_true_art_slice13_vfx_core_airframe_response" in line and "f.write" in line:
        out.append('        f.write("note=l69_freeze_true_art_slice13_vfx_core_airframe_response\\n")\n')
    else:
        out.append(line)
text = "".join(out)
ast.parse(text)
p.write_text(text, encoding="utf-8")
print("FIXED", p.stat().st_size)
print("cam70", "AAA_Cam_L70_" in text)
print("inject", "slice13 vfx core language" in text)
print("ensure13", "ensure_slice13_materials" in text)
print("pointlight", "spawn_point_light" in text)
# host audit
ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop69.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L69", "AAA_L70")
    .replace("loop69", "loop70")
    .replace("Loop 69", "Loop 70")
    .replace("Loop69", "Loop70")
    .replace("AAA_Cam_L69_", "AAA_Cam_L70_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop70.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
