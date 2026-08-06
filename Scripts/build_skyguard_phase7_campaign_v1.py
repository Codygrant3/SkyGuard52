"""Generate the governed Skyguard 52 campaign-definition asset set.

This script creates data definitions only. It does not generate level geometry,
finished maps, art, audio, or playable mission assemblies.
"""

import hashlib
import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ASSET_ROOT = "/Game/Skyguard/Data/Campaign_v1"
CAMPAIGN_PATH = ASSET_ROOT + "/DA_Campaign_Skyguard52"
REPORT_PATH = ROOT / "Saved/Reports/PHASE7_CAMPAIGN_V1_BUILD.json"
GOVERNANCE_VERSION = "Campaign_v1"


MISSIONS = [
    {
        "id": "M01_CoastalIntercept",
        "name": "Coastal Intercept",
        "boss": "Pathfinder",
        "weather": ("ClearNoon", "CLEAR", 13.5, 5.0, 0.0, 0.20),
        "route": [(0, -18000, 6500), (32000, -15000, 6000), (65000, -9000, 5200), (95000, 1000, 5800)],
        "protect": ("ProtectCoastalRadar", "Protect the coastal radar"),
        "exclusive": ("DisableCommandNetwork", "Disable Pathfinder's command network", "SCAN_TARGETS", 2),
        "weakpoints": [("CommandAntenna", "Rifle", "NoseCamera"), ("NoseCamera", "Rifle", "Engine"), ("Engine", "Igla", "ControlLinkage"), ("ControlLinkage", "Rifle", "")],
        "briefing": "Intercept the low-altitude formation before Pathfinder can direct it across the beach.",
        "radio": ["Coastal radar has multiple tracks.", "Keep the city behind your firing arc.", "Pathfinder is coordinating the formation."],
        "success": "Command drone destroyed. Coastal radar remains operational.",
        "failure": "The formation crossed the defensive line.",
        "medals": 0,
    },
    {
        "id": "M02_HarborShield",
        "name": "Harbor Shield",
        "boss": "Breakwater",
        "weather": ("HarborOvercast", "OVERCAST", 15.0, 7.0, 0.0, 0.75),
        "route": [(0, 26000, 5200), (27000, 30000, 4700), (56000, 23000, 4300), (90000, 16000, 5200)],
        "protect": ("ProtectFuelTerminal", "Protect the fuel terminal"),
        "exclusive": ("StripArmorPanels", "Strip Breakwater's armor panels", "DESTROY_TARGETS", 2),
        "weakpoints": [("PortLatch", "Rifle", "StarboardLatch"), ("StarboardLatch", "Rifle", "DecoyPods"), ("DecoyPods", "Rifle", "Engine"), ("Engine", "Igla", "")],
        "briefing": "Defend the harbor fuel terminal while Breakwater uses cranes to mask its approach.",
        "radio": ["Harbor control reports an armored contact.", "Expect line-of-sight breaks behind cranes.", "Decoys must be suppressed before lock."],
        "success": "Breakwater is down in the harbor. Fuel storage is secure.",
        "failure": "The fuel terminal has sustained catastrophic damage.",
        "medals": 1,
    },
    {
        "id": "M03_ConvoyEscort",
        "name": "Convoy Escort",
        "boss": "RoadHunter",
        "weather": ("DryMorning", "CLEAR", 8.0, 4.0, 0.0, 0.12),
        "route": [(0, -5000, 7000), (23000, 7000, 6400), (51000, 22000, 6100), (84000, 39000, 6900)],
        "protect": ("ProtectConvoyCore", "Keep the convoy core alive"),
        "exclusive": ("BlindTargetingCamera", "Blind Road Hunter's targeting camera", "DESTROY_TARGETS", 1),
        "weakpoints": [("TargetingCamera", "Rifle", "LeftActuator"), ("LeftActuator", "Rifle", "Engine"), ("RightActuator", "Rifle", "Engine"), ("Engine", "Igla", "")],
        "briefing": "Escort the relief convoy through repeated ridge-to-highway crossing attacks.",
        "radio": ["Convoy is entering the exposed highway.", "Road Hunter is predicting the lead vehicle.", "Choose the orbit that exposes its camera."],
        "success": "The protected convoy core reached the tunnel.",
        "failure": "The convoy core has been destroyed.",
        "medals": 2,
    },
    {
        "id": "M04_NightBlackout",
        "name": "Night Blackout",
        "boss": "BlackKite",
        "weather": ("BlackoutNight", "NIGHT_OVERCAST", 22.5, 3.0, 0.0, 0.82),
        "route": [(0, 12000, 5800), (30000, 5000, 5100), (59000, -7000, 4800), (88000, -15000, 5600)],
        "protect": ("ProtectSubstation", "Protect the emergency substation"),
        "exclusive": ("HoldSearchlightTrack", "Hold Black Kite in the searchlight track", "SCAN_TARGETS", 3),
        "weakpoints": [("PortNavigationVane", "Rifle", "Jammer"), ("StarboardNavigationVane", "Rifle", "Jammer"), ("Jammer", "Rifle", "PowerBus"), ("PowerBus", "Igla", "")],
        "briefing": "Locate Black Kite by sound and searchlight while the waterfront grid is blacked out.",
        "radio": ["Visual contact will be intermittent.", "Searchlight crews are tracking your bearing.", "Listen for the engine before committing fire."],
        "success": "Black Kite destroyed. Emergency power remains online.",
        "failure": "The emergency substation has failed.",
        "medals": 3,
    },
    {
        "id": "M05_StormFront",
        "name": "Storm Front",
        "boss": "Tempest",
        "weather": ("SevereSquall", "STORM", 17.0, 22.0, 0.92, 1.0),
        "route": [(0, -32000, 8300), (25000, -22000, 7600), (50000, -3000, 6900), (78000, 19000, 7800)],
        "protect": ("ProtectOffshoreCrew", "Protect the distressed trawler"),
        "exclusive": ("DisableDischargeBooms", "Disable Tempest's discharge booms", "DESTROY_TARGETS", 2),
        "weakpoints": [("PortDischargeBoom", "Rifle", "ControlServo"), ("StarboardDischargeBoom", "Rifle", "ControlServo"), ("ControlServo", "Rifle", "EngineIntake"), ("EngineIntake", "Igla", "")],
        "briefing": "Fight through a severe squall to shield a distressed trawler from Tempest.",
        "radio": ["Lightning will silhouette the target.", "Do not hold lock through an active discharge boom.", "Debris warning after the missile strike."],
        "success": "Tempest destroyed. The trawler crew is recovering.",
        "failure": "The distressed vessel has been lost.",
        "medals": 4,
    },
    {
        "id": "M06_AirfieldDefense",
        "name": "Airfield Defense",
        "boss": "RunwayBreaker",
        "weather": ("AirfieldHaze", "OVERCAST", 10.0, 6.0, 0.0, 0.55),
        "route": [(0, 18000, 6600), (28000, 9000, 5900), (57000, 12000, 5300), (92000, 25000, 6200)],
        "protect": ("ProtectAirfieldAssets", "Save at least two airfield targets"),
        "exclusive": ("JamPayloadRacks", "Jam Runway Breaker's payload racks", "DESTROY_TARGETS", 2),
        "weakpoints": [("RunwayRack", "Rifle", "HeatManifold"), ("HangarRack", "Rifle", "HeatManifold"), ("HeatManifold", "Rifle", "PortEngine"), ("PortEngine", "Igla", "")],
        "briefing": "Stop Runway Breaker from striking the runway, hangars, and parked aircraft.",
        "radio": ["Payload doors identify the next target.", "Prioritize the opening rack.", "Asymmetric power will expose the second engine."],
        "success": "The airfield can continue defensive operations.",
        "failure": "All protected airfield targets are disabled.",
        "medals": 6,
    },
    {
        "id": "M07_SearchIntercept",
        "name": "Search and Intercept",
        "boss": "RadarGhost",
        "weather": ("IslandMist", "RAIN", 6.5, 9.0, 0.35, 0.68),
        "route": [(0, -24000, 7600), (21000, -8000, 7200), (47000, 11000, 6700), (79000, 28000, 7400)],
        "protect": ("ProtectRadarChain", "Keep the island radar chain online"),
        "exclusive": ("ClassifyFalseTracks", "Classify and clear false radar tracks", "SCAN_TARGETS", 3),
        "weakpoints": [("SignatureModulator", "Rifle", "RadarReceiver"), ("RadarReceiver", "Rifle", "CoolingDoor"), ("CoolingDoor", "Rifle", "Engine"), ("Engine", "Igla", "")],
        "briefing": "Search the island chain, classify false tracks, and expose Radar Ghost.",
        "radio": ["Fishing traffic is inside the search sector.", "Confirm identity before firing.", "Radar Ghost is altering its return."],
        "success": "Radar Ghost destroyed and the navigation corridor reopened.",
        "failure": "The island radar chain has gone dark.",
        "medals": 8,
    },
    {
        "id": "M08_RescueCover",
        "name": "Rescue Cover",
        "boss": "LifelineHunter",
        "weather": ("RescueSunset", "OVERCAST", 19.2, 8.0, 0.0, 0.62),
        "route": [(0, 9000, 6200), (18000, 21000, 5500), (39000, 18000, 5000), (62000, 4000, 6100)],
        "protect": ("ProtectRescueFlight", "Protect the rescue helicopter and survivors"),
        "exclusive": ("CompleteHoistWindows", "Hold cover through survivor hoist windows", "RESCUE", 3),
        "weakpoints": [("OpticalTracker", "Rifle", "WeaponServo"), ("WeaponServo", "Rifle", "CountermeasurePod"), ("CountermeasurePod", "Rifle", "Engine"), ("Engine", "Igla", "")],
        "briefing": "Orbit the rescue zone and keep Lifeline Hunter away during three hoist windows.",
        "radio": ["Rescue One is beginning the first hoist.", "Avoid firing through the helicopter.", "Hunter is turning toward the survivors."],
        "success": "All survivors recovered. Rescue flight is clear.",
        "failure": "The rescue flight or survivor group has been lost.",
        "medals": 10,
    },
    {
        "id": "M09_SaturationAttack",
        "name": "Saturation Attack",
        "boss": "IronRain",
        "weather": ("CityDusk", "OVERCAST", 20.1, 11.0, 0.08, 0.78),
        "route": [(0, -10000, 8800), (26000, 5000, 8000), (52000, 17000, 7400), (90000, 9000, 8300)],
        "protect": ("ProtectCityInfrastructure", "Keep two infrastructure nodes operational"),
        "exclusive": ("BreakSwarmRelays", "Break Iron Rain's swarm relays", "DESTROY_TARGETS", 3),
        "weakpoints": [("PortRelay", "Rifle", "CommandCore"), ("CenterRelay", "Rifle", "CommandCore"), ("StarboardRelay", "Rifle", "CommandCore"), ("CommandCore", "Igla", "")],
        "briefing": "Prioritize simultaneous threats while Iron Rain coordinates a metropolitan saturation attack.",
        "radio": ["Multiple waves are crossing separate sectors.", "Power station and bridge are both under threat.", "Break the relays to disrupt the swarm."],
        "success": "Iron Rain destroyed. Critical city infrastructure survived.",
        "failure": "The protected infrastructure network has collapsed.",
        "medals": 12,
    },
    {
        "id": "M10_EvacuationFinale",
        "name": "Evacuation Finale",
        "boss": "LastFlight",
        "weather": ("EvacuationDawn", "RAIN", 5.4, 13.0, 0.50, 0.88),
        "route": [(0, 30000, 9200), (24000, 19000, 8300), (55000, 2000, 7600), (98000, -18000, 8600)],
        "protect": ("ProtectEvacuationHub", "Protect the ferry and civilian convoy hub"),
        "exclusive": ("ClearEvacuationLanes", "Clear all evacuation attack lanes", "SURVIVE", 4),
        "weakpoints": [("JammerArray", "Rifle", "PayloadController"), ("PayloadController", "Rifle", "ArmorSeam"), ("ArmorSeam", "Rifle", "TwinEngineCore"), ("TwinEngineCore", "Igla", "")],
        "briefing": "Hold the evacuation corridor against Last Flight while the final ferry and convoy depart.",
        "radio": ["The ferry cannot leave until the lane is clear.", "Ambulances are still entering the terminal.", "Last Flight is beginning its final attack."],
        "success": "Evacuation complete. Last Flight has been destroyed.",
        "failure": "The evacuation hub was overrun before departure.",
        "medals": 15,
    },
]


