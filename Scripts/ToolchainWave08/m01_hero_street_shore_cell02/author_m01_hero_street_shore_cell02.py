"""Author a fresh Mission 1 Hero Street/Shore Cell02 map.

Cell02 keeps the accepted Cell01 composition, replaces its blank inland parcels
with the accepted textured CoastalA district, retains the accepted MidriseB
triplet and its separately authored window actors in alignment, regrounds
promenade props to the accepted district hardscape, and applies only bounded
presentation corrections in the derived map.
"""

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
INPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell01_Recovery01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell01_Recovery01.umap"
INPUT_BYTES = 746_684
INPUT_SHA256 = "449c4d1153da7a149375f8b288c0908401ffe1db21104f83088039ed9b3656f2"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell02"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell02.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL02/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

ADJUDICATION = ROOT / "Saved/Reports/M01_HERO_STREET_SHORE_CELL02_COMPOSITION_OFFLINE_ADJUDICATION01.json"
ADJUDICATION_BYTES = 3_552
ADJUDICATION_SHA256 = "9cda4c4f101e31441048c567c5f94121e6caae04f94d7d6cf28684aa7bc12981"
CELL01_FREEZE = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json"
CELL01_FREEZE_BYTES = 5_278
CELL01_FREEZE_SHA256 = "c1c13e4a30366ff5fde357ec969b8418928e7a53d62ee098a0b6673c0ca65094"
IMPORT_RECEIPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01/attempt_01/full_kit_import_receipt.json"
IMPORT_RECEIPT_BYTES = 58_338
IMPORT_RECEIPT_SHA256 = "04895051591b7df6dfa39f87d1afa9f6bb72944c3cdde80e950d7cdcd35cad63"

DISTRICT_ASSETS = {
    "HARDSCAPE": "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_HARDSCAPE.SM_M01_CoastalA_HARDSCAPE",
    "TERRAIN": "/Game/M01/EnvKit02/M01_COASTAL_DISTRICT_A/StaticMeshes/SM_M01_CoastalA_TERRAIN.SM_M01_CoastalA_TERRAIN",
}
DISTRICT_SLOTS = {"HARDSCAPE": 6, "TERRAIN": 1}
DISTRICT_LOCATION_CM = (5_500.0, 13_500.0, -29.0)
EXPECTED_ACTORS_BEFORE = 120
EXPECTED_ACTORS_AFTER = 122

MIDRISE_LABELS = tuple(
    f"M01_ACA03R01_City_R00_C02_MidriseB_{group}"
    for group in ("STRUCTURAL", "GLAZING", "DETAILS")
)

PROP_PREFIXES = (
    "M01_HSSC01R01_Prop_",
    "M01_Promenade_Bollard_",
    "M01_Promenade_BicycleRack_",
    "M01_Promenade_LitterBin_",
    "M01_Promenade_UtilityCabinet_",
)
TARGET_SKYLIGHT_INTENSITY = 4.5
TARGET_EXPOSURE_BIAS = 0.75
TARGET_FILM_TOE = 0.62


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


def require_file(path: Path, size: int, digest: str) -> dict[str, object]:
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == size, f"Authority byte count changed: {path}")
    require(sha256(path) == digest, f"Authority hash changed: {path}")
    return record(path)


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def vector(value: object) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def actor_state(actor: object) -> dict[str, object]:
    rotation = actor.get_actor_rotation()
    return {
        "location_cm": vector(actor.get_actor_location()),
        "rotation_deg": [float(rotation.roll), float(rotation.pitch), float(rotation.yaw)],
        "scale": vector(actor.get_actor_scale3d()),
    }


def verify_authorities() -> list[dict[str, object]]:
    return [
        require_file(PROJECT, PROJECT_BYTES, PROJECT_SHA256),
        require_file(INPUT_FILE, INPUT_BYTES, INPUT_SHA256),
        require_file(ADJUDICATION, ADJUDICATION_BYTES, ADJUDICATION_SHA256),
        require_file(CELL01_FREEZE, CELL01_FREEZE_BYTES, CELL01_FREEZE_SHA256),
        require_file(IMPORT_RECEIPT, IMPORT_RECEIPT_BYTES, IMPORT_RECEIPT_SHA256),
    ]


