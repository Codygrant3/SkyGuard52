"""Author one reversible Mission 1 hero street-and-shore cell.

This gate derives a fresh map from the structurally accepted Assembly03
Recovery01 map. It uses only accepted local Unreal assets. It does not import,
promote, or mutate accepted source packages.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_AcceptedCandidateAssembly03_Recovery01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_AcceptedCandidateAssembly03_Recovery01.umap"
INPUT_BYTES = 751_687
INPUT_SHA256 = "73097ef783735e2c3dd72b1ea17f9e0240b98d7e5e30d0df4d54bb2468550aba"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_HeroStreetShoreCell01"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01/attempt_01"
RECEIPT = ATTEMPT / "authoring_receipt.json"

SOURCE_DISCOVERY = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL01_SOURCE_DISCOVERY.json"
SOURCE_DISCOVERY_BYTES = 9_252
SOURCE_DISCOVERY_SHA256 = "41149f23430fca49d6f5fa8e0c3ccdc36e4de9e07446b14bf3c711950d648a4d"
DESIGN_FREEZE = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL01_OFFLINE_PRODUCTION_DESIGN_FREEZE.json"
DESIGN_FREEZE_BYTES = 4_418
DESIGN_FREEZE_SHA256 = "c7602ec2c333d24826c42867dbf994b5c61ed52e301c7b0def6b22d16fa691c6"
WINDOW_IMPORT_FREEZE = ROOT / "Docs/AAA_Review/M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_ACCEPTANCE_FREEZE.json"
WINDOW_IMPORT_FREEZE_BYTES = 2_226
WINDOW_IMPORT_FREEZE_SHA256 = "362579881b7df83bf32ce48a50e104f51149c08e3a1949b1894fad57a413b58c"

WINDOW_ASSETS = {
    "FRAME": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.SM_M01_PrewarWindowBay_A01_FrameFacadeHardware",
    "GLASS": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass.SM_M01_PrewarWindowBay_A01_Glass",
    "INTERIOR": "/Game/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior.SM_M01_PrewarWindowBay_A01_Interior",
}
WINDOW_SLOTS = {"FRAME": 5, "GLASS": 1, "INTERIOR": 9}
WINDOW_FILES = {
    "FRAME": (ISOLATED / "Content/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.uasset", 494_317, "239cda422cd0165aba9c1781be31ca4b7abc8c608aa7792375ad8602177eb280"),
    "GLASS": (ISOLATED / "Content/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Glass.uasset", 52_319, "f3172f306242ef95a8d4a35c976ec70b2a018bf5e919e433acc21d8a10fbf535"),
    "INTERIOR": (ISOLATED / "Content/T08/GW02/StaticMeshes/SM_M01_PrewarWindowBay_A01_Interior.uasset", 262_688, "3841b74d078bd4c3d7d9a738fc276993e12d3b4d8cee209741f7c1e3dae6729a"),
}

EXPECTED_ACTORS_BEFORE = 119
EXPECTED_BUILDING_TRIPLET_PREFIX = "M01_ACA03R01_City_"
CELL_PREFIX = "M01_HSSC01_"
CELL_CENTER_X_CM = 12_500.0
CELL_X_RANGE_CM = (7_000.0, 18_000.0)
CELL_Y_RANGE_CM = (-2_500.0, 18_500.0)

KEEP_BUILDING_PLACEMENTS = (
    "M01_ACA03R01_City_R00_C02_MidriseB",
    "M01_ACA03R01_City_R01_C01_ApartmentA",
    "M01_ACA03R01_City_R01_C02_CornerC",
)

# Twelve architecturally coherent, real-depth window modules on the inland
# facade of the accepted MidriseB. The existing structural wall provides the
# building envelope; each triplet supplies reveal, glazing and 2.5 m interior.
# The retained MidriseB structural envelope is approximately X=10,141..13,259
# cm. Keep every 3.6 m bay origin inside that measured envelope.
WINDOW_COLUMNS_CM = (10_600.0, 11_020.0, 11_440.0)
WINDOW_FLOOR_ORIGINS_CM = (760.0, 1_210.0, 1_660.0, 2_110.0)
WINDOW_FACADE_Y_CM = 11_010.0
WINDOW_YAW_DEGREES = 2.0

EXPECTED_PROP_COUNTS = {
    "M01_Promenade_Bollard_": 13,
    "M01_Promenade_BicycleRack_": 8,
    "M01_Promenade_LitterBin_": 10,
    "M01_Promenade_StormDrain_": 12,
    "M01_Promenade_UtilityCabinet_": 5,
}
EXPECTED_ACTORS_AFTER = 120

# Additional copies remain intentionally bounded. Raw imported axis rotations
# are derived from accepted sibling actors at runtime, never guessed here.
PROP_COPIES = (
    ("Bollard", "M01_Promenade_Bollard_02", 8_150.0, 8_280.0, 0.98, 31.0),
    ("Bollard", "M01_Promenade_Bollard_03", 9_700.0, 8_345.0, 1.01, 53.0),
    ("Bollard", "M01_Promenade_Bollard_04", 13_100.0, 8_245.0, 0.97, 71.0),
    ("Bollard", "M01_Promenade_Bollard_02", 14_900.0, 8_315.0, 1.02, 89.0),
    ("BicycleRack", "M01_Promenade_BicycleRack_02", 8_800.0, 7_980.0, 0.99, -3.0),
    ("BicycleRack", "M01_Promenade_BicycleRack_02", 16_250.0, 8_070.0, 1.01, 4.0),
    ("LitterBin", "M01_Promenade_LitterBin_02", 10_250.0, 8_060.0, 0.98, -12.0),
    ("LitterBin", "M01_Promenade_LitterBin_03", 15_250.0, 8_015.0, 1.02, 18.0),
    ("StormDrain", "M01_Promenade_StormDrain_02", 11_200.0, 7_350.0, 1.0, 0.0),
    ("StormDrain", "M01_Promenade_StormDrain_03", 16_500.0, 7_365.0, 1.0, 0.0),
    ("UtilityCabinet", "M01_Promenade_UtilityCabinet_01", 15_600.0, 9_560.0, 0.97, 8.0),
)

TARGET_SKYLIGHT_INTENSITY = 11.0
TARGET_EXPOSURE_BIAS = 1.35
TARGET_FILM_TOE = 0.68


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
    require(path.is_file(), f"Authority is missing: {path}")
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


def rotation(value: object) -> list[float]:
    return [float(value.pitch), float(value.yaw), float(value.roll)]


def transform_state(actor: object) -> dict[str, object]:
    return {
        "location_cm": vector(actor.get_actor_location()),
        "rotation_degrees": rotation(actor.get_actor_rotation()),
        "scale": vector(actor.get_actor_scale3d()),
    }


def promenade_surface_z_cm(x_cm: float, y_cm: float) -> float:
    x = x_cm / 100.0
    y = y_cm / 100.0
    long_wave = 0.045 * math.sin(x / 72.0) + 0.025 * math.sin(x / 19.0 + 0.7)
    shore = 38.0 + 2.45 * math.sin(x / 47.0) + 0.82 * math.sin(x / 13.0 + 0.4)
    boundaries = [
        (18.0, -1.25),
        (shore, -0.54 + long_wave),
        (shore + 10.0 + 0.65 * math.sin(x / 23.0), -0.10 + long_wave),
        (shore + 29.0 + 1.35 * math.sin(x / 39.0 + 0.8), 0.42 + long_wave),
        (78.0 + 0.62 * math.sin(x / 61.0), 0.70 + long_wave * 0.35),
        (86.0, 0.72 + long_wave * 0.20),
        (100.0, 0.56 + long_wave * 0.15),
        (104.0, 0.72 + long_wave * 0.15),
    ]
    if y >= 104.0:
        return (0.76 + 0.025 * math.sin(x / 31.0)) * 100.0
    for (left_y, left_z), (right_y, right_z) in zip(boundaries, boundaries[1:]):
        if left_y <= y <= right_y:
            alpha = (y - left_y) / max(0.0001, right_y - left_y)
            return (left_z + (right_z - left_z) * alpha) * 100.0
    return boundaries[0][1] * 100.0


def verify_authorities() -> list[dict[str, object]]:
    rows = [
        require_file(PROJECT, PROJECT_BYTES, PROJECT_SHA256),
        require_file(INPUT_FILE, INPUT_BYTES, INPUT_SHA256),
        require_file(SOURCE_DISCOVERY, SOURCE_DISCOVERY_BYTES, SOURCE_DISCOVERY_SHA256),
        require_file(DESIGN_FREEZE, DESIGN_FREEZE_BYTES, DESIGN_FREEZE_SHA256),
        require_file(WINDOW_IMPORT_FREEZE, WINDOW_IMPORT_FREEZE_BYTES, WINDOW_IMPORT_FREEZE_SHA256),
    ]
    for path, size, digest in WINDOW_FILES.values():
        rows.append(require_file(path, size, digest))
    return rows


def run_offline_contract_test() -> int:
    verify_authorities()
    require(len(KEEP_BUILDING_PLACEMENTS) == 3, "Hero-cell building count changed")
    require(len(WINDOW_COLUMNS_CM) * len(WINDOW_FLOOR_ORIGINS_CM) == 12, "Window-bay count changed")
    require(len(PROP_COPIES) == 11, "Bounded prop-copy count changed")
    require(not OUTPUT_FILE.exists(), "Fresh hero-cell map already exists")
    require(not ATTEMPT.exists(), "Fresh hero-cell attempt already exists")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print("PASS_M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT")
    return 0


def run_unreal() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-hero-street-shore-cell01.authoring.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "runtime_promotion": False,
        "authorities": [],
        "input_map_before": None,
        "input_map_after": None,
        "output_map": None,
        "actor_count_before": None,
        "actor_count_after": None,
        "removed_city_triplets": [],
        "retained_building_triplets": [],
        "window_modules": [],
        "prop_copies": [],
        "lighting": None,
        "deferred": [
            "production_vegetation",
            "accepted_vehicles",
            "accepted_signage",
            "streetlight_bench_railing_candidates",
            "lighthouse_refinement",
            "water_waves_native_api_probe",
            "full_route_propagation",
        ],
        "rollback_manifest": {
            "created_map": OUTPUT_ASSET,
            "accepted_input_mutated": False,
            "accepted_asset_packages_mutated": False,
            "runtime_promotion": False,
        },
        "error": None,
        "traceback": None,
    }

    try:
        result["authorities"] = verify_authorities()
        result["input_map_before"] = record(INPUT_FILE)
        require(not OUTPUT_FILE.exists(), "Fresh hero-cell output package exists")
        require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Fresh hero-cell asset exists")

        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        require(levels is not None and actors_api is not None, "Required editor subsystems unavailable")
        require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to clone Assembly03 Recovery01")
        actors = list(actors_api.get_all_level_actors())
        result["actor_count_before"] = len(actors)
        require(len(actors) == EXPECTED_ACTORS_BEFORE, f"Assembly03 actor count changed: {len(actors)}")
        by_label = {actor.get_actor_label(): actor for actor in actors}
        require(len(by_label) == len(actors), "Duplicate actor labels in source map")

        # Keep exactly one accepted ApartmentA, MidriseB and CornerC triplet in
        # the proof cell. The full source map remains unchanged on disk.
        city_labels = [label for label in by_label if label.startswith(EXPECTED_BUILDING_TRIPLET_PREFIX)]
        require(len(city_labels) == 54, f"Accepted city actor count changed: {len(city_labels)}")
        keep_labels = {
            f"{placement}_{group}"
            for placement in KEEP_BUILDING_PLACEMENTS
            for group in ("STRUCTURAL", "GLAZING", "DETAILS")
        }
        require(keep_labels.issubset(by_label), "One or more accepted cell triplet actors are missing")
        removals = [by_label[label] for label in city_labels if label not in keep_labels]
        require(len(removals) == 45, f"Expected 45 out-of-cell building actors; found {len(removals)}")
        for actor in removals:
            label = actor.get_actor_label()
            require(actors_api.destroy_actor(actor), f"Failed to remove out-of-cell actor: {label}")
            result["removed_city_triplets"].append(label)
        result["retained_building_triplets"] = list(KEEP_BUILDING_PLACEMENTS)

        # The legacy radar is neither a passed hero nor part of this cell.
        radar = by_label.get("M01_RS01_Radar_Hero")
        require(radar is not None, "Expected inherited radar actor is missing")
        require(actors_api.destroy_actor(radar), "Failed to remove nonaccepted radar from derived cell")

        # Load the accepted window-bay triplet and preserve its slot contract.
        window_meshes: dict[str, object] = {}
        for semantic, asset_path in WINDOW_ASSETS.items():
            mesh = unreal.load_asset(asset_path)
            require(mesh is not None and isinstance(mesh, unreal.StaticMesh), f"Accepted window asset failed to load: {semantic}")
            require(len(list(mesh.get_editor_property("static_materials"))) == WINDOW_SLOTS[semantic], f"Window material slots changed: {semantic}")
            window_meshes[semantic] = mesh

        for floor_index, z_origin in enumerate(WINDOW_FLOOR_ORIGINS_CM):
            for column_index, x_origin in enumerate(WINDOW_COLUMNS_CM):
                module_id = f"F{floor_index:02d}_C{column_index:02d}"
                shared_transform = None
                for semantic in ("FRAME", "GLASS", "INTERIOR"):
                    actor = actors_api.spawn_actor_from_class(
                        unreal.StaticMeshActor,
                        unreal.Vector(x_origin, WINDOW_FACADE_Y_CM, z_origin),
                        unreal.Rotator(roll=0.0, pitch=0.0, yaw=WINDOW_YAW_DEGREES),
                        False,
                    )
                    require(actor is not None, f"Failed to spawn window {module_id} {semantic}")
                    actor.set_actor_label(f"{CELL_PREFIX}Window_{module_id}_{semantic}")
                    actor.set_folder_path("M01/HeroStreetShoreCell01/Facade/WindowBay")
                    component = actor.get_component_by_class(unreal.StaticMeshComponent)
                    require(component is not None, f"Window StaticMeshComponent missing: {module_id} {semantic}")
                    component.set_static_mesh(window_meshes[semantic])
                    component.set_mobility(unreal.ComponentMobility.STATIC)
                    component.set_collision_profile_name("BlockAll" if semantic == "FRAME" else "NoCollision")
                    state = transform_state(actor)
                    if shared_transform is None:
                        shared_transform = state
                    else:
                        require(state == shared_transform, f"Window triplet transform mismatch: {module_id}")
                result["window_modules"].append({"module": module_id, "transform": shared_transform})

        # Validate that every window module is in the real Midrise structural
        # envelope rather than floating in front of an empty lot.
        midrise = by_label["M01_ACA03R01_City_R00_C02_MidriseB_STRUCTURAL"]
        midrise_origin, midrise_extent = midrise.get_actor_bounds(False)
        midrise_min = [float(midrise_origin.x - midrise_extent.x), float(midrise_origin.y - midrise_extent.y), float(midrise_origin.z - midrise_extent.z)]
        midrise_max = [float(midrise_origin.x + midrise_extent.x), float(midrise_origin.y + midrise_extent.y), float(midrise_origin.z + midrise_extent.z)]
        require(all(midrise_min[0] <= x <= midrise_max[0] for x in WINDOW_COLUMNS_CM), "Window columns exceed Midrise X envelope")
        require(midrise_min[1] <= WINDOW_FACADE_Y_CM <= midrise_max[1] + 80.0, "Window facade is detached from Midrise Y envelope")
        require(min(WINDOW_FLOOR_ORIGINS_CM) - 400.0 >= midrise_min[2] - 20.0, "Lowest window module falls below Midrise")
        require(max(WINDOW_FLOOR_ORIGINS_CM) <= midrise_max[2] + 20.0, "Highest window module exceeds Midrise")

        # Validate all inherited accepted prop counts before adding bounded copies.
        current = list(actors_api.get_all_level_actors())
        for prefix, expected in EXPECTED_PROP_COUNTS.items():
            require(sum(actor.get_actor_label().startswith(prefix) for actor in current) == expected, f"Accepted prop count changed: {prefix}")

        for copy_index, (kind, source_label, x_cm, y_cm, scale, yaw_delta) in enumerate(PROP_COPIES, 1):
            source_actor = by_label.get(source_label)
            require(source_actor is not None, f"Accepted prop source actor missing: {source_label}")
            source_component = source_actor.get_component_by_class(unreal.StaticMeshComponent)
            require(source_component is not None, f"Accepted prop source component missing: {source_label}")
            mesh = source_component.get_editor_property("static_mesh")
            require(mesh is not None, f"Accepted prop source mesh missing: {source_label}")
            source_rotation = source_actor.get_actor_rotation()
            actor = actors_api.spawn_actor_from_class(
                unreal.StaticMeshActor,
                unreal.Vector(x_cm, y_cm, 0.0),
                unreal.Rotator(
                    roll=float(source_rotation.roll),
                    pitch=float(source_rotation.pitch),
                    yaw=float(source_rotation.yaw) + yaw_delta,
                ),
                False,
            )
            require(actor is not None, f"Failed to spawn accepted prop copy {copy_index}")
            actor.set_actor_label(f"{CELL_PREFIX}Prop_{copy_index:02d}_{kind}")
            actor.set_folder_path(f"M01/HeroStreetShoreCell01/Promenade/{kind}")
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            component = actor.get_component_by_class(unreal.StaticMeshComponent)
            require(component is not None, f"Prop-copy component missing: {copy_index}")
            component.set_static_mesh(mesh)
            component.set_mobility(unreal.ComponentMobility.STATIC)
            component.set_collision_profile_name("BlockAll")
            origin_before, extent_before = actor.get_actor_bounds(False)
            target_z = promenade_surface_z_cm(x_cm, y_cm)
            bottom_before = float(origin_before.z - extent_before.z)
            location = actor.get_actor_location()
            actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + target_z - bottom_before), False, True)
            origin_after, extent_after = actor.get_actor_bounds(False)
            bottom_after = float(origin_after.z - extent_after.z)
            require(abs(bottom_after - target_z) <= 1.0, f"Prop grounding failed: {copy_index}")
            require(CELL_X_RANGE_CM[0] <= float(origin_after.x) <= CELL_X_RANGE_CM[1], f"Prop outside cell X: {copy_index}")
            require(6_800.0 <= float(origin_after.y) <= 10_200.0, f"Prop outside promenade band: {copy_index}")
            require(float(extent_after.z) <= 250.0, f"Prop copy has implausible vertical extent: {copy_index}")
            result["prop_copies"].append({
                "label": actor.get_actor_label(),
                "source_label": source_label,
                "mesh": mesh.get_path_name(),
                "transform": transform_state(actor),
                "target_surface_z_cm": target_z,
                "bottom_after_cm": bottom_after,
                "bounds_extent_cm": vector(extent_after),
            })

        # Bounded exposure correction in the derived map. Geometry and accepted
        # material packages remain untouched.
        sky = by_label.get("M01_RS01_SkyLight")
        post = by_label.get("M01_RS01_PostProcess")
        require(sky is not None and post is not None, "Accepted lighting actors are missing")
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        require(sky_component is not None, "SkyLightComponent is missing")
        before_sky = float(sky_component.get_editor_property("intensity"))
        sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky_component.set_editor_property("intensity", TARGET_SKYLIGHT_INTENSITY)
        sky_component.set_editor_property("real_time_capture", True)
        sky_component.set_editor_property("lower_hemisphere_is_solid_color", False)
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
            "auto_exposure_bias_before": before_bias,
            "auto_exposure_bias_after": float(post.get_editor_property("settings").get_editor_property("auto_exposure_bias")),
            "film_toe_before": before_toe,
            "film_toe_after": float(post.get_editor_property("settings").get_editor_property("film_toe")),
        }

        final_actors = list(actors_api.get_all_level_actors())
        result["actor_count_after"] = len(final_actors)
        require(len(final_actors) == EXPECTED_ACTORS_AFTER, f"Hero-cell actor count changed: {len(final_actors)}")
        require(len(result["window_modules"]) == 12, "Hero window-module count changed")
        require(len(result["prop_copies"]) == 11, "Hero cell prop-copy count changed")
        require(sum(actor.get_actor_label().startswith(EXPECTED_BUILDING_TRIPLET_PREFIX) for actor in final_actors) == 9, "Hero cell building-triplet count changed")
        require(not any(actor.get_actor_label().startswith("M01_RS01_Tree_") for actor in final_actors), "Rejected proxy tree returned")
        require(not any(actor.get_actor_label() == "M01_RS01_Radar_Hero" for actor in final_actors), "Nonaccepted radar survived")
        require(sum(actor.get_actor_label().startswith(CELL_PREFIX + "Window_") for actor in final_actors) == 36, "Window actor count changed")
        require(sum(actor.get_actor_label().startswith(CELL_PREFIX + "Prop_") for actor in final_actors) == 11, "Cell prop actor count changed")

        require(levels.save_current_level(), "Failed to save Hero Street/Shore Cell01")
        require(OUTPUT_FILE.is_file(), "Hero Street/Shore Cell01 output map is missing")
        result["output_map"] = record(OUTPUT_FILE)
        result["input_map_after"] = record(INPUT_FILE)
        require(result["input_map_after"]["sha256"] == INPUT_SHA256, "Accepted Assembly03 map changed")
        for path, size, digest in WINDOW_FILES.values():
            require_file(path, size, digest)
        result["classification"] = "PASSED_M01_HERO_STREET_SHORE_CELL01_READY_FOR_D3D12_MAPPED_VISUAL_PROOF"
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
        raise RuntimeError(result["error"] or "Hero Street/Shore Cell01 authoring failed")


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
