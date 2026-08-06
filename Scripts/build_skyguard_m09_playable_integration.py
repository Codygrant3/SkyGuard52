"""Promote the preserved M09 assembly into a separate playable candidate."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M09_SaturationAttack"
REPORT = ROOT / "Saved/Reports/M09_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M09_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Preserved M09 assembly is missing")
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
            raise RuntimeError("Could not duplicate the M09 assembly")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load M09 playable candidate")

    director_class = require_class(
        "/Script/Skyguard52.SkyguardMission09IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardIronRainBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")
    forbidden = {
        "SkyguardMission09IntegrationDirector",
        "SkyguardYak52Aircraft",
        "SkyguardIronRainBoss",
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
        unreal.Vector(0.0, -10000.0, 8800.0),
        unreal.Rotator(0.0, 28.0, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")
    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(72000.0, 8000.0, 7600.0),
        unreal.Rotator(0.0, 198.0, 0.0),
    )
    boss.set_actor_label(PREFIX + "Boss_IronRain_Runtime")
    world_settings = (
        unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    )
    world_settings.set_editor_property("default_game_mode", game_mode_class)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("M09 playable map did not save")

    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    target = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not mission or not target:
        raise RuntimeError("M09 mission or playable world failed to load")
    mission.set_editor_property("mission_map", target)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.PlayableMapGovernance", "Mission09Playable_v1"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("M09 mission binding did not save")

    package = (
        ROOT
        / "Content/Skyguard/Maps/Campaign_v1/"
        "Lvl_M09_SaturationAttack_Playable_v1.umap"
    )
    report = {
        "schema": "skyguard.m09-playable-integration-build.v1",
        "gate": "PASS",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "source_preserved": unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP),
        "actors": [
            director.get_actor_label(),
            yak.get_actor_label(),
            boss.get_actor_label(),
        ],
        "performance_contract": {
            "wave_counts": [8, 12, 16],
            "max_active_threats": 24,
            "pool_capacity": 48,
            "max_active_decoys": 12,
            "max_simultaneous_explosions": 6,
            "boss_breakup_pieces": 3,
            "runtime_spawning_in_composed_map": False,
        },
        "package_sha256": (
            hashlib.sha256(package.read_bytes()).hexdigest()
            if package.exists()
            else None
        ),
        "limitations": [
            "Dense skyline, power station, bridge and boss retain proxy visual art.",
            "This build report is not PIE, render, input, performance, cook or package proof.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM09PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
