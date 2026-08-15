"""Read-only UE probe of the preserved failed Stage04 import namespace."""

from __future__ import annotations

import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
DESTINATION = "/Game/M01/VisibleEnvironmentStage04/FacadeBayR02"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY01_IMPORT_PROBE01/attempt_01"
RECEIPT = ATTEMPT / "import_slot_probe.json"
EXPECTED = {
    "SM_M01_CoastalFacadeBay_A_BalconyDetails",
    "SM_M01_CoastalFacadeBay_A_Glass",
    "SM_M01_CoastalFacadeBay_A_Interior",
    "SM_M01_CoastalFacadeBay_A_StructureFrame",
}


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def object_path(value: object) -> str | None:
    return None if value is None else str(value.get_path_name())


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


result = {
    "schema": "skyguard.m01-visible-environment-stage04-recovery01.import-probe01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "read_only": True,
    "destination": DESTINATION,
    "meshes": [],
    "errors": [],
}

try:
    paths = sorted(unreal.EditorAssetLibrary.list_assets(DESTINATION, recursive=True, include_folder=False))
    require(paths, "Preserved failed Stage04 import namespace is empty")
    names = set()
    for path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(asset, unreal.StaticMesh):
            continue
        name = asset.get_name()
        if name not in EXPECTED:
            continue
        names.add(name)
        slots = list(asset.get_editor_property("static_materials"))
        result["meshes"].append({
            "name": name,
            "path": asset.get_path_name(),
            "material_slot_count": len(slots),
            "material_names": [object_path(slot.get_editor_property("material_interface")) for slot in slots],
            "bounds_origin_cm": vector(asset.get_bounds().origin),
            "bounds_extent_cm": vector(asset.get_bounds().box_extent),
        })
    result["meshes"].sort(key=lambda row: row["name"])
    require(names == EXPECTED, f"Preserved failed import mesh set changed: {sorted(names)}")
    result["classification"] = "PASSED_FAILED_IMPORT_SLOT_EVIDENCE_READY_FOR_STAGE04_RECOVERY01"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_STAGE04_RECOVERY01_IMPORT_PROBE=" + result["classification"])
if result["classification"] != "PASSED_FAILED_IMPORT_SLOT_EVIDENCE_READY_FOR_STAGE04_RECOVERY01":
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Stage04 import slot probe failed")
