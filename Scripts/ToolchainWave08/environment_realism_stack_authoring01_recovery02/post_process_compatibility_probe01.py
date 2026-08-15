import hashlib
import json
import os
import traceback

import unreal


ATTEMPT_ROOT = r"D:\Skyguard52\Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY02_POST_PROCESS_COMPATIBILITY_PROBE01\attempt_01"
RECEIPT_PATH = os.path.join(ATTEMPT_ROOT, "probe_receipt.json")
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


def try_property(value, name, setting):
    row = {"property": name, "setting": str(setting), "supported": False, "readback": None, "error": None}
    try:
        original = value.get_editor_property(name)
        value.set_editor_property(name, setting)
        row["readback"] = str(value.get_editor_property(name))
        value.set_editor_property(name, original)
        row["supported"] = True
    except Exception as exc:
        row["error"] = str(exc)
    return row


receipt = {
    "schema": "skyguard.m01-environment-realism-stack-authoring01-recovery02-post-process-compatibility-probe01.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "map_asset": MAP_ASSET,
    "map_sha256_before": None,
    "map_sha256_after": None,
    "map_unchanged": False,
    "world_saved": False,
    "spawned_actor_destroyed": False,
    "post_process_volume_candidates": [],
    "post_process_settings_properties": [],
    "accepted_post_process_volume_property": None,
    "error": None,
}

post = None
actors = None
try:
    require(os.path.isfile(MAP_FILE), "Accepted input map is missing")
    receipt["map_sha256_before"] = sha256(MAP_FILE)
    require(receipt["map_sha256_before"] == EXPECTED_MAP_SHA256, "Accepted input map hash mismatch")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels and levels.load_level(MAP_ASSET), "Accepted input map failed to load")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(actors is not None, "EditorActorSubsystem is unavailable")
    post = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0.0, 0.0, -100000.0), unreal.Rotator(0.0, 0.0, 0.0), transient=True)
    require(post is not None, "Transient PostProcessVolume failed to spawn")
    post.set_actor_label("M01_RS01_PostProcessCompatibilityProbe")

    for candidate in ("b_unbound", "unbound"):
        receipt["post_process_volume_candidates"].append(try_property(post, candidate, True))
    supported_candidates = [row["property"] for row in receipt["post_process_volume_candidates"] if row["supported"]]
    require(supported_candidates == ["unbound"], f"Unexpected PostProcessVolume Python property resolution: {supported_candidates}")
    receipt["accepted_post_process_volume_property"] = "unbound"

    settings = post.get_editor_property("settings")
    required_settings = (
        ("override_auto_exposure_method", True),
        ("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
        ("override_auto_exposure_bias", True),
        ("auto_exposure_bias", 0.5),
        ("override_bloom_intensity", True),
        ("bloom_intensity", 0.15),
        ("override_vignette_intensity", True),
        ("vignette_intensity", 0.18),
    )
    for name, setting in required_settings:
        receipt["post_process_settings_properties"].append(try_property(settings, name, setting))
    failures = [row for row in receipt["post_process_settings_properties"] if not row["supported"]]
    require(not failures, f"Unsupported PostProcessSettings properties: {[row['property'] for row in failures]}")

    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.5)
    settings.set_editor_property("override_bloom_intensity", True)
    settings.set_editor_property("bloom_intensity", 0.15)
    settings.set_editor_property("override_vignette_intensity", True)
    settings.set_editor_property("vignette_intensity", 0.18)
    post.set_editor_property("unbound", True)
    post.set_editor_property("settings", settings)
    require(bool(post.get_editor_property("unbound")), "PostProcessVolume unbound readback failed")
    applied = post.get_editor_property("settings")
    require(str(applied.get_editor_property("auto_exposure_method")) == str(unreal.AutoExposureMethod.AEM_MANUAL), "Manual exposure readback failed")
    receipt["classification"] = "PASSED_POST_PROCESS_PYTHON_COMPATIBILITY_READY_FOR_AUTHORING_RECOVERY02"
except Exception as exc:
    receipt["error"] = {"message": str(exc), "traceback": traceback.format_exc()}
finally:
    if post is not None and actors is not None:
        try:
            receipt["spawned_actor_destroyed"] = bool(actors.destroy_actor(post))
        except Exception as exc:
            receipt["spawned_actor_destroyed"] = False
            if receipt["error"] is None:
                receipt["error"] = {"message": f"Transient actor cleanup failed: {exc}", "traceback": traceback.format_exc()}
                receipt["classification"] = "FAILED_WITH_EVIDENCE"
    if os.path.isfile(MAP_FILE):
        receipt["map_sha256_after"] = sha256(MAP_FILE)
        receipt["map_unchanged"] = receipt["map_sha256_after"] == receipt["map_sha256_before"]
    if not receipt["map_unchanged"] or not receipt["spawned_actor_destroyed"]:
        receipt["classification"] = "FAILED_WITH_EVIDENCE"
    write_json_atomic(RECEIPT_PATH, receipt)
    print("SKYGUARD_POST_PROCESS_COMPATIBILITY_PROBE01=" + receipt["classification"])
