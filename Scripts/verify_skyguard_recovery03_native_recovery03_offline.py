from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
SUPERVISOR = ROOT / "Scripts/build_skyguard_recovery03_native_recovery03_once.ps1"
CONTRACT = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_SUPERVISOR_CONTRACT.json"
PATHS = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_PROJECTED_PATHS.json"
TEST = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_EXACT_HOST_TEST.json"
ATTEMPT = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY03/build_attempt_01"
RUNTIME = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY03/runtime_attempt_01"
MANIFEST = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_EMERGENCY_RECEIPT.jsonl"
PACKAGE = pathlib.Path(r"D:\SG52R03B04")


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    paths = json.loads(PATHS.read_text(encoding="utf-8"))
    test = json.loads(TEST.read_text(encoding="utf-8"))
    source = SUPERVISOR.read_text(encoding="utf-8")
    ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"), filename=__file__)

    require(contract["contract_id"] == "P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY03", "contract id")
    require(contract["future_execution"]["package"] == "D:/SG52R03B04", "package root")
    require(contract["future_execution"]["automatic_retry"] is False, "retry prohibition")
    require(contract["hashing"]["module_autoload_required"] is False, "hashing must be self-contained")
    require(paths["gate"] == "PASS" and paths["longest_projected_length"] <= 213, "path limit")
    require(paths["longest_projected_length"] < 240, "hard path limit")

    forbidden_hash_command = "Get-" + "FileHash"
    require(forbidden_hash_command not in source, "forbidden hash command")
    require("System.IO.FileStream" in source, "FileStream hashing")
    require("System.Security.Cryptography.SHA256" in source, "SHA256 implementation")
    require(source.count("Start-Process -FilePath $dotnet") == 1, "one normal-build Start-Process")
    require("AutomationTool.exe" not in source, "AutomationTool.exe prohibited")
    require("RunUAT.bat" not in source, "RunUAT prohibited")
    require("cmd.exe" not in source, "cmd prohibited")
    require(r"C:\Program Files\dotnet" not in source, "system dotnet prohibited")
    require("[switch]$OfflineContractTest" in source, "offline mode")
    require("[switch]$AuthorizeSingleBuild" in source, "authorization guard")
    require("} finally {" in source, "outer terminal finally")
    require("Write-Emergency" in source, "emergency receipt")
    require("$processHandle = $process.Handle" in source, "process handle retention")
    require("$process.WaitForExit()" in source and "$process.Refresh()" in source, "exit stabilization")
    require("$process.ExitCode -isnot [int]" in source, "numeric exit validation")
    require("Copy-DirectoryFiles" in source and "$state.rebound = $true" in source, "gated rebind")
    require("retry_count = 0" in source and "automatic_retry = $false" in source, "no retry")
    require(
        re.search(r"Start-Process[^\r\n]*(UnrealEditor|UnrealEditor-Cmd)", source, re.IGNORECASE) is None,
        "no UnrealEditor launch path",
    )

    require(test["gate"] == "PASS", "exact-host test")
    require(test["powershell_host"]["exit_code"] == 0, "PowerShell exit")
    require(test["powershell_host"]["exit_code_type"] == "System.Int32", "PowerShell exit type")
    require(test["offline_terminal_manifest"]["preflight_passed"] is True, "offline preflight")
    require(test["offline_terminal_manifest"]["governed_build_namespace_created"] is False, "offline isolation")
    require(test["bundled_dotnet_success"]["exit_code"] == 0, "dotnet success")
    require(test["bundled_dotnet_success"]["exit_code_type"] == "System.Int32", "dotnet success type")
    require(test["bundled_dotnet_success"]["sdk_version"] == "10.0.203", "SDK version")
    require(test["bundled_dotnet_failure"]["exit_code"] != 0, "dotnet failure")
    require(test["bundled_dotnet_failure"]["exit_code_type"] == "System.Int32", "dotnet failure type")
    require(test["null_exit_code_rejected"] is True, "null rejection")
    require(test["automation_tool_launched"] is False and test["native_build_launched"] is False, "no build")

    for future in (ATTEMPT, RUNTIME, MANIFEST, EMERGENCY, PACKAGE):
        require(not future.exists(), f"future namespace exists: {future}")

    output = {
        "schema": "skyguard.recovery03-native-build-recovery03-offline-verification.v1",
        "gate": "PASS",
        "contract_sha256": sha256(CONTRACT),
        "supervisor_sha256": sha256(SUPERVISOR),
        "path_report_sha256": sha256(PATHS),
        "exact_host_test_sha256": sha256(TEST),
        "future_namespaces_absent": True,
        "native_build_launched": False,
        "unreal_launched": False,
        "blender_launched": False,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise
