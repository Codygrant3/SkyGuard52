import hashlib
import json
import math
import os
import random
import traceback

import unreal


ROOT = r"D:\Skyguard52"
ATTEMPT_ROOT = os.path.join(
    ROOT,
    r"Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01\attempt_01",
)
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "authoring_receipt.json")
INPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack01_Recovery01"
INPUT_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
OUTPUT_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery01.umap"
EXPECTED_INPUT_SHA256 = "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f"
AUTHORING_PREFIX = "/Game/ToolchainWave08/Environment/RealismStack01_Recovery01"
RANDOM_SEED = 520811

REFINEMENT_ROOT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/"
)
ENGINE_TREE_ROOT = "/PCG/SampleContent/SimpleForest/Meshes/"
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

REMOVE_PREFIXES = (
    "M01_A01_Beach_",
    "M01_A01_Seawall_",
    "M01_A01_Promenade_",
    "M01_A01_Road_",
    "M01_A01_City_",
    "M01_A01_Tree_",
)
REMOVE_EXACT = {
    "M01_A01_Lighthouse_Hero",
    "M01_A01_Radar_Hero",
    "M01_A01_Sun",
    "M01_A01_SkyLight",
    "M01_A01_SkyAtmosphere",
    "M01_A01_HeightFog",
    "M01_A01_VolumetricCloud",
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, path)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def prop(value, *names):
    for name in names:
        try:
            return value.get_editor_property(name)
        except Exception:
            pass
        try:
            return getattr(value, name)
        except Exception:
            pass
    raise AttributeError("Property not found: " + ", ".join(names))


def vec(value):
    return [float(value.x), float(value.y), float(value.z)]


def load_required_asset(path):
    asset = unreal.load_asset(path)
    require(asset is not None, f"Asset failed to load: {path}")
    return asset


def actor_snapshot(actor):
    location = actor.get_actor_location()
    return {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_path_name(),
        "location_cm": vec(location),
        "tags": [str(tag) for tag in actor.tags],
    }


def find_exact(actors, label):
    matches = [actor for actor in actors if actor.get_actor_label() == label]
    require(len(matches) == 1, f"Expected exactly one actor labeled {label}; found {len(matches)}")
    return matches[0]


def spawn_actor(subsystem, class_path, label, location, rotation=(0.0, 0.0, 0.0)):
    actor_class = unreal.load_class(None, class_path)
    require(actor_class is not None, f"Class failed to resolve: {class_path}")
    actor = subsystem.spawn_actor_from_class(
        actor_class,
        unreal.Vector(*location),
        unreal.Rotator(rotation[0], rotation[1], rotation[2]),
        transient=False,
    )
    require(actor is not None, f"Actor failed to spawn: {label}")
    actor.set_actor_label(label)
    actor.tags = list(actor.tags) + ["Skyguard.RealismStack01", f"Skyguard.RealismStack01.{label}"]
    return actor


