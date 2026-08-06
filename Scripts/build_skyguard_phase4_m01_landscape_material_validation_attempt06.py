"""Immutable Attempt06 authoring entrypoint.

This script is inert unless explicitly launched by the Attempt06 supervisor.
It refuses every pre-existing Attempt06 output and never overwrites Attempt05.
"""

from __future__ import annotations

import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import build_skyguard_phase4_m01_landscape_material_validation as authorer
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


TARGET_MAP = (
    "/Game/Skyguard/Maps/"
    "Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v6_attempt06"
)
MATERIAL_ROOT = (
    "/Game/Skyguard/Materials/Mission01/LandscapeValidation_v6_attempt06"
)
MATERIAL_PATH = (
    MATERIAL_ROOT + "/M_M01_Landscape_Validation_v6_attempt06"
)
REPORT_PATH = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_MATERIAL_BUILD_ATTEMPT06.json"
)


def main() -> None:
    contract = load_attempt06_contract()
    outputs = contract["repair"]["future_immutable_outputs"]
    if contract["candidate"]["immutable_map"] != TARGET_MAP:
        raise RuntimeError("Attempt06 map differs from immutable contract")
    if contract["candidate"]["landscape_material"] != MATERIAL_PATH:
        raise RuntimeError("Attempt06 material differs from immutable contract")
    for asset in (
        TARGET_MAP,
        MATERIAL_PATH,
        outputs["coverage_material"],
        outputs["component_id_material"],
    ):
        if unreal.EditorAssetLibrary.does_asset_exist(asset):
            raise RuntimeError(
                "Attempt06 immutable output already exists; refusing overwrite: "
                + asset
            )
    authorer.TARGET_MAP = TARGET_MAP
    authorer.MATERIAL_ROOT = MATERIAL_ROOT
    authorer.MATERIAL_PATH = MATERIAL_PATH
    authorer.REPORT_PATH = REPORT_PATH
    authorer.load_effective_contract = load_attempt06_contract
    authorer.main()


if __name__ == "__main__":
    main()
