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
DOCS = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery04"
CONTRACT = DOCS / "execution_contract.json"
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04\build_m01_visible_environment_kit_refinement01_stagea_recovery04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04\invoke_m01_visible_environment_kit_refinement01_stagea_recovery04_once.ps1"
BASE = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py"
R3_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json"
R3_INVENTORY = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY03_ATTEMPT01_ARTIFACT_INVENTORY.json"
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04\attempt_01",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery04",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_TERMINAL_SUPERVISOR.json",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_EMERGENCY_RECEIPT.jsonl",
)
DOC_FILES = (
    "recovery03_evidence_reconciliation.json",
    "art_remediation_contract.json",
    "geometry_material_specification.json",
    "lighting_exposure_contract.json",
    "camera_visual_rubric.json",
    "execution_contract.json",
)


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, size: int, digest: str) -> None:
    require(path.is_file(), f"missing file: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(sha256(path) == digest, f"hash mismatch: {path}")


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_stagea_recovery04_worker", WORKER)
    require(spec is not None and spec.loader is not None, "worker import spec unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_powershell() -> None:
    escaped = str(SUPERVISOR).replace("'", "''")
    command = (
        "$e=$null;$t=$null;"
        f"[Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|ForEach-Object{$_.Message};exit 1}else{exit 0}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    require(result.returncode == 0, f"PowerShell parse failed: {result.stdout}{result.stderr}")


def verify_freeze(path: Path, size: int, digest: str, count: int) -> int:
    verify_file(path, size, digest)
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("classification") == "FAILED_WITH_EVIDENCE", f"classification drift: {path}")
    require(data.get("member_count") == count, f"member count drift: {path}")
    members = data.get("members", [])
    require(len(members) == count, f"member list drift: {path}")
    for member in members:
        verify_file(Path(member["path"]), int(member["bytes"]), member["sha256"])
    return len(members)


def main() -> int:
    verify_file(BASE, 42238, "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12")
    verify_file(WORKER, 41658, "bbd3cdc704ad9346c74f832eaae261e60ecc5597623dad0caba361b25b6f4159")
    r3_members = verify_freeze(R3_FREEZE, 3229, "2c413e1833e35840140a55bdf2302ccf6f3829f9031336454d0ad77b4610be61", 7)
    r3_inventory_members = verify_freeze(R3_INVENTORY, 6475, "84ebdcc3b1a4843271ce2be4a1cd78ef3c6cbc065d01a78f02e59fe83c41cf61", 24)

    for name in DOC_FILES:
        path = DOCS / name
        require(path.is_file(), f"missing design artifact: {path}")
        json.loads(path.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["gate"] == "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04", "gate drift")
    require(contract["execution"]["timeout_seconds"] == 3600, "timeout drift")
    require(contract["execution"]["blender_launch_count"] == 1, "launch count drift")
    require(contract["execution"]["automatic_retry_count"] == 0, "retry count drift")
    require(contract["output_contract"]["expected_total_file_count"] == 37, "output cardinality drift")
    require(contract["output_contract"]["final_png_count"] == 15, "final render count drift")
    require(contract["output_contract"]["checkpoint_png_count"] == 3, "checkpoint count drift")

    module = load_worker()
    corrected, receipt = module.load_recovery04_source()
    tree = ast.parse(corrected, filename="bounded_stagea_recovery04_worker.py")
    functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    require(set(module.REPLACEMENTS) <= functions, "a governed replacement function is absent")
    require(receipt["function_replacement_count"] == 13, "replacement cardinality drift")
    require(receipt["failed_output_geometry_reused"] is False, "failed geometry reuse drift")
    require(receipt["threshold_relaxation"] is False, "threshold relaxation drift")
    require(receipt["preliminary_conditions"] == ["daylight", "overcast", "night"], "checkpoint condition drift")
    require("VisibleEnvironmentKit_Refinement01_StageA_Recovery03" not in corrected, "Recovery03 output read/reuse path present")
    require("SM_M01_STAGEA_DuneGrass_" not in corrected, "failed L-shaped vegetation remains")
    require('0.008 if condition == "night" else 0.025' in corrected, "mean-luminance guard changed")
    require('0.70 if condition == "night" else 0.42' in corrected, "black-fraction guard changed")
    require('"night": ((0.025, 0.045, 0.095, 1.0), 0.23, 0.38, 1550.0, 1050.0, 520.0, 1.10)' in corrected, "night setup drift")
    require('require(len(results) == 15, "Final render count is not exactly fifteen")' in corrected, "final cardinality guard missing")
    require("bpy.data.images.load(str(path), check_existing=False)" in corrected, "saved-PNG measurement missing")
    require("luma.size == width * height and luma.size > 0" in corrected, "fail-closed luma validation missing")

    supervisor = SUPERVISOR.read_text(encoding="utf-8-sig")
    require(len(re.findall(r"\bStart-Process\b", supervisor)) == 1, "supervisor must contain exactly one Start-Process")
    require("$TimeoutSeconds = 3600" in supervisor, "supervisor timeout drift")
    require("Assert-Recovery03TerminalFreeze" in supervisor, "Recovery03 authority binding missing")
    require("recovery03_artifact_members_verified = 24" in supervisor, "Recovery03 artifact inventory binding missing")
    require("stagea_recovery04" in supervisor and "StageA_Recovery04" in supervisor, "fresh Recovery04 namespace binding missing")
    require("Start-Process" not in supervisor.split("if ($OfflineContractTest)", 1)[1].split("else", 1)[0], "offline mode can reach Blender launch")
    parse_powershell()

    for path in FUTURE:
        require(not path.exists(), f"future namespace already exists: {path}")

    report = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery04.offline-verification.v1",
        "classification": "PASS",
        "recovery03_terminal_members_verified": r3_members,
        "recovery03_artifact_members_verified": r3_inventory_members,
        "worker_python_ast": "PASS",
        "worker_function_replacements": 13,
        "threshold_relaxation": False,
        "failed_geometry_reused": False,
        "supervisor_start_process_count": 1,
        "powershell_5_1_parse": "PASS",
        "future_namespaces_absent": True,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2), file=sys.stderr)
        raise SystemExit(1)
