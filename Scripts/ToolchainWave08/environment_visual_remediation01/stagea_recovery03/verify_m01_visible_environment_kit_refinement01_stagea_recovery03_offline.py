from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageARecovery03/execution_contract.json"
WRAPPER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery02/build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery03/invoke_m01_visible_environment_kit_refinement01_stagea_recovery03_once.ps1"
RECOVERY01_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
RECOVERY02_TERMINAL_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02_OFFLINE_CONTRACT_ATTEMPT01_TERMINAL_FREEZE.json"
RECOVERY01_CHECKPOINT = ROOT / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA_Recovery01/renders/checkpoints/checkpoint_01_cross_section.png"
FUTURE = (
    ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03/attempt_01",
    ROOT / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA_Recovery03",
    ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_TERMINAL_SUPERVISOR.json",
    ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_EMERGENCY_RECEIPT.jsonl",
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
    spec = importlib.util.spec_from_file_location("stagea_recovery03_bound_worker", WRAPPER)
    require(spec is not None and spec.loader is not None, "wrapper import spec failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    require(len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n", f"invalid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def verify_recovery01_freeze() -> int:
    verify_file(RECOVERY01_FREEZE, 5197, "fc74e099a87ca1829d3f1e25b90df89112662a1b265dee6308da217f7c6466c9")
    freeze = json.loads(RECOVERY01_FREEZE.read_text(encoding="utf-8"))
    require(freeze["classification"] == "FAILED_WITH_EVIDENCE", "Recovery01 classification drift")
    require(freeze["member_count"] == 13, "Recovery01 member count drift")
    for member in freeze["members"]:
        verify_file(Path(member["path"]), int(member["bytes"]), str(member["sha256"]))
    return len(freeze["members"])


def verify_recovery02_terminal_freeze() -> int:
    verify_file(
        RECOVERY02_TERMINAL_FREEZE,
        1668,
        "ffcaab137433f713e931c579fb580c8c624646a1131ece36e79f397f4cc6c848",
    )
    freeze = json.loads(RECOVERY02_TERMINAL_FREEZE.read_text(encoding="utf-8"))
    require(
        freeze["classification"]
        == "FAILED_WITH_EVIDENCE_NO_BLENDER_LAUNCHED_RECOVERY02_NAMESPACE_TERMINAL",
        "Recovery02 offline-contract classification drift",
    )
    require(freeze["member_count"] == 4, "Recovery02 terminal member count drift")
    for member in freeze["members"]:
        verify_file(Path(member["path"]), int(member["bytes"]), str(member["sha256"]))
    return len(freeze["members"])


def validate() -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    ast.parse(wrapper_text, filename=str(WRAPPER))
    parse_powershell(SUPERVISOR)

    require(contract["gate"] == "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03", "gate drift")
    correction = contract["bounded_correction"]
    for key in ("geometry_changes", "material_changes", "camera_changes", "render_setting_changes", "export_changes", "receipt_contract_changes"):
        require(correction[key] == 0, f"unauthorized correction drift: {key}")
    require(contract["execution"]["blender_launch_count"] == 1, "launch count drift")
    require(contract["execution"]["automatic_retry_count"] == 0, "retry count drift")
    require(contract["execution"]["timeout_seconds"] == 2700, "timeout drift")
    require(contract["output_contract"]["final_png_count"] == 15, "render count drift")
    require(contract["output_contract"]["checkpoint_png_count"] == 3, "checkpoint count drift")
    for authority in contract["authorities"]:
        verify_file(Path(authority["path"]), int(authority["bytes"]), str(authority["sha256"]))

    module = load_wrapper()
    corrected, receipt = module.load_bounded_source()
    ast.parse(corrected, filename="bounded_stagea_recovery03_worker.py")
    require(receipt["passed"] is True, "bounded patch receipt failed")
    require(receipt["roughness_token_count"] == 1, "roughness token cardinality drift")
    require(receipt["measurement_token_count"] == 1, "measurement token cardinality drift")
    require("rough = np.repeat(rough, size, axis=1)" not in corrected, "redundant repeat remains")
    require(corrected.count("rough.shape == (size, size, 1)") == 1, "shape assertion cardinality drift")
    require(corrected.count("bpy.data.images.load(str(path), check_existing=False)") == 1, "saved-PNG load cardinality drift")
    require(corrected.count("bpy.data.images.remove(measured)") == 1, "temporary image cleanup cardinality drift")
    require("bpy.data.images.get(\"Render Result\")" not in corrected, "empty Render Result path remains")
    require("luma.size == width * height and luma.size > 0" in corrected, "fail-closed luma validation missing")
    require(corrected.count("np.repeat(base_rgb, size, axis=1)") == 1, "unrelated base-color path changed")
    require("np.repeat(rough, 3, axis=2)" in corrected, "RGB channel expansion changed")

    require(len(re.findall(r"\bStart-Process\b", supervisor_text)) == 1, "supervisor must contain exactly one Start-Process")
    require("$AuthorizeSingleBlender" in supervisor_text and "$OfflineContractTest" in supervisor_text, "supervisor modes missing")
    require("Get-Sha256Lower" in supervisor_text and "Get-PngDimensions" in supervisor_text, "self-contained validation missing")
    require("Write-TerminalEvidence" in supervisor_text and "EmergencyReceipt" in supervisor_text, "terminal lifecycle missing")
    require("retry_count = 0" in supervisor_text, "zero-retry evidence missing")
    require("$hasOfflineEvidenceRoot" in supervisor_text, "safe offline-evidence routing missing")
    require(
        "$writeTerminal = ($hasOfflineEvidenceRoot -or $AuthorizeSingleBlender)" in supervisor_text,
        "invalid offline invocation can still write the governed terminal namespace",
    )
    require("Assert-Recovery02TerminalFreeze" in supervisor_text, "Recovery02 terminal authority binding missing")

    frozen_members = verify_recovery01_freeze()
    recovery02_terminal_members = verify_recovery02_terminal_freeze()
    require(png_dimensions(RECOVERY01_CHECKPOINT) == (1280, 720), "saved Recovery01 checkpoint is not 1280x720")
    require(not any(path.exists() for path in FUTURE), "future governed namespace already exists")

    return {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery03.offline-verification.v1",
        "classification": "PASS",
        "authority_count": len(contract["authorities"]),
        "recovery01_frozen_members_verified": frozen_members,
        "recovery02_terminal_members_verified": recovery02_terminal_members,
        "wrapper_python_ast": "PASS",
        "bounded_source_python_ast": "PASS",
        "supervisor_powershell_5_1_parse": "PASS",
        "saved_checkpoint_dimensions": [1280, 720],
        "single_saved_png_measurement_replacement": True,
        "one_start_process": True,
        "automatic_retries": 0,
        "future_namespaces_absent": True,
        "failed_recovery01_preserved": True,
        "failed_recovery02_terminal_preserved": True,
        "missing_offline_evidence_root_cannot_create_governed_terminal": True,
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