def spawn_static_mesh(subsystem, mesh, label, location, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    actor = spawn_actor(subsystem, "/Script/Engine.StaticMeshActor", label, location, rotation)
    component = actor.static_mesh_component
    require(component is not None, f"Static mesh component missing: {label}")
    component.set_editor_property("static_mesh", mesh)
    component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor


def sample_summary(result, name):
    return {
        "name": name,
        "success": bool(prop(result, "success", "b_success")),
        "required_sample_count": int(prop(result, "required_sample_count")),
        "valid_sample_count": int(prop(result, "valid_sample_count")),
        "supported_fraction": float(prop(result, "supported_fraction")),
        "minimum_height_cm": float(prop(result, "minimum_height_centimeters")),
        "maximum_height_cm": float(prop(result, "maximum_height_centimeters")),
        "mean_height_cm": float(prop(result, "mean_height_centimeters")),
        "height_delta_cm": float(prop(result, "height_delta_centimeters")),
        "error": str(prop(result, "error")),
    }


def footprint_points(origin, extent, count):
    cx, cy = float(origin.x), float(origin.y)
    ex = max(1.0, float(extent.x) * 0.98)
    ey = max(1.0, float(extent.y) * 0.98)
    xy = [
        (cx, cy),
        (cx - ex, cy - ey),
        (cx + ex, cy - ey),
        (cx - ex, cy + ey),
        (cx + ex, cy + ey),
    ]
    if count >= 9:
        xy += [(cx - ex, cy), (cx + ex, cy), (cx, cy - ey), (cx, cy + ey)]
    if count == 13:
        xy += [
            (cx - ex * 0.5, cy - ey),
            (cx + ex * 0.5, cy - ey),
            (cx - ex * 0.5, cy + ey),
            (cx + ex * 0.5, cy + ey),
        ]
    require(len(xy) == count, f"Footprint sample count mismatch: {len(xy)} != {count}")
    return [unreal.Vector(x, y, 100000.0) for x, y in xy]


def align_bottom(actor, target_z):
    origin, extent = actor.get_actor_bounds(False)
    bottom_before = float(origin.z - extent.z)
    location = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(location.x, location.y, location.z + target_z - bottom_before),
        False,
        False,
    )
    after_origin, after_extent = actor.get_actor_bounds(False)
    bottom_after = float(after_origin.z - after_extent.z)
    gap = bottom_after - float(target_z)
    require(abs(gap) <= 1.0, f"Grounding gap exceeded for {actor.get_actor_label()}: {gap} cm")
    return {
        "target_ground_z_cm": float(target_z),
        "bottom_before_cm": bottom_before,
        "bottom_after_cm": bottom_after,
        "gap_cm": gap,
    }


def ground_by_footprint(library, landscape, actor, count, maximum_delta, category):
    origin, extent = actor.get_actor_bounds(False)
    sampled = library.sample_landscape_footprint(landscape, footprint_points(origin, extent, count))
    summary = sample_summary(sampled, actor.get_actor_label())
    require(summary["success"], f"Unsupported footprint for {actor.get_actor_label()}: {summary['error']}")
    require(summary["supported_fraction"] == 1.0, f"Incomplete footprint support for {actor.get_actor_label()}")
    require(summary["height_delta_cm"] <= maximum_delta, f"Terrain delta too large for {actor.get_actor_label()}: {summary['height_delta_cm']} cm")
    summary.update(align_bottom(actor, summary["mean_height_cm"]))
    summary["category"] = category
    summary["actor_bounds_origin_cm"] = vec(origin)
    summary["actor_bounds_extent_cm"] = vec(extent)
    return summary


def ground_point(library, landscape, actor, category):
    location = actor.get_actor_location()
    sampled = library.sample_landscape_height(landscape, unreal.Vector(location.x, location.y, 100000.0))
    valid = bool(prop(sampled, "valid", "b_valid"))
    require(valid, f"Unsupported point placement for {actor.get_actor_label()}: {prop(sampled, 'error')}")
    target = float(prop(sampled, "height_centimeters"))
    row = {
        "name": actor.get_actor_label(),
        "success": True,
        "required_sample_count": 1,
        "valid_sample_count": 1,
        "supported_fraction": 1.0,
        "minimum_height_cm": target,
        "maximum_height_cm": target,
        "mean_height_cm": target,
        "height_delta_cm": 0.0,
        "error": "",
        "category": category,
        "query_location_cm": [float(location.x), float(location.y), 100000.0],
    }
    row.update(align_bottom(actor, target))
    return row