def enum_value(enum_type, name):
    return getattr(enum_type, name)


def make_struct(struct_type, values):
    instance = struct_type()
    for key, value in values.items():
        instance.set_editor_property(key, value)
    return instance


def route_definition(spec):
    points = []
    for index, location in enumerate(spec["route"]):
        points.append(
            make_struct(
                unreal.SkyguardRoutePoint,
                {
                    "point_id": unreal.Name("P%02d" % (index + 1)),
                    "world_location": unreal.Vector(*location),
                    "target_airspeed_kph": 210.0 + (index * 8.0),
                    "look_ahead_seconds": 2.0 + (index * 0.25),
                    "allow_combat_orbit": index in (1, 2),
                },
            )
        )
    return make_struct(
        unreal.SkyguardRouteDefinition,
        {"route_id": unreal.Name(spec["id"] + "_Route"), "points": points},
    )


def objective_definitions(spec):
    boss = make_struct(
        unreal.SkyguardObjectiveDefinition,
        {
            "objective_id": unreal.Name("Defeat" + spec["boss"]),
            "display_name": "Defeat " + spec["boss"],
            "type": enum_value(unreal.SkyguardMissionObjectiveType, "BOSS_PHASE"),
            "required_progress": 4,
            "required_for_mission_success": True,
            "failure_ends_mission": False,
            "score_reward": 3000,
        },
    )
    protect = make_struct(
        unreal.SkyguardObjectiveDefinition,
        {
            "objective_id": unreal.Name(spec["protect"][0]),
            "display_name": spec["protect"][1],
            "type": enum_value(unreal.SkyguardMissionObjectiveType, "PROTECT_ASSET"),
            "required_progress": 1,
            "required_for_mission_success": True,
            "failure_ends_mission": True,
            "score_reward": 2000,
        },
    )
    exclusive = make_struct(
        unreal.SkyguardObjectiveDefinition,
        {
            "objective_id": unreal.Name(spec["exclusive"][0]),
            "display_name": spec["exclusive"][1],
            "type": enum_value(
                unreal.SkyguardMissionObjectiveType, spec["exclusive"][2]
            ),
            "required_progress": spec["exclusive"][3],
            "required_for_mission_success": False,
            "failure_ends_mission": False,
            "score_reward": 1500,
        },
    )
    return [protect, exclusive, boss]


