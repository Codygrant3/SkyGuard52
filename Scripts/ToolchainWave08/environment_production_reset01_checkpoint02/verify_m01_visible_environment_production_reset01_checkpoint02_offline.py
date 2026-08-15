"""Fail-closed offline verifier for production Checkpoint02."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01_checkpoint02"
GENERATOR = HERE / "build_m01_visible_environment_production_reset01_checkpoint02.py"
ADJUDICATOR = HERE / "adjudicate_m01_visible_environment_production_reset01_checkpoint02.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentProductionReset01Checkpoint02\execution_contract.json"
AUTH = ROOT / r"Production\standing_heavy_process_authorization.json"
PROBE = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json"
FAILURE_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY02_TERMINAL_FREEZE.json"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02\attempt_01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for path in (GENERATOR, ADJUDICATOR, CONTRACT, AUTH, PROBE, FAILURE_FREEZE):
        assert path.is_file(), path
    ast.parse(GENERATOR.read_text(encoding="utf-8"), filename=str(GENERATOR))
    ast.parse(ADJUDICATOR.read_text(encoding="utf-8"), filename=str(ADJUDICATOR))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    assert auth["status"] == "ACTIVE"
    assert auth["execution_policy"]["per_run_user_authorization_required"] is False
    assert contract["execution"]["blender_launch_count"] == 1
    assert contract["execution"]["automatic_retry_count"] == 0
    assert contract["execution"]["unreal_launch_count"] == 0
    assert not OUTPUT.exists(), OUTPUT
    assert not ATTEMPT.exists(), ATTEMPT
    source = GENERATOR.read_text(encoding="utf-8")
    for token in ("bpy.ops.wm.open_mainfile", "bpy.ops.import_scene", "subprocess", "requests", "urllib"):
        assert token not in source, token
    for token in (
        'projection = "BOX"', "build_irregular_ribbon", "add_checkpoint02_facade_detail",
        "MULTIPLE_SCATTERING", "aerosol_density", "factory-empty Checkpoint01",
    ):
        assert token in source, token
    print(json.dumps({
        "classification": "PASS_READY_FOR_SINGLE_CHECKPOINT02_BLENDER",
        "generator": {"bytes": GENERATOR.stat().st_size, "sha256": sha256(GENERATOR)},
        "adjudicator": {"bytes": ADJUDICATOR.stat().st_size, "sha256": sha256(ADJUDICATOR)},
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
