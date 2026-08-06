"""Fresh-process persistence audit for M04 playable integration."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M04_NightBlackout_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M04_NightBlackout_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M04_NightBlackout"
REPORT = ROOT / "Saved/Reports/M04_PLAYABLE_INTEGRATION_AUDIT.json"
PREFIX = "M04_PLAYABLE_"


def normalize(value):
    return (
        (bool(value[0]), list(value[1]))
        if isinstance(value, tuple)
        else (bool(value), [])
    )


def main():
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("M04 playable map failed fresh load")
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    names = [actor.get_class().get_name() for actor in actors]
    directors = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission04IntegrationDirector"
    ]
    assemblies = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMissionMapAssemblyDirector"
    ]
    bosses = [
        actor
        for actor in actors
        if actor.get_class().get_name() == "SkyguardBlackKiteBoss"
    ]
    governed = [
        actor
        for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    component_names = []
    if len(directors) == 1:
        component_names = [
            component.get_class().get_name()
            for component in directors[0].get_components_by_class(
                unreal.ActorComponent
            )
        ]
    valid, errors, mission_id = False, [], ""
    assembly_readiness = {}
    if len(assemblies) == 1:
        mission_id = str(assemblies[0].get_editor_property("mission_id"))
        _, errors = normalize(assemblies[0].validate_assembly())
        readiness = assemblies[0].get_editor_property("readiness")
        assembly_readiness = {
            "definition_valid": bool(
                readiness.get_editor_property("definition_valid")
            ),
            "route_matches_definition": bool(
                readiness.get_editor_property("route_matches_definition")
            ),
            "required_objectives_anchored": bool(
                readiness.get_editor_property("required_objectives_anchored")
            ),
            "weather_matches_definition": bool(
                readiness.get_editor_property("weather_matches_definition")
            ),
            "landmarks_distinct": bool(
                readiness.get_editor_property("landmarks_distinct")
            ),
        }
        valid = all(assembly_readiness.values())
    weakpoints, debris = [], 0
    if len(bosses) == 1:
        weakpoints = sorted(
            str(component.get_editor_property("weak_point_id"))
            for component in bosses[0].get_components_by_class(
                unreal.SkyguardBossWeakPointComponent
            )
        )
        debris = int(bosses[0].get_defeat_debris_piece_count())
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    mission_map = (
        str(mission.get_editor_property("mission_map")) if mission else ""
    )
    game_mode = (
        unreal.EditorLevelLibrary.get_editor_world()
        .get_world_settings()
        .get_editor_property("default_game_mode")
    )
    checks = {
        "source_preserved": unreal.EditorAssetLibrary.does_asset_exist(
            SOURCE_MAP
        ),
        "target_loaded": True,
        "single_assembly": len(assemblies) == 1,
        "assembly_identity": mission_id == "M04_NightBlackout",
        "assembly_valid": valid,
        "single_integration": len(directors) == 1,
        "single_yak": names.count("SkyguardYak52Aircraft") == 1,
        "single_black_kite": len(bosses) == 1,
        "three_governed_actors": len(governed) == 3,
        "presentation_components": all(
            item in component_names
            for item in [
                "SkyguardMissionBriefingComponent",
                "SkyguardAudioDirectorComponent",
                "SkyguardRadioChatterComponent",
            ]
        ),
        "paired_searchlights": component_names.count("SpotLightComponent")
        == 2,
        "four_physical_weakpoints": weakpoints
        == sorted(
            [
                "PortNavigationVane",
                "StarboardNavigationVane",
                "Jammer",
                "PowerBus",
            ]
        ),
        "bounded_debris": debris == 3,
        "game_mode": bool(game_mode)
        and game_mode.get_name() == "SkyguardGameMode",
        "mission_map_binding": TARGET_MAP in mission_map,
    }
    report = {
        "schema": "skyguard.m04-playable-integration-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "assembly_errors": [str(error) for error in errors],
        "assembly_readiness": assembly_readiness,
        "weakpoints": weakpoints,
        "limitations": [
            "Persistence is not PIE, rendering, input, performance, or packaging proof.",
            "Blackout city, searchlight batteries and boss remain proxy art.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM04PlayableAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("M04 playable persistence audit failed")


if __name__ == "__main__":
    main()
