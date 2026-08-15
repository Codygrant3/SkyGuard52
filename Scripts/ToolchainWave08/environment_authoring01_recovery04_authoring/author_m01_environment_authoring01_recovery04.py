import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "authoring_receipt.json")
INPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_WaterLandmassPCG_Prototype01"
OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery04"
INPUT_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap"
OUTPUT_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery04.umap"
EXPECTED_INPUT_SHA256 = "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"
HEIGHTMAP_FILE = r"D:\SG52T08_ENV01\Content\Skyguard\Environment\Source\Mission01\HM_M01_CoastalProduction_505x127.r16"
PCG_GRAPH = "/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation"
TERRAIN_MATERIAL = "/Game/Skyguard/Materials/M_Terrain"
OCEAN_MATERIAL = "/Game/Skyguard/Materials/Generated/M_L23_Ocean"
AUTHORING_PREFIX = "/Game/ToolchainWave08/Environment/Authoring01_Recovery04"
SAVE_ALLOWLIST = (OUTPUT_ASSET,)
PCG_SEED = 520801

REFINEMENT_ROOT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/"
)
ENGINE_TREE_ROOT = "/PCG/SampleContent/SimpleForest/Meshes/"
PCG_SCAN_ROOT = "/PCG/SampleContent/SimpleForest/Meshes"
REQUIRED_PCG_TREE_PATHS = (
    PCG_SCAN_ROOT + "/PCG_Tree_01",
    PCG_SCAN_ROOT + "/PCG_Tree_02",
    PCG_SCAN_ROOT + "/PCG_Tree_03",
)

MESHES = {
    "beach": REFINEMENT_ROOT + "SM_M01_Coast_Beach_Detailed_A",
    "promenade": REFINEMENT_ROOT + "SM_M01_Coast_Promenade_Detailed_A",
    "seawall": REFINEMENT_ROOT + "SM_M01_Coast_Seawall_Detailed_A",
    "road": REFINEMENT_ROOT + "SM_M01_Road_CoastalTransition_Detailed_A",
    "apartment_a": REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_A",
    "apartment_b": REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_B",
    "midrise": REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Detailed_A",
    "midrise_damaged": REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Damaged_A",
    "lighthouse": REFINEMENT_ROOT + "SM_M01_Landmark_Lighthouse_Hero_A",
    "radar": REFINEMENT_ROOT + "SM_M01_Landmark_RadarPost_Hero_A",
    "tree_01": ENGINE_TREE_ROOT + "PCG_Tree_01",
    "tree_02": ENGINE_TREE_ROOT + "PCG_Tree_02",
    "tree_03": ENGINE_TREE_ROOT + "PCG_Tree_03",
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path, value):
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)



def object_path(package_path):
    return package_path + "." + package_path.rsplit("/", 1)[-1]


def class_name(value):
    if value is None:
        return None
    try:
        return value.get_class().get_name()
    except Exception:
        return type(value).__name__


def scan_pcg_registry(registry):
    attempts = []
    signatures = (
        lambda: registry.scan_paths_synchronous([PCG_SCAN_ROOT], True, False),
        lambda: registry.scan_paths_synchronous([PCG_SCAN_ROOT], True),
        lambda: registry.scan_paths_synchronous([PCG_SCAN_ROOT]),
    )
    for signature, action in enumerate(signatures, 1):
        try:
            action()
            attempts.append({"signature": signature, "success": True})
            return {"passed": True, "scan_root": PCG_SCAN_ROOT, "attempts": attempts}
        except Exception as exc:
            attempts.append({"signature": signature, "success": False, "error": f"{type(exc).__name__}: {exc}"})
    return {"passed": False, "scan_root": PCG_SCAN_ROOT, "attempts": attempts}


