from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
OLD_SOURCE = ROOT / (
    r"References\CombatAssets\CombatBlockout_Cycle02_Recovery02_OfflineDesign"
    r"\source\blender_gate7_combat_blockout_cycle02_recovery02_attempt01.py"
)
SOURCE = ROOT / (
    r"References\CombatAssets\CombatBlockout_Cycle02_Recovery03_OfflineDesign"
    r"\source\blender_gate7_combat_blockout_cycle02_recovery03_attempt01.py"
)
OLD_SUPERVISOR = ROOT / r"Scripts\invoke_gate7_combat_blockout_cycle02_recovery02_once.ps1"
SUPERVISOR = ROOT / r"Scripts\invoke_gate7_combat_blockout_cycle02_recovery03_once.ps1"
HARNESS = ROOT / r"Scripts\test_gate7_recovery03_process_exit_capture.ps1"
PROBES = ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_EXIT_CODE_PROBES.json"

AUTHORITIES = {
    ROOT / r"Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json":
        (7991, "9a255b9ab21c2794951b89631aa9d52588249f91c83999d02d4d372a21d5a873"),
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01_POSTFLIGHT.json":
        (10708, "1950863e4361d67b935aa8e78aa490918072bfca3bb362290d91994ef5bab666"),
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_TERMINAL_SUPERVISOR_MANIFEST.json":
        (7362, "cb31309f5c7d530719964ac9e19e69f957cd22ddab12f2fc8efbf82cce856894"),
    ROOT / r"Docs\AAA_Review\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_OFFLINE_DESIGN_FREEZE.json":
        (4229, "211d30e6167dc735cdf5489a413e0cd27d7311b64a2b2f2f2e7f8ce5d6b2da5b"),
    OLD_SUPERVISOR:
        (18751, "32fca763ef2d833dcca15e6dc136afbf9fa1d928c38dce70e1b31042b49d6db1"),
    OLD_SOURCE:
        (19609, "7123bd7c45ceb6a7fc299b2ac34ab7eb2749bd89cb1ee1cc66b81cb2a31c2b45"),
    Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"):
        (112975320, "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7"),
}

JSON_ARTIFACTS = (
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_CORRECTION_CONTRACT.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_SOURCE_DIFF.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_SUPERVISOR_DIFF.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_TERMINAL_EVIDENCE_RECONCILIATION.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_PROCESS_EXIT_FAILURE_ANALYSIS.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_PROJECTED_PATH_REPORT.json",
    PROBES,
)

