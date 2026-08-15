import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
RECOVERY01_FREEZE = ROOT / "Docs/AAA_Review/M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
RECOVERY01_PROBE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_pivot01/runtime_probe_recovery01/probe_landscape_grounding_runtime_recovery01.py"
PROBE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_pivot01/runtime_probe_recovery02/probe_landscape_grounding_runtime_recovery02.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_pivot01/runtime_probe_recovery02/invoke_runtime_probe_recovery02_once.ps1"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02_EMERGENCY_RECEIPT.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_freeze_members(errors: list[str]) -> None:
    require(RECOVERY01_FREEZE.is_file(), "Recovery01 terminal freeze is missing", errors)
    if not RECOVERY01_FREEZE.is_file():
        return
    require(RECOVERY01_FREEZE.stat().st_size == 3238, "Recovery01 freeze byte mismatch", errors)
    require(sha256(RECOVERY01_FREEZE) == "c965133a56b5a7c8d98ec285f9a7092b6aae7ad60cf3cc00808936d3efad603f", "Recovery01 freeze hash mismatch", errors)
    payload = json.loads(RECOVERY01_FREEZE.read_text(encoding="utf-8"))
    for member in payload.get("members", []):
        path = ROOT / member["path"]
        require(path.is_file(), f"Frozen member is missing: {member['path']}", errors)
        if path.is_file():
            require(path.stat().st_size == member["bytes"], f"Frozen member byte mismatch: {member['path']}", errors)
            require(sha256(path) == member["sha256"], f"Frozen member hash mismatch: {member['path']}", errors)


def main() -> int:
    errors: list[str] = []
    verify_freeze_members(errors)
    for path in (RECOVERY01_PROBE, PROBE, SUPERVISOR):
        require(path.is_file(), f"Required source is missing: {path}", errors)
    if not errors:
        old_probe = RECOVERY01_PROBE.read_text(encoding="utf-8")
        new_probe = PROBE.read_text(encoding="utf-8")
        expected_probe = old_probe.replace(
            r"M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01\attempt_01",
            r"M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02\attempt_01",
        )
        require(new_probe == expected_probe, "Recovery02 probe differs beyond the fresh attempt namespace", errors)
        require(PROBE.stat().st_size == 7274, "Recovery02 probe byte count changed", errors)
        require(sha256(PROBE) == "bcc3e9700035cf0cb97f87d3342a49efd2d21a0741c423f3e303832a3741ac31", "Recovery02 probe hash mismatch", errors)

        source = SUPERVISOR.read_text(encoding="utf-8")
        require(source.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain exactly one Unreal Start-Process path", errors)
        require("$NativeHandle = $Process.Handle" in source, "Supervisor does not retain the native process handle", errors)
        require(source.index("$NativeHandle = $Process.Handle") < source.index("while (-not $Process.HasExited"), "Native process handle is retained too late", errors)
        require("Assert-NumericExitCode $CapturedExitCode" in source, "Numeric exit-code validation is missing", errors)
        require("$CapturedExitCode.GetType().FullName" in source, "Exit-code type persistence is missing", errors)
        require("retry_count = 0" in source, "Zero-retry evidence is missing", errors)
        require("$OfflineContractTest" in source and "PASS_OFFLINE_CONTRACT" in source, "Offline contract mode is missing", errors)
        require("Write-JsonAtomic $TerminalManifest $State" in source, "Guaranteed terminal manifest path is missing", errors)
        require("M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01\\attempt_01" not in source, "Supervisor reuses the Recovery01 attempt namespace", errors)
        malformed_throw = re.findall(r"(?m)\bthrow(?=['\"A-Za-z])", source)
        require(not malformed_throw, "Malformed compact throw tokenization is present", errors)
        require("Start-Process" not in source.split("function Invoke-OfflineContractTest", 1)[1].split("if ($OfflineContractTest)", 1)[0], "Offline contract function contains a process launch", errors)

    require(not ATTEMPT.exists(), "Recovery02 governed attempt namespace already exists", errors)
    require(not TERMINAL.exists(), "Recovery02 terminal manifest already exists", errors)
    require(not EMERGENCY.exists(), "Recovery02 emergency receipt already exists", errors)

    result = {
        "schema": "skyguard.m01-landscape-grounding-bridge01.runtime-probe-recovery02-offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": {
            "recovery01_freeze_and_members_verified": not any("Recovery01" in error or "Frozen member" in error for error in errors),
            "probe_diff_bounded_to_namespace": not any("probe" in error.lower() for error in errors),
            "single_unreal_launch_path": not any("Start-Process" in error for error in errors),
            "native_handle_retained": not any("native process handle" in error.lower() for error in errors),
            "malformed_throw_tokens_absent": not any("throw tokenization" in error for error in errors),
            "future_namespaces_absent": not any("already exists" in error for error in errors),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