def add_linear_modules(subsystem, loaded, library, landscape, result):
    ocean_z = result["ocean_z_cm"]
    # Ten 48 m beach pieces create a continuous 480 m seaward transition. The
    # beach center is intentionally outside the Landscape and is tied to the
    # measured water plane instead of pretending that Landscape support exists.
    for index in range(10):
        x = 2400.0 + index * 4800.0
        actor = spawn_static_mesh(subsystem, loaded[MESHES["beach"]], f"M01_RS01_Beach_{index:02d}", (x, 6050.0, 0.0))
        row = align_bottom(actor, ocean_z + 65.0)
        row.update({"name": actor.get_actor_label(), "category": "seaward_beach", "support_mode": "WATERLINE_RELATIONSHIP", "ocean_z_cm": ocean_z})
        result["grounding_records"].append(row)
        result["created_actor_labels"].append(actor.get_actor_label())

    specs = (
        ("seawall", "Seawall", 20, 1215.0, 2430.0, 7330.0, 13, 150.0),
        ("promenade", "Promenade", 16, 1500.0, 3000.0, 7850.0, 13, 150.0),
        ("road", "CoastalRoad", 16, 1500.0, 3000.0, 8800.0, 13, 125.0),
    )
    for mesh_key, label_prefix, count, start_x, stride_x, y, samples, max_delta in specs:
        for index in range(count):
            x = start_x + index * stride_x
            actor = spawn_static_mesh(subsystem, loaded[MESHES[mesh_key]], f"M01_RS01_{label_prefix}_{index:02d}", (x, y, 0.0))
            result["grounding_records"].append(ground_by_footprint(library, landscape, actor, samples, max_delta, mesh_key))
            result["created_actor_labels"].append(actor.get_actor_label())

    for column, x in enumerate((6000.0, 16000.0, 26000.0, 36000.0, 46000.0)):
        for segment, y in enumerate((10600.0, 13600.0, 16600.0)):
            actor = spawn_static_mesh(
                subsystem,
                loaded[MESHES["road"]],
                f"M01_RS01_CrossStreet_{column:02d}_{segment:02d}",
                (x, y, 0.0),
                (0.0, 0.0, 90.0),
            )
            result["grounding_records"].append(ground_by_footprint(library, landscape, actor, 13, 125.0, "cross_street"))
            result["created_actor_labels"].append(actor.get_actor_label())


def add_city(subsystem, loaded, library, landscape, result):
    rows = (10800.0, 13100.0, 15400.0, 17800.0)
    x_base = (3500.0, 8500.0, 13500.0, 18500.0, 23500.0, 28500.0, 33500.0, 38500.0, 43500.0)
    shifts = (0.0, 900.0, -700.0, 600.0)
    mesh_cycle = ("apartment_a", "midrise", "apartment_b", "midrise_damaged")
    yaw_cycle = (-7.0, 0.0, 6.0, 180.0, -3.0, 4.0)
    scale_cycle = (0.96, 1.0, 1.04, 0.98, 1.02)
    for row_index, y in enumerate(rows):
        for column_index, base_x in enumerate(x_base):
            x = base_x + shifts[row_index]
            mesh_key = mesh_cycle[(column_index + row_index * 2) % len(mesh_cycle)]
            yaw = yaw_cycle[(column_index + row_index) % len(yaw_cycle)]
            scale = scale_cycle[(column_index * 2 + row_index) % len(scale_cycle)]
            label = f"M01_RS01_City_R{row_index:02d}_C{column_index:02d}_{mesh_key}"
            actor = spawn_static_mesh(subsystem, loaded[MESHES[mesh_key]], label, (x, y, 0.0), (0.0, 0.0, yaw), (scale, scale, scale))
            result["grounding_records"].append(ground_by_footprint(library, landscape, actor, 9, 100.0, "building"))
            result["created_actor_labels"].append(actor.get_actor_label())
            result["building_signature_counts"][mesh_key] += 1


def add_trees(subsystem, loaded, library, landscape, result):
    rng = random.Random(RANDOM_SEED)
    bands = (9900.0, 12000.0, 14300.0, 16600.0, 18800.0)
    for band_index, base_y in enumerate(bands):
        for index in range(12):
            x = 1800.0 + index * 3900.0 + rng.uniform(-550.0, 550.0)
            y = base_y + rng.uniform(-280.0, 280.0)
            mesh_key = ("tree_01", "tree_02", "tree_03")[(index + band_index) % 3]
            yaw = rng.uniform(0.0, 360.0)
            scale = rng.uniform(0.86, 1.14)
            actor = spawn_static_mesh(
                subsystem,
                loaded[MESHES[mesh_key]],
                f"M01_RS01_Tree_B{band_index:02d}_{index:02d}",
                (x, y, 0.0),
                (0.0, 0.0, yaw),
                (scale, scale, scale),
            )
            result["grounding_records"].append(ground_point(library, landscape, actor, "tree"))
            result["created_actor_labels"].append(actor.get_actor_label())


