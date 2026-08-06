"""Fresh-process persistence and bounded-density audit for M09."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1"
TARGET_MAP = "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Playable_v1"
MISSION_ASSET = "/Game/Skyguard/Data/Campaign_v1/DA_Mission_M09_SaturationAttack"
REPORT = ROOT / "Saved/Reports/M09_PLAYABLE_INTEGRATION_AUDIT.json"
PREFIX = "M09_PLAYABLE_"


def normalize(value):
    return (
        (bool(value[0]), list(value[1]))
        if isinstance(value, tuple)
        else (bool(value), [])
    )


def main():
    if not unreal.EditorLevelLibrary.load_level(TARGET_MAP):
        raise RuntimeError("M09 playable map failed fresh load")
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    names = [actor.get_class().get_name() for actor in actors]
    directors = [
        actor for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission09IntegrationDirector"
    ]
    assemblies = [
        actor for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMissionMapAssemblyDirector"
    ]
    bosses = [
        actor for actor in actors
        if actor.get_class().get_name() == "SkyguardIronRainBoss"
    ]
    governed = [
        actor for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]

    mission_id, errors, route_points, roles = "", [], [], []
    readiness = {}
    if len(assemblies) == 1:
        mission_id = str(assemblies[0].get_editor_property("mission_id"))
        _, errors = normalize(assemblies[0].validate_assembly())
        route_points = list(assemblies[0].get_editor_property("route_points"))
        roles = [
            str(anchor.get_editor_property("role"))
            for anchor in assemblies[0].get_editor_property("landmark_anchors")
        ]
        value = assemblies[0].get_editor_property("readiness")
        readiness = {
            "definition_valid": bool(value.get_editor_property("definition_valid")),
            "route_matches_definition": bool(
                value.get_editor_property("route_matches_definition")
            ),
            "required_objectives_anchored": bool(
                value.get_editor_property("required_objectives_anchored")
            ),
            "weather_matches_definition": bool(
                value.get_editor_property("weather_matches_definition")
            ),
            "landmarks_distinct": bool(
                value.get_editor_property("landmarks_distinct")
            ),
        }
    route_x_span = (
        max(point.x for point in route_points) - min(point.x for point in route_points)
        if route_points else 0.0
    )
    route_y_span = (
        max(point.y for point in route_points) - min(point.y for point in route_points)
        if route_points else 0.0
    )

    component_names, pool_budget = [], {}
    if len(directors) == 1:
        component_names = [
            component.get_name()
            for component in directors[0].get_components_by_class(
                unreal.ActorComponent
            )
        ]
        budget = directors[0].get_editor_property("pool_budget")
        pool_budget = {
            "max_active_threats": int(
                budget.get_editor_property("max_active_threats")
            ),
            "pool_capacity": int(budget.get_editor_property("pool_capacity")),
            "max_active_decoys": int(
                budget.get_editor_property("max_active_decoys")
            ),
            "max_simultaneous_explosions": int(
                budget.get_editor_property("max_simultaneous_explosions")
            ),
        }
    weakpoints, debris = [], 0
    if len(bosses) == 1:
        weakpoints = sorted(
            str(component.get_editor_property("weak_point_id"))
            for component in bosses[0].get_components_by_class(
                unreal.SkyguardBossWeakPointComponent
            )
        )
        debris = int(bosses[0].get_defeat_debris_piece_count())

    expected_weakpoints = sorted([
        "DispenserPort", "DispenserCenter", "DispenserStarboard",
        "CommandAntennaPort", "CommandAntennaStarboard", "DecoyController",
        "EnginePodPort", "EnginePodCenter", "EnginePodStarboard",
        "FuelControlPort", "FuelControlStarboard",
    ])
    mission = unreal.EditorAssetLibrary.load_asset(MISSION_ASSET)
    mission_map = (
        str(mission.get_editor_property("mission_map")) if mission else ""
    )
    game_mode = (
        unreal.EditorLevelLibrary.get_editor_world()
        .get_world_settings()
        .get_editor_property("default_game_mode")
    )
    protected_component_names = {
        "ProtectedMetropolitanSkyline",
        "ProtectedCoastalPowerStation",
        "ProtectedMajorBridge",
    }
    checks = {
        "source_preserved": unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP),
        "target_loaded": True,
        "single_assembly": len(assemblies) == 1,
        "assembly_identity": mission_id == "M09_SaturationAttack",
        "assembly_valid": bool(readiness) and all(readiness.values()) and not errors,
        "distinct_dense_canyon_route": len(route_points) == 4
        and route_x_span >= 90000.0
        and route_y_span >= 25000.0,
        "protected_metropolitan_roles": all(
            role in roles for role in [
                "DenseMetroSkylineProxy",
                "PowerInfrastructureProxy",
                "BridgeInfrastructureProxy",
            ]
        ),
        "single_integration": len(directors) == 1,
        "single_yak": names.count("SkyguardYak52Aircraft") == 1,
        "single_iron_rain": len(bosses) == 1,
        "three_governed_runtime_actors": len(governed) == 3,
        "protected_target_components": protected_component_names.issubset(
            set(component_names)
        ),
        "eleven_physical_weakpoints": weakpoints == expected_weakpoints,
        "bounded_pre_authored_breakup": debris == 3,
        "bounded_pool_budget": pool_budget == {
            "max_active_threats": 24,
            "pool_capacity": 48,
            "max_active_decoys": 12,
            "max_simultaneous_explosions": 6,
        },
        "game_mode": bool(game_mode)
        and game_mode.get_name() == "SkyguardGameMode",
        "mission_map_binding": TARGET_MAP in mission_map,
    }
    report = {
        "schema": "skyguard.m09-playable-integration-audit.v1",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "assembly_errors": [str(error) for error in errors],
        "assembly_readiness": readiness,
        "route_point_count": len(route_points),
        "route_x_span": route_x_span,
        "route_y_span": route_y_span,
        "landmark_roles": roles,
        "pool_budget": pool_budget,
        "weakpoints": weakpoints,
        "limitations": [
            "Persistence is not PIE, rendered playability, frame-time, cook or packaging proof.",
            "Metropolitan environment and Iron Rain remain proxy art.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[SkyguardM09PlayableAudit] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("M09 playable persistence audit failed")


if __name__ == "__main__":
    main()