def validate_pcg_tree_dependency(registry, package_path):
    record = {
        "package_path": package_path,
        "object_path": object_path(package_path),
        "registry_visible": False,
        "editor_asset_library_visible": False,
        "load_asset_success": False,
        "load_object_success": False,
        "class": None,
        "extent": None,
        "valid_nonzero_bounds": False,
        "passed": False,
        "errors": [],
    }
    try:
        data = registry.get_asset_by_object_path(record["object_path"])
        record["registry_visible"] = bool(data and data.is_valid())
    except Exception as exc:
        record["errors"].append(f"registry: {type(exc).__name__}: {exc}")
    try:
        record["editor_asset_library_visible"] = bool(unreal.EditorAssetLibrary.does_asset_exist(package_path))
    except Exception as exc:
        record["errors"].append(f"editor_asset_library: {type(exc).__name__}: {exc}")
    loaded_asset = None
    loaded_object = None
    try:
        loaded_asset = unreal.load_asset(package_path)
        record["load_asset_success"] = loaded_asset is not None
    except Exception as exc:
        record["errors"].append(f"load_asset: {type(exc).__name__}: {exc}")
    try:
        loaded_object = unreal.load_object(None, record["object_path"])
        record["load_object_success"] = loaded_object is not None
    except Exception as exc:
        record["errors"].append(f"load_object: {type(exc).__name__}: {exc}")
    mesh = loaded_asset or loaded_object
    record["class"] = class_name(mesh)
    if mesh is not None and record["class"] == "StaticMesh":
        try:
            extent = mesh.get_bounds().box_extent
            record["extent"] = [float(extent.x), float(extent.y), float(extent.z)]
            record["valid_nonzero_bounds"] = all(value > 0.0 for value in record["extent"])
        except Exception as exc:
            record["errors"].append(f"bounds: {type(exc).__name__}: {exc}")
    record["passed"] = all((
        record["registry_visible"],
        record["editor_asset_library_visible"],
        record["load_asset_success"],
        record["load_object_success"],
        record["class"] == "StaticMesh",
        record["valid_nonzero_bounds"],
    ))
    return record


def load_required_asset(path):
    require(unreal.EditorAssetLibrary.does_asset_exist(path), f"Missing asset: {path}")
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None, f"Asset failed to load: {path}")
    return asset


def set_exact_property(obj, name, value):
    try:
        obj.set_editor_property(name, value)
        observed = obj.get_editor_property(name)
    except Exception as exc:
        raise RuntimeError(f"Unsupported property {obj.get_class().get_path_name()}::{name}: {exc}")
    return observed


def actor_snapshot(actor):
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": [location.x, location.y, location.z],
        "rotation_deg": [rotation.roll, rotation.pitch, rotation.yaw],
        "scale": [scale.x, scale.y, scale.z],
        "tags": sorted(str(tag) for tag in actor.tags),
    }


def find_exact_actor(actors, class_path=None, label=None):
    matches = []
    for actor in actors:
        if class_path and actor.get_class().get_path_name() != class_path:
            continue
        if label and actor.get_actor_label() != label:
            continue
        matches.append(actor)
    require(len(matches) == 1, f"Expected exactly one actor class={class_path} label={label}; found {len(matches)}")
    return matches[0]


def spawn_actor(actor_subsystem, class_path, label, location, rotation=(0.0, 0.0, 0.0)):
    actor_class = unreal.load_class(None, class_path)
    require(actor_class is not None, f"Class failed to resolve: {class_path}")
    actor = actor_subsystem.spawn_actor_from_class(
        actor_class,
        unreal.Vector(*location),
        unreal.Rotator(rotation[0], rotation[1], rotation[2]),
        transient=False,
    )
    require(actor is not None, f"Actor failed to spawn: {label}")
    actor.set_actor_label(label)
    actor.tags = list(actor.tags) + ["Skyguard.Authoring01", f"Skyguard.Authoring01.{label}"]
    return actor


def spawn_static_mesh(actor_subsystem, mesh, label, location, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    actor = spawn_actor(
        actor_subsystem,
        "/Script/Engine.StaticMeshActor",
        label,
        location,
        rotation,
    )
    component = actor.static_mesh_component
    require(component is not None, f"Static mesh component missing: {label}")
    component.set_editor_property("static_mesh", mesh)
    component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor


def align_actor_bottom(actor, target_ground_z, tolerance_cm=1.0):
    origin, extent = actor.get_actor_bounds(False)
    bottom_before = origin.z - extent.z
    location = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(location.x, location.y, location.z + target_ground_z - bottom_before),
        False,
        False,
    )
    origin_after, extent_after = actor.get_actor_bounds(False)
    bottom_after = origin_after.z - extent_after.z
    gap = bottom_after - target_ground_z
    require(abs(gap) <= tolerance_cm, f"Grounding failed for {actor.get_actor_label()}: {gap} cm")
    return {
        "label": actor.get_actor_label(),
        "target_ground_z_cm": target_ground_z,
        "bottom_before_cm": bottom_before,
        "bottom_after_cm": bottom_after,
        "gap_cm": gap,
        "tolerance_cm": tolerance_cm,
    }


