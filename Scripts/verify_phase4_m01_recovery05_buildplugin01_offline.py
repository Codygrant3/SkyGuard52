from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SUPERVISOR = ROOT / "Scripts" / "build_phase4_m01_recovery05_buildplugin01_once.ps1"
MIGRATION_FREEZE = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_TERMINAL_FREEZE.json"
POST_INVENTORY = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_ACTIVE_PLUGIN_ROOT_MIGRATION01_POST_MIGRATION_INVENTORY.json"
RECOVERY04_FREEZE = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json"
FUTURE = [
    Path(r"D:\SG52R05P01"),
    ROOT / "Saved/BuildAttempts/PHASE4_M01_RECOVERY05_BUILDPLUGIN01/build_attempt_01",
    ROOT / "Saved/BuildAttempts/PHASE4_M01_RECOVERY05_BUILDPLUGIN01/runtime_attempt_01",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY05_BUILDPLUGIN01_EMERGENCY_RECEIPT.jsonl",
]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)

def main() -> int:
    require(MIGRATION_FREEZE.stat().st_size == 3428 and digest(MIGRATION_FREEZE) == "681254354931d611aeed0bf702086064d50b4b47d90446f2de26faf7a1394f27", "Migration freeze mismatch")
    require(POST_INVENTORY.stat().st_size == 12569 and digest(POST_INVENTORY) == "8c4db237b825e88941b48c232898f087cb0fe23253b4a3f96500af52d3cb9fc6", "Post-migration inventory mismatch")
    require(RECOVERY04_FREEZE.stat().st_size == 5005 and digest(RECOVERY04_FREEZE) == "f23f8858ff4e0b65735cd498e022c7dcc32a0755b13a23f18f878ab363002aa5", "Recovery04 freeze mismatch")
    freeze = json.loads(MIGRATION_FREEZE.read_text(encoding="utf-8"))
    require(freeze["classification"] == "PASSED_READY_FOR_EXPLICIT_RECOVERY05_PLUGIN_BUILD_AUTHORIZATION", "Migration classification mismatch")
    for member in freeze["members"]:
        path = Path(member["path"])
        require(path.stat().st_size == member["bytes"] and digest(path) == member["sha256"], f"Frozen member mismatch: {path}")
    inventory = json.loads(POST_INVENTORY.read_text(encoding="utf-8"))
    require((inventory["record_count"], inventory["active_record_count"], inventory["quarantine_record_count"]) == (23, 5, 18), "Inventory counts mismatch")
    for record in inventory["records"]:
        path = Path(record["current_path"])
        require(path.stat().st_size == record["bytes"] and digest(path) == record["sha256"], f"Plugin record mismatch: {path}")
    roots = sorted(p.name for p in (ROOT / "Plugins").iterdir() if p.is_dir())
    require(roots == ["SkyguardRecovery03NativeRecovery05"], f"Unexpected active plugin roots: {roots}")
    descriptor = json.loads((ROOT / "Plugins/SkyguardRecovery03NativeRecovery05/SkyguardRecovery03NativeRecovery05.uplugin").read_text(encoding="utf-8-sig"))
    require(descriptor.get("EnabledByDefault") is False, "Plugin is not disabled by default")
    module_names = [m["Name"] for m in descriptor["Modules"]]
    require(module_names == ["SkyguardRecovery03NativeRecovery05"], "Module identity mismatch")
    build_cs = (ROOT / "Plugins/SkyguardRecovery03NativeRecovery05/Source/SkyguardRecovery03NativeRecovery05/SkyguardRecovery03NativeRecovery05.Build.cs").read_text(encoding="utf-8")
    require(len(re.findall(r"class\s+SkyguardRecovery03NativeRecovery05\b", build_cs)) == 1, "ModuleRules identity mismatch")
    source = SUPERVISOR.read_text(encoding="utf-8")
    require(source.count("Start-Process") == 1, "Supervisor must contain exactly one Start-Process")
    require("while (-not $process.HasExited" in source and "retry_count = 0" in source, "Process or retry contract missing")
    for forbidden in ("AutomationTool.exe", "RunUAT.bat", "cmd.exe"):
        require(forbidden not in source, f"Forbidden launcher present: {forbidden}")
    required_tokens = [
        r"D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe",
        r"D:\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll",
        "BuildPlugin", "-TargetPlatforms=Win64", "-Rocket", "-StrictIncludes", "-NoP4",
        r"-Plugin=$Descriptor", r"-Package=$PackageRoot",
        "OfflineContractTest", "AuthorizeSingleBuild", "Get-Sha256", "EmergencyReceipt",
    ]
    for token in required_tokens:
        require(token in source, f"Required supervisor token missing: {token}")
    for path in FUTURE:
        require(not path.exists(), f"Future namespace already exists: {path}")
    print(json.dumps({"classification": "PASS", "verified_plugin_records": 23, "active_records": 5, "quarantine_records": 18, "start_process_count": 1, "retry_count": 0}, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
