import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02\attempt_01"
RESULT_PATH = os.path.join(ATTEMPT_ROOT, "probe_result.json")
ISOLATED_PROJECT = r"D:\SG52T08_ENV01\Skyguard52.uproject"
CANONICAL_PROJECT = r"D:\Skyguard52\Skyguard52.uproject"
CANONICAL_SOURCE_FILE = r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap"
ISOLATED_SOURCE_FILE = r"D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap"
CLONE_FILE = r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype02.umap"
SOURCE_ASSET = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v4"
CLONE_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_WaterLandmassPCG_Prototype02"
CLASS_PROBES = (
    ("/Script/Water.WaterBodyOcean", "Water"),
    ("/Script/LandmassEditor.LandmassActor", "LandmassEditor"),
    (
        "/Script/PCGGeometryScriptInterop.PCGCreateEmptyDynamicMeshSettings",
        "PCGGeometryScriptInterop",
    ),
)
REQUIRED_PLUGINS = (
    "PythonScriptPlugin",
    "EditorScriptingUtilities",
    "PCG",
    "GeometryScripting",
    "PCGGeometryScriptInterop",
    "Water",
    "Landmass",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def descriptor_state():
    with open(ISOLATED_PROJECT, "r", encoding="utf-8-sig") as stream:
        descriptor = json.load(stream)
    states = {
        entry.get("Name"): bool(entry.get("Enabled"))
        for entry in descriptor.get("Plugins", [])
    }
    modules = descriptor.get("Modules", [])
    return {
        "plugin_states": {name: states.get(name, False) for name in REQUIRED_PLUGINS},
        "runtime_modules": modules,
        "skyguard_runtime_module_retained": any(
            entry.get("Name") == "Skyguard52"
            and entry.get("Type") == "Runtime"
            and entry.get("LoadingPhase") == "Default"
            for entry in modules
        ),
    }


result = {
    "schema": "skyguard.toolchain-wave08.environment-clone-smoke-probe.recovery02.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "engine_version": None,
    "project_path": None,
    "plugin_states": {},
    "runtime_modules": [],
    "skyguard_runtime_module_retained": False,
    "class_probes": [],
    "source_asset": SOURCE_ASSET,
    "clone_asset": CLONE_ASSET,
    "source_asset_loaded": False,
    "clone_asset_absent_before": False,
    "clone_asset_created": False,
    "clone_asset_saved": False,
    "clone_asset_loaded_after": False,
    "source_object_path": None,
    "clone_object_path": None,
    "distinct_package_paths": False,
    "canonical_descriptor_sha256_before": sha256(CANONICAL_PROJECT),
    "isolated_descriptor_sha256_before": sha256(ISOLATED_PROJECT),
    "canonical_source_sha256_before": sha256(CANONICAL_SOURCE_FILE),
    "isolated_source_sha256_before": sha256(ISOLATED_SOURCE_FILE),
    "canonical_descriptor_sha256_after": None,
    "isolated_descriptor_sha256_after": None,
    "canonical_source_sha256_after": None,
    "isolated_source_sha256_after": None,
    "clone_file_exists_after": False,
    "clone_file_sha256": None,
    "saved_asset_allowlist": [CLONE_ASSET],
    "source_map_save_attempted": False,
    "canonical_asset_save_attempted": False,
    "environment_authoring_attempted": False,
    "error": None,
}

try:
    result["engine_version"] = unreal.SystemLibrary.get_engine_version()
    result["project_path"] = unreal.Paths.convert_relative_path_to_full(
        unreal.Paths.get_project_file_path()
    )
    result.update(descriptor_state())
    if not all(result["plugin_states"].values()):
        raise RuntimeError("One or more required environment plugins are disabled")
    if not result["skyguard_runtime_module_retained"]:
        raise RuntimeError("Governed Skyguard52 runtime module is not retained")

    for class_path, expected_module in CLASS_PROBES:
        loaded_class = unreal.load_class(None, class_path)
        if loaded_class is None:
            raise RuntimeError(f"Class did not resolve: {class_path}")
        module_name = class_path.split(".", 1)[0].split("/Script/", 1)[1]
        entry = {
            "requested_path": class_path,
            "resolved_name": loaded_class.get_name(),
            "resolved_path": loaded_class.get_path_name(),
            "owning_module": module_name,
            "expected_module": expected_module,
            "module_match": module_name == expected_module,
        }
        result["class_probes"].append(entry)
        if not entry["module_match"]:
            raise RuntimeError(f"Unexpected module for {class_path}: {module_name}")

    if unreal.EditorAssetLibrary.does_asset_exist(CLONE_ASSET):
        raise RuntimeError("Clone asset already exists; namespace reuse is prohibited")
    if os.path.exists(CLONE_FILE):
        raise RuntimeError("Clone map file already exists; namespace reuse is prohibited")
    result["clone_asset_absent_before"] = True

    source_object = unreal.EditorAssetLibrary.load_asset(SOURCE_ASSET)
    if source_object is None:
        raise RuntimeError(f"Unable to load source map asset: {SOURCE_ASSET}")
    result["source_asset_loaded"] = True
    result["source_object_path"] = source_object.get_path_name()

    clone_object = unreal.EditorAssetLibrary.duplicate_asset(SOURCE_ASSET, CLONE_ASSET)
    if clone_object is None:
        raise RuntimeError("Unreal editor asset API failed to duplicate the source map")
    result["clone_asset_created"] = True
    result["clone_object_path"] = clone_object.get_path_name()
    result["distinct_package_paths"] = (
        result["source_object_path"] != result["clone_object_path"]
        and SOURCE_ASSET != CLONE_ASSET
    )
    if not result["distinct_package_paths"]:
        raise RuntimeError("Source and clone did not resolve as distinct packages")

    result["clone_asset_saved"] = bool(
        unreal.EditorAssetLibrary.save_asset(CLONE_ASSET, only_if_is_dirty=False)
    )
    if not result["clone_asset_saved"]:
        raise RuntimeError("Failed to save the isolated cloned map")

    loaded_clone = unreal.EditorAssetLibrary.load_asset(CLONE_ASSET)
    result["clone_asset_loaded_after"] = loaded_clone is not None
    if not result["clone_asset_loaded_after"]:
        raise RuntimeError("Saved clone could not be loaded")

    result["clone_file_exists_after"] = os.path.isfile(CLONE_FILE)
    if not result["clone_file_exists_after"]:
        raise RuntimeError(f"Expected isolated clone file is missing: {CLONE_FILE}")
    result["clone_file_sha256"] = sha256(CLONE_FILE)

    result["canonical_descriptor_sha256_after"] = sha256(CANONICAL_PROJECT)
    result["isolated_descriptor_sha256_after"] = sha256(ISOLATED_PROJECT)
    result["canonical_source_sha256_after"] = sha256(CANONICAL_SOURCE_FILE)
    result["isolated_source_sha256_after"] = sha256(ISOLATED_SOURCE_FILE)
    if result["canonical_descriptor_sha256_before"] != result["canonical_descriptor_sha256_after"]:
        raise RuntimeError("Canonical project descriptor changed")
    if result["isolated_descriptor_sha256_before"] != result["isolated_descriptor_sha256_after"]:
        raise RuntimeError("Isolated project descriptor changed")
    if result["canonical_source_sha256_before"] != result["canonical_source_sha256_after"]:
        raise RuntimeError("Canonical source map changed")
    if result["isolated_source_sha256_before"] != result["isolated_source_sha256_after"]:
        raise RuntimeError("Isolated source map changed")

    result["classification"] = "PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE"
except Exception as exc:
    result["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    for key, path in (
        ("canonical_descriptor_sha256_after", CANONICAL_PROJECT),
        ("isolated_descriptor_sha256_after", ISOLATED_PROJECT),
        ("canonical_source_sha256_after", CANONICAL_SOURCE_FILE),
        ("isolated_source_sha256_after", ISOLATED_SOURCE_FILE),
    ):
        if result[key] is None and os.path.isfile(path):
            result[key] = sha256(path)
    if result["clone_file_sha256"] is None and os.path.isfile(CLONE_FILE):
        result["clone_file_exists_after"] = True
        result["clone_file_sha256"] = sha256(CLONE_FILE)
    temporary_path = RESULT_PATH + ".tmp"
    with open(temporary_path, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary_path, RESULT_PATH)
    print("SKYGUARD_ENVIRONMENT_CLONE_SMOKE=" + result["classification"])

if result["classification"] != "PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE":
    raise RuntimeError(
        result["error"]["message"]
        if result["error"]
        else "Environment clone smoke failed"
    )
