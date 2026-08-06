"""Build definition-driven M05-M07 campaign assembly maps with proxy art."""

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
REPORT_PATH = ROOT / "Saved/Reports/PHASE7_WAVE2_MISSION_MAP_BUILD.json"
REVISION = "CampaignMapAssembly_v1"
RADAR_HERO = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/SM_M01_Landmark_RadarPost_Hero_A"
)
LIGHTHOUSE_HERO = (
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/"
    "m01_wave1_aaa_refinement/StaticMeshes/SM_M01_Landmark_Lighthouse_Hero_A"
)


MAP_SPECS = [
    {
        "short": "M05",
        "mission_id": "M05_StormFront",
        "mission_asset": DATA_ROOT + "/DA_Mission_M05_StormFront",
        "map": MAP_ROOT + "/Lvl_M05_StormFront_Assembly_v1",
        "style": "OFFSHORE_STORM",
        "objectives": {
            "ProtectOffshoreCrew": (42000, -12000, -50),
            "DisableDischargeBooms": (59000, -5000, 6900),
            "DefeatTempest": (70000, 24000, 7600),
        },
        "boss_spawn": (70000, 24000, 7600),
        "landmarks": [
            ("DistressedTrawler", "RescuePressure", (42000, -12000, -50), True),
            ("OffshorePlatform", "IndustrialOffshore", (20000, 16000, 0), True),
            ("SeaStackGate", "NaturalFlightGate", (57000, 31000, 0), True),
            ("StormBuoyLine", "NavigationHazard", (36000, 4000, -100), False),
        ],
        "hero": [
            ("Trawler", "/Game/Skyguard/Meshes/Hero/freighter_proxy", (42000, -12000, -100), (0, 15, 0), (0.55, 0.55, 0.55), "RescuePressure"),
            ("PlatformDeck_A", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (19000, 16000, 0), (0, 90, 0), (2.2, 2.2, 1.0), "IndustrialOffshore"),
            ("PlatformDeck_B", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (24000, 16000, 0), (0, 90, 0), (2.2, 2.2, 1.0), "IndustrialOffshore"),
            ("PlatformCrane", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (22000, 19000, 0), (0, 180, 0), (0.8, 0.8, 0.8), "IndustrialOffshore"),
            ("SeaStack_A", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (54000, 30000, -200), (0, 0, 0), (1.8, 1.8, 2.5), "NaturalFlightGate"),
            ("SeaStack_B", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (62000, 33000, -200), (0, 90, 0), (1.5, 1.5, 2.1), "NaturalFlightGate"),
        ],
    },
    {
        "short": "M06",
        "mission_id": "M06_AirfieldDefense",
        "mission_asset": DATA_ROOT + "/DA_Mission_M06_AirfieldDefense",
        "map": MAP_ROOT + "/Lvl_M06_AirfieldDefense_Assembly_v1",
        "style": "AIRFIELD_MILITARY",
        "objectives": {
            "ProtectAirfieldAssets": (57000, 34000, 100),
            "JamPayloadRacks": (48000, 9000, 5400),
            "DefeatRunwayBreaker": (78000, 22000, 6000),
        },
        "boss_spawn": (78000, 22000, 6000),
        "landmarks": [
            ("PrimaryRunway", "RunwayAxis", (50000, 39000, 0), True),
            ("ControlTower", "AirfieldCommand", (24000, 53000, 0), True),
            ("HardenedShelters", "ProtectedAircraft", (69000, 56000, 0), True),
            ("HangarLine", "IndustrialAirfield", (44000, 57000, 0), False),
        ],
        "hero": [
            ("ControlTower", "/Game/Skyguard/Meshes/Hero/facade_tower_proxy", (24000, 53000, 0), (0, 0, 0), (0.7, 0.7, 1.2), "AirfieldCommand"),
            ("Shelter_A", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (65000, 57000, 0), (0, 90, 0), (1.4, 2.0, 0.65), "ProtectedAircraft"),
            ("Shelter_B", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (72000, 57000, 0), (0, 90, 0), (1.4, 2.0, 0.65), "ProtectedAircraft"),
            ("AirDefense_A", "/Game/Skyguard/Meshes/Hero/flak_emplacement_proxy", (17000, 35000, 0), (0, 220, 0), (1.0, 1.0, 1.0), "AirfieldDefense"),
            ("AirDefense_B", "/Game/Skyguard/Meshes/Hero/flak_emplacement_proxy", (82000, 50000, 0), (0, 30, 0), (1.0, 1.0, 1.0), "AirfieldDefense"),
        ],
    },
    {
        "short": "M07",
        "mission_id": "M07_SearchIntercept",
        "mission_asset": DATA_ROOT + "/DA_Mission_M07_SearchIntercept",
        "map": MAP_ROOT + "/Lvl_M07_SearchIntercept_Assembly_v1",
        "style": "ISLAND_SEARCH",
        "objectives": {
            "ProtectRadarChain": (51000, 39000, 200),
            "ClassifyFalseTracks": (34000, -5000, 7100),
            "DefeatRadarGhost": (73000, 32000, 7200),
        },
        "boss_spawn": (73000, 32000, 7200),
        "landmarks": [
            ("IslandRadar", "RadarObjective", (51000, 39000, 200), True),
            ("NavigationLighthouse", "NavigationReference", (17000, 23000, 0), True),
            ("FishingFleet", "IdentificationTraffic", (36000, -17000, -50), True),
            ("OuterIslandStation", "SearchBoundary", (76000, 52000, 100), False),
        ],
        "hero": [
            ("RadarStation", RADAR_HERO, (51000, 39000, 200), (0, 20, 0), (1.0, 1.0, 1.0), "RadarObjective"),
            ("NavigationLighthouse", LIGHTHOUSE_HERO, (17000, 23000, 0), (0, 0, 0), (1.0, 1.0, 1.0), "NavigationReference"),
            ("FishingBoat_A", "/Game/Skyguard/Meshes/Hero/freighter_proxy", (32000, -18000, -100), (0, 35, 0), (0.28, 0.28, 0.28), "IdentificationTraffic"),
            ("FishingBoat_B", "/Game/Skyguard/Meshes/Hero/freighter_proxy", (38000, -15000, -100), (0, 15, 0), (0.24, 0.24, 0.24), "IdentificationTraffic"),
            ("FishingBoat_C", "/Game/Skyguard/Meshes/Hero/freighter_proxy", (43000, -20000, -100), (0, -10, 0), (0.2, 0.2, 0.2), "IdentificationTraffic"),
            ("OuterRadarTruck", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (76000, 52000, 100), (0, 190, 0), (0.9, 0.9, 0.9), "SearchBoundary"),
        ],
    },
]


