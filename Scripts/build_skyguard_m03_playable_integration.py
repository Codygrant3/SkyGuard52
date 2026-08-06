"""Promote the accepted M03 proxy assembly into a playable candidate map."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = (
    "/Game/Skyguard/Maps/Campaign_v1/"
    "Lvl_M03_ConvoyEscort_Assembly_v1"
)
TARGET_MAP = (
    "/Game/Skyguard/Maps/Campaign_v1/"
    "Lvl_M03_ConvoyEscort_Playable_v1"
)
MISSION_ASSET = (
    "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M03_ConvoyEscort"
)
REPORT = ROOT / "Saved/Reports/M03_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M03_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Accepted M03 source assembly is missing")
    # Duplicate only once. Deleting a loaded/referenced World may remain
    # pending through garbage collection and makes immediate replacement
    # nondeterministic. Reruns update only the governed actors below.
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
            raise RuntimeError("Could not duplicate accepted M03 assembly")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load governed M03 playable map")

    integration_class = require_class(
        "/Script/Skyguard52.SkyguardMission03IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardRoadHunterBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    if not mission:
        raise RuntimeError("M03 mission definition failed to load")

    forbidden = {
        "SkyguardMission03IntegrationDirector",
        "SkyguardYak52Aircraft",
        "SkyguardRoadHunterBoss",
    }
    existing = list(unreal.EditorLevelLibrary.get_all_level_actors())
    assembly_count = 0
    for actor in existing:
        if (
            actor.get_class().get_name()
            == "SkyguardMissionMapAssemblyDirector"
        ):
            assembly_count += 1
            actor.set_editor_property("mission_definition", mission)
            actor.set_editor_property(
                "mission_id",
                mission.get_editor_property("mission_id"),
            )
            weather = mission.get_editor_property("weather")
            actor.set_editor_property(
                "weather_profile_id",
                weather.get_editor_property("profile_id"),
            )
            actor.rebuild_route_spline()
            actor.validate_assembly()
    if assembly_count != 1:
        raise RuntimeError(
            "M03 playable map requires exactly one assembly director"
        )

    for actor in existing:
        if actor.get_class().get_name() in forbidden:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    integration = unreal.EditorLevelLibrary.spawn_actor_from_class(
        integration_class, unreal.Vector()
    )
    integration.set_actor_label(PREFIX + "IntegrationDirector")
    integration.set_editor_property("allow_bounded_actor_spawning", False)

    yak = unreal.EditorLevelLibrary.spawn_actor_from_class(
        yak_class,
        unreal.Vector(0.0, -5000.0, 7000.0),
        unreal.Rotator(0.0, 27.5, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")

    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(70000.0, 45000.0, 6100.0),
        unreal.Rotator(0.0, 210.0, 0.0),
    )
    boss.set_actor_label(PREFIX + "Boss_RoadHunter_Runtime")

    world = unreal.EditorLevelLibrary.get_editor_world()
    world.get_world_settings().set_editor_property(
        "default_game_mode", game_mode_class
    )
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("M03 playable map did not save")

    target_world = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not mission or not target_world:
        raise RuntimeError("M03 mission or target world failed to load")
    mission.set_editor_property("mission_map", target_world)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.PlayableMapGovernance", "Mission03Playable_v1"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("M03 playable-map binding did not save")

    package_file = (
        ROOT
        / "Content/Skyguard/Maps/Campaign_v1/"
        "Lvl_M03_ConvoyEscort_Playable_v1.umap"
    )
    report = {
        "schema": "skyguard.m03-playable-integration-build.v1",
        "gate": "PASS",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "mission_asset": MISSION_ASSET,
        "actors": {
            "integration_director": integration.get_actor_label(),
            "yak_runtime": yak.get_actor_label(),
            "road_hunter_runtime": boss.get_actor_label(),
        },
        "package_sha256": (
            hashlib.sha256(package_file.read_bytes()).hexdigest()
            if package_file.exists()
            else None
        ),
        "content_state": "playable_integration_candidate_with_proxy_environment",
        "limitations": [
            "The accepted M03 proxy assembly remains the source map.",
            "Convoy motion is a native spline anchor; proxy vehicle art is not yet attached as production runtime actors.",
            "Road Hunter uses bounded native gameplay with placeholder geometry.",
            "Possession, rendering, input, audio mix, performance, and packaging need later gates.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM03PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
