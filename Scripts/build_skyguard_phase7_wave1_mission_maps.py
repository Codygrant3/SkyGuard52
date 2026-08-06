"""Build distinct, definition-driven M02-M04 campaign assembly maps.

These are governed spatial/gameplay assemblies with placeholder art. They do
not represent final environment art, finished mission scripting, or AAA maps.
"""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
MAP_ROOT = "/Game/Skyguard/Maps/Campaign_v1"
DATA_ROOT = "/Game/Skyguard/Data/Campaign_v1"
REPORT_PATH = ROOT / "Saved/Reports/PHASE7_WAVE1_MISSION_MAP_BUILD.json"
REVISION = "CampaignMapAssembly_v1"

MAP_SPECS = [
    {
        "short": "M02",
        "mission_id": "M02_HarborShield",
        "mission_asset": DATA_ROOT + "/DA_Mission_M02_HarborShield",
        "map": MAP_ROOT + "/Lvl_M02_HarborShield_Assembly_v1",
        "style": "HARBOR_INDUSTRIAL",
        "objective_locations": {
            "ProtectFuelTerminal": (71000, 43000, 100),
            "DefeatBreakwater": (65000, -8000, 4300),
        },
        "landmarks": [
            ("FuelTerminal", "DefendedObjective", (71000, 43000, 100), True),
            ("ContainerShip", "MaritimeHero", (43000, -9000, -100), True),
            ("CraneCorridor", "IndustrialSkyline", (47000, 44000, 0), False),
            ("SubmarinePatrol", "OffshoreSilhouette", (16000, -14000, -250), True),
        ],
        "placements": [
            ("Hero_ContainerShip", "/Game/Skyguard/Meshes/Hero/container_ship_proxy", (43000, -9000, -50), (0, 0, 0), (1.5, 1.5, 1.5), "MaritimeHero"),
            ("Hero_Submarine", "/Game/Skyguard/Meshes/Hero/submarine_proxy", (16000, -14000, -250), (0, 15, 0), (1.3, 1.3, 1.3), "OffshoreSilhouette"),
            ("FuelTerminal_A", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (70000, 42000, 0), (0, 0, 0), (2.0, 2.0, 1.2), "DefendedObjective"),
            ("FuelTerminal_B", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (76000, 45000, 0), (0, 90, 0), (1.6, 1.6, 1.0), "DefendedObjective"),
            ("Pier_A", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (25000, 33000, 0), (0, 0, 0), (2.2, 1.0, 1.0), "Pier"),
            ("Pier_B", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (45000, 35000, 0), (0, 0, 0), (2.2, 1.0, 1.0), "Pier"),
            ("Pier_C", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (65000, 37000, 0), (0, 0, 0), (2.2, 1.0, 1.0), "Pier"),
            ("Crane_A", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (22000, 46000, 0), (0, 0, 0), (1.1, 1.1, 1.1), "IndustrialSkyline"),
            ("Crane_B", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (39000, 45000, 0), (0, 10, 0), (1.2, 1.2, 1.2), "IndustrialSkyline"),
            ("Crane_C", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (56000, 47000, 0), (0, -8, 0), (1.1, 1.1, 1.1), "IndustrialSkyline"),
            ("Crane_D", "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy", (74000, 48000, 0), (0, 5, 0), (1.25, 1.25, 1.25), "IndustrialSkyline"),
        ],
        "shared_blocks": [(12000 + i * 7000, 56000 + (i % 2) * 3500, 0) for i in range(11)],
    },
    {
        "short": "M03",
        "mission_id": "M03_ConvoyEscort",
        "mission_asset": DATA_ROOT + "/DA_Mission_M03_ConvoyEscort",
        "map": MAP_ROOT + "/Lvl_M03_ConvoyEscort_Assembly_v1",
        "style": "COASTAL_HIGHWAY",
        "objective_locations": {
            "ProtectConvoyCore": (46000, 18500, 100),
            "DefeatRoadHunter": (70000, 45000, 6100),
        },
        "landmarks": [
            ("ReliefConvoy", "MovingObjective", (46000, 18500, 100), True),
            ("CoastalBridge", "BridgeCrossing", (30000, 10500, 0), True),
            ("TunnelPortal", "RouteDestination", (83000, 41000, 0), True),
            ("RidgeSettlement", "InlandSkyline", (57000, 59000, 0), False),
        ],
        "placements": [
            ("Convoy_Command", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (45500, 18200, 100), (0, 25, 0), (0.9, 0.9, 0.9), "MovingObjective"),
            ("Convoy_Bus_A", "/Game/Skyguard/Meshes/Hero/city_bus_proxy", (42000, 16000, 100), (0, 25, 0), (0.85, 0.85, 0.85), "MovingObjective"),
            ("Convoy_Bus_B", "/Game/Skyguard/Meshes/Hero/city_bus_proxy", (49500, 20500, 100), (0, 25, 0), (0.85, 0.85, 0.85), "MovingObjective"),
            ("Bridge_Pier_A", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (28000, 8000, 0), (0, 35, 0), (1.8, 0.8, 1.0), "BridgeCrossing"),
            ("Bridge_Pier_B", "/Game/Skyguard/Meshes/Hero/pier_section_proxy", (33000, 12000, 0), (0, 35, 0), (1.8, 0.8, 1.0), "BridgeCrossing"),
            ("Tunnel_Left", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (82000, 36000, 0), (0, 20, 0), (1.3, 1.3, 0.8), "RouteDestination"),
            ("Tunnel_Right", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (85000, 44000, 0), (0, 200, 0), (1.3, 1.3, 0.8), "RouteDestination"),
        ] + [
            ("Convoy_Car_%02d" % i, "/Game/Skyguard/Meshes/Hero/city_car_proxy", (35000 + i * 2800, 12000 + i * 1700, 100), (0, 25, 0), (0.8, 0.8, 0.8), "MovingObjective")
            for i in range(7)
        ],
        "shared_blocks": [(18000 + i * 6500, 60000 + (i % 3) * 4200, 0) for i in range(10)],
    },
    {
        "short": "M04",
        "mission_id": "M04_NightBlackout",
        "mission_asset": DATA_ROOT + "/DA_Mission_M04_NightBlackout",
        "map": MAP_ROOT + "/Lvl_M04_NightBlackout_Assembly_v1",
        "style": "BLACKOUT_URBAN",
        "objective_locations": {
            "ProtectSubstation": (61000, 21000, 100),
            "DefeatBlackKite": (70000, -17000, 4700),
        },
        "landmarks": [
            ("EmergencySubstation", "DefendedObjective", (61000, 21000, 100), True),
            ("SearchlightBattery", "IlluminationMechanic", (31000, 24000, 0), True),
            ("BlackoutSkyline", "DarkUrbanSkyline", (53000, 33000, 0), False),
            ("WaterfrontRadar", "BearingReference", (82000, 25000, 0), True),
        ],
        "placements": [
            ("Substation_Core", "/Game/Skyguard/Meshes/Hero/coast_block_proxy", (61000, 21000, 0), (0, 0, 0), (1.7, 1.7, 0.8), "DefendedObjective"),
            ("Searchlight_A", "/Game/Skyguard/Meshes/Hero/flak_emplacement_proxy", (27000, 23000, 0), (0, 180, 0), (1.0, 1.0, 1.0), "IlluminationMechanic"),
            ("Searchlight_B", "/Game/Skyguard/Meshes/Hero/flak_emplacement_proxy", (35000, 26000, 0), (0, 210, 0), (1.0, 1.0, 1.0), "IlluminationMechanic"),
            ("Radar_Bearing", "/Game/Skyguard/Meshes/Hero/radar_truck_proxy", (82000, 25000, 0), (0, 190, 0), (1.0, 1.0, 1.0), "BearingReference"),
            ("Ruined_Tower", "/Game/Skyguard/Meshes/Hero/ruined_tower_proxy", (51000, 36000, 0), (0, 20, 0), (1.4, 1.4, 1.5), "DarkUrbanSkyline"),
            ("Facade_Tower", "/Game/Skyguard/Meshes/Hero/facade_tower_proxy", (65000, 39000, 0), (0, -15, 0), (1.1, 1.1, 1.4), "DarkUrbanSkyline"),
        ] + [
            ("StreetLamp_%02d" % i, "/Game/Skyguard/Meshes/Hero/street_lamp_proxy", (12000 + i * 6000, 30000 + (i % 2) * 4500, 0), (0, 0, 0), (1.0, 1.0, 1.0), "BlackoutStreet")
            for i in range(12)
        ],
        "shared_blocks": [(9000 + i * 5000, 43000 + (i % 4) * 4800, 0) for i in range(15)],
    },
]