def set_property(value, name, setting):
    value.set_editor_property(name, setting)
    return {"property": name, "value": str(setting), "passed": True}


def add_atmosphere(subsystem, result):
    sun = spawn_actor(subsystem, "/Script/Engine.DirectionalLight", "M01_RS01_Sun", (22500.0, 8000.0, 18000.0), (-34.0, -24.0, 0.0))
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    require(sun_component is not None, "DirectionalLightComponent is missing")
    result["atmosphere_properties"].append(set_property(sun_component, "intensity", 8.0))
    result["atmosphere_properties"].append(set_property(sun_component, "use_temperature", True))
    result["atmosphere_properties"].append(set_property(sun_component, "temperature", 5600.0))
    result["atmosphere_properties"].append(set_property(sun_component, "atmosphere_sun_light", True))

    sky = spawn_actor(subsystem, "/Script/Engine.SkyLight", "M01_RS01_SkyLight", (22500.0, 8000.0, 12000.0))
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    require(sky_component is not None, "SkyLightComponent is missing")
    result["atmosphere_properties"].append(set_property(sky_component, "intensity", 0.85))
    result["atmosphere_properties"].append(set_property(sky_component, "real_time_capture", True))

    spawn_actor(subsystem, "/Script/Engine.SkyAtmosphere", "M01_RS01_SkyAtmosphere", (22500.0, 8000.0, 0.0))
    fog = spawn_actor(subsystem, "/Script/Engine.ExponentialHeightFog", "M01_RS01_HeightFog", (22500.0, 5500.0, -80.0))
    fog_component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    require(fog_component is not None, "ExponentialHeightFogComponent is missing")
    result["atmosphere_properties"].append(set_property(fog_component, "fog_density", 0.012))
    result["atmosphere_properties"].append(set_property(fog_component, "fog_height_falloff", 0.2))
    fog_component.set_volumetric_fog(True)
    result["atmosphere_properties"].append({"property": "set_volumetric_fog", "value": "True", "passed": True})
    spawn_actor(subsystem, "/Script/Engine.VolumetricCloud", "M01_RS01_VolumetricCloud", (22500.0, 8000.0, 0.0))

    post = spawn_actor(subsystem, "/Script/Engine.PostProcessVolume", "M01_RS01_PostProcess", (22500.0, 12000.0, 500.0))
    result["atmosphere_properties"].append(set_property(post, "b_unbound", True))
    settings = post.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.5)
    settings.set_editor_property("override_bloom_intensity", True)
    settings.set_editor_property("bloom_intensity", 0.15)
    settings.set_editor_property("override_vignette_intensity", True)
    settings.set_editor_property("vignette_intensity", 0.18)
    post.set_editor_property("settings", settings)
    result["post_process"] = {
        "unbound": True,
        "auto_exposure_method": "AEM_MANUAL",
        "auto_exposure_bias": 0.5,
        "bloom_intensity": 0.15,
        "vignette_intensity": 0.18,
    }
    result["created_actor_labels"].extend(
        [
            sun.get_actor_label(),
            sky.get_actor_label(),
            "M01_RS01_SkyAtmosphere",
            fog.get_actor_label(),
            "M01_RS01_VolumetricCloud",
            post.get_actor_label(),
        ]
    )


result = {
    "schema": "skyguard.m01-environment-realism-stack-authoring01-recovery01.receipt.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "input_asset": INPUT_ASSET,
    "output_asset": OUTPUT_ASSET,
    "input_sha256_before": None,
    "input_sha256_after": None,
    "output_sha256": None,
    "random_seed": RANDOM_SEED,
    "pre_actor_inventory": [],
    "post_actor_inventory": [],
    "removed_actor_labels": [],
    "created_actor_labels": [],
    "grounding_records": [],
    "building_signature_counts": {key: 0 for key in ("apartment_a", "apartment_b", "midrise", "midrise_damaged")},
    "atmosphere_properties": [],
    "post_process": None,
    "ocean_z_cm": None,
    "shore_contact": None,
    "density_metrics": None,
    "saved_assets": [],
    "unexpected_assets": [],
    "error": None,
}