FUTURE = (
    ROOT / r"Saved\BuildAttempts\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03\attempt_01",
    ROOT / r"Blender\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / r"Saved\Reports\GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_EMERGENCY_RECEIPT.jsonl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    failures: list[str] = []

    for path, (size, digest) in AUTHORITIES.items():
        check(path.is_file(), f"Missing authority: {path}", failures)
        if path.is_file():
            check(path.stat().st_size == size, f"Authority byte mismatch: {path}", failures)
            check(sha256(path) == digest, f"Authority hash mismatch: {path}", failures)

    for path in JSON_ARTIFACTS:
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Invalid JSON {path}: {exc}")

    check(SOURCE.stat().st_size == 19609, "Recovery03 source byte count changed", failures)
    check(
        sha256(SOURCE) == "f486afea2547d246d653a5507a9957ea39b1f4dcdcc9a6ac66447ebd7fd84c9a",
        "Recovery03 source hash changed",
        failures,
    )
    try:
        ast.parse(SOURCE.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        failures.append(f"Recovery03 source syntax failed: {exc}")

    old_lines = OLD_SOURCE.read_text(encoding="utf-8").splitlines()
    new_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    changes = [(a, b) for a, b in zip(old_lines, new_lines, strict=True) if a != b]
    check(len(changes) == 1, "Blender source diff is not exactly one line", failures)
    if changes:
        check(
            changes[0]
            == (
                'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01"',
                'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01"',
            ),
            "Unexpected Blender source identity diff",
            failures,
        )
    check('scene.render.engine = "BLENDER_EEVEE"' in "\n".join(new_lines), "EEVEE binding changed", failures)

    supervisor = SUPERVISOR.read_text(encoding="utf-8-sig")
    check(supervisor.count("Start-Process") == 1, "Supervisor must contain one Start-Process", failures)
    check("$process.ExitCode.GetType()" not in supervisor, "Unsafe direct ExitCode.GetType pattern remains", failures)
    positions = {
        "launch": supervisor.index("Start-Process"),
        "handle": supervisor.index("$nativeHandle = $process.Handle"),
        "poll": supervisor.index("while (-not $process.HasExited"),
        "wait": supervisor.rindex("$process.WaitForExit()"),
        "refresh": supervisor.rindex("$process.Refresh()"),
        "capture": supervisor.index("$capturedExitCode = $process.ExitCode"),
        "null": supervisor.index("if ($null -eq $capturedExitCode)"),
        "int32": supervisor.index("$capturedExitCode -isnot [System.Int32]"),
        "type": supervisor.index("$State.exit_code_type = $capturedExitCode.GetType().FullName"),
    }
    check(
        positions["launch"] < positions["handle"] < positions["poll"],
        "Native handle is not retained before polling",
        failures,
    )
    check(
        positions["wait"] < positions["refresh"] < positions["capture"] < positions["null"]
        < positions["int32"] < positions["type"],
        "Exit-code validation ordering is invalid",
        failures,
    )
    check("native_handle_retained = $false" in supervisor, "Handle state field missing", failures)
    check("$State.native_handle_retained = $true" in supervisor, "Handle success persistence missing", failures)
    check("System.Security.Cryptography.SHA256" in supervisor, "Self-contained SHA-256 missing", failures)
    check("Write-TerminalEvidence" in supervisor, "Terminal lifecycle missing", failures)
    check("retry_count = 0" in supervisor, "Zero-retry contract missing", failures)
    check("-FilePath $BlenderExecutable" in supervisor, "Exact Blender launch binding missing", failures)

    harness = HARNESS.read_text(encoding="utf-8-sig")
    check(harness.count("Start-Process") == 1, "Probe harness should have one reusable Start-Process", failures)
    check("Invoke-ExitProbe 0" in harness and "Invoke-ExitProbe 7" in harness, "Required probes missing", failures)
    check("$process.Handle" in harness, "Probe native-handle retention missing", failures)
    check("$process.ExitCode.GetType()" not in harness, "Probe contains unsafe direct type access", failures)

    probe_data = json.loads(PROBES.read_text(encoding="utf-8-sig"))
    check(probe_data.get("classification") == "PASS", "Exit-code probes failed", failures)
    check(probe_data.get("child_launch_count") == 2, "Probe launch count is not two", failures)
    check(probe_data["success_probe"]["captured_exit_code"] == 0, "Success probe exit code mismatch", failures)
    check(probe_data["failure_probe"]["captured_exit_code"] == 7, "Failure probe exit code mismatch", failures)
    check(probe_data["success_probe"]["exit_code_type"] == "System.Int32", "Success type mismatch", failures)
    check(probe_data["failure_probe"]["exit_code_type"] == "System.Int32", "Failure type mismatch", failures)
    check(probe_data["null_probe"]["rejected"] is True, "Null probe was not rejected", failures)
    check(probe_data["null_probe"]["coerced_to_zero"] is False, "Null was coerced to zero", failures)
    check(probe_data.get("blender_launch_count") == 0, "Probe launched Blender", failures)
    check(probe_data.get("unreal_launch_count") == 0, "Probe launched Unreal", failures)

    for path in FUTURE:
        check(not path.exists(), f"Future governed namespace exists: {path}", failures)

    result = {
        "classification": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": {
            "authority_count": len(AUTHORITIES),
            "source_diff_count": len(changes),
            "supervisor_start_process_count": supervisor.count("Start-Process"),
            "probe_child_launch_count": probe_data.get("child_launch_count"),
            "future_namespaces_absent": all(not path.exists() for path in FUTURE),
        },
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
