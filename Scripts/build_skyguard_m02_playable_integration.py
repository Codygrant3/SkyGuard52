"""Promote the accepted M02 proxy assembly into a playable candidate map."""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = (
    "/Game/Skyguard/Maps/Campaign_v1/"
    "Lvl_M02_HarborShield_Assembly_v1"
)
TARGET_MAP = (
    "/Game/Skyguard/Maps/Campaign_v1/"
    "Lvl_M02_HarborShield_Playable_v1"
)
MISSION_ASSET = (
    "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M02_HarborShield"
)
REPORT = ROOT / "Saved/Reports/M02_PLAYABLE_INTEGRATION_BUILD.json"
PREFIX = "M02_PLAYABLE_"


def require_class(path):
    value = unreal.load_class(None, path)
    if not value:
        raise RuntimeError("Missing native class: " + path)
    return value


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP):
        raise RuntimeError("Accepted M02 source assembly is missing: " + SOURCE_MAP)

    # Duplicate only once. Force-deleting a referenced World can remain pending
    # until garbage collection, making an immediate duplicate nondeterministic
    # in commandlet runs. Subsequent governed runs instead load the persisted
    # target and replace only the owned runtime actors below.
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        if not unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, TARGET_MAP):
            raise RuntimeError("Could not duplicate accepted M02 assembly")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Could not load governed M02 playable map")

    integration_class = require_class(
        "/Script/Skyguard52.SkyguardMission02IntegrationDirector"
    )
    yak_class = require_class("/Script/Skyguard52.SkyguardYak52Aircraft")
    boss_class = require_class("/Script/Skyguard52.SkyguardBreakwaterBoss")
    game_mode_class = require_class("/Script/Skyguard52.SkyguardGameMode")
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    if not mission:
        raise RuntimeError("M02 mission definition failed to load")

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
            "M02 playable map requires exactly one assembly director"
        )

    forbidden_classes = {
        "SkyguardMission02IntegrationDirector",
        "SkyguardYak52Aircraft",
        "SkyguardBreakwaterBoss",
    }
    for actor in existing:
        if actor.get_class().get_name() in forbidden_classes:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    integration = unreal.EditorLevelLibrary.spawn_actor_from_class(
        integration_class, unreal.Vector()
    )
    integration.set_actor_label(PREFIX + "IntegrationDirector")
    integration.set_editor_property("allow_bounded_actor_spawning", False)

    yak = unreal.EditorLevelLibrary.spawn_actor_from_class(
        yak_class,
        unreal.Vector(0.0, 26000.0, 5200.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    yak.set_actor_label(PREFIX + "Yak52_Runtime")

    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_class,
        unreal.Vector(65000.0, -8000.0, 4300.0),
        unreal.Rotator(0.0, 180.0, 0.0),
    )
    boss.set_actor_label(PREFIX + "Boss_Breakwater_Runtime")

    world = unreal.EditorLevelLibrary.get_editor_world()
    world.get_world_settings().set_editor_property(
        "default_game_mode", game_mode_class
    )
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("M02 playable map did not save")

    target_world = unreal.EditorAssetLibrary.load_asset(TARGET_MAP)
    if not mission or not target_world:
        raise RuntimeError("M02 mission definition or target world failed to load")
    mission.set_editor_property("mission_map", target_world)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission,
        "Skyguard.PlayableMapGovernance",
        "Mission02Playable_v1",
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("M02 DataAsset playable-map binding did not save")

    package_file = (
        ROOT
        / "Content/Skyguard/Maps/Campaign_v1/"
        "Lvl_M02_HarborShield_Playable_v1.umap"
    )
    report = {
        "schema": "skyguard.m02-playable-integration-build.v1",
        "gate": "PASS",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "mission_asset": MISSION_ASSET,
        "actors": {
            "integration_director": integration.get_actor_label(),
            "yak_runtime": yak.get_actor_label(),
            "breakwater_runtime": boss.get_actor_label(),
        },
        "package_sha256": (
            hashlib.sha256(package_file.read_bytes()).hexdigest()
            if package_file.exists()
            else None
        ),
        "content_state": "playable_integration_candidate_with_proxy_environment",
        "limitations": [
            "The accepted M02 proxy assembly is preserved as the source map.",
            "Breakwater uses bounded native gameplay with placeholder visual meshes.",
            "Player possession, input, rendering, audio mix, performance, and packaging require later runtime gates.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM02PlayableBuild] " + json.dumps(report))


if __name__ == "__main__":
    main()
