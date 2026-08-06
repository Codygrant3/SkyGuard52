"""Promote the accepted M06 assembly into a separate playable candidate."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M06_AirfieldDefense_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M06_AirfieldDefense_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M06_AirfieldDefense"
REPORT = ROOT / "Saved/Reports/M06_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M06_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Accepted M06 source assembly is missing")
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
            raise RuntimeError("Could not duplicate accepted M06 assembly")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load M06 playable duplicate")

    director_class = require_class(
        "/Script/Skyguard52.SkyguardMission06IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardRunwayBreakerBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")
    forbidden = {
        "SkyguardMission06IntegrationDirector",
        "SkyguardYak52Aircraft",
        "SkyguardRunwayBreakerBoss",
    }
    for actor in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        if actor.get_class().get_name() in forbidden:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector()
    )
    director.set_actor_label(PREFIX + "IntegrationDirector")
    director.set_editor_property("allow_bounded_actor_spawning", False)
    yak = unreal.EditorLevelLibrary.spawn_actor_from_class(
        yak_class,
        unreal.Vector(0.0, 18000.0, 6600.0),
        unreal.Rotator(0.0, -18.0, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")
    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(78000.0, 22000.0, 6000.0),
        unreal.Rotator(0.0, 180.0, 0.0),
    )
    boss.set_actor_label(PREFIX + "Boss_RunwayBreaker_Runtime")
    unreal.EditorLevelLibrary.get_editor_world().get_world_settings().set_editor_property(
        "default_game_mode", game_mode_class
    )
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("M06 playable map did not save")

    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    target = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not mission or not target:
        raise RuntimeError("M06 mission or target world failed to load")
    mission.set_editor_property("mission_map", target)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.PlayableMapGovernance", "Mission06Playable_v1"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("M06 mission map binding did not save")

    package = (
        ROOT
        / "Content/Skyguard/Maps/Campaign_v1/"
        "Lvl_M06_AirfieldDefense_Playable_v1.umap"
    )
    report = {
        "schema": "skyguard.m06-playable-integration-build.v1",
        "gate": "PASS",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "actors": [
            director.get_actor_label(),
            yak.get_actor_label(),
            boss.get_actor_label(),
        ],
        "package_sha256": (
            hashlib.sha256(package.read_bytes()).hexdigest()
            if package.exists()
            else None
        ),
        "limitations": [
            "Airfield and payload carrier remain proxy visual art.",
            "Native timing/state tests do not prove rendered playability or performance.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM06PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
