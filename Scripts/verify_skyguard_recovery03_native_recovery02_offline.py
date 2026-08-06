from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY02_SUPERVISOR_CONTRACT.json"
SUPERVISOR = ROOT / "Scripts/build_skyguard_recovery03_native_recovery02_once.ps1"
HOST_TEST = ROOT / "Scripts/test_skyguard_recovery03_native_recovery02_bundled_host.ps1"
PATH_REPORT = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY02_PROJECTED_PATHS.json"
HOST_RESULT = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY02_BUNDLED_HOST_TEST.json"
ATTEMPT = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY02/build_attempt_01"
RUNTIME = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY02/runtime_attempt_01"
PACKAGE = pathlib.Path(r"D:\SG52R03B03")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    paths = json.loads(PATH_REPORT.read_text(encoding="utf-8"))
    source = SUPERVISOR.read_text(encoding="utf-8")
    test_source = HOST_TEST.read_text(encoding="utf-8")
    result = json.loads(HOST_RESULT.read_text(encoding="utf-8"))

    require(contract["contract_id"] == "P4.6-M01-RECOVERY03-NATIVE-BUILD-RECOVERY02", "contract id")
    require(contract["future_execution"]["executable"].endswith("/DotNet/10.0/win-x64/dotnet.exe"), "bundled dotnet executable")
    require(contract["future_execution"]["arguments"][0].endswith("/AutomationTool/AutomationTool.dll"), "AutomationTool.dll first argument")
    require(contract["future_execution"]["package"] == "D:/SG52R03B03", "fresh package root")
    require(contract["future_execution"]["automatic_retry"] is False, "automatic retry prohibited")
    require(paths["gate"] == "PASS" and paths["longest_projected_length"] <= 213, "path limit")
    require(paths["longest_projected_length"] < 240, "hard path limit")

    require(source.count("Start-Process -FilePath $dotnet") == 1, "exactly one build Start-Process")
    require("$automationAssembly," in source and "$arguments = @(" in source, "managed assembly argument")
    require("'BuildPlugin'" in source and "'-NoP4'" in source, "exact build argument set")
    require("$retry_count" not in source.lower(), "no retry loop variable")
    require("retry_count = 0" in source and "automatic_retry = $false" in source, "retry prohibition evidence")
    require("} finally {" in source and "terminal_supervisor_manifest.json" in source, "terminal manifest in outer finally")
    require("Write-Emergency" in source and "emergency_receipt.jsonl" in source, "emergency receipt")
    require("$process.WaitForExit()" in source and "$process.Refresh()" in source, "exit stabilization")
    require("$processHandle = $process.Handle" in source, "native process handle retention")
    require("$process.ExitCode -isnot [int]" in source, "numeric exit validation")
    require("actual_exit_code_type" in source, "exit type persistence")
    require("if ($null -eq $issue)" in source and "Copy-Item" in source, "success-gated rebind")
    require(source.index("if (Test-Path -LiteralPath $attemptRoot)") < source.index("New-Item -ItemType Directory -Path $logsRoot"), "preflight precedes namespace creation")
    require("Assert-File $terminalFreeze" in source and "Assert-File $sourceFreeze" in source, "freeze authority checks")
    require("$immutableFiles" in source and "foreach ($authority in $immutableFiles)" in source, "frozen file checks")
    for forbidden in ("cmd.exe", "RunUAT.bat", "AutomationTool.exe"):
        require(forbidden not in source, f"forbidden execution path: {forbidden}")
    require("ThirdParty\\DotNet\\10.0\\win-x64\\dotnet.exe" in source, "exact bundled host")
    require("DotNET\\AutomationTool\\AutomationTool.dll" in source, "exact AutomationTool assembly")
    require("Start-Process -FilePath $dotnet" in test_source, "host test direct launch")
    require("AutomationTool" not in test_source, "host test must not launch AutomationTool")

    for path in (ATTEMPT, RUNTIME, PACKAGE):
        require(not path.exists(), f"future namespace already exists: {path}")

    require(result["gate"] == "PASS", "bundled-host gate")
    require(result["success_probe"]["exit_code"] == 0, "success exit code")
    require(result["success_probe"]["exit_code_type"] == "System.Int32", "success exit type")
    require(result["success_probe"]["process_handle_retained"] is True, "success process handle retention")
    require(re.search(r"\b10\.0", result["success_probe"]["sdk_version"]) is not None, "bundled .NET 10 proof")
    require(result["failure_probe"]["exit_code"] != 0, "failure nonzero exit")
    require(result["failure_probe"]["exit_code_type"] == "System.Int32", "failure exit type")
    require(result["failure_probe"]["process_handle_retained"] is True, "failure process handle retention")
    require(result["null_exit_code_rejected"] is True, "null rejection")
    require(result["automation_tool_launched"] is False, "AutomationTool prohibition")

    output = {
        "schema": "skyguard.recovery03-native-build-recovery02-offline-verification.v1",
        "gate": "PASS",
        "contract_sha256": sha256(CONTRACT),
        "supervisor_sha256": sha256(SUPERVISOR),
        "host_test_sha256": sha256(HOST_TEST),
        "host_result_sha256": sha256(HOST_RESULT),
        "projected_paths_sha256": sha256(PATH_REPORT),
        "bundled_host_result": result,
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
