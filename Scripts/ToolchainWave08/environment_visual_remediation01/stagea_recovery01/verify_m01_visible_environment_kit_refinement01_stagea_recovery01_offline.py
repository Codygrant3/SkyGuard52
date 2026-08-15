from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageARecovery01/execution_contract.json"
WRAPPER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery01/build_m01_visible_environment_kit_refinement01_stagea_recovery01.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery01/invoke_m01_visible_environment_kit_refinement01_stagea_recovery01_once.ps1"
TERMINAL_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_ATTEMPT01_TERMINAL_FREEZE.json"
FAILED_OUTPUT = ROOT / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA"
FUTURE = (
    ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01/attempt_01",
    ROOT / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA_Recovery01",
    ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01_TERMINAL_SUPERVISOR.json",
    ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01_EMERGENCY_RECEIPT.jsonl",
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path: Path, size: int, digest: str) -> None:
    require(path.is_file(), f"missing authority: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(sha256(path) == digest.lower(), f"hash mismatch: {path}")


def parse_powershell(path: Path) -> None:
    escaped = str(path).replace("'", "''")
    command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|%{$_.ToString()};exit 1}else{'PASS'}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    require(result.returncode == 0 and "PASS" in result.stdout, f"PowerShell parse failed: {result.stdout} {result.stderr}")


def load_wrapper():
    spec = importlib.util.spec_from_file_location("stagea_recovery01_wrapper", WRAPPER)
    require(spec is not None and spec.loader is not None, "wrapper import spec failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_terminal_freeze() -> int:
    freeze = json.loads(TERMINAL_FREEZE.read_text(encoding="utf-8"))
    require(freeze["classification"] == "FAILED_WITH_EVIDENCE", "Attempt01 classification drift")
    for member in freeze["members"]:
        verify_file(Path(member["path"]), int(member["bytes"]), str(member["sha256"]))
    return len(freeze["members"])


def validate() -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    ast.parse(wrapper_text, filename=str(WRAPPER))
    parse_powershell(SUPERVISOR)

    require(contract["gate"] == "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01", "gate drift")
    require(contract["bounded_correction"]["geometry_changes"] == 0, "geometry correction is not permitted")
    require(contract["bounded_correction"]["render_camera_changes"] == 0, "camera correction is not permitted")
    require(contract["execution"]["blender_launch_count"] == 1, "launch count drift")
    require(contract["execution"]["automatic_retry_count"] == 0, "retry count drift")
    require(contract["execution"]["timeout_seconds"] == 2700, "timeout drift")
    require(contract["output_contract"]["final_png_count"] == 15, "render count drift")
    require(contract["output_contract"]["checkpoint_png_count"] == 3, "checkpoint count drift")
    for authority in contract["authorities"]:
        verify_file(Path(authority["path"]), int(authority["bytes"]), str(authority["sha256"]))

    module = load_wrapper()
    corrected, receipt = module.load_bounded_source()
    ast.parse(corrected, filename="bounded_stagea_recovery01.py")
    require(receipt["passed"] is True, "bounded patch receipt failed")
    require(receipt["old_token_count"] == 1, "old-token cardinality drift")
    require(receipt["new_token_count"] == 1, "new-token cardinality drift")
    require("rough = np.repeat(rough, size, axis=1)" not in corrected, "redundant repeat remains")
    require(corrected.count("rough.shape == (size, size, 1)") == 1, "shape assertion cardinality drift")
    require(corrected.count("np.repeat(base_rgb, size, axis=1)") == 1, "unrelated guarded base-color path changed")
    require("np.repeat(rough, 3, axis=2)" in corrected, "RGB channel expansion changed")

    require(len(re.findall(r"\bStart-Process\b", supervisor_text)) == 1, "supervisor must contain exactly one Start-Process")
    require("$AuthorizeSingleBlender" in supervisor_text and "$OfflineContractTest" in supervisor_text, "supervisor modes missing")
    require("Get-Sha256Lower" in supervisor_text and "Get-PngDimensions" in supervisor_text, "self-contained validation missing")
    require("Write-TerminalEvidence" in supervisor_text and "EmergencyReceipt" in supervisor_text, "terminal lifecycle missing")
    require("Start-Process" not in re.sub(r"Start-Process[\s\S]*", "", supervisor_text), "unexpected earlier launch path")

    frozen_members = verify_terminal_freeze()
    require(FAILED_OUTPUT.is_dir(), "failed output namespace missing")
    require(not any(path.is_file() for path in FAILED_OUTPUT.rglob("*")), "failed output namespace no longer has zero files")
    require(not any(path.exists() for path in FUTURE), "future governed namespace already exists")

    return {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery01.offline-verification.v1",
        "classification": "PASS",
        "authority_count": len(contract["authorities"]),
        "attempt01_frozen_members_verified": frozen_members,
        "wrapper_python_ast": "PASS",
        "bounded_source_python_ast": "PASS",
        "supervisor_powershell_5_1_parse": "PASS",
        "single_bounded_replacement": True,
        "maximum_contracted_texture_array_bytes": contract["bounded_correction"]["future_memory_bound"]["largest_single_texture_array_bytes"],
        "one_start_process": True,
        "automatic_retries": 0,
        "future_namespaces_absent": True,
        "failed_attempt_preserved": True,
        "heavy_processes_launched": 0,
    }


def main() -> int:
    try:
        print(json.dumps(validate(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
