"""Fresh-process persistence audit for M06 playable integration."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M06_AirfieldDefense_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M06_AirfieldDefense_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M06_AirfieldDefense"
REPORT = ROOT / "Saved/Reports/M06_PLAYABLE_INTEGRATION_AUDIT.json"
PREFIX = "M06_PLAYABLE_"


def normalize(value):
    return (bool(value[0]), list(value[1])) if isinstance(value, tuple) else (bool(value), [])


def main():
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("M06 playable map failed fresh load")
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    names = [a.get_class().get_name() for a in actors]
    directors = [a for a in actors if a.get_class().get_name() == "SkyguardMission06IntegrationDirector"]
    assemblies = [a for a in actors if a.get_class().get_name() == "SkyguardMissionMapAssemblyDirector"]
    bosses = [a for a in actors if a.get_class().get_name() == "SkyguardRunwayBreakerBoss"]
    governed = [a for a in actors if (a.get_actor_label() or "").startswith(PREFIX)]
    components = []
    if len(directors) == 1:
        components = [c.get_class().get_name() for c in directors[0].get_components_by_class(unreal.ActorComponent)]
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
            str(c.get_editor_property("weak_point_id"))
            for c in bosses[0].get_components_by_class(unreal.SkyguardBossWeakPointComponent)
        )
        debris = int(bosses[0].get_defeat_debris_piece_count())
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    mission_map = str(mission.get_editor_property("mission_map")) if mission else ""
    game_mode = unreal.EditorLevelLibrary.get_editor_world().get_world_settings().get_editor_property("default_game_mode")
    checks = {
        "source_preserved": unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP),
        "target_loaded": True,
        "single_assembly": len(assemblies) == 1,
        "assembly_identity": mission_id == "M06_AirfieldDefense",
        "assembly_valid": valid,
        "single_integration": len(directors) == 1,
        "single_yak": names.count("SkyguardYak52Aircraft") == 1,
        "single_payload_carrier": len(bosses) == 1,
        "three_governed_actors": len(governed) == 3,
        "presentation_components": all(
            item in components
            for item in [
                "SkyguardMissionBriefingComponent",
                "SkyguardAudioDirectorComponent",
                "SkyguardRadioChatterComponent",
            ]
        ),
        "four_physical_weakpoints": weakpoints == sorted(
            ["RunwayRack", "HangarRack", "HeatManifold", "PortEngine"]
        ),
        "bounded_debris": debris == 3,
        "game_mode": bool(game_mode) and game_mode.get_name() == "SkyguardGameMode",
        "mission_map_binding": TARGET_MAP in mission_map,
    }
    report = {
        "schema": "skyguard.m06-playable-integration-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "assembly_errors": [str(e) for e in errors],
        "assembly_readiness": assembly_readiness,
        "weakpoints": weakpoints,
        "limitations": [
            "Persistence is not PIE, rendering, input, performance, or packaging proof.",
            "Airfield and boss remain proxy art.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM06PlayableAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("M06 playable persistence audit failed")


if __name__ == "__main__":
    main()
