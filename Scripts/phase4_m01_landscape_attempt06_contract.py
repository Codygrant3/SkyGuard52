"""Load the immutable Attempt06 design with its cameras as the sole authority."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_repair_contract import load_attempt05_contract


ATTEMPT06_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT06.json"
)


def load_attempt06_contract() -> dict:
    effective = copy.deepcopy(load_attempt05_contract())
    repair = json.loads(ATTEMPT06_PATH.read_text(encoding="utf-8-sig"))
    outputs = repair["future_immutable_outputs"]
    capture = repair["capture_revision"]
    effective["schema"] = repair["schema"]
    effective["contract_id"] = repair["contract_id"]
    effective["status"] = repair["status"]
    effective["candidate"]["immutable_map"] = outputs["map"]
    effective["candidate"]["file"] = outputs["map_file"]
    effective["candidate"]["landscape_material"] = outputs["material"]
    effective["candidate"]["must_not_exist_before_authoring"] = True
    effective["candidate"]["must_never_overwrite_baseline"] = True
    # This replacement is mandatory. Attempt05 omitted it and therefore used
    # legacy IDs/transforms while the visual gate expected renamed cameras.
    effective["capture"]["cameras"] = copy.deepcopy(capture["cameras"])
    effective["capture"]["resolution"] = copy.deepcopy(capture["resolution"])
    effective["capture"]["rhi"] = "D3D12"
    effective["capture"]["shader_model"] = "SM6"
    effective["repair"] = repair
    return effective