def wave_definitions(spec, boss_objective_id):
    formation_names = ("VEE", "ECHELON_LEFT", "LOOSE_SWARM")
    waves = []
    for index in range(3):
        formation = make_struct(
            unreal.SkyguardEnemyFormationDefinition,
            {
                "formation_id": unreal.Name(
                    "%s_Formation_%02d" % (spec["id"], index + 1)
                ),
                "formation": enum_value(
                    unreal.SkyguardFormationType, formation_names[index]
                ),
                "unit_count": 2 + index + (1 if spec["id"].startswith(("M09", "M10")) else 0),
                "spacing_centimeters": 1000.0 + (index * 350.0),
            },
        )
        waves.append(
            make_struct(
                unreal.SkyguardEnemyWaveDefinition,
                {
                    "wave_id": unreal.Name(
                        "%s_Wave_%02d" % (spec["id"], index + 1)
                    ),
                    "start_time_seconds": float(index * 75),
                    "formations": [formation],
                    "completion_objective_id": (
                        boss_objective_id if index == 2 else unreal.Name("")
                    ),
                },
            )
        )
    return waves


def boss_definition(spec):
    weakpoints = []
    for weakpoint_id, weapon, exposes in spec["weakpoints"]:
        weakpoints.append(
            make_struct(
                unreal.SkyguardBossWeakPointDefinition,
                {
                    "weak_point_id": unreal.Name(weakpoint_id),
                    "required_weapon": unreal.Name(weapon),
                    "exposes_weak_point_id": unreal.Name(exposes),
                    "integrity": 100.0 if weapon == "Rifle" else 250.0,
                },
            )
        )
    return make_struct(
        unreal.SkyguardBossDefinition,
        {
            "boss_id": unreal.Name(spec["boss"]),
            "callsign": spec["boss"],
            "weak_points": weakpoints,
            "defeat_objective_id": unreal.Name("Defeat" + spec["boss"]),
            "maximum_breakup_pieces": (
                4
                if spec["id"] == "M01_CoastalIntercept"
                else (3 if spec["id"].startswith("M0") else 6)
            ),
        },
    )


