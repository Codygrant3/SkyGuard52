from pathlib import Path
import subprocess
p = Path(r"D:\Skyguard52\Saved\Logs\aaa-builder.pid")
pid = p.read_text(encoding="utf-8").strip() if p.exists() else ""
print("pid", pid)
if pid:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{ '1' }} else {{ '0' }}"],
        capture_output=True,
        text=True,
    )
    print("alive", (r.stdout or "").strip())
log = Path(r"D:\Skyguard52\Saved\Logs\skyguard-aaa-foundation.log")
print("log_exists", log.exists(), "size", log.stat().st_size if log.exists() else 0)
if log.exists():
    t = log.read_text(encoding="utf-8", errors="replace").splitlines()
    hits = [ln for ln in t if ("SkyguardAAA" in ln or "Fatal error" in ln or "LogPython" in ln)][-20:]
    print("HITS")
    print("\n".join(hits))
    print("TAIL")
    print("\n".join(t[-25:]))
m = Path(r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap")
print("map", m.exists(), m.stat().st_size if m.exists() else None)
