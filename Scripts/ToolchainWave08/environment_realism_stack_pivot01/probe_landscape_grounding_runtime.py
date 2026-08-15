import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "runtime_probe_receipt.json")
MAP_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
MAP_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
EXPECTED_MAP_SHA256 = "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f"
LANDSCAPE_LABEL = "M01_A01_Landscape_Production"


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


def vector_row(value):
    return [float(value.x), float(value.y), float(value.z)]


def property_value(value, *names):
    for name in names:
        try:
            return value.get_editor_property(name)
        except Exception:
            pass
        try:
            return getattr(value, name)
        except Exception:
            pass
    raise AttributeError("No property resolved: " + ", ".join(names))


def footprint_points(cx, cy, ex, ey, count):
    points = [
        (cx, cy),
        (cx - ex, cy - ey),
        (cx + ex, cy - ey),
        (cx - ex, cy + ey),
        (cx + ex, cy + ey),
    ]
    if count >= 9:
        points.extend(((cx - ex, cy), (cx + ex, cy), (cx, cy - ey), (cx, cy + ey)))
    if count == 13:
        points.extend(
            (
                (cx - ex * 0.5, cy - ey),
                (cx + ex * 0.5, cy - ey),
                (cx - ex * 0.5, cy + ey),
                (cx + ex * 0.5, cy + ey),
            )
        )
    require(len(points) == count, f"Footprint point count mismatch: {len(points)} != {count}")
    return [unreal.Vector(float(x), float(y), 100000.0) for x, y in points]


def sample_row(sample):
    return {
        "valid": bool(property_value(sample, "valid", "b_valid")),
        "query_location_cm": vector_row(property_value(sample, "query_location")),
        "height_cm": float(property_value(sample, "height_centimeters")),
        "heightfield_source": str(property_value(sample, "heightfield_source")),
        "error": str(property_value(sample, "error")),
    }


def footprint_row(name, result):
    samples = list(property_value(result, "samples"))
    return {
        "name": name,
        "success": bool(property_value(result, "success", "b_success")),
        "required_sample_count": int(property_value(result, "required_sample_count")),
        "valid_sample_count": int(property_value(result, "valid_sample_count")),
        "supported_fraction": float(property_value(result, "supported_fraction")),
        "minimum_height_cm": float(property_value(result, "minimum_height_centimeters")),
        "maximum_height_cm": float(property_value(result, "maximum_height_centimeters")),
        "mean_height_cm": float(property_value(result, "mean_height_centimeters")),
        "height_delta_cm": float(property_value(result, "height_delta_centimeters")),
        "samples": [sample_row(sample) for sample in samples],
        "error": str(property_value(result, "error")),
    }


receipt = {
    "schema": "skyguard.m01-landscape-grounding-bridge01.runtime-probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "world_saved": False,
    "library_resolved": False,
    "landscape": None,
    "single_samples": [],
    "footprints": [],
    "unsupported_probe": None,
    "error": None,
}

try:
    require(os.path.isfile(MAP_FILE), "Recovery07 map file is missing")
    receipt["map_sha256_before"] = sha256(MAP_FILE)
    require(receipt["map_sha256_before"] == EXPECTED_MAP_SHA256, "Recovery07 map hash mismatch")
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(level_subsystem is not None, "LevelEditorSubsystem is unavailable")
    require(level_subsystem.load_level(MAP_ASSET), "Recovery07 map failed to load")
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(actor_subsystem is not None, "EditorActorSubsystem is unavailable")
    matches = [actor for actor in actor_subsystem.get_all_level_actors() if actor.get_actor_label() == LANDSCAPE_LABEL]
    require(len(matches) == 1, f"Expected one governed Landscape; found {len(matches)}")
    landscape = matches[0]
    origin, extent = landscape.get_actor_bounds(False)
    receipt["landscape"] = {
        "label": LANDSCAPE_LABEL,
        "class": landscape.get_class().get_path_name(),
        "origin_cm": vector_row(origin),
        "extent_cm": vector_row(extent),
        "supported_xy_bounds_cm": [origin.x - extent.x, origin.y - extent.y, origin.x + extent.x, origin.y + extent.y],
    }
    library = unreal.SkyguardMission01LandscapeGroundingLibrary
    receipt["library_resolved"] = library is not None
    require(receipt["library_resolved"], "Grounding bridge Python library did not resolve")

    single_points = (
        ("shore_center", 22500.0, 6050.0),
        ("seawall_center", 22500.0, 7000.0),
        ("road_center", 22500.0, 8800.0),
        ("city_band_near", 22500.0, 10300.0),
        ("city_band_far", 22500.0, 12200.0),
    )
    for name, x, y in single_points:
        result = library.sample_landscape_height(landscape, unreal.Vector(x, y, 100000.0))
        row = sample_row(result)
        row["name"] = name
        receipt["single_samples"].append(row)
    require(all(row["valid"] for row in receipt["single_samples"]), "A required single height sample failed")

    footprint_specs = (
        ("shore_module", 22500.0, 6050.0, 2400.0, 900.0, 13),
        ("road_module", 22500.0, 8800.0, 1500.0, 480.0, 13),
        ("building_near", 22500.0, 10300.0, 740.0, 525.0, 9),
        ("building_far", 22500.0, 12200.0, 660.0, 475.0, 9),
        ("tree", 22500.0, 11800.0, 250.0, 250.0, 5),
    )
    for name, cx, cy, ex, ey, count in footprint_specs:
        result = library.sample_landscape_footprint(landscape, footprint_points(cx, cy, ex, ey, count))
        receipt["footprints"].append(footprint_row(name, result))
    require(all(row["success"] for row in receipt["footprints"]), "A required landscape footprint failed")

    unsupported = library.sample_landscape_height(landscape, unreal.Vector(22500.0, 16000.0, 100000.0))
    receipt["unsupported_probe"] = sample_row(unsupported)
    require(not receipt["unsupported_probe"]["valid"], "Out-of-landscape Y=16000 unexpectedly reported support")
    receipt["classification"] = "PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING"
except Exception as exc:
    receipt["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    if os.path.isfile(MAP_FILE):
        receipt["map_sha256_after"] = sha256(MAP_FILE)
        receipt["map_unchanged"] = receipt["map_sha256_after"] == receipt["map_sha256_before"]
    write_json_atomic(RECEIPT_PATH, receipt)
    print("SKYGUARD_GROUNDING_RUNTIME_PROBE=" + receipt["classification"])

if receipt["classification"] != "PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING":
    raise RuntimeError(receipt["error"]["message"] if receipt["error"] else "Runtime probe failed")
