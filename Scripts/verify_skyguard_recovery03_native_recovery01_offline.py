from __future__ import annotations

import json
import pathlib
import subprocess

ROOT = pathlib.Path(r"D:\Skyguard52")
PLUGIN = ROOT / "Plugins/SkyguardRecovery03NativeRecovery01"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> int:
    contract = json.loads((ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_CONTRACT.json").read_text())
    descriptor = json.loads((PLUGIN / "SkyguardRecovery03NativeRecovery01.uplugin").read_text())
    source = (PLUGIN / "Source/SkyguardRecovery03NativeRecovery01/Private/SkyguardRecovery03NativeRecovery01Module.cpp").read_text()
    header = (PLUGIN / "Source/SkyguardRecovery03NativeRecovery01/Public/SkyguardRecovery03NativeRecovery01Module.h").read_text()
    supervisor = (ROOT / "Scripts/build_skyguard_recovery03_native_recovery01_once.ps1").read_text()
    require(descriptor["EnabledByDefault"] is False, "plugin enabled by default")
    require(contract["plugin"]["name"] == "SkyguardRecovery03NativeRecovery01", "plugin identity mismatch")
    forbidden = (
        "TODO",
        "placeholder",
        "native implementation has not passed",
        "intentionally not execution-ready",
        "-ExecutePythonScript",
    )
    for token in forbidden:
        require(token not in source, f"forbidden source marker: {token}")
    for marker in (
        "FTSTicker::GetCoreTicker().AddTicker",
        "VerifyImmutableInputs",
        "VerifyWorldAndAssets",
        "CreateFreshOutput",
        "BindTransientMaterial",
        "RequiredStablePolls",
        "WarmupSeconds",
        "MeasureSeconds",
        "RequiredFrames",
        "RequiredCaptures",
        "CaptureCurrent",
        "RestoreMaterial",
        "WriteTerminalReceipt",
        "RequestExitWithStatus",
        "compilation_resumed_measurement_reset",
    ):
        require(marker in source or marker in header, f"missing lifecycle marker: {marker}")
    require(source.index("VerifyImmutableInputs(Issue)") < source.index("CreateFreshOutput(Issue)"), "namespace precedes immutable preflight")
    require(source.index("WriteTerminalReceipt(") < source.rindex("RequestExitWithStatus("), "shutdown can precede terminal receipt")
    require("AutomationTool.exe" in supervisor, "native AutomationTool executable absent")
    require("cmd.exe" not in supervisor, "failed cmd wrapper retained")
    require(supervisor.count("Start-Process -FilePath $automationTool") == 1, "build launch count is not one")
    require("$process.WaitForExit()" in supervisor and "$process.Refresh()" in supervisor, "exit capture incomplete")
    require("D:\\SG52R03B02" in supervisor, "short package root absent")
    projected = json.loads((ROOT / "Saved/Reports/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_PROJECTED_PATHS.json").read_text())
    require(projected["longest_projected_length"] < 240, "projected path is not below 240")
    exit_probe = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(ROOT / "Scripts/test_skyguard_recovery03_native_recovery01_exit.ps1")],
        check=True, capture_output=True, text=True,
    )
    exit_result = json.loads(exit_probe.stdout)
    require(exit_result["success"]["actual"] == 0, "success exit code lost")
    require(exit_result["failure"]["actual"] == 7, "failure exit code lost")
    require(exit_result["success"]["type"] == "System.Int32", "success exit type changed")
    require(exit_result["failure"]["type"] == "System.Int32", "failure exit type changed")
    require(exit_result["null_rejected"] is True, "null exit code accepted")
    absent = [
        ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01/build_attempt_01",
        ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01/runtime_attempt_01",
        pathlib.Path(r"D:\SG52R03B02"),
    ]
    require(all(not path.exists() for path in absent), "offline gate created a future namespace")
    print(json.dumps({
        "schema": "skyguard.recovery03-native-recovery01-offline-verifier.v1",
        "gate": "PASS",
        "projected_longest_path": projected["longest_projected_length"],
        "exit_test": exit_result,
        "future_namespaces_absent": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
