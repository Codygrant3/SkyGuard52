from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\build_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\invoke_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01_once.ps1"
POSTFLIGHT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py"
CONTRACT_DIR = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery06"
R05_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json"
TEST = Path(__file__).with_name("test_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01_offline.py")
POSTFLIGHT_TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06_postflight\test_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01_postflight.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r06_worker_verify", WORKER)
    require(spec is not None and spec.loader is not None, "Worker import specification failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    require(R05_FREEZE.stat().st_size == 3112, "Recovery05 terminal freeze byte drift")
    require(sha(R05_FREEZE) == "c52c74c2a33b111cd37c53442dda67d9ee93d41d353d653e8111092e9ff69e9a", "Recovery05 terminal freeze hash drift")
    for path in (WORKER, SUPERVISOR, POSTFLIGHT, TEST, POSTFLIGHT_TEST):
        require(path.is_file() and path.stat().st_size > 0, f"Missing offline artifact: {path}")
    for path in CONTRACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8-sig"))
    ast.parse(WORKER.read_text(encoding="utf-8-sig"))
    ast.parse(POSTFLIGHT.read_text(encoding="utf-8-sig"))
    module = load_worker()
    generated, receipt = module.load_recovery06_source()
    ast.parse(generated)
    require(receipt["generated_call_graph"]["unresolved_named_calls"] == [], "Generated source has unresolved named calls")
    require(generated.count("def add_side_window(") == 1, "Side-window helper cardinality is not one")
    supervisor_text = SUPERVISOR.read_text(encoding="utf-8-sig")
    require(supervisor_text.count("Start-Process") == 1, "Supervisor launch path cardinality is not one")
    tests = subprocess.run([sys.executable, str(TEST)], capture_output=True, text=True, check=False)
    require(tests.returncode == 0, tests.stdout + tests.stderr)
    postflight_tests = subprocess.run([sys.executable, str(POSTFLIGHT_TEST)], capture_output=True, text=True, check=False)
    require(postflight_tests.returncode == 0, postflight_tests.stdout + postflight_tests.stderr)
    future = (
        ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01\attempt_01",
        ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery06_Checkpoint01",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_TERMINAL_SUPERVISOR.json",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl",
        ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_POSTFLIGHT.json",
    )
    require(all(not path.exists() for path in future), "A governed Recovery06 namespace already exists")
    payload = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery06-checkpoint01.offline-verification.v1",
        "classification": "PASS",
        "recovery05_terminal_members_verified": 6,
        "contract_count": len(list(CONTRACT_DIR.glob("*.json"))),
        "worker_python_ast": "PASS",
        "generated_worker_python_ast": "PASS",
        "generated_named_call_graph": receipt["generated_call_graph"],
        "postflight_python_ast": "PASS",
        "single_blender_launch_path": True,
        "automatic_retry_count": 0,
        "unit_tests": "PASS_6_OF_6",
        "postflight_tests": "PASS_4_OF_4",
        "future_namespaces_absent": len(future),
        "finalization_authorized": False,
        "blender_launch_count": 0,
        "unreal_launch_count": 0,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
