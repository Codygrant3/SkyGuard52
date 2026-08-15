from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
NAMESPACE = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery01"
CONTRACT = NAMESPACE / "vegetation_staging01_recovery01_contract.json"
WORKER = NAMESPACE / "author_m01_polyhaven_vegetation_staging01_recovery01.py"
SUPERVISOR = NAMESPACE / "invoke_m01_polyhaven_vegetation_staging01_recovery01_once.ps1"
ATTEMPT01_FREEZE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_ATTEMPT01_TERMINAL_FREEZE.json"
REFLECTION_FREEZE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE_TERMINAL_FREEZE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    require(ATTEMPT01_FREEZE.stat().st_size == 3162 and sha(ATTEMPT01_FREEZE) == "6ece421d626c1b7ff11dabb918e45155269e9c090e994dd49dde47abbcb0d549", "Attempt01 freeze changed")
    require(REFLECTION_FREEZE.stat().st_size == 2404 and sha(REFLECTION_FREEZE) == "45407419e75220df5a2ca0337418ec8487d7ef8313ada500d04f1f19a543db31", "Reflection freeze changed")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    compile(WORKER.read_text(encoding="utf-8"), str(WORKER), "exec")
    worker = WORKER.read_text(encoding="utf-8")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require('set_editor_property("generate_lightmap_u_vs", True)' in worker, "Verified UE 5.8 property is absent")
    require('set_editor_property("generate_lightmap_uvs", True)' not in worker, "Rejected property remains")
    require(supervisor.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "One-launch rule failed")
    require("retry_count = 0" in supervisor, "Zero-retry receipt missing")
    require("Remove-Item" not in supervisor, "Deletion path present")
    require(str(contract["fresh_outputs"]["asset_root"]).endswith("VegetationStaging01Recovery01"), "Fresh asset root changed")
    for key in ("asset_disk_root", "map_path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(contract["fresh_outputs"][key]).exists(), f"Fresh Recovery01 namespace exists: {key}")
    parse = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", f"$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('{SUPERVISOR}',[ref]$null,[ref]$e)|Out-Null;if($e.Count){{$e|ForEach-Object{{$_.Message}};exit 1}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    require(parse.returncode == 0, f"PowerShell parse failed: {parse.stdout} {parse.stderr}")
    print(json.dumps({
        "classification": "PASS",
        "contract": {"path": str(CONTRACT), "bytes": CONTRACT.stat().st_size, "sha256": sha(CONTRACT)},
        "worker": {"path": str(WORKER), "bytes": WORKER.stat().st_size, "sha256": sha(WORKER)},
        "supervisor": {"path": str(SUPERVISOR), "bytes": SUPERVISOR.stat().st_size, "sha256": sha(SUPERVISOR)},
        "corrected_property": "generate_lightmap_u_vs",
        "failed_namespace_preserved": True,
        "fresh_recovery01_namespaces_absent": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
