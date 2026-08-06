"""Load the future attempt05 contract without changing attempt04 governance."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


REPAIR_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT05.json"
)


def load_attempt05_contract() -> dict:
    effective = copy.deepcopy(load_effective_contract())
    repair = json.loads(REPAIR_PATH.read_text(encoding="utf-8-sig"))
    outputs = repair["future_immutable_outputs"]
    effective["schema"] = repair["schema"]
    effective["contract_id"] = repair["contract_id"]
    effective["status"] = repair["status"]
    effective["candidate"]["immutable_map"] = outputs["map"]
    effective["candidate"]["file"] = (
        "Content/Skyguard/Maps/"
        "Lvl_M01_CoastalIntercept_LandscapeMaterialValidation_v5_attempt05.umap"
    )
    effective["candidate"]["landscape_material"] = outputs["material"]
    effective["candidate"]["must_not_exist_before_authoring"] = True
    effective["candidate"]["must_never_overwrite_baseline"] = True
    effective["repair"] = repair
    return effective
