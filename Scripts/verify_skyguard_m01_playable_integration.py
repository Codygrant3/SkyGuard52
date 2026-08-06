"""Fresh-process persistence audit for Mission 1 playable integration."""

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
REPORT = ROOT / "Saved/Reports/M01_PLAYABLE_INTEGRATION_AUDIT.json"
PREFIX = "M01_PLAYABLE_"


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError("Playable map is missing")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("Playable map failed fresh-process load")

    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    labels = [actor.get_actor_label() or "" for actor in actors]
    class_names = [actor.get_class().get_name() for actor in actors]
    governed = [actor for actor in actors if (actor.get_actor_label() or "").startswith(PREFIX)]
    directors = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission01IntegrationDirector"
    ]
    environments = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission01EnvironmentDirector"
    ]

    component_names = []
    if len(directors) == 1:
        component_names = [
            component.get_class().get_name()
            for component in directors[0].get_components_by_class(
                unreal.ActorComponent
            )
        ]

    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    mission_map = str(mission.get_editor_property("mission_map")) if mission else ""
    world_settings = unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    game_mode = world_settings.get_editor_property("default_game_mode")
    game_mode_name = game_mode.get_name() if game_mode else ""

    checks = {
        "source_map_preserved": unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP),
        "target_map_fresh_loaded": True,
        "exact_one_integration_director": len(directors) == 1,
        "exact_one_environment_director": len(environments) == 1,
        "exact_one_native_yak": class_names.count("SkyguardYak52Aircraft") == 1,
        "exact_one_native_pathfinder": class_names.count("SkyguardPathfinderBoss") == 1,
        "preview_pathfinder_removed": "M01_P4_Boss_Pathfinder" not in labels,
        "three_governed_runtime_actors": len(governed) == 3,
        "briefing_component_present": (
            "SkyguardMissionBriefingComponent" in component_names
        ),
        "audio_director_present": (
            "SkyguardAudioDirectorComponent" in component_names
        ),
        "radio_chatter_present": (
            "SkyguardRadioChatterComponent" in component_names
        ),
        "game_mode_is_skyguard": game_mode_name == "SkyguardGameMode",
        "mission_dataasset_bound_to_playable_map": TARGET_MAP in mission_map,
    }
    report = {
        "schema": "skyguard.m01-playable-integration-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "checks": checks,
        "governed_actor_labels": sorted(
            actor.get_actor_label() for actor in governed
        ),
        "director_component_classes": sorted(component_names),
        "mission_map_reference": mission_map,
        "game_mode": game_mode_name,
        "limitations": [
            "Fresh-process persistence is not a PIE or packaged gameplay test.",
            "Player possession, mouse input, ADS, rifle, and Igla require runtime validation.",
            "Radio lines are subtitle-ready; voiced audio assignment is not asserted.",
            "No rendered claim is made for final Pathfinder or Yak visual fidelity.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM01PlayableAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 playable persistence audit failed")


if __name__ == "__main__":
    main()
