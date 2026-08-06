"""Build distinct M08-M10 campaign map assemblies with governed proxy art."""

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_skyguard_phase7_wave1_mission_maps as shared


MAP_ROOT = "/Game/Skyguard/Maps/Campaign_v1"
DATA_ROOT = "/Game/Skyguard/Data/Campaign_v1"
REPORT_PATH = ROOT / "Saved/Reports/PHASE7_WAVE3_MISSION_MAP_BUILD.json"
REVISION = "CampaignMapAssembly_v1"


MAP_SPECS = [
    {
        "short": "M08",
        "mission_id": "M08_RescueCover",
        "mission_asset": DATA_ROOT + "/DA_Mission_M08_RescueCover",
        "map": MAP_ROOT + "/Lvl_M08_RescueCover_Assembly_v1",
        "style": "COASTAL_HIGHWAY",
        "objective_locations": {
            "ProtectRescueFlight": (39000, 18000, 5000),
            "DefeatLifelineHunter": (57000, -9000, 5400),
        },
        "landmarks": [
            ("RescueHelicopter", "AnimatedRescueFlightProxy", (39000, 18000, 5000), True),
            ("SurvivorRafts", "HoistObjectiveProxy", (42000, 8000, -100), True),
            ("RescueVessel", "MaritimeRescueProxy", (28000, 3000, -50), True),
            ("RockyRescueCove", "RescueCoastSkyline", (52000, 38000, 0), False),
        ],
        "required_roles": [
            "AnimatedRescueFlightProxy",
            "HoistObjectiveProxy",
            "MaritimeRescueProxy",
        ],
        "placements": [
            ("Hero_RescueHelicopter", "/Game/Skyguard/Meshes/Hero/yak52_proxy", (39000, 18000, 5000), (0, 25, 0), (0.65, 0.65, 0.65), "AnimatedRescueFlightProxy"),
            ("Hero_RescueVessel", "/Game/Skyguard/Meshes/Hero/freighter_proxy", (28000, 3000, -50), (0, 20, 0), (0.75, 0.75, 0.75), "MaritimeRescueProxy"),
            ("Raft_A", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (40500, 6500, -120), (0, 0, 0), (0.22, 0.22, 0.08), "HoistObjectiveProxy"),
            ("Raft_B", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (43000, 8500, -120), (0, 20, 0), (0.22, 0.22, 0.08), "HoistObjectiveProxy"),
            ("Raft_C", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (45000, 6000, -120), (0, -15, 0), (0.22, 0.22, 0.08), "HoistObjectiveProxy"),
            ("Cove_Pier", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (33000, 22000, 0), (0, 35, 0), (1.5, 0.8, 1.0), "RescueCove"),
            ("Cove_Radar", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (59000, 36000, 0), (0, 210, 0), (0.9, 0.9, 0.9), "RescueCove"),
            ("Boss_LifelineHunter_Proxy", "/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy", (57000, -9000, 5400), (0, 160, 0), (1.25, 1.25, 1.25), "BossProxy"),
        ],
        "shared_blocks": [(8000 + i * 6500, 43000 + (i % 3) * 4200, 0) for i in range(13)],
    },
    {
        "short": "M09",
        "mission_id": "M09_SaturationAttack",
        "mission_asset": DATA_ROOT + "/DA_Mission_M09_SaturationAttack",
        "map": MAP_ROOT + "/Lvl_M09_SaturationAttack_Assembly_v1",
        "style": "BLACKOUT_URBAN",
        "objective_locations": {
            "ProtectCityInfrastructure": (52000, 38000, 200),
            "DefeatIronRain": (72000, 8000, 7600),
        },
        "landmarks": [
            ("MetropolitanSkyline", "DenseMetroSkylineProxy", (52000, 47000, 0), False),
            ("CoastalPowerStation", "PowerInfrastructureProxy", (68000, 33000, 0), True),
            ("MajorBridge", "BridgeInfrastructureProxy", (30000, 18000, 0), True),
            ("RooftopRelayCluster", "SwarmRelayProxy", (56000, 44000, 2200), True),
        ],
        "required_roles": [
            "DenseMetroSkylineProxy",
            "PowerInfrastructureProxy",
            "BridgeInfrastructureProxy",
        ],
        "placements": [
            ("Metro_Tower_A", "/Game/Skyguard/Meshes/Hero/facade_tower_proxy", (43000, 45000, 0), (0, 5, 0), (1.5, 1.5, 2.0), "DenseMetroSkylineProxy"),
            ("Metro_Tower_B", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (52000, 50000, 0), (0, -12, 0), (1.7, 1.7, 2.2), "DenseMetroSkylineProxy"),
            ("Metro_Tower_C", "/Game/Skyguard/Meshes/Hero/facade_tower_proxy", (61000, 46000, 0), (0, 20, 0), (1.45, 1.45, 1.8), "DenseMetroSkylineProxy"),
            ("Power_Block_A", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (66000, 32000, 0), (0, 0, 0), (2.0, 1.5, 1.0), "PowerInfrastructureProxy"),
            ("Power_Block_B", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (72000, 35000, 0), (0, 90, 0), (1.6, 1.6, 1.3), "PowerInfrastructureProxy"),
            ("Bridge_Pier_A", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (26000, 15000, 0), (0, 20, 0), (1.8, 0.8, 1.0), "BridgeInfrastructureProxy"),
            ("Bridge_Pier_B", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (34000, 21000, 0), (0, 20, 0), (1.8, 0.8, 1.0), "BridgeInfrastructureProxy"),
            ("Relay_Rooftop_A", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (50000, 43000, 1900), (0, 180, 0), (0.7, 0.7, 0.7), "SwarmRelayProxy"),
            ("Relay_Rooftop_B", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (57000, 47000, 2300), (0, 200, 0), (0.7, 0.7, 0.7), "SwarmRelayProxy"),
            ("Relay_Rooftop_C", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (64000, 44000, 1800), (0, 165, 0), (0.7, 0.7, 0.7), "SwarmRelayProxy"),
            ("Boss_IronRain_Proxy", "/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy", (72000, 8000, 7600), (0, 185, 0), (1.5, 1.5, 1.5), "BossProxy"),
        ],
        "shared_blocks": [(7000 + i * 5700, 54000 + (i % 4) * 4800, 0) for i in range(16)],
    },
    {
        "short": "M10",
        "mission_id": "M10_EvacuationFinale",
        "mission_asset": DATA_ROOT + "/DA_Mission_M10_EvacuationFinale",
        "map": MAP_ROOT + "/Lvl_M10_EvacuationFinale_Assembly_v1",
        "style": "HARBOR_INDUSTRIAL",
        "objective_locations": {
            "ProtectEvacuationHub": (55000, 28000, 100),
            "DefeatLastFlight": (81000, -13000, 7800),
        },
        "landmarks": [
            ("FerryTerminal", "EvacuationTerminalProxy", (52000, 31000, 0), True),
            ("EvacuationShip", "EvacuationShipProxy", (47000, 5000, -50), True),
            ("CivilianConvoyHub", "CivilianConvoyProxy", (65000, 39000, 100), True),
            ("DepartureBreakwater", "FinaleHarborSkyline", (76000, 25000, 0), False),
        ],
        "required_roles": [
            "EvacuationTerminalProxy",
            "EvacuationShipProxy",
            "CivilianConvoyProxy",
        ],
        "placements": [
            ("Hero_EvacuationShip", "/Game/Skyguard/Meshes/Hero/container_ship_proxy", (47000, 5000, -50), (0, 10, 0), (1.4, 1.4, 1.4), "EvacuationShipProxy"),
            ("Terminal_Pier_A", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (47000, 26000, 0), (0, 0, 0), (2.2, 1.0, 1.0), "EvacuationTerminalProxy"),
            ("Terminal_Pier_B", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (59000, 30000, 0), (0, 0, 0), (2.2, 1.0, 1.0), "EvacuationTerminalProxy"),
            ("Terminal_Block", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (54000, 35000, 0), (0, 0, 0), (2.0, 1.7, 1.0), "EvacuationTerminalProxy"),
            ("Convoy_Bus_A", "/Game/Skyguard/Meshes/Hero/city_bus_proxy", (62000, 38000, 100), (0, -20, 0), (0.9, 0.9, 0.9), "CivilianConvoyProxy"),
            ("Convoy_Bus_B", "/Game/Skyguard/Meshes/Hero/city_bus_proxy", (66000, 40000, 100), (0, -20, 0), (0.9, 0.9, 0.9), "CivilianConvoyProxy"),
            ("AmbulanceProxy_A", "/Game/Skyguard/Meshes/Hero/city_car_proxy", (70000, 42000, 100), (0, -20, 0), (0.85, 0.85, 0.85), "CivilianConvoyProxy"),
            ("AmbulanceProxy_B", "/Game/Skyguard/Meshes/Hero/city_car_proxy", (73500, 43500, 100), (0, -20, 0), (0.85, 0.85, 0.85), "CivilianConvoyProxy"),
            ("Breakwater_Crane_A", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (73000, 28000, 0), (0, 5, 0), (1.1, 1.1, 1.1), "FinaleHarborSkyline"),
            ("Breakwater_Crane_B", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (82000, 31000, 0), (0, -8, 0), (1.2, 1.2, 1.2), "FinaleHarborSkyline"),
            ("Boss_LastFlight_Proxy", "/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy", (81000, -13000, 7800), (0, 195, 0), (1.6, 1.6, 1.6), "BossProxy"),
        ],
        "shared_blocks": [(8000 + i * 6200, 50000 + (i % 3) * 4300, 0) for i in range(14)],
    },
]


