import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = os.environ["SKYGUARD_DEPENDENCY_PROBE_ATTEMPT"]
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "dependency_probe_receipt.json")
INPUT_MAP = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap"
EXPECTED_INPUT_HASH = "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"
PCG_TREE_ROOT = "/PCG/SampleContent/SimpleForest/Meshes"
FORBIDDEN_PROXY = "/Game/Skyguard/Meshes/Hero/coast_tree_proxy"

REFINEMENT_ROOT = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/"
)

DEPENDENCIES = [
    ("/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation", "PCGGraph", "pcg_graph"),
    ("/Game/Skyguard/Materials/M_Terrain", "Material", "terrain_material"),
    ("/Game/Skyguard/Materials/Generated/M_L23_Ocean", "Material", "ocean_material"),
    ("/Game/Skyguard/Materials/Generated/M_L23_Beach", "Material", "beach_material"),
    ("/Game/Skyguard/Materials/Generated/M_AsphaltRoad", "Material", "road_material"),
    (REFINEMENT_ROOT + "SM_M01_Coast_Beach_Detailed_A", "StaticMesh", "beach_mesh"),
    (REFINEMENT_ROOT + "SM_M01_Coast_Promenade_Detailed_A", "StaticMesh", "promenade_mesh"),
    (REFINEMENT_ROOT + "SM_M01_Coast_Seawall_Detailed_A", "StaticMesh", "seawall_mesh"),
    (REFINEMENT_ROOT + "SM_M01_Road_CoastalTransition_Detailed_A", "StaticMesh", "road_mesh"),
    (REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_A", "StaticMesh", "apartment_a"),
    (REFINEMENT_ROOT + "SM_M01_Urban_Apartment_Detailed_B", "StaticMesh", "apartment_b"),
    (REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Detailed_A", "StaticMesh", "midrise_a"),
    (REFINEMENT_ROOT + "SM_M01_Urban_Midrise_Damaged_A", "StaticMesh", "midrise_damaged"),
    (REFINEMENT_ROOT + "SM_M01_Landmark_Lighthouse_Hero_A", "StaticMesh", "lighthouse"),
    (REFINEMENT_ROOT + "SM_M01_Landmark_RadarPost_Hero_A", "StaticMesh", "radar"),
    (PCG_TREE_ROOT + "/PCG_Tree_01", "StaticMesh", "tree_01"),
    (PCG_TREE_ROOT + "/PCG_Tree_02", "StaticMesh", "tree_02"),
    (PCG_TREE_ROOT + "/PCG_Tree_03", "StaticMesh", "tree_03"),
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_path(package_path):
    return package_path + "." + package_path.rsplit("/", 1)[-1]


def class_name(value):
    if value is None:
        return None
    try:
        return value.get_class().get_name()
    except Exception:
        return type(value).__name__


def asset_data_record(registry, package_path):
    result = {"valid": False, "asset_name": None, "asset_class": None, "object_path": None, "error": None}
    try:
        data = registry.get_asset_by_object_path(object_path(package_path))
        result["valid"] = bool(data and data.is_valid())
        if result["valid"]:
            result["asset_name"] = str(data.asset_name)
            result["asset_class"] = str(data.asset_class_path.asset_name)
            result["object_path"] = str(data.get_soft_object_path())
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def list_visibility(package_path):
    folder = package_path.rsplit("/", 1)[0]
    try:
        values = [str(x) for x in unreal.EditorAssetLibrary.list_assets(folder, recursive=False, include_folder=False)]
        expected = object_path(package_path)
        return {"folder": folder, "count": len(values), "visible": package_path in values or expected in values, "assets": values}
    except Exception as exc:
        return {"folder": folder, "count": 0, "visible": False, "assets": [], "error": f"{type(exc).__name__}: {exc}"}


def load_record(package_path):
    record = {
        "does_asset_exist": False,
        "load_asset_success": False,
        "load_asset_class": None,
        "load_asset_path": None,
        "load_object_success": False,
        "load_object_class": None,
        "load_object_path": None,
        "errors": [],
    }
    try:
        record["does_asset_exist"] = bool(unreal.EditorAssetLibrary.does_asset_exist(package_path))
    except Exception as exc:
        record["errors"].append(f"does_asset_exist: {type(exc).__name__}: {exc}")
    try:
        value = unreal.load_asset(package_path)
        record["load_asset_success"] = value is not None
        record["load_asset_class"] = class_name(value)
        record["load_asset_path"] = value.get_path_name() if value else None
    except Exception as exc:
        record["errors"].append(f"load_asset: {type(exc).__name__}: {exc}")
    try:
        value = unreal.load_object(None, object_path(package_path))
        record["load_object_success"] = value is not None
        record["load_object_class"] = class_name(value)
        record["load_object_path"] = value.get_path_name() if value else None
    except Exception as exc:
        record["errors"].append(f"load_object: {type(exc).__name__}: {exc}")
    return record


def probe_dependency(registry, package_path, expected_class, purpose):
    return {
        "package_path": package_path,
        "object_path": object_path(package_path),
        "purpose": purpose,
        "expected_class": expected_class,
        "registry": asset_data_record(registry, package_path),
        "listing": list_visibility(package_path),
        "load": load_record(package_path),
    }


def scan_pcg(registry):
    attempts = []
    signatures = [
        lambda: registry.scan_paths_synchronous([PCG_TREE_ROOT], True, False),
        lambda: registry.scan_paths_synchronous([PCG_TREE_ROOT], True),
        lambda: registry.scan_paths_synchronous([PCG_TREE_ROOT]),
    ]
    for index, action in enumerate(signatures, 1):
        try:
            action()
            attempts.append({"signature": index, "success": True})
            return attempts
        except Exception as exc:
            attempts.append({"signature": index, "success": False, "error": f"{type(exc).__name__}: {exc}"})
    return attempts


def extent_record(mesh):
    result = {"valid_nonzero_bounds": False, "extent": None, "error": None}
    if mesh is None:
        return result
    try:
        bounds = mesh.get_bounds()
        extent = bounds.box_extent
        values = [float(extent.x), float(extent.y), float(extent.z)]
        result["extent"] = values
        result["valid_nonzero_bounds"] = all(value > 0.0 for value in values)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def vegetation_candidates():
    roots = ["/Game", "/PCG"]
    terms = ("tree", "pine", "oak", "birch", "veget", "foliage", "forest", "shrub", "bush")
    values = []
    for root in roots:
        try:
            assets = unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False)
        except Exception:
            assets = []
        for raw in assets:
            path = str(raw).split(".", 1)[0]
            lower = path.lower()
            if not any(term in lower for term in terms) or "proxy" in lower or path == FORBIDDEN_PROXY:
                continue
            loaded = unreal.load_asset(path)
            if class_name(loaded) != "StaticMesh":
                continue
            bounds = extent_record(loaded)
            values.append({
                "package_path": path,
                "object_path": loaded.get_path_name(),
                "class": class_name(loaded),
                "bounds": bounds,
                "eligible_runtime": bounds["valid_nonzero_bounds"],
                "source_category": "existing_project" if path.startswith("/Game/") else "installed_ue_plugin_content",
            })
    deduped = {item["package_path"]: item for item in values}
    return [deduped[key] for key in sorted(deduped)]


result = {
    "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery01.dependency-probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "error": None,
    "input_hash_before": None,
    "input_hash_after": None,
    "pcg_mount_points": [],
    "pcg_scan_attempts": [],
    "before_scan": [],
    "after_scan": [],
    "vegetation_candidates": [],
    "correction_decision": None,
    "saved_packages": [],
}

try:
    result["input_hash_before"] = sha256(INPUT_MAP)
    if result["input_hash_before"] != EXPECTED_INPUT_HASH:
        raise RuntimeError("Accepted input map hash mismatch before probe")

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        result["pcg_mount_points"] = [str(x) for x in unreal.SystemLibrary.get_package_mount_point(PCG_TREE_ROOT)]
    except Exception:
        result["pcg_mount_points"] = ["/PCG path tested through registry and load APIs"]

    result["before_scan"] = [probe_dependency(registry, *record) for record in DEPENDENCIES]
    result["pcg_scan_attempts"] = scan_pcg(registry)
    result["after_scan"] = [probe_dependency(registry, *record) for record in DEPENDENCIES]
    result["vegetation_candidates"] = vegetation_candidates()

    non_trees = [x for x in result["after_scan"] if not x["purpose"].startswith("tree_")]
    trees = [x for x in result["after_scan"] if x["purpose"].startswith("tree_")]

    def resolved(item):
        loaded = item["load"]
        expected = item["expected_class"]
        actual = loaded["load_asset_class"] or loaded["load_object_class"]
        return (loaded["load_asset_success"] or loaded["load_object_success"]) and actual == expected

    unresolved_non_trees = [x["package_path"] for x in non_trees if not resolved(x)]
    original_trees_resolved = all(resolved(x) for x in trees)
    eligible = [x for x in result["vegetation_candidates"] if x["eligible_runtime"] and x["package_path"] != FORBIDDEN_PROXY]

    if unresolved_non_trees:
        result["correction_decision"] = {"option": None, "reason": "unresolved_nonvegetation_dependencies", "paths": unresolved_non_trees}
        raise RuntimeError("Nonvegetation dependencies remain unresolved")
    if original_trees_resolved:
        result["correction_decision"] = {"option": "A_REGISTRY_INITIALIZATION", "tree_paths": [x["package_path"] for x in trees]}
    elif eligible:
        result["correction_decision"] = {"option": "B_VERIFIED_LOCAL_REPLACEMENT", "tree_paths": [x["package_path"] for x in eligible[:3]]}
    else:
        result["correction_decision"] = {"option": None, "reason": "no_runtime_loadable_nonproxy_vegetation"}
        raise RuntimeError("No eligible runtime-loadable vegetation asset exists")

    result["input_hash_after"] = sha256(INPUT_MAP)
    if result["input_hash_after"] != EXPECTED_INPUT_HASH:
        raise RuntimeError("Accepted input map hash changed during probe")
    result["classification"] = "PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE"
except Exception as exc:
    result["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
    result["input_hash_after"] = sha256(INPUT_MAP) if os.path.isfile(INPUT_MAP) else None
finally:
    os.makedirs(ATTEMPT_ROOT, exist_ok=True)
    with open(RECEIPT_PATH + ".tmp", "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(RECEIPT_PATH + ".tmp", RECEIPT_PATH)
    unreal.log(f"SKYGUARD_DEPENDENCY_PROBE={result['classification']}")

if result["classification"] != "PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY01_FREEZE":
    raise RuntimeError(result["error"]["message"] if result["error"] else "Dependency probe failed")