def normalize_validation(result):
    if isinstance(result, tuple):
        return bool(result[0]), [str(item) for item in result[1]]
    if isinstance(result, list) or type(result).__name__.endswith("Array"):
        errors = [str(item) for item in result]
        return not errors, errors
    return bool(result), []


def add_tags(actor, *tags):
    values = list(actor.get_editor_property("tags") or [])
    for tag in tags:
        value = unreal.Name(tag)
        if value not in values:
            values.append(value)
    actor.set_editor_property("tags", values)


def load_required_asset(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        raise RuntimeError("Missing required reusable asset: " + path)
    return asset


def spawn_static(prefix, label, mesh_path, location, rotation, scale, role):
    mesh = load_required_asset(mesh_path)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
        unreal.Rotator(rotation[1], rotation[2], rotation[0]),
    )
    if actor is None:
        raise RuntimeError("Could not spawn " + label)
    actor.set_actor_label(prefix + label)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    add_tags(actor, "Skyguard.CampaignMap.Placeholder", "Skyguard.Role." + role)
    return actor


def spawn_cube(prefix, label, location, scale, role, material=None):
    actor = spawn_static(
        prefix,
        label,
        "/Engine/BasicShapes/Cube",
        location,
        (0, 0, 0),
        scale,
        role,
    )
    if material:
        actor.static_mesh_component.set_material(0, material)
    return actor