def spawn_target(prefix, label, location, *tags):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.TargetPoint, unreal.Vector(*location), unreal.Rotator()
    )
    if actor is None:
        raise RuntimeError("Could not spawn target " + label)
    actor.set_actor_label(prefix + label)
    shared.add_tags(actor, *tags)
    return actor


def add_common_director(spec, mission, prefix):
    cls = unreal.load_class(
        None, "/Script/Skyguard52.SkyguardMissionMapAssemblyDirector"
    )
    if cls is None:
        raise RuntimeError("Native mission-map assembly director is unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        cls, unreal.Vector(), unreal.Rotator()
    )
    director.set_actor_label(prefix + "AssemblyDirector")
    director.set_editor_property("mission_definition", mission)
    director.set_editor_property("mission_id", unreal.Name(spec["mission_id"]))
    director.set_editor_property("assembly_revision", unreal.Name(REVISION))
    director.set_editor_property(
        "skyline_style",
        getattr(unreal.SkyguardMissionSkylineStyle, spec["style"]),
    )
    weather = mission.get_editor_property("weather")
    director.set_editor_property(
        "weather_profile_id", weather.get_editor_property("profile_id")
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
            for objective_id, location in spec["objectives"].items()
        ],
    )
    director.set_editor_property(
        "landmark_anchors",
        [shared.landmark_anchor(*landmark) for landmark in spec["landmarks"]],
    )
    director.rebuild_route_spline()
    valid, errors = shared.normalize_validation(director.validate_assembly())
    if not valid:
        raise RuntimeError("Native map validation failed: " + "; ".join(errors))
    shared.add_tags(
        director,
        "Skyguard.CampaignMap.Director",
        "Skyguard.Mission." + spec["mission_id"],
        "Skyguard.Assembly." + REVISION,
    )
    return director, route_points, str(weather.get_editor_property("profile_id"))


def build_storm(spec, prefix, ocean, land):
    shared.spawn_cube(prefix, "Ocean", (48000, 0, -950), (1200, 1000, 2), "StormOcean", ocean)
    shared.spawn_cube(prefix, "DistantCoast", (45000, 65000, -700), (1000, 240, 5), "DistantCoast", land)
    for item in spec["hero"]:
        shared.spawn_static(prefix, *item)
    for index in range(10):
        x = 9000 + index * 7500
        y = -3000 + (index % 3) * 5000
        shared.spawn_static(
            prefix,
            "StormBuoy_%02d" % index,
            "/Engine/BasicShapes/Sphere",
            (x, y, -150),
            (0, 0, 0),
            (0.35, 0.35, 0.7),
            "NavigationHazard",
        )


def build_airfield(spec, prefix, asphalt, land):
    shared.spawn_cube(prefix, "AirfieldTerrain", (50000, 44000, -700), (1150, 650, 6), "AirfieldTerrain", land)
    shared.spawn_cube(prefix, "RunwayPrimary", (50000, 39000, -30), (850, 45, 1), "RunwayAxis", asphalt)
    shared.spawn_cube(prefix, "Taxiway", (50000, 50000, -35), (700, 18, 1), "Taxiway", asphalt)
    for item in spec["hero"]:
        shared.spawn_static(prefix, *item)
    for index in range(6):
        shared.spawn_cube(
            prefix,
            "Hangar_%02d" % index,
            (33000 + index * 7500, 58000, 800),
            (55, 80, 18),
            "IndustrialAirfield",
            land,
        )
    for index in range(9):
        mesh = (
            "/Game/Skyguard/Meshes/Hero/city_bus_proxy"
            if index % 4 == 0
            else "/Game/Skyguard/Meshes/Hero/city_car_proxy"
        )
        shared.spawn_static(
            prefix,
            "ParkedAircraftProxy_%02d" % index,
            mesh,
            (27000 + index * 6200, 48000 + (index % 2) * 3500, 0),
            (0, 90, 0),
            (0.8, 0.8, 0.8),
            "ProtectedAircraft",
        )


