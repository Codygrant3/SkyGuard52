from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
NS = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery02"
CONTRACT = NS / "vegetation_staging01_recovery02_contract.json"
WORKER = NS / "author_m01_polyhaven_vegetation_staging01_recovery02.py"
SUPERVISOR = NS / "invoke_m01_polyhaven_vegetation_staging01_recovery02_once.ps1"
BOUNDS = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY.json"
FAILURE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    require(BOUNDS.stat().st_size == 7858 and sha(BOUNDS) == "3528b8c143d6f77f383a13787519d491fc32a5b92cc9d9e882ee0883334c67ab", "Exact bounds authority changed")
    require(FAILURE.stat().st_size == 8712 and sha(FAILURE) == "fef9027bdbe914b1690572b101c225758a7da27f6250aeee62abe1fc82f0cfe7", "Recovery01 failure changed")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    bounds = {row["asset_id"]: row for row in json.loads(BOUNDS.read_text(encoding="utf-8"))["assets"]}
    compile(WORKER.read_text(encoding="utf-8"), str(WORKER), "exec")
    worker = WORKER.read_text(encoding="utf-8")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require('set_editor_property("generate_lightmap_u_vs", True)' in worker, "Reflection-proven property absent")
    require('set_editor_property("generate_lightmap_uvs", True)' not in worker, "Rejected property remains")
    require(supervisor.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "One-launch contract failed")
    require("Remove-Item" not in supervisor and "retry_count = 0" in supervisor, "Preservation rule failed")
    for asset in contract["assets"]:
        require(asset["dimension_authority"] == "EXACT_GLTF_TRANSFORMED_POSITION_VERTICES", f"Dimension authority changed: {asset['id']}")
        expected = bounds[asset["id"]]["dimensions_cm"]
        require(all(abs(float(a)-float(b)) < 1e-9 for a,b in zip(asset["expected_dimensions_cm"], expected)), f"Bounds mismatch: {asset['id']}")
    for key in ("asset_disk_root", "map_path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(contract["fresh_outputs"][key]).exists(), f"Fresh Recovery02 namespace exists: {key}")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('{SUPERVISOR}',[ref]$null,[ref]$e)|Out-Null;if($e.Count){{$e|ForEach-Object{{$_.Message}};exit 1}}"], capture_output=True, text=True, check=False)
    require(result.returncode == 0, f"PowerShell parse failed: {result.stdout} {result.stderr}")
    print(json.dumps({"classification":"PASS","contract":{"bytes":CONTRACT.stat().st_size,"sha256":sha(CONTRACT)},"worker":{"bytes":WORKER.stat().st_size,"sha256":sha(WORKER)},"supervisor":{"bytes":SUPERVISOR.stat().st_size,"sha256":sha(SUPERVISOR)},"exact_bounds_assets":len(bounds),"fresh_namespaces_absent":True}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
