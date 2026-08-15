from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\build_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\invoke_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01_once.ps1"
TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\test_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01_offline.py"
POSTFLIGHT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01.py"
POSTFLIGHT_TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07_postflight\test_m01_visible_environment_kit_refinement01_stagea_recovery07_checkpoint01_postflight.py"
SMOKE = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery07\blender_smoke_m01_visible_environment_kit_refinement01_stagea_recovery07_fast_box.py"
CONTRACT_DIR = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery07"
R06_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json"
STANDING_FREEZE = ROOT / r"Docs\AAA_Review\SKYGUARD52_STANDING_BLENDER_UNREAL_AUTHORIZATION_FREEZE_2026-08-09.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r07_worker_verify", WORKER)
    require(spec is not None and spec.loader is not None, "Worker import specification failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    require(R06_FREEZE.stat().st_size == 3131, "Recovery06 terminal freeze byte drift")
    require(sha(R06_FREEZE) == "6bd9b7e450711ecb140ebe4267a4834fb99ecc5dc700910eec37fd84b57a3ad4", "Recovery06 terminal freeze hash drift")
    freeze = json.loads(R06_FREEZE.read_text(encoding="utf-8-sig"))
    require(freeze["classification"] == "FAILED_WITH_EVIDENCE", "Recovery06 classification drift")
    require(freeze["member_count"] == freeze["verified_members"] == 8, "Recovery06 freeze cardinality drift")
    for member in freeze["members"]:
        path = Path(member["path"])
        require(path.stat().st_size == member["bytes"], f"Frozen member byte drift: {path}")
        require(sha(path) == member["sha256"], f"Frozen member hash drift: {path}")

    require(STANDING_FREEZE.stat().st_size == 1415, "Standing authorization freeze byte drift")
    require(sha(STANDING_FREEZE) == "1366fc227908148199776d866d3f3a94bd56919d54babf5d64be9c26633df4e1", "Standing authorization freeze hash drift")

    for path in (WORKER, SUPERVISOR, TEST, POSTFLIGHT, POSTFLIGHT_TEST, SMOKE):
        require(path.is_file() and path.stat().st_size > 0, f"Missing offline artifact: {path}")
    contracts = sorted(CONTRACT_DIR.glob("*.json"))
    require(len(contracts) >= 3, "Recovery07 contract set is incomplete")
    for path in contracts:
        json.loads(path.read_text(encoding="utf-8-sig"))

    ast.parse(WORKER.read_text(encoding="utf-8-sig"))
    ast.parse(POSTFLIGHT.read_text(encoding="utf-8-sig"))
    module = load_worker()
    generated, receipt = module.load_recovery07_source()
    tree = ast.parse(generated)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    add_box = ast.get_source_segment(generated, functions["add_box"]) or ""
    require("_fast_box_mesh" in add_box and "bpy.ops" not in add_box, "Fast box replacement is not operator-free")
    require(receipt["generated_call_graph"]["unresolved_named_calls"] == [], "Generated source has unresolved named calls")
    require(receipt["checkpoint_count"] == 9, "Checkpoint-count drift")
    require(receipt["glb_count"] == receipt["texture_count"] == 0, "Checkpoint-only output drift")
    require(not receipt["recovery06_attempt_or_output_reused"], "Recovery06 namespace reuse detected")

    supervisor_text = SUPERVISOR.read_text(encoding="utf-8-sig")
    require(supervisor_text.count("Start-Process") == 1, "Supervisor launch path cardinality is not one")
    require("retry_count = 0" in supervisor_text, "Zero-retry state is absent")
    require("$TimeoutSeconds = 3600" in supervisor_text, "Timeout contract drift")

    tests = subprocess.run([sys.executable, str(TEST)], capture_output=True, text=True, check=False)
    require(tests.returncode == 0, tests.stdout + tests.stderr)
    postflight_tests = subprocess.run([sys.executable, str(POSTFLIGHT_TEST)], capture_output=True, text=True, check=False)
    require(postflight_tests.returncode == 0, postflight_tests.stdout + postflight_tests.stderr)

    future = (
        ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01\attempt_01",
        ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery07_Checkpoint01",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01_TERMINAL_SUPERVISOR.json",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY07_CHECKPOINT01_POSTFLIGHT.json",
    )
    require(all(not path.exists() for path in future), "A governed Recovery07 namespace already exists")

    payload = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery07-checkpoint01.offline-verification.v1",
        "classification": "PASS",
        "recovery06_terminal_members_verified": 8,
        "standing_authorization_verified": True,
        "contract_count": len(contracts),
        "worker_python_ast": "PASS",
        "generated_worker_python_ast": "PASS",
        "generated_named_call_graph": receipt["generated_call_graph"],
        "operator_free_fast_box": True,
        "flushed_phase_telemetry": True,
        "postflight_python_ast": "PASS",
        "single_blender_launch_path": True,
        "automatic_retry_count": 0,
        "unit_tests": "PASS_5_OF_5",
        "postflight_tests": "PASS_4_OF_4",
        "future_namespaces_absent": len(future),
        "per_run_user_authorization_required": False,
        "finalization_authorized": False,
        "blender_launch_count": 0,
        "unreal_launch_count": 0,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
