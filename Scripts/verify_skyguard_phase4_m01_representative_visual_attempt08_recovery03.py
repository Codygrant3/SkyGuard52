from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
RECOVERY03_ATTEMPT = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03/attempt_01"
RECOVERY03_LAUNCHER = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03/launcher_attempt_01"
RECOVERY03_PREFLIGHT = ROOT / "Saved/Reports/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_EXECUTION_PREFLIGHT.json"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    terminal = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_TERMINAL_FREEZE.json"
    require(terminal.stat().st_size > 0, "Recovery02 terminal freeze missing")
    require(
        sha256(terminal) == "d0aa35e85168ad900b90fd753d74ffb939a14cc7195e7e9c4ec17354ccccc238",
        "Recovery02 terminal freeze changed",
    )
    contract_path = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    require(contract["classification"] == "FAILED_WITH_EVIDENCE", "dishonest Recovery03 classification")
    require(contract["lifecycle"]["execute_python_script_forbidden"] is True, "ExecutePythonScript not forbidden")
    require(contract["network"]["network_attempts_required"] == 0, "network count is not zero")
    require(contract["render"]["total_png_count"] == 8, "capture count changed")
    require(contract["render"]["warmup_seconds"] == 30, "warmup changed")
    require(contract["render"]["measurement_seconds"] == 30, "measurement changed")
    require(contract["render"]["minimum_frame_samples"] == 900, "sample minimum changed")
    for path in (RECOVERY03_ATTEMPT, RECOVERY03_LAUNCHER, RECOVERY03_PREFLIGHT):
        require(not path.exists(), f"reserved offline namespace exists: {path}")
    supervisor = (ROOT / "Scripts/invoke_skyguard_phase4_m01_representative_visual_attempt08_recovery03.ps1").read_text(encoding="utf-8")
    require("-ExecutePythonScript" not in supervisor, "supervisor still owns lifecycle through ExecutePythonScript")
    require(supervisor.count("Start-Process -FilePath $editor") == 1, "supervisor must have exactly one Unreal launch path")
    require("while (" not in supervisor.lower(), "retry loop detected")
    require("$process.WaitForExit" in supervisor and "$process.Refresh()" in supervisor, "numeric exit lifecycle incomplete")
    require("actual_exit_code_type" in supervisor, "exit-code type not persisted")
    require("-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared" in supervisor, "plugin suppression mismatch")
    require("bSendUsageData=False" in supervisor, "analytics override missing")
    native = (ROOT / "Plugins/SkyguardRecovery03/Source/SkyguardRecovery03/Private/SkyguardRecovery03Module.cpp").read_text(encoding="utf-8")
    for marker in (
        "FTSTicker::GetCoreTicker().AddTicker",
        "bTerminalReceiptWritten",
        "RestoreOriginalMaterial",
        "RequestExitWithStatus",
        "RequiredAuthorization",
        "RequiredAttemptSuffix",
    ):
        require(marker in native, f"native lifecycle marker missing: {marker}")
    require("ExecutePythonScript" not in native, "native source mentions forbidden lifecycle owner")
    exit_test = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(ROOT / "Scripts/test_skyguard_recovery03_process_exit.ps1")],
        check=True,
        capture_output=True,
        text=True,
    )
    exit_result = json.loads(exit_test.stdout)
    require(exit_result["success"]["actual"] == 0, "success exit code not retained")
    require(exit_result["failure"]["actual"] == 7, "failure exit code not retained")
    require(exit_result["null_rejected"] is True, "null exit code not rejected")
    print(json.dumps({
        "schema": "skyguard.recovery03.offline-verifier.v1",
        "gate": "FAILED_WITH_EVIDENCE",
        "design_checks_passed": True,
        "unreal_ready": False,
        "blocking_prerequisite": "compiled and hash-frozen Recovery03 plugin binary",
        "reserved_namespaces_absent": True,
        "lightweight_exit_test": exit_result,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

