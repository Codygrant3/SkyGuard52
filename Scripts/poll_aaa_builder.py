from pathlib import Path
import time
import subprocess

log = Path(r"D:\Skyguard52\Saved\Logs\skyguard-aaa-foundation.log")
pid_path = Path(r"D:\Skyguard52\Saved\Logs\aaa-builder.pid")
pid = int(pid_path.read_text(encoding="utf-8").strip()) if pid_path.exists() else None
print("pid", pid)
for i in range(48):
    alive = "?"
    if pid is not None:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{ '1' }} else {{ '0' }}"],
            capture_output=True,
            text=True,
        )
        alive = (r.stdout or "").strip()
    size = log.stat().st_size if log.exists() else 0
    hits = []
    if log.exists():
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [ln for ln in lines if ("SkyguardAAA" in ln or "Fatal error" in ln or "Error:" in ln and "datarouter" not in ln)][-10:]
    print(f"tick={i} alive={alive} size={size}")
    for h in hits:
        print(h[:250])
    if alive == "0":
        break
    time.sleep(5)
print("DONE")
if log.exists():
    print("\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-35:]))
# map size
m = Path(r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap")
print("map_exists", m.exists(), "size", m.stat().st_size if m.exists() else None)
mats = list(Path(r"D:\Skyguard52\Content\Skyguard\Materials").glob("*.uasset")) if Path(r"D:\Skyguard52\Content\Skyguard\Materials").exists() else []
print("materials", len(mats))
