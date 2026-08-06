"""Future immutable attempt05 authoring entrypoint.

This module reuses the reviewed six-sampler authorer with new immutable paths
and the native live render-readiness gate. It must be launched only by the
authorized attempt05 supervisor.
"""

from __future__ import annotations

import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import build_skyguard_phase4_m01_landscape_material_validation as authorer
from phase4_m01_landscape_repair_contract import load_attempt05_contract


TARGET_MAP = (
    "/Game/Skyguard/Maps/"
    "Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v5_attempt05"
)
MATERIAL_ROOT = (
    "/Game/Skyguard/Materials/Mission01/LandscapeValidation_v5_attempt05"
)
MATERIAL_PATH = (
    MATERIAL_ROOT + "/M_M01_Landscape_Validation_v5_attempt05"
)
REPORT_PATH = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_MATERIAL_BUILD_ATTEMPT05.json"
)


def main() -> None:
    contract = load_attempt05_contract()
    if contract["candidate"]["immutable_map"] != TARGET_MAP:
        raise RuntimeError("Attempt05 map differs from repair contract")
    if contract["candidate"]["landscape_material"] != MATERIAL_PATH:
        raise RuntimeError("Attempt05 material differs from repair contract")
    authorer.TARGET_MAP = TARGET_MAP
    authorer.MATERIAL_ROOT = MATERIAL_ROOT
    authorer.MATERIAL_PATH = MATERIAL_PATH
    authorer.REPORT_PATH = REPORT_PATH
    authorer.load_effective_contract = load_attempt05_contract
    authorer.main()


if __name__ == "__main__":
    main()