def weather_profile(spec):
    profile, weather, time_of_day, wind, precipitation, cloud = spec["weather"]
    return make_struct(
        unreal.SkyguardWeatherProfile,
        {
            "profile_id": unreal.Name(profile),
            "weather": enum_value(unreal.SkyguardMissionWeather, weather),
            "time_of_day_hours": float(time_of_day),
            "wind_speed_meters_per_second": float(wind),
            "precipitation": float(precipitation),
            "cloud_coverage": float(cloud),
        },
    )


def presentation(spec):
    return make_struct(
        unreal.SkyguardMissionPresentation,
        {
            "briefing": spec["briefing"],
            "radio_chatter": spec["radio"],
            "success_debrief": spec["success"],
            "failure_debrief": spec["failure"],
            "minimum_briefing_warmup_seconds": 3.0,
        },
    )


def score_rules(order):
    return make_struct(
        unreal.SkyguardMissionScoreRules,
        {
            "completion_score": 5000 + ((order - 1) * 250),
            "perfect_accuracy_bonus": 2500,
            "no_damage_bonus": 1500,
            "bronze_threshold": 7000 + ((order - 1) * 250),
            "silver_threshold": 9500 + ((order - 1) * 250),
            "gold_threshold": 12000 + ((order - 1) * 250),
        },
    )


