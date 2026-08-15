import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY01\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "runtime_probe_receipt.json")
MAP_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
MAP_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"
EXPECTED_MAP_SHA256 = "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f"


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


def vector(value):
    return [float(value.x), float(value.y), float(value.z)]


def sample_row(name, sample):
    return {
        "name": name,
        "valid": bool(prop(sample, "valid", "b_valid")),
        "query_location_cm": vector(prop(sample, "query_location")),
        "height_cm": float(prop(sample, "height_centimeters")),
        "heightfield_source": str(prop(sample, "heightfield_source")),
        "error": str(prop(sample, "error")),
    }


def footprint_points(cx, cy, ex, ey, count):
    xy = [(cx, cy), (cx - ex, cy - ey), (cx + ex, cy - ey), (cx - ex, cy + ey), (cx + ex, cy + ey)]
    if count >= 9:
        xy += [(cx - ex, cy), (cx + ex, cy), (cx, cy - ey), (cx, cy + ey)]
    if count == 13:
        xy += [(cx - ex * 0.5, cy - ey), (cx + ex * 0.5, cy - ey), (cx - ex * 0.5, cy + ey), (cx + ex * 0.5, cy + ey)]
    require(len(xy) == count, "Footprint count mismatch")
    return [unreal.Vector(float(x), float(y), 100000.0) for x, y in xy]


def footprint_row(name, result):
    samples = list(prop(result, "samples"))
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
        "samples": [sample_row(f"{name}_{index:02d}", sample) for index, sample in enumerate(samples)],
        "error": str(prop(result, "error")),
    }


receipt = {
    "schema": "skyguard.m01-landscape-grounding-bridge01.runtime-probe-recovery01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "world_saved": False,
    "library_resolved": False,
    "landscape": None,
    "supported_samples": [],
    "expected_unsupported_samples": [],
    "footprints": [],
    "error": None,
}

try:
    require(os.path.isfile(MAP_FILE), "Recovery07 map file is missing")
    receipt["map_sha256_before"] = sha256(MAP_FILE)
    require(receipt["map_sha256_before"] == EXPECTED_MAP_SHA256, "Recovery07 map hash mismatch")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels and levels.load_level(MAP_ASSET), "Recovery07 map failed to load")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    matches = [actor for actor in actors.get_all_level_actors() if actor.get_actor_label() == "M01_A01_Landscape_Production"]
    require(len(matches) == 1, f"Expected one governed Landscape; found {len(matches)}")
    landscape = matches[0]
    origin, extent = landscape.get_actor_bounds(False)
    bounds = [origin.x - extent.x, origin.y - extent.y, origin.x + extent.x, origin.y + extent.y]
    receipt["landscape"] = {"class": landscape.get_class().get_path_name(), "origin_cm": vector(origin), "extent_cm": vector(extent), "supported_xy_bounds_cm": bounds}
    require(bounds == [0.0, 7000.0, 50400.0, 19600.0], f"Unexpected Landscape bounds: {bounds}")
    library = unreal.SkyguardMission01LandscapeGroundingLibrary
    receipt["library_resolved"] = library is not None

    for name, x, y in (
        ("landward_shore", 22500.0, 7100.0),
        ("road_center", 22500.0, 8800.0),
        ("city_near", 22500.0, 10300.0),
        ("city_mid", 22500.0, 13200.0),
        ("city_far", 22500.0, 17000.0),
        ("tree", 22500.0, 18000.0),
    ):
        receipt["supported_samples"].append(sample_row(name, library.sample_landscape_height(landscape, unreal.Vector(x, y, 100000.0))))
    require(all(row["valid"] for row in receipt["supported_samples"]), "A supported-corridor sample failed")

    for name, x, y in (("seaward_beach", 22500.0, 6050.0), ("beyond_inland_edge", 22500.0, 20500.0)):
        receipt["expected_unsupported_samples"].append(sample_row(name, library.sample_landscape_height(landscape, unreal.Vector(x, y, 100000.0))))
    require(all(not row["valid"] for row in receipt["expected_unsupported_samples"]), "An outside-corridor sample unexpectedly succeeded")

    specs = (
        ("landward_shore_transition", 22500.0, 7700.0, 2400.0, 500.0, 13),
        ("road_module", 22500.0, 8800.0, 1500.0, 480.0, 13),
        ("building_near", 22500.0, 10800.0, 740.0, 525.0, 9),
        ("building_mid", 22500.0, 13800.0, 660.0, 475.0, 9),
        ("building_far", 22500.0, 17300.0, 610.0, 450.0, 9),
        ("tree", 22500.0, 18500.0, 250.0, 250.0, 5),
    )
    for name, cx, cy, ex, ey, count in specs:
        receipt["footprints"].append(footprint_row(name, library.sample_landscape_footprint(landscape, footprint_points(cx, cy, ex, ey, count))))
    require(all(row["success"] for row in receipt["footprints"]), "A required footprint sample failed")
    require(all(row["supported_fraction"] == 1.0 for row in receipt["footprints"]), "Footprint support is incomplete")
    receipt["classification"] = "PASSED_GROUNDING_BRIDGE_RUNTIME_READY_FOR_MEASURED_AUTHORING"
except Exception as exc:
    receipt["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    if os.path.isfile(MAP_FILE):
        receipt["map_sha256_after"] = sha256(MAP_FILE)
        receipt["map_unchanged"] = receipt["map_sha256_after"] == receipt["map_sha256_before"]
    write_json_atomic(RECEIPT_PATH, receipt)
    print("SKYGUARD_GROUNDING_RUNTIME_PROBE_RECOVERY01=" + receipt["classification"])