def run_offline_contract_test() -> int:
    verify_authorities()
    require(not OUTPUT_FILE.exists(), "Fresh Cell02 output map already exists")
    require(not ATTEMPT.exists(), "Fresh Cell02 authoring attempt already exists")
    require(len(MIDRISE_LABELS) == 3, "Midrise triplet contract changed")
    require(set(DISTRICT_ASSETS) == {"HARDSCAPE", "TERRAIN"}, "District groups changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_HERO_STREET_SHORE_CELL02_AUTHORING_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-hero-street-shore-cell02.authoring.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "runtime_promotion": False,
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "district_actors": [],
        "retained_midrise_triplet": [],
        "regrounded_props": [],
        "lighting": None,
        "rollback_manifest": {
            "created_map": OUTPUT_ASSET,
            "accepted_input_mutated": False,
            "accepted_asset_packages_mutated": False,
            "runtime_promotion": False,
        },
        "deferred": [
            "production_vegetation",
            "accepted_vehicles",
            "accepted_signage",
            "lighthouse_refinement",
            "water_surface_and_shore_contact_d3d12_review",
        ],
        "error": None,
        "traceback": None,
    }

    try:
        result["authorities"] = verify_authorities()
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists(), "Fresh Cell02 output package exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh Cell02 asset exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone accepted Cell01 map")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == EXPECTED_ACTORS_BEFORE, f"Cell01 actor count changed: {len(actors)}")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate actor labels in Cell01 map")

        district_meshes: dict[str, object] = {}
        for group, path in DISTRICT_ASSETS.items():
            mesh = unreal.load_asset(path)
            require(mesh is not None and isinstance(mesh, unreal.StaticMesh), f"District asset failed to load: {group}")
            require(len(list(mesh.get_editor_property("static_materials"))) == DISTRICT_SLOTS[group], f"District material slots changed: {group}")
            district_meshes[group] = mesh

        for group in ("TERRAIN", "HARDSCAPE"):
            actor = actors_api.spawn_actor_from_class(
                unreal.StaticMeshActor,
                unreal.Vector(*DISTRICT_LOCATION_CM),
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
                False,
            )
            require(actor is not None, f"Failed to spawn CoastalA {group}")
            actor.set_actor_label(f"M01_HSSC02_CoastalA_{group}")
            actor.set_folder_path("M01/HeroStreetShoreCell02/CoastalDistrict")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"StaticMeshComponent missing: {group}")
            component.set_static_mesh(district_meshes[group])
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("BlockAll")
            origin, extent = actor.get_actor_bounds(False)
            result["district_actors"].append({
                "group": group,
                "asset": DISTRICT_ASSETS[group],
                "transform": actor_state(actor),
                "bounds_origin_cm": vector(origin),
                "bounds_extent_cm": vector(extent),
                "bounds_min_z_cm": float(origin.z - extent.z),
            })

        # Retain the accepted building triplet exactly where Cell01 placed it.
        # Its facade windows are independent actors, so moving only the triplet
        # would break the accepted assembled facade. The added district terrain
        # is the intended grounding surface beneath this building.
        for label in MIDRISE_LABELS:
            actor = by_label.get(label)
            require(actor is not None, f"Accepted Midrise actor missing: {label}")
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None and component.get_editor_property("static_mesh") is not None,
                    f"Accepted Midrise mesh missing: {label}")
            state = actor_state(actor)
            origin, extent = actor.get_actor_bounds(False)
            result["retained_midrise_triplet"].append({
                "label": label,
                "state_before": state,
                "bounds_origin_cm": vector(origin),
                "bounds_extent_cm": vector(extent),
                "bounds_min_z_cm": float(origin.z - extent.z),
            })

        # Ground retained promenade props onto the new hardscape datum while
        # preserving X/Y, rotation, scale, mesh and material assignments.
        for actor in actors_api.get_all_level_actors():
            label = actor.get_actor_label()
            if not label.startswith(PROP_PREFIXES):
                continue
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if component is None or component.get_editor_property("static_mesh") is None:
                continue
            location = actor.get_actor_location()
            if not (5_500.0 <= float(location.x) <= 19_500.0 and 7_805.0 <= float(location.y) <= 9_935.0):
                continue
            origin_before, extent_before = actor.get_actor_bounds(False)
            bottom_before = float(origin_before.z - extent_before.z)
            target_bottom = 71.0
            actor.set_actor_location(
                unreal.Vector(location.x, location.y, location.z + target_bottom - bottom_before),
                False,
                True,
            )
            origin_after, extent_after = actor.get_actor_bounds(False)
            bottom_after = float(origin_after.z - extent_after.z)
            require(abs(bottom_after - target_bottom) <= 1.0, f"Prop grounding failed: {label}")
            result["regrounded_props"].append({
                "label": label,
                "bottom_before_cm": bottom_before,
                "bottom_after_cm": bottom_after,
                "target_bottom_cm": target_bottom,
                "bounds_extent_cm": vector(extent_after),
            })

        require(len(result["regrounded_props"]) >= 10, "Too few intersecting props were regrounded")

        # Keep the accepted lifted glazing overrides inherited from Cell01 and
        # apply a conservative presentation lift in this derived map only.
        sky = by_label.get("M01_RS01_SkyLight")
        post = by_label.get("M01_RS01_PostProcess")
        require(sky is not None and post is not None, "Accepted lighting actors missing")
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        require(sky_component is not None, "SkyLightComponent missing")
        before_sky = float(sky_component.get_editor_property("intensity"))
        sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
        sky_component.set_editor_property("real_time_capture", True)
        sky_component.set_editor_property("lower_hemisphere_is_black", False)
        settings = post.get_editor_property("settings")
        before_bias = float(settings.get_editor_property("auto_exposure_bias"))
        before_toe = float(settings.get_editor_property("film_toe"))
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", TARGET_EXPOSURE_BIAS)
        settings.set_editor_property("override_film_toe", True)
        settings.set_editor_property("film_toe", TARGET_FILM_TOE)
        post.set_editor_property("settings", settings)
        result["lighting"] = {
            "skylight_intensity_before": before_sky,
            "skylight_intensity_after": float(sky_component.get_editor_property("intensity")),
            "exposure_bias_before": before_bias,
            "exposure_bias_after": float(settings.get_editor_property("auto_exposure_bias")),
            "film_toe_before": before_toe,
            "film_toe_after": float(settings.get_editor_property("film_toe")),
        }

        final_actors = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(final_actors)
        require(len(final_actors) == EXPECTED_ACTORS_AFTER, f"Cell02 actor count changed: {len(final_actors)}")
        require(sum(a.get_actor_label().startswith("M01_HSSC02_CoastalA_") for a in final_actors) == 2, "District actor count changed")
        require(len(result["retained_midrise_triplet"]) == 3, "Midrise triplet retention count changed")
        final_by_label = {actor.get_actor_label(): actor for actor in final_actors}
        for retained in result["retained_midrise_triplet"]:
            label = retained["label"]
            require(actor_state(final_by_label[label]) == retained["state_before"],
                    f"Accepted Midrise transform changed: {label}")
        require(levels.save_current_level(), "Failed to save Cell02 map")
        require(OUTPUT_FILE.is_file(), "Cell02 output map missing")
        result["output_map"] = record(OUTPUT_FILE)
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted Cell01 map changed")
        result["classification"] = "PASSED_M01_HERO_STREET_SHORE_CELL02_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        if result["input_map_after"] is None and INPUT_FILE.is_file():
            result["input_map_after"] = record(INPUT_FILE)
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Cell02 authoring failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
