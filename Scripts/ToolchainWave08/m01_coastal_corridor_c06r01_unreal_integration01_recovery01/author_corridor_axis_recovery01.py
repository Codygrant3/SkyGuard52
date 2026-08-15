"""Clone the accepted corridor integration map and correct its imported Y handedness."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap"
INPUT_BYTES = 705_359
INPUT_SHA256 = "1e8164704968153e59c69f463ce1b76d03c9deafb32c8d6b239574b1406ae5db"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01/attempt_01"
RECEIPT = ATTEMPT / "axis_correction_receipt.json"
EXPECTED_ACTOR_COUNT = 100
EXPECTED = {
    "M01_C06R01_Corridor_TERRAIN": {
        "before_origin_y": -11486.601318359375,
        "after_origin_y": 11486.601318359375,
        "extent_y": 8013.398681640625,
    },
    "M01_C06R01_Corridor_HARDSCAPE": {
        "before_origin_y": -13060.8935546875,
        "after_origin_y": 13060.8935546875,
        "extent_y": 6439.1064453125,
    },
    "M01_C06R01_Corridor_DETAILS": {
        "before_origin_y": -9347.952392578125,
        "after_origin_y": 9347.952392578125,
        "extent_y": 2368.047607421875,
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def close(left: float, right: float, tolerance: float = 2.0) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def validate_authorities() -> None:
    require(PROJECT.is_file(), "Isolated project is missing")
    require(PROJECT.stat().st_size == PROJECT_BYTES, "Isolated project byte count changed")
    require(sha256(PROJECT) == PROJECT_SHA256, "Isolated project hash changed")
    require(INPUT_FILE.is_file(), "Accepted corridor integration map is missing")
    require(INPUT_FILE.stat().st_size == INPUT_BYTES, "Accepted corridor integration map byte count changed")
    require(sha256(INPUT_FILE) == INPUT_SHA256, "Accepted corridor integration map hash changed")


def run_offline_contract_test() -> int:
    validate_authorities()
    require(not OUTPUT_FILE.exists(), "Fresh Recovery01 output map already exists")
    require(not ATTEMPT.exists(), "Fresh Recovery01 attempt namespace already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-coastal-corridor-c06r01.axis-recovery01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "input_asset": INPUT_ASSET,
        "output_asset": OUTPUT_ASSET,
        "input_sha256_before": None,
        "input_sha256_after": None,
        "output_map": None,
        "actor_count": None,
        "transformed_actors": [],
        "unchanged_non_corridor_actor_count": None,
        "rollback_manifest": {
            "created_map": OUTPUT_ASSET,
            "accepted_input_mutated": False,
            "imported_assets_mutated": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        validate_authorities()
        result["input_sha256_before"] = sha256(INPUT_FILE)
        require(not OUTPUT_FILE.exists(), "Fresh Recovery01 output map exists on disk")
        require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Recovery01 output asset exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems are unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone corridor integration map")

        actors = list(actors_api.get_all_level_actors())
        result["actor_count"] = len(actors)
        require(len(actors) == EXPECTED_ACTOR_COUNT, f"Accepted actor count changed: {len(actors)}")
        by_label: dict[str, list[object]] = {}
        for actor in actors:
            by_label.setdefault(actor.get_actor_label(), []).append(actor)
        for label in EXPECTED:
            require(len(by_label.get(label, [])) == 1, f"Expected exactly one governed corridor actor: {label}")

        transformed = []
        for label, bounds_contract in EXPECTED.items():
            actor = by_label[label][0]
            location_before = actor.get_actor_location()
            rotation_before = actor.get_actor_rotation()
            scale_before = actor.get_actor_scale3d()
            origin_before, extent_before = actor.get_actor_bounds(False)
            require(close(location_before.x, 0.0, 0.01) and close(location_before.y, 0.0, 0.01) and close(location_before.z, 0.0, 0.01), f"Unexpected actor location: {label}")
            require(close(scale_before.x, 1.0, 0.001) and close(scale_before.y, 1.0, 0.001) and close(scale_before.z, 1.0, 0.001), f"Unexpected input scale: {label}")
            require(close(origin_before.y, bounds_contract["before_origin_y"]), f"Unexpected input Y bounds origin: {label} -> {origin_before.y}")
            require(close(extent_before.y, bounds_contract["extent_y"]), f"Unexpected input Y bounds extent: {label} -> {extent_before.y}")

            actor.set_actor_scale3d(unreal.Vector(1.0, -1.0, 1.0))
            location_after = actor.get_actor_location()
            rotation_after = actor.get_actor_rotation()
            scale_after = actor.get_actor_scale3d()
            origin_after, extent_after = actor.get_actor_bounds(False)
            require(close(scale_after.x, 1.0, 0.001) and close(scale_after.y, -1.0, 0.001) and close(scale_after.z, 1.0, 0.001), f"Y mirror failed: {label}")
            require(close(origin_after.y, bounds_contract["after_origin_y"]), f"Corrected Y bounds origin failed: {label} -> {origin_after.y}")
            require(close(extent_after.y, extent_before.y), f"Y bounds extent changed: {label}")
            require(close(origin_after.x, origin_before.x) and close(origin_after.z, origin_before.z), f"Non-Y bounds origin changed: {label}")
            require(close(extent_after.x, extent_before.x) and close(extent_after.z, extent_before.z), f"Non-Y bounds extent changed: {label}")
            require(close(location_after.x, location_before.x, 0.01) and close(location_after.y, location_before.y, 0.01) and close(location_after.z, location_before.z, 0.01), f"Actor location changed: {label}")
            require(close(rotation_after.roll, rotation_before.roll, 0.01) and close(rotation_after.pitch, rotation_before.pitch, 0.01) and close(rotation_after.yaw, rotation_before.yaw, 0.01), f"Actor rotation changed: {label}")
            transformed.append({
                "label": label,
                "location_before_cm": vector(location_before),
                "location_after_cm": vector(location_after),
                "rotation_before_deg": [float(rotation_before.roll), float(rotation_before.pitch), float(rotation_before.yaw)],
                "rotation_after_deg": [float(rotation_after.roll), float(rotation_after.pitch), float(rotation_after.yaw)],
                "scale_before": vector(scale_before),
                "scale_after": vector(scale_after),
                "bounds_origin_before_cm": vector(origin_before),
                "bounds_origin_after_cm": vector(origin_after),
                "bounds_extent_before_cm": vector(extent_before),
                "bounds_extent_after_cm": vector(extent_after),
            })

        terrain = next(row for row in transformed if row["label"].endswith("TERRAIN"))
        terrain_min_y = terrain["bounds_origin_after_cm"][1] - terrain["bounds_extent_after_cm"][1]
        terrain_max_y = terrain["bounds_origin_after_cm"][1] + terrain["bounds_extent_after_cm"][1]
        require(3000.0 <= terrain_min_y <= 4000.0, f"Corrected terrain shoreline bound is unexpected: {terrain_min_y}")
        require(19400.0 <= terrain_max_y <= 19600.0, f"Corrected terrain city-side bound is unexpected: {terrain_max_y}")
        result["transformed_actors"] = transformed
        result["unchanged_non_corridor_actor_count"] = len(actors) - len(transformed)
        require(result["unchanged_non_corridor_actor_count"] == 97, "Non-corridor actor count changed")

        require(levels.save_current_level(), "Failed to save fresh Recovery01 map")
        require(OUTPUT_FILE.is_file(), "Fresh Recovery01 map file was not created")
        result["input_sha256_after"] = sha256(INPUT_FILE)
        require(result["input_sha256_after"] == INPUT_SHA256, "Accepted corridor integration map changed")
        result["output_map"] = record(OUTPUT_FILE)
        result["classification"] = "PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Corridor axis Recovery01 failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