def objective_anchor(objective_id, location):
    anchor = unreal.SkyguardMissionObjectiveAnchor()
    anchor.set_editor_property("objective_id", unreal.Name(objective_id))
    anchor.set_editor_property("world_location", unreal.Vector(*location))
    return anchor


def landmark_anchor(landmark_id, role, location, exclusive):
    anchor = unreal.SkyguardMissionLandmarkAnchor()
    anchor.set_editor_property("landmark_id", unreal.Name(landmark_id))
    anchor.set_editor_property("role", unreal.Name(role))
    anchor.set_editor_property("world_location", unreal.Vector(*location))
    anchor.set_editor_property("mission_exclusive", bool(exclusive))
    return anchor


def spawn_environment(prefix, night=False):
    created = []
    classes = [
        ("/Script/Engine.SkyAtmosphere", "SkyAtmosphere"),
        ("/Script/Engine.DirectionalLight", "DirectionalLight"),
        ("/Script/Engine.ExponentialHeightFog", "HeightFog"),
    ]
    for class_path, suffix in classes:
        cls = unreal.load_class(None, class_path)
        if cls is None:
            continue
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            cls, unreal.Vector(), unreal.Rotator()
        )
        if actor:
            actor.set_actor_label(prefix + suffix)
            add_tags(actor, "Skyguard.CampaignMap.Environment")
            created.append(actor)
            if suffix == "DirectionalLight":
                component = actor.get_component_by_class(unreal.DirectionalLightComponent)
                if component:
                    component.set_editor_property("intensity", 0.15 if night else 8.0)
                    if night:
                        component.set_editor_property(
                            "light_color", unreal.Color(70, 90, 130, 255)
                        )
    return created


def clear_owned_actors(prefix):
    removed = 0
    for actor in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        if (actor.get_actor_label() or "").startswith(prefix):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            removed += 1
    return removed


