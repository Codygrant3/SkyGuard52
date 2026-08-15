"""Offline verifier for the bounded Blender 5.2 Recovery01 binding."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01_recovery01"
ORIGINAL = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py"
FAILED_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentProductionReset01Checkpoint01Recovery01\execution_contract.json"
WRAPPER = HERE / "build_m01_visible_environment_production_reset01_checkpoint01_recovery01.py"
ADJUDICATOR = HERE / "adjudicate_m01_visible_environment_production_reset01_checkpoint01_recovery01.py"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01_Recovery01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY01\attempt_01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    assert sha256(ORIGINAL) == "fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891"
    assert sha256(FAILED_FREEZE) == "a32ab971f4aa4d2cbfd332592716150fb9a3410a41e92eb22055b45506a01e10"
    for path in (WRAPPER, ADJUDICATOR, CONTRACT):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path)) if path.suffix == ".py" else json.loads(path.read_text(encoding="utf-8"))
    source = WRAPPER.read_text(encoding="utf-8")
    assert 'MULTIPLE_SCATTERING' in source
    assert 'NISHITA -> MULTIPLE_SCATTERING' in source
    assert 'bpy.ops.wm.open_mainfile' not in source
    assert 'failed output' in source.lower()
    assert not OUTPUT.exists(), OUTPUT
    assert not ATTEMPT.exists(), ATTEMPT
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["failure_correction"]["only_functional_change"] == "NISHITA -> MULTIPLE_SCATTERING"
    assert contract["failure_correction"]["geometry_logic_change"] is False
    assert contract["preserved_requirements"]["one_blender_launch"] is True
    assert contract["preserved_requirements"]["automatic_retry_count"] == 0
    print(json.dumps({
        "classification": "PASS_READY_FOR_SINGLE_RECOVERY01_BLENDER",
        "wrapper": {"bytes": WRAPPER.stat().st_size, "sha256": sha256(WRAPPER)},
        "adjudicator": {"bytes": ADJUDICATOR.stat().st_size, "sha256": sha256(ADJUDICATOR)},
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)}
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
