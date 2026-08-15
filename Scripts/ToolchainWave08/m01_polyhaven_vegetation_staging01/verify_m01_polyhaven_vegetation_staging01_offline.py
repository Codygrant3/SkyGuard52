from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
NAMESPACE = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01"
CONTRACT = NAMESPACE / "vegetation_staging01_contract.json"
WORKER = NAMESPACE / "author_m01_polyhaven_vegetation_staging01.py"
SUPERVISOR = NAMESPACE / "invoke_m01_polyhaven_vegetation_staging01_once.ps1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "PASSED_READY_FOR_EXPLICIT_SINGLE_UNREAL_STAGING_AUTHORIZATION", "Contract classification changed")
    compile(WORKER.read_text(encoding="utf-8"), str(WORKER), "exec")
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require(supervisor.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "Supervisor must contain one Unreal launch")
    require("retry_count = 0" in supervisor, "Zero-retry receipt is missing")
    require("Remove-Item" not in supervisor, "Supervisor contains a deletion path")
    require("-NullRHI" in supervisor, "Staging authoring must use NullRHI")
    require("RuntimePromotionAllowed\", \"false" in WORKER.read_text(encoding="utf-8"), "Promotion guard is absent")
    require(len(contract["assets"]) == 5, "Candidate count changed")
    require(all(asset["id"] != "tree_small_02" for asset in contract["assets"]), "Held tree entered contract")
    require(sum(int(asset["placement_count"]) for asset in contract["assets"]) == 28, "Placement count changed")
    for entry in [contract["project"], contract["editor"], *contract["accepted_source_authorities"]]:
        path = Path(entry["path"])
        require(path.is_file() and path.stat().st_size == int(entry["bytes"]) and sha256(path) == entry["sha256"], f"Authority mismatch: {path}")
    for asset in contract["assets"]:
        path = Path(asset["gltf"])
        require(path.is_file() and path.stat().st_size == int(asset["gltf_bytes"]) and sha256(path) == asset["gltf_sha256"], f"Source mismatch: {path}")
    fresh = contract["fresh_outputs"]
    for key in ("asset_disk_root", "map_path", "attempt", "terminal_manifest", "emergency_receipt"):
        require(not Path(fresh[key]).exists(), f"Fresh namespace exists: {fresh[key]}")
    parse = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", f"$e=$null;[System.Management.Automation.Language.Parser]::ParseFile('{SUPERVISOR}',[ref]$null,[ref]$e)|Out-Null;if($e.Count){{$e|ForEach-Object{{$_.Message}};exit 1}}"],
        text=True,
        capture_output=True,
        check=False,
    )
    require(parse.returncode == 0, f"PowerShell parse failed: {parse.stdout} {parse.stderr}")
    print(json.dumps({
        "classification": "PASS",
        "contract": {"path": str(CONTRACT), "bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)},
        "worker": {"path": str(WORKER), "bytes": WORKER.stat().st_size, "sha256": sha256(WORKER)},
        "supervisor": {"path": str(SUPERVISOR), "bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR)},
        "candidate_count": 5,
        "placement_count": 28,
        "fresh_namespaces_absent": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