def build_map(spec):
    if unreal.EditorAssetLibrary.does_asset_exist(spec["map"]):
        if not unreal.EditorLevelLibrary.load_level(spec["map"]):
            raise RuntimeError("Could not load governed map: " + spec["map"])
    elif not unreal.EditorLevelLibrary.new_level(spec["map"]):
        raise RuntimeError("Could not create governed map: " + spec["map"])

    prefix = "P7W1_%s_" % spec["short"]
    removed = clear_owned_actors(prefix)
    mission = load_required_asset(spec["mission_asset"])
    valid, errors = normalize_validation(mission.validate_definition())
    if not valid:
        raise RuntimeError(
            "Mission DataAsset failed native validation: " + "; ".join(errors)
        )

    director_class = unreal.load_class(
        None, "/Script/Skyguard52.SkyguardMissionMapAssemblyDirector"
    )
    if director_class is None:
        raise RuntimeError("Native mission-map assembly director is unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector(), unreal.Rotator()
    )
    director.set_actor_label(prefix + "AssemblyDirector")
    director.set_editor_property("mission_definition", mission)
    director.set_editor_property("mission_id", unreal.Name(spec["mission_id"]))
    director.set_editor_property("assembly_revision", unreal.Name(REVISION))
    weather = mission.get_editor_property("weather")
    director.set_editor_property(
        "weather_profile_id", weather.get_editor_property("profile_id")
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
            objective_anchor(objective_id, location)
            for objective_id, location in spec["objective_locations"].items()
        ],
    )
    director.set_editor_property(
        "landmark_anchors",
        [
            landmark_anchor(*landmark)
            for landmark in spec["landmarks"]
        ],
    )
    director.rebuild_route_spline()
    assembly_valid, assembly_errors = normalize_validation(
        director.validate_assembly()
    )
    if not assembly_valid:
        raise RuntimeError(
            "Native map assembly validation failed: " + "; ".join(assembly_errors)
        )
    add_tags(
        director,
        "Skyguard.CampaignMap.Director",
        "Skyguard.Mission." + spec["mission_id"],
        "Skyguard.Assembly." + REVISION,
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
    spawn_cube(prefix, "LandMass", (50000, 52000, -650), (1100, 650, 6), "SharedCoast", land)
    spawn_cube(prefix, "CoastalShelf", (50000, 29000, -550), (1100, 160, 4), "SharedCoast", land)
    spawn_cube(prefix, "Ocean", (50000, -25000, -850), (1150, 750, 2), "SharedOcean", ocean)

    if spec["short"] == "M03":
        for index in range(8):
            spawn_cube(
                prefix,
                "Highway_%02d" % index,
                (8000 + index * 11000, -2000 + index * 5600, -50),
                (120, 18, 1),
                "CoastalHighway",
                asphalt,
            )
    elif spec["short"] == "M04":
        for index in range(7):
            spawn_cube(
                prefix,
                "BlackoutRoad_%02d" % index,
                (12000 + index * 11500, 28000, -50),
                (125, 16, 1),
                "BlackoutRoad",
                asphalt,
            )
    else:
        for index in range(6):
            spawn_cube(
                prefix,
                "PortApron_%02d" % index,
                (13000 + index * 14500, 39000, -50),
                (140, 45, 1),
                "PortApron",
                asphalt,
            )

    for placement in spec["placements"]:
        spawn_static(prefix, *placement)
    for index, location in enumerate(spec["shared_blocks"]):
        mesh_path = (
            "/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy"
            if index % 2 == 0
            else "/Game/Skyguard/Meshes/Hero/coast_block_proxy"
        )
        spawn_static(
            prefix,
            "SharedBlock_%02d" % index,
            mesh_path,
            location,
            (0, (index * 17) % 360, 0),
            (1.0 + (index % 3) * 0.2, 1.0, 1.0 + (index % 4) * 0.15),
            "SharedCoastalKit",
        )

    for objective_id, location in spec["objective_locations"].items():
        target = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.TargetPoint, unreal.Vector(*location), unreal.Rotator()
        )
        target.set_actor_label(prefix + "Objective_" + objective_id)
        add_tags(
            target,
            "Skyguard.CampaignMap.ObjectiveAnchor",
            "Skyguard.Objective." + objective_id,
        )
    spawn_environment(prefix, night=spec["short"] == "M04")

    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Could not save governed map: " + spec["map"])
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
        "objective_anchors": len(spec["objective_locations"]),
        "landmarks": len(spec["landmarks"]),
        "mission_exclusive_landmarks": sum(1 for item in spec["landmarks"] if item[3]),
        "hero_placeholder_count": len(spec["placements"]),
        "shared_block_count": len(spec["shared_blocks"]),
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
        "map_root": MAP_ROOT,
        "map_count": len(maps),
        "spec_sha256": canonical_spec_hash(),
        "maps": maps,
        "limitations": [
            "Maps use proxy/reusable meshes and primitive terrain surfaces.",
            "No map is claimed as final art, lighting, audio, mission scripting, boss implementation, or packaged playability.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_WAVE1_MAP_BUILD " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
