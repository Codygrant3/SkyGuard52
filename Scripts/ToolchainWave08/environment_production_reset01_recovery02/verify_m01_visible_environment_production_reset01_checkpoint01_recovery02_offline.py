"""Offline verifier for the API-bound Recovery02 Blender gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01_recovery02"
WRAPPER = HERE / "build_m01_visible_environment_production_reset01_checkpoint01_recovery02.py"
ADJ = HERE / "adjudicate_m01_visible_environment_production_reset01_checkpoint01_recovery02.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentProductionReset01Checkpoint01Recovery02\execution_contract.json"
ORIGINAL = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py"
PROBE = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01_Recovery02"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01_RECOVERY02\attempt_01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    assert sha256(ORIGINAL) == "fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891"
    assert sha256(PROBE) == "c017409181b17a9f27fc909445d458ada586d096f0ab66a40fe4fe2b3d37f53e"
    for path in (WRAPPER, ADJ):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source = WRAPPER.read_text(encoding="utf-8")
    for token in ("MULTIPLE_SCATTERING", "aerosol_density", "gltf_export_properties", "BLENDER_EEVEE"):
        assert token in source, token
    assert "bpy.ops.wm.open_mainfile" not in source
    assert contract["preserved_contract"]["geometry_logic_change"] is False
    assert contract["preserved_contract"]["failed_output_read_or_reuse"] is False
    assert contract["preserved_contract"]["one_blender_launch"] is True
    assert contract["preserved_contract"]["automatic_retry_count"] == 0
    assert not OUTPUT.exists(), OUTPUT
    assert not ATTEMPT.exists(), ATTEMPT
    print(json.dumps({
        "classification": "PASS_READY_FOR_SINGLE_RECOVERY02_BLENDER",
        "wrapper": {"bytes": WRAPPER.stat().st_size, "sha256": sha256(WRAPPER)},
        "adjudicator": {"bytes": ADJ.stat().st_size, "sha256": sha256(ADJ)},
        "contract": {"bytes": CONTRACT.stat().st_size, "sha256": sha256(CONTRACT)}
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
