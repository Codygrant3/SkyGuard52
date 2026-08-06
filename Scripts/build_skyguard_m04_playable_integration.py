"""Promote the accepted M04 assembly into a separate playable candidate."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M04_NightBlackout_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M04_NightBlackout_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M04_NightBlackout"
REPORT = ROOT / "Saved/Reports/M04_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M04_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Accepted M04 source assembly is missing")
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
            raise RuntimeError("Could not duplicate accepted M04 assembly")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load M04 playable duplicate")

    director_class = require_class(
        "/Script/Skyguard52.SkyguardMission04IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardBlackKiteBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    if not mission:
        raise RuntimeError("M04 mission definition failed to load")
    forbidden = {
        "SkyguardMission04IntegrationDirector",
        "SkyguardYak52Aircraft",
        "SkyguardBlackKiteBoss",
    }
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    assemblies = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMissionMapAssemblyDirector"
    ]
    if len(assemblies) != 1:
        raise RuntimeError("M04 playable map requires one assembly director")
    weather = mission.get_editor_property("weather")
    assemblies[0].set_editor_property(
        "weather_profile_id",
        weather.get_editor_property("profile_id"),
    )
    for actor in actors:
        if actor.get_class().get_name() in forbidden:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector()
    )
    director.set_actor_label(PREFIX + "IntegrationDirector")
    director.set_editor_property("allow_bounded_actor_spawning", False)
    yak = unreal.EditorLevelLibrary.spawn_actor_from_class(
        yak_class,
        unreal.Vector(0.0, 12000.0, 5800.0),
        unreal.Rotator(0.0, -12.0, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")
    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(69000.0, -11000.0, 5200.0),
        unreal.Rotator(0.0, 170.0, 0.0),
    )
    boss.set_actor_label(PREFIX + "Boss_BlackKite_Runtime")
    world_settings = (
        unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    )
    world_settings.set_editor_property("default_game_mode", game_mode_class)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("M04 playable map did not save")

    target = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not target:
        raise RuntimeError("M04 mission or target world failed to load")
    mission.set_editor_property("mission_map", target)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.PlayableMapGovernance", "Mission04Playable_v1"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("M04 mission map binding did not save")

    package = (
        ROOT
        / "Content/Skyguard/Maps/Campaign_v1/"
        "Lvl_M04_NightBlackout_Playable_v1.umap"
    )
    report = {
        "schema": "skyguard.m04-playable-integration-build.v1",
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
            "Blackout city, searchlight batteries and Black Kite use proxy visual art.",
            "Native timing/state tests do not prove rendered playability or performance.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM04PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