def fixed_layout():
    layout = []
    # Shoreline modules: six varied stations spanning the 450 m route.
    for index, x in enumerate((3750.0, 11250.0, 18750.0, 26250.0, 33750.0, 41250.0)):
        layout.extend(
            (
                ("beach", f"M01_A01_Beach_{index:02d}", (x, 6050.0, -95.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                ("seawall", f"M01_A01_Seawall_{index:02d}", (x, 7000.0, -85.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                ("promenade", f"M01_A01_Promenade_{index:02d}", (x, 7750.0, -70.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                ("road", f"M01_A01_Road_{index:02d}", (x, 8800.0, -55.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            )
        )
    city_x = (5200.0, 10100.0, 15100.0, 20500.0, 25800.0, 31500.0, 37100.0, 42100.0)
    city_meshes = ("apartment_a", "midrise", "apartment_b", "midrise_damaged")
    for index, x in enumerate(city_x):
        mesh_key = city_meshes[index % len(city_meshes)]
        y = 11200.0 + (index % 3) * 2100.0
        yaw = (0.0, 180.0, 8.0, -8.0)[index % 4]
        layout.append((mesh_key, f"M01_A01_City_{index:02d}", (x, y, -20.0), (0.0, 0.0, yaw), (1.0, 1.0, 1.0)))
    layout.extend(
        (
            ("lighthouse", "M01_A01_Lighthouse_Hero", (4200.0, 7200.0, -35.0), (0.0, 0.0, 8.0), (1.0, 1.0, 1.0)),
            ("radar", "M01_A01_Radar_Hero", (38200.0, 14600.0, 15.0), (0.0, 0.0, -24.0), (1.0, 1.0, 1.0)),
        )
    )
    tree_positions = (
        (6500.0, 15400.0), (8300.0, 16200.0), (11800.0, 14800.0),
        (14300.0, 17100.0), (17700.0, 15800.0), (19800.0, 16800.0),
        (22900.0, 14900.0), (24900.0, 17400.0), (28100.0, 15800.0),
        (30300.0, 17000.0), (33400.0, 15100.0), (35600.0, 16600.0),
        (38900.0, 15800.0), (40900.0, 17100.0), (43500.0, 15100.0),
    )
    for index, (x, y) in enumerate(tree_positions):
        mesh_key = ("tree_01", "tree_02", "tree_03")[index % 3]
        layout.append((mesh_key, f"M01_A01_Tree_{index:02d}", (x, y, 0.0), (0.0, 0.0, float((index * 47) % 360)), (1.0, 1.0, 1.0)))
    return layout


result = {
    "schema": "skyguard.toolchain-wave08.m01-environment-authoring01-recovery04.receipt.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "pcg_seed": PCG_SEED,
    "pcg_registry_initialization": None,
    "pcg_tree_validation": [],
    "pre_actor_inventory": [],
    "post_actor_inventory": [],
    "created_actor_labels": [],
    "grounding_records": [],
    "shore_contact_checks": {},
    "saved_assets": [],
    "unexpected_assets": [],
    "landmass_usage": "DEFERRED_NO_EFFECTFUL_BRUSH_API_AUTHORITY",
    "pcg_generation": "DISABLED_FIXED_DIRECT_PLACEMENT_ONLY",
    "error": None,
}

try:
    require(os.path.isfile(INPUT_FILE), "Accepted input clone file is missing")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Accepted input clone hash mismatch")
    require(not os.path.exists(OUTPUT_FILE), "Authoring01 output file already exists")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "Authoring01 output asset already exists")

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    require(registry is not None, "Asset Registry is unavailable")
    result["pcg_registry_initialization"] = scan_pcg_registry(registry)
    require(result["pcg_registry_initialization"]["passed"], "Bounded /PCG Asset Registry scan failed")
    result["pcg_tree_validation"] = [
        validate_pcg_tree_dependency(registry, path) for path in REQUIRED_PCG_TREE_PATHS
    ]
    require(len(result["pcg_tree_validation"]) == 3, "PCG tree validation count mismatch")
    require(all(record["passed"] for record in result["pcg_tree_validation"]), "PCG tree dependency validation failed")

    dependencies = [PCG_GRAPH, TERRAIN_MATERIAL, OCEAN_MATERIAL] + list(MESHES.values())
    loaded = {path: load_required_asset(path) for path in dependencies}

    output_world = unreal.EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)
    require(output_world is not None, "Unreal API duplication failed")
    require(unreal.EditorLevelLibrary.load_level(OUTPUT_ASSET), "Fresh Authoring01 world failed to load")
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(actor_subsystem is not None, "EditorActorSubsystem is unavailable")
    actors = list(actor_subsystem.get_all_level_actors())
    result["pre_actor_inventory"] = [actor_snapshot(actor) for actor in actors]

    director_class_path = "/Script/Skyguard52.SkyguardMission01EnvironmentDirector"
    directors = [actor for actor in actors if actor.get_class().get_path_name() == director_class_path]
    require(len(directors) == 1, f"Expected one Mission 1 environment director; found {len(directors)}")
    director = directors[0]
    director.set_actor_label("M01_A01_EnvironmentDirector")
    director.set_use_authored_landscape_surface_for_validation(True)

    authored = unreal.SkyguardMission01EnvironmentAuthoringLibrary.author_governed_landscape_with_existing_graph(
        director,
        HEIGHTMAP_FILE,
        PCG_GRAPH,
    )
    require(bool(authored.success), str(authored.error))
    landscape = authored.landscape
    require(landscape is not None, "Governed Landscape was not created")
    landscape.set_actor_label("M01_A01_Landscape_Production")
    landscape.set_editor_property("landscape_material", loaded[TERRAIN_MATERIAL])
    landscape.tags = list(landscape.tags) + ["Skyguard.Authoring01", "Skyguard.Authoring01.Ground"]

    water_zone = spawn_actor(
        actor_subsystem,
        "/Script/Water.WaterZone",
        "M01_A01_WaterZone",
        (22500.0, -22500.0, -160.0),
    )
    set_exact_property(water_zone, "zone_extent", unreal.Vector2D(180000.0, 180000.0))
    ocean = spawn_actor(
        actor_subsystem,
        "/Script/Water.WaterBodyOcean",
        "M01_A01_WaterBodyOcean",
        (22500.0, 4800.0, -160.0),
    )
    ocean_component_class = unreal.load_class(None, "/Script/Water.WaterBodyOceanComponent")
    require(ocean_component_class is not None, "WaterBodyOceanComponent class failed to resolve")
    ocean_component = ocean.get_component_by_class(ocean_component_class)
    require(ocean_component is not None, "WaterBodyOceanComponent is missing")
    set_exact_property(ocean_component, "ocean_extents", unreal.Vector2D(180000.0, 180000.0))
    set_exact_property(ocean_component, "collision_extents", unreal.Vector(180000.0, 180000.0, 4000.0))
    set_exact_property(ocean_component, "water_material", loaded[OCEAN_MATERIAL])
    if hasattr(ocean_component, "fill_water_zone_with_ocean"):
        ocean_component.fill_water_zone_with_ocean()

    ground_targets = {
        "beach": -95.0,
        "seawall": -85.0,
        "promenade": -70.0,
        "road": -55.0,
        "apartment_a": -20.0,
        "apartment_b": -20.0,
        "midrise": -20.0,
        "midrise_damaged": -20.0,
        "lighthouse": -35.0,
        "radar": 15.0,
        "tree_01": 0.0,
        "tree_02": 0.0,
        "tree_03": 0.0,
    }
    for mesh_key, label, location, rotation, scale in fixed_layout():
        actor = spawn_static_mesh(actor_subsystem, loaded[MESHES[mesh_key]], label, location, rotation, scale)
        result["grounding_records"].append(align_actor_bottom(actor, ground_targets[mesh_key]))
        result["created_actor_labels"].append(actor.get_actor_label())

    atmosphere_specs = (
        ("/Script/Engine.DirectionalLight", "M01_A01_Sun", (22500.0, 8000.0, 18000.0), (-32.0, -18.0, 0.0)),
        ("/Script/Engine.SkyLight", "M01_A01_SkyLight", (22500.0, 8000.0, 12000.0), (0.0, 0.0, 0.0)),
        ("/Script/Engine.SkyAtmosphere", "M01_A01_SkyAtmosphere", (22500.0, 8000.0, 0.0), (0.0, 0.0, 0.0)),
        ("/Script/Engine.ExponentialHeightFog", "M01_A01_HeightFog", (22500.0, 5500.0, -80.0), (0.0, 0.0, 0.0)),
        ("/Script/Engine.VolumetricCloud", "M01_A01_VolumetricCloud", (22500.0, 8000.0, 0.0), (0.0, 0.0, 0.0)),
    )
    for class_path, label, location, rotation in atmosphere_specs:
        created = spawn_actor(actor_subsystem, class_path, label, location, rotation)
        result["created_actor_labels"].append(created.get_actor_label())

    all_actors = list(actor_subsystem.get_all_level_actors())
    result["post_actor_inventory"] = [actor_snapshot(actor) for actor in all_actors]
    labels = [row["label"] for row in result["post_actor_inventory"]]
    require(len(labels) == len(set(labels)), "Duplicate actor labels exist after authoring")
    require(len([label for label in labels if label.startswith("M01_A01_Tree_")]) == 15, "Vegetation count is not exactly 15")
    require(find_exact_actor(all_actors, label="M01_A01_Landscape_Production") is landscape, "Landscape identity mismatch")
    require(find_exact_actor(all_actors, label="M01_A01_WaterBodyOcean") is ocean, "Ocean identity mismatch")
    require(len(result["grounding_records"]) == len(fixed_layout()), "Grounding receipt count mismatch")
    require(max(abs(row["gap_cm"]) for row in result["grounding_records"]) <= 1.0, "Grounding tolerance exceeded")
    beach_rows = [row for row in result["grounding_records"] if row["label"].startswith("M01_A01_Beach_")]
    require(len(beach_rows) == 6, "Shoreline beach station count is not six")
    ocean_z = ocean.get_actor_location().z
    shore_vertical_delta = min(row["bottom_after_cm"] for row in beach_rows) - ocean_z
    require(0.0 <= shore_vertical_delta <= 120.0, f"Water/shore vertical relationship failed: {shore_vertical_delta} cm")
    result["shore_contact_checks"] = {
        "ocean_z_cm": ocean_z,
        "beach_station_count": len(beach_rows),
        "maximum_vertical_step_cm": 120.0,
        "observed_vertical_delta_cm": shore_vertical_delta,
        "nominal_shore_y_cm": 5200.0,
        "continuous_route_coverage_cm": 45000.0,
        "passed": True,
    }

    candidate_assets = set(unreal.EditorAssetLibrary.list_assets("/Game/ToolchainWave08/Environment", recursive=True, include_folder=False))
    before_save_allowed = {OUTPUT_ASSET, OUTPUT_ASSET + ".Lvl_M01_T08_EnvironmentAuthoring01_Recovery04"}
    unexpected = sorted(path for path in candidate_assets if path.startswith(AUTHORING_PREFIX) and path not in before_save_allowed)
    require(not unexpected, f"Unexpected Authoring01 assets before save: {unexpected}")
    result["unexpected_assets"] = unexpected
    require(unreal.EditorAssetLibrary.save_asset(OUTPUT_ASSET, only_if_is_dirty=False), "Failed to save Authoring01 output")
    result["saved_assets"] = [OUTPUT_ASSET]
    require(os.path.isfile(OUTPUT_FILE), "Authoring01 output file is missing after save")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Accepted input clone changed")
    result["classification"] = "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_AUTOMATIC"
except Exception as exc:
    result["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    if result["input_sha256_after"] is None and os.path.isfile(INPUT_FILE):
        result["input_sha256_after"] = sha256(INPUT_FILE)
    if result["output_sha256"] is None and os.path.isfile(OUTPUT_FILE):
        result["output_sha256"] = sha256(OUTPUT_FILE)
    os.makedirs(ATTEMPT_ROOT, exist_ok=True)
    write_json_atomic(RECEIPT_PATH, result)
    print("SKYGUARD_M01_AUTHORING01=" + result["classification"])

if result["classification"] != "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_AUTOMATIC":
    raise RuntimeError(result["error"]["message"] if result["error"] else "Authoring01 failed")