def create_or_load_data_asset(asset_name, asset_class):
    asset_path = ASSET_ROOT + "/" + asset_name
    asset = (
        unreal.EditorAssetLibrary.load_asset(asset_path)
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path)
        else None
    )
    if asset:
        if asset.get_class().get_path_name() != asset_class.get_path_name():
            raise RuntimeError("Governed path contains the wrong class: " + asset_path)
        return asset
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", asset_class)
    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, ASSET_ROOT, asset_class, factory
    )
    if not asset:
        raise RuntimeError("Could not create " + asset_path)
    return asset


def canonical_spec_hash():
    return hashlib.sha256(
        json.dumps(MISSIONS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main():
    unreal.EditorAssetLibrary.make_directory(ASSET_ROOT)
    mission_class = unreal.SkyguardMissionDefinition.static_class()
    campaign_class = unreal.SkyguardCampaignDefinition.static_class()
    mission_assets = []
    report_missions = []

    for order, spec in enumerate(MISSIONS, start=1):
        asset_name = "DA_Mission_" + spec["id"]
        asset = create_or_load_data_asset(asset_name, mission_class)
        objectives = objective_definitions(spec)
        boss_objective_id = unreal.Name("Defeat" + spec["boss"])
        prerequisites = (
            [unreal.Name(MISSIONS[order - 2]["id"])] if order > 1 else []
        )
        asset.set_editor_property("mission_id", unreal.Name(spec["id"]))
        asset.set_editor_property("display_name", spec["name"])
        asset.set_editor_property("campaign_order", order)
        asset.set_editor_property("route", route_definition(spec))
        asset.set_editor_property("objectives", objectives)
        asset.set_editor_property(
            "waves", wave_definitions(spec, boss_objective_id)
        )
        asset.set_editor_property("boss", boss_definition(spec))
        asset.set_editor_property("weather", weather_profile(spec))
        asset.set_editor_property("presentation", presentation(spec))
        asset.set_editor_property("score_rules", score_rules(order))
        asset.set_editor_property("prerequisite_mission_ids", prerequisites)
        asset.set_editor_property("required_campaign_medals", spec["medals"])
        unreal.EditorAssetLibrary.set_metadata_tag(
            asset, "Skyguard.GovernedVersion", GOVERNANCE_VERSION
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            asset, "Skyguard.ContentState", "DefinitionOnly_NoFinishedMapOrArt"
        )
        if not unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False):
            raise RuntimeError("Could not save mission asset: " + asset_name)
        mission_assets.append(asset)
        report_missions.append(
            {
                "path": ASSET_ROOT + "/" + asset_name,
                "mission_id": spec["id"],
                "order": order,
                "boss": spec["boss"],
                "route_points": len(spec["route"]),
                "objectives": len(objectives),
                "waves": 3,
                "weak_points": len(spec["weakpoints"]),
                "required_campaign_medals": spec["medals"],
            }
        )

    campaign = create_or_load_data_asset("DA_Campaign_Skyguard52", campaign_class)
    campaign.set_editor_property("campaign_id", unreal.Name("Skyguard52MainCampaign"))
    campaign.set_editor_property("display_name", "Skyguard 52")
    campaign.set_editor_property("missions", mission_assets)
    unreal.EditorAssetLibrary.set_metadata_tag(
        campaign, "Skyguard.GovernedVersion", GOVERNANCE_VERSION
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        campaign, "Skyguard.ContentState", "DefinitionOnly_NoFinishedMapOrArt"
    )
    if not unreal.EditorAssetLibrary.save_loaded_asset(campaign, only_if_is_dirty=False):
        raise RuntimeError("Could not save campaign asset")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "gate": "BUILT_PENDING_FRESH_PROCESS_AUDIT",
        "governance_version": GOVERNANCE_VERSION,
        "content_scope": "data_definitions_only_not_completed_art_or_maps",
        "asset_root": ASSET_ROOT,
        "campaign_path": CAMPAIGN_PATH,
        "mission_count": len(mission_assets),
        "spec_sha256": canonical_spec_hash(),
        "missions": report_missions,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_CAMPAIGN_BUILD " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
