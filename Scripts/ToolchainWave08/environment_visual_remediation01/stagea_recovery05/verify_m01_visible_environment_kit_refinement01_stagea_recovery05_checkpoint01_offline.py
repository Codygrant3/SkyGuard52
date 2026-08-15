from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\build_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\invoke_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01_once.ps1"
POSTFLIGHT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01.py"
WORKER_TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\test_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01_offline.py"
POSTFLIGHT_TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05_postflight\test_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01_postflight.py"
CONTRACT_DIR = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery05"
REPORT = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_OFFLINE_VERIFICATION.json"
R04_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json"

EXPECTED = {
    WORKER: (79498, "11c87230cfd1464bc83fea7b4b7d14efe4341be5f1adeb0512116e5e0a3aaa95"),
    SUPERVISOR: (21606, "5307938b53e98d2d1d768c0d3771201771f2a7d21bd98a9d12f8245d8a1fe508"),
    POSTFLIGHT: (7259, "051a2504d7a8e1e2476a3590531946ca0433bee5f65747f8324463759124a96c"),
    WORKER_TEST: (4191, "4af46950b922ca0a5f8315ae9afd802a594fdf998bd5dca738aaaa9f163e6a96"),
    POSTFLIGHT_TEST: (2034, "de70c574963001549f842f6dc1eb1b8563eb78b240409ce3e3f36aceda3796a1"),
    R04_FREEZE: (4822, "fda28107ec833226dd1b6dbaef626ca7f8607e7562079a95d46d1abacd0540e6"),
}
CONTRACT_NAMES = {
    "execution_contract.json",
    "art_redesign_contract.json",
    "checkpoint_camera_contract.json",
    "visual_acceptance_rubric.json",
    "png_validator_contract.json",
    "finalization01_deferred_contract.json",
    "recovery04_evidence_reconciliation.json",
    "source_diff_contract.json",
}
FUTURE = [
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01\attempt_01",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery05_Checkpoint01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_TERMINAL_SUPERVISOR.json",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_POSTFLIGHT.json",
]


class VerificationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_file(path: Path, size: int, digest: str) -> None:
    require(path.is_file(), f"Missing file: {path}")
    require(path.stat().st_size == size, f"Byte mismatch: {path}")
    require(sha256(path) == digest, f"Hash mismatch: {path}")


def load_worker():
    spec = importlib.util.spec_from_file_location("recovery05_checkpoint_worker", WORKER)
    require(spec is not None and spec.loader is not None, "Worker loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_powershell(path: Path) -> None:
    command = (
        "$e=$null;$t=$null;"
        f"[Management.Automation.Language.Parser]::ParseFile('{str(path).replace("'", "''")}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|ForEach-Object{$_.Message};exit 1}else{exit 0}"
    )
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=30)
    require(result.returncode == 0, f"PowerShell parse failed: {result.stdout} {result.stderr}")


def main() -> int:
    for path, (size, digest) in EXPECTED.items():
        verify_file(path, size, digest)
    freeze = json.loads(R04_FREEZE.read_text(encoding="utf-8-sig"))
    require(freeze["classification"] == "FAILED_WITH_EVIDENCE" and freeze["member_count"] == 8, "Recovery04 terminal freeze drift")
    for member in freeze["members"]:
        verify_file(Path(member["path"]), member["bytes"], member["sha256"])

    contract_paths = sorted(CONTRACT_DIR.glob("*.json"))
    require({path.name for path in contract_paths} == CONTRACT_NAMES, "Contract file set drift")
    contracts = {path.name: json.loads(path.read_text(encoding="utf-8-sig")) for path in contract_paths}
    execution = contracts["execution_contract.json"]
    require(execution["gate"] == "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01", "Gate drift")
    require(execution["output_contract"]["checkpoint_png_count"] == 9, "Checkpoint count drift")
    require(execution["output_contract"]["expected_total_file_count"] == 16, "Total file-count drift")
    require(execution["output_contract"]["glb_count"] == execution["output_contract"]["final_png_count"] == execution["output_contract"]["texture_png_count"] == 0, "Checkpoint-only contract drift")
    require(contracts["finalization01_deferred_contract.json"]["authorized"] is False, "Finalization is not deferred")

    module = load_worker()
    embedded, receipt = module.load_recovery05_source()
    tree = ast.parse(embedded)
    require(receipt["passed"] and receipt["checkpoint_only"] and receipt["checkpoint_count"] == 9, "Embedded worker receipt failed")
    require(receipt["recovery04_output_geometry_reused"] is False, "Recovery04 output geometry reuse drift")
    main_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    calls = [node.func.id for node in ast.walk(main_node) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
    for forbidden in ("create_texture_atlas", "render_final_views", "export_glb"):
        require(forbidden not in calls, f"Checkpoint main invokes {forbidden}")
    ast.parse(POSTFLIGHT.read_text(encoding="utf-8"))
    ast.parse(WORKER_TEST.read_text(encoding="utf-8"))
    ast.parse(POSTFLIGHT_TEST.read_text(encoding="utf-8"))
    parse_powershell(SUPERVISOR)
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    require(len(re.findall(r"\bStart-Process\b", supervisor)) == 1, "Supervisor launch path cardinality is not one")
    require("([int]$bytes[16] * 16777216)" in supervisor and "$bytes[16] -shl 24" not in supervisor, "Int32-safe PNG correction missing")
    require("New-PngHeaderFixture" in supervisor and "malformed signature" in supervisor and "truncated header" in supervisor and "wrong dimensions" in supervisor, "PNG fixture coverage missing")
    require("retry_count = 0" in supervisor, "Zero-retry contract missing")
    require("struct.unpack(\">II\", header[16:24])" in POSTFLIGHT.read_text(encoding="utf-8"), "Independent Python PNG decoder missing")
    for path in FUTURE:
        require(not path.exists(), f"Future governed namespace exists: {path}")

    payload = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery05-checkpoint01.offline-verification.v1",
        "classification": "PASS",
        "recovery04_terminal_members_verified": 8,
        "contract_count": len(contract_paths),
        "worker_python_ast": "PASS",
        "embedded_worker_python_ast": "PASS",
        "postflight_python_ast": "PASS",
        "powershell_5_1_parse": "PASS",
        "single_blender_launch_path": True,
        "automatic_retry_count": 0,
        "png_decoder": "INT32_SAFE_PLUS_PYTHON_INDEPENDENT",
        "future_namespaces_absent": len(FUTURE),
        "finalization_authorized": False,
        "blender_launch_count": 0,
        "unreal_launch_count": 0,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
