"""Read-only adjudication of the saved Stage04 Recovery03 map after shutdown crash."""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
MAP_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentStage04Recovery03"
MAP_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage04Recovery03.umap"
MAP_AUTHORITY = (978545, "70b0929008acafcd4d2c943e9eba6de02d0533752081e6794494b872966a5c18")
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentStage03.umap"
INPUT_AUTHORITY = (911233, "28c3462ffe39b6fe753e2ba96761aa0e54d3aa947b41c1c9be4c760202980cad")
AUTHORING_RECEIPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY03/attempt_01/authoring_receipt.json"
AUTHORING_RECEIPT_AUTHORITY = (63288, "30b2a0a90cf88811990a27aeb49c5e554093bbe65f6089d106650e351db58c2f")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01/attempt_01"
RECEIPT = ATTEMPT / "postflight_receipt.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def asset_identity(value: object) -> str:
    return "" if value is None else str(value.get_path_name())


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


result: dict[str, object] = {
    "schema": "skyguard.m01-visible-environment-stage04-recovery03.postflight01.v1",
    "classification": "FAILED_WITH_EVIDENCE", "read_only": True, "world_saved": False,
    "map_before": None, "map_after": None, "input_before": None, "input_after": None,
    "actor_count": None, "hidden_legacy_count": 0, "facade_actor_count": 0,
    "lighthouse_actor_count": 0, "vegetation_count": 0,
    "material_contract": [], "created_actor_bounds": [], "lighting": {}, "errors": [],
}

