"""Idempotently compose the accepted Mission 1 systems into a playable map."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = (
    "/Game/Skyguard/Maps/"
    "Lvl_M01_CoastalIntercept_ProductionEnvironment_v4_attempt02"
)
TARGET_MAP = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"
MISSION_ASSET = (
    "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept"
)
REPORT = ROOT / "Saved/Reports/M01_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M01_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Accepted source map is missing: " + SOURCE_MAP)

    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.delete_asset(TARGET_MAP):
            raise RuntimeError("Could not replace governed target map")
    if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
        raise RuntimeError("Could not duplicate accepted source map")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load duplicated playable map")

    integration_class = require_class(
        "/Script/Skyguard52.SkyguardMission01IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardPathfinderBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")

    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    preview_bosses = [
        actor
        for actor in actors
        if (actor.get_actor_label() or "") == "M01_P4_Boss_Pathfinder"
    ]
    boss_location = (
        preview_bosses[0].get_actor_location()
        if preview_bosses
        else unreal.Vector(56000.0, -7800.0, 6100.0)
    )
    boss_rotation = (
        preview_bosses[0].get_actor_rotation()
        if preview_bosses
        else unreal.Rotator(0.0, 180.0, 0.0)
    )
    boss_scale = (
        preview_bosses[0].get_actor_scale3d()
        if preview_bosses
        else unreal.Vector(1.0, 1.0, 1.0)
    )
    for actor in preview_bosses:
        unreal.EditorLevelLibrary.destroy_actor(actor)

    integration = unreal.EditorLevelLibrary.spawn_actor_from_class(
        integration_class, unreal.Vector(0.0, 0.0, 0.0)
    )
    integration.set_actor_label(PREFIX + "IntegrationDirector")

    yak = unreal.EditorLevelLibrary.spawn_actor_from_class(
        yak_class,
        unreal.Vector(0.0, -18000.0, 6500.0),
        unreal.Rotator(0.0, 5.4, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")

    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        boss_location,
        boss_rotation,
    )
    boss.set_actor_scale3d(boss_scale)
    boss.set_actor_label(PREFIX + "Boss_Pathfinder_Runtime")

    world = unreal.EditorLevelLibrary.get_editor_world()
    world.get_world_settings().set_editor_property(
        "default_game_mode", game_mode_class
    )
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Playable map did not save")

    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    target_world = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not mission or not target_world:
        raise RuntimeError("Mission definition or target world failed to load")
    mission.set_editor_property("mission_map", target_world)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.PlayableMapGovernance", "Mission01Playable_v1"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("Mission DataAsset map binding did not save")

    package_file = ROOT / "Content/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1.umap"
    report = {
        "schema": "skyguard.m01-playable-integration-build.v1",
        "gate": "PASS",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "mission_asset": MISSION_ASSET,
        "actors": {
            "integration_director": integration.get_actor_label(),
            "yak_runtime": yak.get_actor_label(),
            "pathfinder_runtime": boss.get_actor_label(),
        },
        "package_sha256": (
            hashlib.sha256(package_file.read_bytes()).hexdigest()
            if package_file.exists()
            else None
        ),
        "limitations": [
            "Builder composition does not prove player possession or input.",
            "Rendered GPU review and packaged runtime validation remain pending.",
            "Native Pathfinder art is not asserted as the final refined hero mesh.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM01PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
