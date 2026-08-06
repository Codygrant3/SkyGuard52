"""Structural audit for the isolated L88 Unreal validation map."""

import hashlib
import json
import os
from pathlib import Path

import unreal


MAP_PATH = "/Game/Skyguard/Maps/Lvl_Yak52_L88_Validation_v2"
MESH_FOLDER = "/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout"
SOURCE = Path(r"D:\Skyguard52\Content\Skyguard\Meshes\Source\L88\yak52_l88_silhouette_blockout.glb")
REPORT = Path(r"D:\Skyguard52\Saved\Reports\L88_VALIDATION_IMPORT.json")


def log(message):
    unreal.log("[SkyguardL88Audit] " + str(message))


def main():
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    labels = []
    class_counts = {}
    for actor in actors:
        label = actor.get_actor_label() or actor.get_name()
        labels.append(label)
        class_name = actor.get_class().get_name()
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    validation_mesh_actors = [
        label for label in labels
        if label.startswith("L88_Validation_") and label != "L88_Validation_Floor"
    ]
    forbidden = [
        label for label in labels
        if label.startswith(("AAA_", "L52_", "L86_", "L87_", "WebGame_"))
    ]
    imported_assets = unreal.EditorAssetLibrary.list_assets(MESH_FOLDER, True, False)
    static_mesh_assets = []
    for path in imported_assets:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            static_mesh_assets.append(path)

    source_bytes = SOURCE.read_bytes() if SOURCE.is_file() else b""
    source_hash = hashlib.sha256(source_bytes).hexdigest() if source_bytes else None

    result = {
        "map": MAP_PATH,
        "actor_count": len(actors),
        "validation_mesh_actor_count": len(validation_mesh_actors),
        "static_mesh_asset_count": len(static_mesh_assets),
        "static_mesh_assets": sorted(static_mesh_assets),
        "source_glb": str(SOURCE),
        "source_glb_bytes": len(source_bytes),
        "source_glb_sha256": source_hash,
        "class_counts": class_counts,
        "forbidden_legacy_labels": forbidden,
        "has_floor": "L88_Validation_Floor" in labels,
        "has_beauty_camera": "L88_Cam_Beauty" in labels,
        "has_rear_cockpit_camera": "L88_Cam_RearCockpit" in labels,
        "has_ads_camera": "L88_Cam_ADS" in labels,
        "gate": "PASS" if (
            len(validation_mesh_actors) == len(static_mesh_assets)
            and len(static_mesh_assets) >= 60
            and not forbidden
            and "L88_Validation_Floor" in labels
            and "L88_Cam_RearCockpit" in labels
            and "L88_Cam_ADS" in labels
        ) else "FAIL",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    log(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