def build_search(spec, prefix, ocean, land):
    shared.spawn_cube(prefix, "Ocean", (48000, 5000, -950), (1200, 1100, 2), "IslandOcean", ocean)
    islands = [
        (15000, 23000, 220, 170),
        (50000, 39000, 260, 210),
        (76000, 52000, 190, 155),
        (65000, -18000, 150, 130),
    ]
    for index, (x, y, sx, sy) in enumerate(islands):
        shared.spawn_cube(
            prefix,
            "Island_%02d" % index,
            (x, y, -650),
            (sx, sy, 6),
            "IslandTerrain",
            land,
        )
        for tree_index in range(5):
            shared.spawn_static(
                prefix,
                "Island_%02d_Tree_%02d" % (index, tree_index),
                "/Game/Skyguard/Meshes/Hero/coast_tree_proxy",
                (x - 5000 + tree_index * 2200, y + ((tree_index % 2) * 2600), 0),
                (0, tree_index * 35, 0),
                (0.8, 0.8, 0.8),
                "IslandVegetation",
            )
    for item in spec["hero"]:
        shared.spawn_static(prefix, *item)


def build_map(spec):
    if unreal.EditorAssetLibrary.does_asset_exist(spec["map"]):
        if not unreal.EditorLevelLibrary.load_level(spec["map"]):
            raise RuntimeError("Could not load " + spec["map"])
    elif not unreal.EditorLevelLibrary.new_level(spec["map"]):
        raise RuntimeError("Could not create " + spec["map"])

    prefix = "P7W2_%s_" % spec["short"]
    removed = shared.clear_owned_actors(prefix)
    mission = shared.load_required_asset(spec["mission_asset"])
    mission_valid, mission_errors = shared.normalize_validation(
        mission.validate_definition()
    )
    if not mission_valid:
        raise RuntimeError("Mission definition invalid: " + "; ".join(mission_errors))
    director, route_points, weather_id = add_common_director(spec, mission, prefix)

    asphalt = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_AsphaltRoad"
    )
    ocean = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_L23_Ocean"
    )
    land = unreal.EditorAssetLibrary.load_asset(
        "/Game/Skyguard/Materials/Generated/M_L23_Beach"
    )
    if spec["short"] == "M05":
        build_storm(spec, prefix, ocean, land)
    elif spec["short"] == "M06":
        build_airfield(spec, prefix, asphalt, land)
    else:
        build_search(spec, prefix, ocean, land)

    for objective_id, location in spec["objectives"].items():
        spawn_target(
            prefix,
            "Objective_" + objective_id,
            location,
            "Skyguard.CampaignMap.ObjectiveAnchor",
            "Skyguard.Objective." + objective_id,
        )
    boss = mission.get_editor_property("boss")
    boss_id = str(boss.get_editor_property("boss_id"))
    spawn_target(
        prefix,
        "BossSpawn_" + boss_id,
        spec["boss_spawn"],
        "Skyguard.CampaignMap.BossSpawn",
        "Skyguard.Boss." + boss_id,
    )
    shared.spawn_environment(prefix, night=False)

    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Could not save " + spec["map"])
    owned = [
        actor
        for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if (actor.get_actor_label() or "").startswith(prefix)
    ]
    return {
        "map": spec["map"],
        "mission_id": spec["mission_id"],
        "style": spec["style"],
        "weather_profile_id": weather_id,
        "boss_id": boss_id,
        "boss_spawn": spec["boss_spawn"],
        "route_points": len(route_points),
        "objective_anchors": len(spec["objectives"]),
        "landmarks": len(spec["landmarks"]),
        "exclusive_landmarks": sum(1 for item in spec["landmarks"] if item[3]),
        "owned_actor_count": len(owned),
        "removed_prior_owned_actors": removed,
        "content_state": "spatial_gameplay_assembly_with_placeholder_art",
    }


def canonical_spec_hash():
    return hashlib.sha256(
        json.dumps(MAP_SPECS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main():
    unreal.EditorAssetLibrary.make_directory(MAP_ROOT)
    maps = [build_map(spec) for spec in MAP_SPECS]
    report = {
        "gate": "BUILT_PENDING_FRESH_PROCESS_AUDIT",
        "revision": REVISION,
        "map_count": len(maps),
        "spec_sha256": canonical_spec_hash(),
        "maps": maps,
        "limitations": [
            "Maps remain proxy-art spatial assemblies.",
            "Storm, airfield, search, boss, objective, wave, audio, and cinematic behaviors are not implemented by this builder.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE2_MAP_BUILD " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
