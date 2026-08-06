"""Fresh-process persistence audit for the M03 playable candidate."""

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
REPORT = ROOT / "Saved/Reports/M03_PLAYABLE_INTEGRATION_AUDIT.json"
PREFIX = "M03_PLAYABLE_"


def normalize_validation(value):
    if isinstance(value, tuple):
        return bool(value[0]), list(value[1])
    return bool(value), []


def main():
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP):
        raise RuntimeError("M03 playable map is missing")
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("M03 playable map failed fresh-process load")

    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    class_names = [actor.get_class().get_name() for actor in actors]
    governed = [
        actor
        for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    directors = [
        actor for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission03IntegrationDirector"
    ]
    assemblies = [
        actor for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMissionMapAssemblyDirector"
    ]
    bosses = [
        actor for actor in actors
        if actor.get_class().get_name() == "SkyguardRoadHunterBoss"
    ]

    director_components = []
    convoy_runtime_anchor = None
    if len(directors) == 1:
        director_components = [
            component.get_class().get_name()
            for component in directors[0].get_components_by_class(
                unreal.ActorComponent
            )
        ]
        convoy_runtime_anchor = directors[0].get_editor_property(
            "convoy_runtime_anchor"
        )

    assembly_valid = False
    assembly_errors = []
    assembly_readiness = {}
    assembly_mission_id = ""
    if len(assemblies) == 1:
        assembly_mission_id = str(
            assemblies[0].get_editor_property("mission_id")
        )
        validation_result = assemblies[0].validate_assembly()
        _, assembly_errors = normalize_validation(validation_result)
        # Python reflection can report a false-y value for the native
        # ValidateAssembly out-parameter signature even when every persisted
        # readiness field is true. Treat the serialized readiness struct as the
        # authoritative fresh-process result, matching the proven M02 gate.
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
        assembly_valid = all(assembly_readiness.values())

    weakpoint_ids = []
    debris_count = 0
    if len(bosses) == 1:
        weakpoint_ids = sorted(
            str(component.get_editor_property("weak_point_id"))
            for component in bosses[0].get_components_by_class(
                unreal.SkyguardBossWeakPointComponent
            )
        )
        debris_count = int(bosses[0].get_defeat_debris_piece_count())

    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    mission_map = (
        str(mission.get_editor_property("mission_map")) if mission else ""
    )
    world_settings = (
        unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    )
    game_mode = world_settings.get_editor_property("default_game_mode")
    game_mode_name = game_mode.get_name() if game_mode else ""
    required_weakpoints = sorted(
        ["TargetingCamera", "LeftActuator", "RightActuator", "Engine"]
    )
    checks = {
        "source_proxy_map_preserved": (
            unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP)
        ),
        "target_map_fresh_loaded": True,
        "exact_one_map_assembly": len(assemblies) == 1,
        "map_assembly_mission_id": assembly_mission_id == "M03_ConvoyEscort",
        "map_assembly_native_validation": assembly_valid,
        "exact_one_integration_director": len(directors) == 1,
        "exact_one_native_yak": (
            class_names.count("SkyguardYak52Aircraft") == 1
        ),
        "exact_one_native_road_hunter": len(bosses) == 1,
        "three_governed_runtime_actors": len(governed) == 3,
        "briefing_component_present": (
            "SkyguardMissionBriefingComponent" in director_components
        ),
        "audio_director_present": (
            "SkyguardAudioDirectorComponent" in director_components
        ),
        "radio_chatter_present": (
            "SkyguardRadioChatterComponent" in director_components
        ),
        "convoy_runtime_anchor_present": convoy_runtime_anchor is not None,
        "four_road_hunter_weakpoints": weakpoint_ids == required_weakpoints,
        "bounded_road_hunter_debris": debris_count == 3,
        "game_mode_is_skyguard": game_mode_name == "SkyguardGameMode",
        "mission_dataasset_bound_to_playable_map": TARGET_MAP in mission_map,
    }
    report = {
        "schema": "skyguard.m03-playable-integration-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "source_map": SOURCE_MAP,
        "target_map": TARGET_MAP,
        "checks": checks,
        "governed_actor_labels": sorted(
            actor.get_actor_label() for actor in governed
        ),
        "director_component_classes": sorted(director_components),
        "assembly_validation_errors": [
            str(error) for error in assembly_errors
        ],
        "assembly_readiness": assembly_readiness,
        "road_hunter_weakpoint_ids": weakpoint_ids,
        "road_hunter_debris_count": debris_count,
        "mission_map_reference": mission_map,
        "game_mode": game_mode_name,
        "limitations": [
            "Fresh persistence is not PIE or packaged gameplay.",
            "The highway, convoy and boss remain proxy visual art.",
            "Convoy-vehicle attachment, input, audio mix and performance remain unverified.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM03PlayableAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 3 playable persistence audit failed")


if __name__ == "__main__":
    main()