def canonical_spec_hash():
    return hashlib.sha256(
        json.dumps(MAP_SPECS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_map(spec):
    if unreal.EditorAssetLibrary.does_asset_exist(spec["map"]):
        if not unreal.EditorLevelLibrary.load_level(spec["map"]):
            raise RuntimeError("Could not load governed map: " + spec["map"])
    elif not unreal.EditorLevelLibrary.new_level(spec["map"]):
        raise RuntimeError("Could not create governed map: " + spec["map"])

    prefix = "P7W3_%s_" % spec["short"]
    removed = shared.clear_owned_actors(prefix)
    mission = shared.load_required_asset(spec["mission_asset"])
    valid, errors = shared.normalize_validation(mission.validate_definition())
    if not valid:
        raise RuntimeError("Mission validation failed: " + "; ".join(errors))

    director_class = unreal.load_class(
        None, "/Script/Skyguard52.SkyguardMissionMapAssemblyDirector"
    )
    if not director_class:
        raise RuntimeError("Native mission map director is unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector(), unreal.Rotator()
    )
    director.set_actor_label(prefix + "AssemblyDirector")
    director.set_editor_property("mission_definition", mission)
    director.set_editor_property("mission_id", unreal.Name(spec["mission_id"]))
    director.set_editor_property("assembly_revision", unreal.Name(REVISION))
    weather = mission.get_editor_property("weather")
    director.set_editor_property(
        "weather_profile_id",
        weather.get_editor_property("profile_id"),
    )
    director.set_editor_property(
        "skyline_style",
        getattr(unreal.SkyguardMissionSkylineStyle, spec["style"]),
    )
    route = mission.get_editor_property("route")
    route_points = [
        point.get_editor_property("world_location")
        for point in route.get_editor_property("points")
    ]
    director.set_editor_property("route_points", route_points)
    director.set_editor_property(
        "objective_anchors",
        [
            shared.objective_anchor(objective_id, location)
            for objective_id, location in spec["objective_locations"].items()
        ],
    )
    director.set_editor_property(
        "landmark_anchors",
        [shared.landmark_anchor(*item) for item in spec["landmarks"]],
    )
    director.rebuild_route_spline()
    assembly_valid, assembly_errors = shared.normalize_validation(
        director.validate_assembly()
    )
    if not assembly_valid:
        raise RuntimeError("Assembly validation failed: " + "; ".join(assembly_errors))
    shared.add_tags(
        director,
        "Skyguard.CampaignMap.Director",
        "Skyguard.Mission." + spec["mission_id"],
        "Skyguard.Assembly." + REVISION,
        "Skyguard.Wave3",
    )

    asphalt = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_AsphaltRoad"
    )
    ocean = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_L23_Ocean"
    )
    land = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_L23_Beach"
    )
    shared.spawn_cube(prefix, "LandMass", (50000, 52000, -650), (1100, 650, 6), "SharedCoast", land)
    shared.spawn_cube(prefix, "Ocean", (50000, -25000, -850), (1150, 750, 2), "SharedOcean", ocean)

    if spec["short"] == "M08":
        for index in range(6):
            shared.spawn_cube(prefix, "RescueCoast_%02d" % index, (9000 + index * 14500, 30000 + (index % 2) * 5000, -50), (150, 30, 1), "RescueCoastRoute", asphalt)
    elif spec["short"] == "M09":
        for index in range(9):
            shared.spawn_cube(prefix, "MetroAvenue_%02d" % index, (7000 + index * 10500, 34000 + (index % 3) * 6500, -50), (110, 20, 1), "MetropolitanRoadGrid", asphalt)
    else:
        for index in range(7):
            shared.spawn_cube(prefix, "EvacuationLane_%02d" % index, (10000 + index * 12500, 36000 + (index % 2) * 5000, -50), (130, 28, 1), "EvacuationLane", asphalt)

    for placement in spec["placements"]:
        shared.spawn_static(prefix, *placement)
    for index, location in enumerate(spec["shared_blocks"]):
        mesh = (
            "/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy"
            if index % 2 == 0
            else "/Game/Skyguard/Meshes/Hero/coast_block_proxy"
        )
        shared.spawn_static(
            prefix,
            "SharedBlock_%02d" % index,
            mesh,
            location,
            (0, (index * 19) % 360, 0),
            (1.0 + (index % 3) * 0.2, 1.0, 1.0 + (index % 4) * 0.2),
            "SharedCoastalKit",
        )
    for objective_id, location in spec["objective_locations"].items():
        target = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.TargetPoint, unreal.Vector(*location), unreal.Rotator()
        )
        target.set_actor_label(prefix + "Objective_" + objective_id)
        shared.add_tags(
            target,
            "Skyguard.CampaignMap.ObjectiveAnchor",
            "Skyguard.Objective." + objective_id,
        )
    shared.spawn_environment(prefix, night=False)

    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Could not save governed map: " + spec["map"])
    map_asset = unreal.EditorAssetLibrary.load_asset(spec["map"])
    mission.set_editor_property("mission_map", map_asset)
    unreal.EditorAssetLibrary.set_metadata_tag(
        mission, "Skyguard.CampaignMapAssembly", REVISION
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(mission):
        raise RuntimeError("Could not persist mission map binding")

    actors = [
        actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if (actor.get_actor_label() or "").startswith(prefix)
    ]
    return {
        "map": spec["map"],
        "mission_id": spec["mission_id"],
        "style": spec["style"],
        "removed_prior_owned_actors": removed,
        "owned_actor_count": len(actors),
        "route_points": len(route_points),
        "hero_placeholder_count": len(spec["placements"]),
        "required_hero_roles": spec["required_roles"],
        "content_state": "distinct_spatial_gameplay_assembly_with_proxy_art",
    }


def main():
    unreal.EditorAssetLibrary.make_directory(MAP_ROOT)
    maps = [build_map(spec) for spec in MAP_SPECS]
    report = {
        "schema": "skyguard.phase7.wave3-map-build.v1",
        "gate": "BUILT_PENDING_FRESH_PROCESS_AUDIT",
        "revision": REVISION,
        "spec_sha256": canonical_spec_hash(),
        "maps": maps,
        "limitations": [
            "Rescue, metro, bridge, ferry, evacuation and boss landmarks use proxy art.",
            "No final visual, animation, mission-logic, collision, streaming, or packaged-playability claim is made.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE3_MAP_BUILD " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