try:
    require(os.path.isfile(INPUT_FILE), "Recovery07 input map is missing")
    result["input_sha256_before"] = sha256(INPUT_FILE)
    require(result["input_sha256_before"] == EXPECTED_INPUT_SHA256, "Recovery07 input map hash mismatch")
    require(not os.path.exists(OUTPUT_FILE), "RealismStack01 Recovery01 output file already exists")
    require(not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT_ASSET), "RealismStack01 Recovery01 output asset already exists")

    loaded = {path: load_required_asset(path) for path in MESHES.values()}
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels is not None, "LevelEditorSubsystem is unavailable")
    require(levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET), "Failed to create RealismStack01 Recovery01 from Recovery07")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(actors is not None, "EditorActorSubsystem is unavailable")
    before = list(actors.get_all_level_actors())
    result["pre_actor_inventory"] = [actor_snapshot(actor) for actor in before]

    landscape = find_exact(before, "M01_A01_Landscape_Production")
    ocean = find_exact(before, "M01_A01_WaterBodyOcean")
    find_exact(before, "M01_A01_WaterZone")
    director = find_exact(before, "M01_A01_EnvironmentDirector")
    require(director.get_class().get_path_name() == "/Script/Skyguard52.SkyguardMission01EnvironmentDirector", "Environment director class mismatch")
    director.set_use_authored_landscape_surface_for_validation(True)
    result["ocean_z_cm"] = float(ocean.get_actor_location().z)

    for actor in before:
        label = actor.get_actor_label()
        if label in REMOVE_EXACT or any(label.startswith(prefix) for prefix in REMOVE_PREFIXES):
            require(actors.destroy_actor(actor), f"Failed to remove inherited actor: {label}")
            result["removed_actor_labels"].append(label)

    library = unreal.SkyguardMission01LandscapeGroundingLibrary
    require(library is not None, "Landscape grounding library is unavailable")
    add_linear_modules(actors, loaded, library, landscape, result)
    add_city(actors, loaded, library, landscape, result)
    add_trees(actors, loaded, library, landscape, result)

    for mesh_key, label, location, rotation in (
        ("lighthouse", "M01_RS01_Lighthouse_Hero", (3200.0, 7600.0, 0.0), (0.0, 0.0, 8.0)),
        ("radar", "M01_RS01_Radar_Hero", (42000.0, 18500.0, 0.0), (0.0, 0.0, -24.0)),
    ):
        actor = spawn_static_mesh(actors, loaded[MESHES[mesh_key]], label, location, rotation)
        result["grounding_records"].append(ground_by_footprint(library, landscape, actor, 9, 120.0, "landmark"))
        result["created_actor_labels"].append(actor.get_actor_label())

    add_atmosphere(actors, result)

    post = list(actors.get_all_level_actors())
    result["post_actor_inventory"] = [actor_snapshot(actor) for actor in post]
    labels = [row["label"] for row in result["post_actor_inventory"]]
    require(len(labels) == len(set(labels)), "Duplicate actor labels exist")
    counts = {
        "beach": len([label for label in labels if label.startswith("M01_RS01_Beach_")]),
        "seawall": len([label for label in labels if label.startswith("M01_RS01_Seawall_")]),
        "promenade": len([label for label in labels if label.startswith("M01_RS01_Promenade_")]),
        "coastal_road": len([label for label in labels if label.startswith("M01_RS01_CoastalRoad_")]),
        "cross_street": len([label for label in labels if label.startswith("M01_RS01_CrossStreet_")]),
        "building": len([label for label in labels if label.startswith("M01_RS01_City_")]),
        "tree": len([label for label in labels if label.startswith("M01_RS01_Tree_")]),
        "landmark": len([label for label in labels if label in {"M01_RS01_Lighthouse_Hero", "M01_RS01_Radar_Hero"}]),
        "atmosphere": len([label for label in labels if label in {"M01_RS01_Sun", "M01_RS01_SkyLight", "M01_RS01_SkyAtmosphere", "M01_RS01_HeightFog", "M01_RS01_VolumetricCloud", "M01_RS01_PostProcess"}]),
    }
    expected_counts = {"beach": 10, "seawall": 20, "promenade": 16, "coastal_road": 16, "cross_street": 15, "building": 36, "tree": 60, "landmark": 2, "atmosphere": 6}
    require(counts == expected_counts, f"Density contract mismatch: {counts}")
    require(all(value >= 8 for value in result["building_signature_counts"].values()), f"Building signature balance failed: {result['building_signature_counts']}")
    require(len(result["grounding_records"]) == 175, f"Grounding receipt count mismatch: {len(result['grounding_records'])}")
    landscape_grounded = [row for row in result["grounding_records"] if row.get("support_mode") != "WATERLINE_RELATIONSHIP"]
    require(all(row.get("success", True) for row in landscape_grounded), "A Landscape grounding record failed")
    require(max(abs(row["gap_cm"]) for row in result["grounding_records"]) <= 1.0, "A final actor-bottom gap exceeded one centimeter")
    beach_rows = [row for row in result["grounding_records"] if row["category"] == "seaward_beach"]
    observed_delta = min(row["bottom_after_cm"] for row in beach_rows) - result["ocean_z_cm"]
    require(abs(observed_delta - 65.0) <= 1.0, f"Waterline transition delta is {observed_delta} cm")
    result["shore_contact"] = {
        "ocean_z_cm": result["ocean_z_cm"],
        "beach_bottom_delta_cm": observed_delta,
        "continuous_coverage_cm": 48000.0,
        "beach_modules": len(beach_rows),
        "passed": True,
    }
    result["density_metrics"] = {
        "counts": counts,
        "expected_counts": expected_counts,
        "total_new_visible_actors": sum(counts.values()),
        "city_depth_bands": 4,
        "building_signatures": result["building_signature_counts"],
        "route_coverage_cm": 48000.0,
    }

    candidates = set(unreal.EditorAssetLibrary.list_assets("/Game/ToolchainWave08/Environment", recursive=True, include_folder=False))
    unexpected = sorted(path for path in candidates if path.startswith(AUTHORING_PREFIX) and path != OUTPUT_ASSET)
    require(not unexpected, f"Unexpected RealismStack01 assets: {unexpected}")
    result["unexpected_assets"] = unexpected
    require(unreal.EditorAssetLibrary.save_asset(OUTPUT_ASSET, only_if_is_dirty=False), "Failed to save RealismStack01 Recovery01 map")
    result["saved_assets"] = [OUTPUT_ASSET]
    require(os.path.isfile(OUTPUT_FILE), "RealismStack01 Recovery01 output file is missing after save")
    result["output_sha256"] = sha256(OUTPUT_FILE)
    result["input_sha256_after"] = sha256(INPUT_FILE)
    require(result["input_sha256_after"] == EXPECTED_INPUT_SHA256, "Recovery07 input map changed")
    result["classification"] = "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_AUTOMATIC"
except Exception as exc:
    result["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    if result["input_sha256_after"] is None and os.path.isfile(INPUT_FILE):
        result["input_sha256_after"] = sha256(INPUT_FILE)
    if result["output_sha256"] is None and os.path.isfile(OUTPUT_FILE):
        result["output_sha256"] = sha256(OUTPUT_FILE)
    write_json_atomic(RECEIPT_PATH, result)
    print("SKYGUARD_M01_REALISM_STACK_AUTHORING01=" + result["classification"])

if result["classification"] != "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_AUTOMATIC":
    raise RuntimeError(result["error"]["message"] if result["error"] else "RealismStack01 Recovery01 authoring failed")
