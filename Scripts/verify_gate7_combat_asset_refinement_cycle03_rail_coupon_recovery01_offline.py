from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
CONTRACT = PROJECT / (
    r"References\CombatAssets\CombatAsset_Refinement_Cycle03_Rail_Coupon_Recovery01_OfflineDesign"
    r"\contracts\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_EXECUTION_CONTRACT.json"
)
CONTRACT_BYTES = 6798
CONTRACT_SHA256 = "f57e5251344e8eda6b8ab6a91a50bf745d9b8ca2b5316558acb0438253b520a0"
WRAPPER = PROJECT / (
    r"References\CombatAssets\CombatAsset_Refinement_Cycle03_Rail_Coupon_Recovery01_OfflineDesign"
    r"\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_recovery01_attempt01.py"
)
WRAPPER_BYTES = 1715
WRAPPER_SHA256 = "1a82efe7cdd7c412cf3d8d200558ac97801c7afbfbcb356851ce5d65b4f2843e"
SUPERVISOR = PROJECT / r"Scripts\invoke_gate7_combat_asset_refinement_cycle03_rail_coupon_recovery01_once.ps1"
SUPERVISOR_BYTES = 16781
SUPERVISOR_SHA256 = "6fb9926ddf01050ca3f556dd0bf848c1d498280be8bb07b640db5914ee376c2d"
FUTURE_PATHS = [
    PROJECT / r"Saved\BuildAttempts\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01\attempt_01",
    PROJECT / r"Blender\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_ATTEMPT01",
    PROJECT / r"Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_TERMINAL_SUPERVISOR_MANIFEST.json",
    PROJECT / r"Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_EMERGENCY_RECEIPT.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path, expected_bytes: int, expected_hash: str) -> dict[str, object]:
    if not path.is_file():
        raise AssertionError(f"Missing file: {path}")
    actual_bytes = path.stat().st_size
    actual_hash = sha256(path)
    if actual_bytes != expected_bytes:
        raise AssertionError(f"Byte mismatch for {path}: {actual_bytes} != {expected_bytes}")
    if actual_hash != expected_hash:
        raise AssertionError(f"Hash mismatch for {path}: {actual_hash} != {expected_hash}")
    return {"path": str(path), "bytes": actual_bytes, "sha256": actual_hash}


def main() -> int:
    result: dict[str, object] = {
        "classification": "FAIL",
        "contract": None,
        "authority_count": 0,
        "wrapper": None,
        "supervisor": None,
        "json_validation_count": 0,
        "python_syntax": False,
        "powershell_parse": False,
        "start_process_count": 0,
        "normal_launch_is_blender_only": False,
        "retry_loop_absent": False,
        "future_namespaces_absent": False,
        "heavy_process_count": None,
        "errors": [],
    }
    try:
        result["contract"] = verify(CONTRACT, CONTRACT_BYTES, CONTRACT_SHA256)
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        result["json_validation_count"] = 1
        authority_records = []
        for authority in contract["authority_files"]:
            authority_records.append(
                verify(Path(authority["path"]), int(authority["bytes"]), authority["sha256"])
            )
        result["authority_count"] = len(authority_records)
        result["wrapper"] = verify(WRAPPER, WRAPPER_BYTES, WRAPPER_SHA256)
        wrapper_text = WRAPPER.read_text(encoding="utf-8")
        compile(wrapper_text, str(WRAPPER), "exec")
        if wrapper_text.count("EXPECTED_SOURCE_SHA256") < 2:
            raise AssertionError("Recovery wrapper lacks explicit immutable source verification")
        if wrapper_text.count("OLD_GATE") < 2 or wrapper_text.count("NEW_GATE") < 2:
            raise AssertionError("Recovery wrapper lacks bounded gate-identity substitution")
        result["python_syntax"] = True

        result["supervisor"] = verify(SUPERVISOR, SUPERVISOR_BYTES, SUPERVISOR_SHA256)
        supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
        result["start_process_count"] = len(re.findall(r"\bStart-Process\b", supervisor_text))
        if result["start_process_count"] != 1:
            raise AssertionError("Recovery supervisor must contain exactly one Start-Process")
        launch_lines = [line.strip() for line in supervisor_text.splitlines() if "Start-Process" in line]
        result["normal_launch_is_blender_only"] = (
            len(launch_lines) == 1 and "-FilePath $BlenderExecutable" in launch_lines[0]
        )
        if not result["normal_launch_is_blender_only"]:
            raise AssertionError("Recovery supervisor has an unexpected launch path")
        result["retry_loop_absent"] = not bool(
            re.search(r"(?im)^\s*(for|foreach|while)\b.*\bretry\b", supervisor_text)
        )
        if not result["retry_loop_absent"]:
            raise AssertionError("Recovery supervisor contains a retry loop")

        command = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            (
                "$e=$null; "
                "[void][System.Management.Automation.Language.Parser]::ParseFile("
                f"'{str(SUPERVISOR).replace(chr(39), chr(39) * 2)}',[ref]$null,[ref]$e); "
                "if($e.Count){$e|ConvertTo-Json -Compress;exit 7}else{exit 0}"
            ),
        ]
        parsed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        result["powershell_parse"] = parsed.returncode == 0
        if not result["powershell_parse"]:
            raise AssertionError(f"Windows PowerShell parser failed: {parsed.stdout} {parsed.stderr}")

        result["future_namespaces_absent"] = all(not path.exists() for path in FUTURE_PATHS)
        if not result["future_namespaces_absent"]:
            raise AssertionError("A future governed Recovery01 namespace exists")

        process_probe = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                (
                    "@(Get-CimInstance Win32_Process|?{$_.Name -match "
                    "'^(blender|UnrealEditor|ShaderCompileWorker|AutomationTool|UnrealBuildTool|cl|link)(\\.exe)?$'}).Count"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if process_probe.returncode != 0:
            raise AssertionError(f"Heavy-process probe failed: {process_probe.stderr}")
        result["heavy_process_count"] = int(process_probe.stdout.strip())
        if result["heavy_process_count"] != 0:
            raise AssertionError("Heavy process detected during offline verification")

        for path in [
            PROJECT / r"Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_TERMINAL_EVIDENCE_RECONCILIATION.json",
            PROJECT / r"Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_MEMBER_PARITY.json",
            PROJECT / r"Saved\Reports\GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_INVENTORY_SEMANTIC_COMPARISON.json",
        ]:
            json.loads(path.read_text(encoding="utf-8"))
            result["json_validation_count"] += 1

        result["classification"] = "PASS"
    except Exception as exc:
        result["errors"].append(str(exc))

    print(json.dumps(result, indent=2))
    return 0 if result["classification"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
