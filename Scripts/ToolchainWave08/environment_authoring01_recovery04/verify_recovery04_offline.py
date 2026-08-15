import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(r"D:\Skyguard52")
SCRIPT_DIR = ROOT / "Scripts" / "ToolchainWave08" / "environment_authoring01_recovery04"
SUPERVISOR = SCRIPT_DIR / "invoke_dependency_probe_once.ps1"
PROBE = SCRIPT_DIR / "probe_environment_dependencies.py"
OLD_PROBE = ROOT / "Scripts" / "ToolchainWave08" / "environment_authoring01_recovery03" / "probe_environment_dependencies.py"
INPUT_MAP = pathlib.Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
EXPECTED_INPUT = "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"
FUTURE = [
    ROOT / "Saved" / "BuildAttempts" / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_DEPENDENCY_PROBE" / "attempt_01",
    ROOT / "Saved" / "Reports" / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_DEPENDENCY_PROBE_TERMINAL_MANIFEST.json",
    ROOT / "Saved" / "Reports" / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_DEPENDENCY_PROBE_EMERGENCY_RECEIPT.jsonl",
    ROOT / "Saved" / "BuildAttempts" / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04" / "attempt_01",
    pathlib.Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery04.umap"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    failures = []
    for path in (SUPERVISOR, PROBE, OLD_PROBE, INPUT_MAP):
        if not path.is_file():
            failures.append(f"missing file: {path}")
    if failures:
        print(json.dumps({"classification": "FAIL", "failures": failures}, indent=2))
        return 1
    source = SUPERVISOR.read_text(encoding="utf-8-sig")
    if digest(PROBE) != digest(OLD_PROBE):
        failures.append("Recovery04 probe is not byte-identical to Recovery03")
    if digest(INPUT_MAP) != EXPECTED_INPUT:
        failures.append("accepted input map hash mismatch")
    if source.count("$process.Start()") != 1:
        failures.append("authorized process start count is not exactly one")
    if "Start-Process" in source:
        failures.append("alternate Start-Process command exists")
    if re.search(r"(?i)\b(retry|relaunch)\s*\(", source):
        failures.append("retry function detected")
    dispatch = source.find("# Mode dispatch occurs before the governed lifecycle")
    governed = source.find("# Governed paths and the outer terminal lifecycle exist only in authorized mode")
    if dispatch < 0 or governed < 0 or dispatch >= governed:
        failures.append("mode dispatch does not precede governed lifecycle")
    offline_segment = source[source.find("function Invoke-OfflineContractTest"):source.find("function Invoke-AuthorizationRefusal")]
    refusal_segment = source[source.find("function Invoke-AuthorizationRefusal"):source.find("function Invoke-CapturedProcess")]
    if "Write-Output" in offline_segment or "Write-Output" in refusal_segment:
        failures.append("mode function writes diagnostics to the success pipeline")
    conflict_segment = source[source.find("if ($OfflineContractTest -and $AuthorizeSingleDependencyProbe)"):source.find("if ($OfflineContractTest) {")]
    if "Write-Error" in conflict_segment:
        failures.append("conflicting-switch branch contains terminating Write-Error")
    if "[Console]::Error.WriteLine" not in conflict_segment or "[Environment]::Exit([int]3)" not in conflict_segment:
        failures.append("conflicting-switch nonterminating diagnostic or exit 3 is missing")
    stale_recovery02 = [line for line in source.splitlines() if "recovery02" in line.lower()]
    if stale_recovery02:
        failures.append("stale Recovery02 version label remains in Recovery04 supervisor")
    if "PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY04_FREEZE" not in source:
        failures.append("Recovery04 successful-probe classification is missing")
    if offline_segment.count("return [int]") != 2:
        failures.append("offline mode does not contain exactly two scalar Int32 returns")
    if refusal_segment.count("return [int]") != 1:
        failures.append("authorization refusal does not contain exactly one scalar Int32 return")
    for required in ("returned a null exit code", "returned a collection", "expected System.Int32"):
        if required not in source:
            failures.append(f"missing scalar/type assertion: {required}")
    if "%TEMP%" in offline_segment:
        failures.append("literal TEMP expansion used instead of .NET temp path")
    if "GetTempPath" not in source or "[Guid]::NewGuid" not in source:
        failures.append("unique temporary offline root contract missing")
    if "Invoke-CapturedProcess" in offline_segment:
        failures.append("offline test contains Unreal launch call")
    if "-NoSaveOnExit" not in source or "-NullRHI" not in source:
        failures.append("read-only Unreal arguments missing")
    prohibited = ("duplicate_asset", "save_asset", "save_loaded_asset", "save_map")
    probe_text = PROBE.read_text(encoding="utf-8-sig").lower()
    for token in prohibited:
        if token in probe_text:
            failures.append(f"probe contains prohibited mutation token: {token}")
    existing = [str(path) for path in FUTURE if path.exists()]
    if existing:
        failures.append("future governed namespaces exist: " + ", ".join(existing))
    result = {
        "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery04.offline-verifier.v1",
        "classification": "PASS" if not failures else "FAIL",
        "failures": failures,
        "supervisor_sha256": digest(SUPERVISOR),
        "probe_sha256": digest(PROBE),
        "input_sha256": digest(INPUT_MAP),
        "future_namespaces_absent": not existing,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