try:
    require(MAP_FILE.is_file() and MAP_FILE.stat().st_size == MAP_AUTHORITY[0] and sha256(MAP_FILE) == MAP_AUTHORITY[1], "Saved Recovery03 map authority changed")
    require(INPUT_FILE.is_file() and INPUT_FILE.stat().st_size == INPUT_AUTHORITY[0] and sha256(INPUT_FILE) == INPUT_AUTHORITY[1], "Immutable Stage03 map authority changed")
    require(AUTHORING_RECEIPT.is_file() and AUTHORING_RECEIPT.stat().st_size == AUTHORING_RECEIPT_AUTHORITY[0] and sha256(AUTHORING_RECEIPT) == AUTHORING_RECEIPT_AUTHORITY[1], "Authoring receipt authority changed")
    authoring = json.loads(AUTHORING_RECEIPT.read_text(encoding="utf-8"))
    require(authoring.get("classification") == "PASSED_STAGE04_RECOVERY03_AUTHORING_AWAITING_GOVERNED_D3D12_VISUAL_PROOF", "Authoring receipt did not pass")
    require(authoring.get("actor_count_after") == 230, "Authoring receipt actor count changed")
    require(len(authoring.get("material_slot_cleanup", [])) == 2, "Exact material cleanup receipt changed")
    result["map_before"], result["input_before"] = record(MAP_FILE), record(INPUT_FILE)

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
    require(bool(levels.load_level(MAP_ASSET)), "Saved Recovery03 map failed to load")
    actors = list(actors_api.get_all_level_actors())
    result["actor_count"] = len(actors)
    require(len(actors) == 230, f"Saved Recovery03 actor count changed: {len(actors)}")
    by_label = {actor.get_actor_label(): actor for actor in actors}

    legacy = [actor for actor in actors if actor.get_actor_label().startswith(("M01_HSSC01R01_Window_", "M01_HSSC03_RearWindow_"))]
    legacy += [by_label[label] for label in (
        "M01_STAGE03_Lighthouse_Hero_DETAILS", "M01_STAGE03_Lighthouse_Hero_GLAZING", "M01_STAGE03_Lighthouse_Hero_STRUCTURAL"
    )]
    require(len(legacy) == 75, f"Legacy hidden-set count changed: {len(legacy)}")
    for actor in legacy:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        require(component is not None, f"Legacy component missing: {actor.get_actor_label()}")
        require(not bool(component.get_editor_property("visible")) and bool(component.get_editor_property("hidden_in_game")), f"Legacy actor visible: {actor.get_actor_label()}")
    result["hidden_legacy_count"] = len(legacy)

    facades = [actor for actor in actors if actor.get_actor_label().startswith("M01_STAGE04R03_Facade_")]
    lighthouses = [actor for actor in actors if actor.get_actor_label().startswith("M01_STAGE04R03_LighthouseHero_")]
    require(len(facades) == 32 and len(lighthouses) == 3, f"Created actor groups changed: facade={len(facades)} lighthouse={len(lighthouses)}")
    result["facade_actor_count"], result["lighthouse_actor_count"] = len(facades), len(lighthouses)
    for actor in sorted(facades + lighthouses, key=lambda row: row.get_actor_label()):
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        require(component is not None and component.get_editor_property("static_mesh") is not None, f"Created actor mesh missing: {actor.get_actor_label()}")
        origin, extent = actor.get_actor_bounds(False)
        require(float(extent.x) > 0 and float(extent.y) > 0 and float(extent.z) > 0, f"Degenerate created actor: {actor.get_actor_label()}")
        result["created_actor_bounds"].append({"label": actor.get_actor_label(), "origin_cm": vector(origin), "extent_cm": vector(extent), "mesh": asset_identity(component.get_editor_property("static_mesh"))})
    tower = by_label["M01_STAGE04R03_LighthouseHero_Lighthouse_Tower_A"]
    tower_origin, tower_extent = tower.get_actor_bounds(False)
    require(abs(float(tower_origin.z - tower_extent.z) - 66.5229151920468) <= 1.0, "Lighthouse ground contact changed")

    mesh_contract = {
        "SM_M01_CoastalFacadeBay_A_BalconyDetails": 3,
        "SM_M01_CoastalFacadeBay_A_Glass": 1,
        "SM_M01_CoastalFacadeBay_A_Interior": 9,
        "SM_M01_CoastalFacadeBay_A_StructureFrame": 8,
        "SM_M01_Lighthouse_Details_A": 7,
        "SM_M01_Lighthouse_Lantern_A": 7,
        "SM_M01_Lighthouse_Tower_A": 3,
    }
    seen: dict[str, object] = {}
    for actor in facades + lighthouses:
        mesh = actor.get_component_by_class(unreal.StaticMeshComponent).get_editor_property("static_mesh")
        seen[mesh.get_name()] = mesh
    require(set(seen) == set(mesh_contract), f"Created mesh identities changed: {sorted(seen)}")
    for name, expected_slots in mesh_contract.items():
        mesh = seen[name]
        slots = list(mesh.get_editor_property("static_materials"))
        names = [slot.get_editor_property("material_interface").get_name() if slot.get_editor_property("material_interface") else "" for slot in slots]
        require(len(slots) == expected_slots, f"Material slot count changed: {name}: {len(slots)}")
        require("M_REVIEW_M01_CoastalFacadeBay_R02_Collision" not in names, f"Collision-only material survived: {name}")
        result["material_contract"].append({"mesh": name, "slot_count": len(slots), "materials": names})

    vegetation = [actor for actor in actors if actor.get_actor_label().startswith("M01_PHV02_")]
    require(len(vegetation) == 28, f"Vegetation count changed: {len(vegetation)}")
    for actor in vegetation:
        origin, extent = actor.get_actor_bounds(False)
        require(float(origin.z - extent.z) > -200.0, f"Vegetation is substantially below terrain: {actor.get_actor_label()}")
    result["vegetation_count"] = len(vegetation)

    sun = by_label["M01_RS01_Sun"].get_component_by_class(unreal.DirectionalLightComponent)
    fill = by_label["M01_PR01_FillSun"].get_component_by_class(unreal.DirectionalLightComponent)
    sky = by_label["M01_RS01_SkyLight"].get_component_by_class(unreal.SkyLightComponent)
    require(sun is not None and fill is not None and sky is not None, "Lighting components missing")
    result["lighting"] = {"sun": float(sun.get_editor_property("intensity")), "fill": float(fill.get_editor_property("intensity")), "sky": float(sky.get_editor_property("intensity"))}
    require(abs(result["lighting"]["sun"] - 5.0) < 0.01 and abs(result["lighting"]["fill"] - 7.5) < 0.01 and abs(result["lighting"]["sky"] - 9.0) < 0.01, f"Lighting contract changed: {result['lighting']}")

    result["map_after"], result["input_after"] = record(MAP_FILE), record(INPUT_FILE)
    require(result["map_after"] == result["map_before"], "Read-only postflight changed Recovery03 map")
    require(result["input_after"] == result["input_before"], "Read-only postflight changed Stage03 map")
    result["classification"] = "PASSED_STAGE04_RECOVERY03_SAVED_MAP_READY_FOR_GOVERNED_D3D12_VISUAL_PROOF"
except Exception as exc:
    result["errors"].append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
finally:
    if result["map_after"] is None and MAP_FILE.is_file():
        result["map_after"] = record(MAP_FILE)
    if result["input_after"] is None and INPUT_FILE.is_file():
        result["input_after"] = record(INPUT_FILE)
    write_json_atomic(RECEIPT, result)

print("SKYGUARD_STAGE04_RECOVERY03_POSTFLIGHT=" + str(result["classification"]))
if not str(result["classification"]).startswith("PASSED_"):
    raise RuntimeError(result["errors"][-1]["message"] if result["errors"] else "Recovery03 postflight failed")
