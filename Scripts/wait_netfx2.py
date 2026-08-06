from pathlib import Path
import time
import subprocess
for i in range(18):
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "if (Get-Process winget -ErrorAction SilentlyContinue) { '1' } else { '0' }"],
        capture_output=True, text=True,
    )
    alive = (r.stdout or "").strip()
    print(i, "winget", alive)
    for p in [
        r"C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A",
        r"C:\Program Files (x86)\Microsoft SDKs\NETFXSDK",
        r"C:\Program Files (x86)\Windows Kits\NETFXSDK",
    ]:
        print(" ", Path(p).exists(), p)
    if alive == "0":
        break
    time.sleep(10)
print("final checks")
for p in [
    r"C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A",
    r"C:\Program Files (x86)\Microsoft SDKs\NETFXSDK",
    r"C:\Program Files (x86)\Windows Kits\NETFXSDK",
]:
    print(Path(p).exists(), p)
