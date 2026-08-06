"""Fresh-process persistence audit for governed Phase 7 campaign data."""

import json
import math
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_skyguard_phase7_campaign_v1 as source


REPORT_PATH = ROOT / "Saved/Reports/PHASE7_CAMPAIGN_V1_PERSISTENCE_AUDIT.json"


def name_text(value):
    return str(value)


def vector_tuple(vector):
    return (float(vector.x), float(vector.y), float(vector.z))


def close_vector(actual, expected, tolerance=0.01):
    return all(
        math.isclose(a, float(e), abs_tol=tolerance)
        for a, e in zip(actual, expected)
    )


def normalize_asset_path(path):
    return str(path).split(".", 1)[0]


def native_validation(asset):
    result = asset.validate_definition()
    if isinstance(result, tuple):
        valid = bool(result[0])
        errors = [str(item) for item in result[1]] if len(result) > 1 else []
        return valid, errors
    # UE Python collapses this C++ signature to the single OutErrors array:
    # bool ValidateDefinition(TArray<FText>& OutErrors). An empty returned array
    # therefore means the native validator accepted the definition.
    if isinstance(result, list) or type(result).__name__.endswith("Array"):
        errors = [str(item) for item in result]
        return not errors, errors
    return bool(result), []


def main():
    checks = {}
    failures = []

    persisted_paths = sorted(
        {
            normalize_asset_path(path)
            for path in unreal.EditorAssetLibrary.list_assets(
                source.ASSET_ROOT, recursive=True, include_folder=False
            )
        }
    )
    expected_paths = sorted(
        [source.CAMPAIGN_PATH]
        + [
            source.ASSET_ROOT + "/DA_Mission_" + spec["id"]
            for spec in source.MISSIONS
        ]
    )
    checks["exact_governed_asset_set"] = persisted_paths == expected_paths
    if not checks["exact_governed_asset_set"]:
        failures.append("Governed folder does not contain exactly eleven expected assets")

    mission_assets = []
    mission_reports = []
    route_signatures = set()
    weather_profiles = set()
    boss_ids = set()
    exclusive_objectives = set()

    for order, spec in enumerate(source.MISSIONS, start=1):
        path = source.ASSET_ROOT + "/DA_Mission_" + spec["id"]
        asset = unreal.EditorAssetLibrary.load_asset(path)
        mission_assets.append(asset)
        entry_checks = {}
        if asset is None:
            failures.append("Missing mission asset " + path)
            mission_reports.append({"path": path, "checks": {"loaded": False}})
            continue

        entry_checks["loaded"] = True
        entry_checks["class"] = asset.get_class().get_name() == "SkyguardMissionDefinition"
        entry_checks["mission_id"] = name_text(
            asset.get_editor_property("mission_id")
        ) == spec["id"]
        entry_checks["campaign_order"] = (
            int(asset.get_editor_property("campaign_order")) == order
        )
        entry_checks["required_campaign_medals"] = (
            int(asset.get_editor_property("required_campaign_medals"))
            == spec["medals"]
        )
        prerequisites = [
            name_text(item)
            for item in asset.get_editor_property("prerequisite_mission_ids")
        ]
        expected_prerequisites = (
            [source.MISSIONS[order - 2]["id"]] if order > 1 else []
        )
        entry_checks["linear_prerequisite"] = prerequisites == expected_prerequisites

        route = asset.get_editor_property("route")
        points = list(route.get_editor_property("points"))
        route_locations = [
            vector_tuple(point.get_editor_property("world_location"))
            for point in points
        ]
        entry_checks["route_id"] = name_text(
            route.get_editor_property("route_id")
        ) == spec["id"] + "_Route"
        entry_checks["route_points"] = len(points) == 4 and all(
            close_vector(actual, expected)
            for actual, expected in zip(route_locations, spec["route"])
        )
        route_signatures.add(tuple(route_locations))

        objectives = list(asset.get_editor_property("objectives"))
        objective_ids = {
            name_text(item.get_editor_property("objective_id"))
            for item in objectives
        }
        expected_objectives = {
            spec["protect"][0],
            spec["exclusive"][0],
            "Defeat" + spec["boss"],
        }
        entry_checks["objectives"] = (
            len(objectives) == 3 and objective_ids == expected_objectives
        )
        exclusive_objectives.add(spec["exclusive"][0])

        waves = list(asset.get_editor_property("waves"))
        entry_checks["waves_and_formations"] = (
            len(waves) == 3
            and all(len(list(wave.get_editor_property("formations"))) == 1 for wave in waves)
        )

        boss = asset.get_editor_property("boss")
        persisted_boss = name_text(boss.get_editor_property("boss_id"))
        weakpoints = list(boss.get_editor_property("weak_points"))
        weakpoint_ids = [
            name_text(item.get_editor_property("weak_point_id"))
            for item in weakpoints
        ]
        entry_checks["boss"] = persisted_boss == spec["boss"]
        entry_checks["boss_weakpoint_graph"] = (
            weakpoint_ids == [item[0] for item in spec["weakpoints"]]
            and name_text(boss.get_editor_property("defeat_objective_id"))
            == "Defeat" + spec["boss"]
        )
        boss_ids.add(persisted_boss)

        weather = asset.get_editor_property("weather")
        persisted_weather_profile = name_text(
            weather.get_editor_property("profile_id")
        )
        entry_checks["weather_profile"] = (
            persisted_weather_profile == spec["weather"][0]
        )
        weather_profiles.add(persisted_weather_profile)

        presentation = asset.get_editor_property("presentation")
        entry_checks["presentation"] = (
            bool(str(presentation.get_editor_property("briefing")).strip())
            and len(list(presentation.get_editor_property("radio_chatter"))) == 3
            and bool(str(presentation.get_editor_property("success_debrief")).strip())
            and bool(str(presentation.get_editor_property("failure_debrief")).strip())
        )

        entry_checks["governance_metadata"] = (
            unreal.EditorAssetLibrary.get_metadata_tag(
                asset, "Skyguard.GovernedVersion"
            )
            == source.GOVERNANCE_VERSION
            and unreal.EditorAssetLibrary.get_metadata_tag(
                asset, "Skyguard.ContentState"
            )
            == "DefinitionOnly_NoFinishedMapOrArt"
        )
        try:
            valid, validation_errors = native_validation(asset)
        except Exception as exc:
            valid, validation_errors = False, ["exception: " + str(exc)]
        entry_checks["native_validation"] = valid and not validation_errors

        failed_entry_checks = [
            key for key, passed in entry_checks.items() if not passed
        ]
        if failed_entry_checks:
            failures.append(
                "%s failed: %s" % (spec["id"], ", ".join(failed_entry_checks))
            )
        mission_reports.append(
            {
                "path": path,
                "mission_id": spec["id"],
                "boss": persisted_boss,
                "route_signature": route_locations,
                "objective_ids": sorted(objective_ids),
                "weakpoint_ids": weakpoint_ids,
                "native_validation_errors": validation_errors,
                "checks": entry_checks,
            }
        )

    checks["ten_missions_loaded"] = (
        len(mission_assets) == 10 and all(asset is not None for asset in mission_assets)
    )
    checks["routes_are_distinct"] = len(route_signatures) == 10
    checks["weather_profiles_are_distinct"] = len(weather_profiles) == 10
    checks["bosses_are_distinct"] = len(boss_ids) == 10
    checks["exclusive_objectives_are_distinct"] = len(exclusive_objectives) == 10

    campaign = unreal.EditorAssetLibrary.load_asset(source.CAMPAIGN_PATH)
    checks["campaign_loaded"] = campaign is not None
    campaign_errors = []
    if campaign:
        checks["campaign_class"] = (
            campaign.get_class().get_name() == "SkyguardCampaignDefinition"
        )
        checks["campaign_id"] = name_text(
            campaign.get_editor_property("campaign_id")
        ) == "Skyguard52MainCampaign"
        campaign_missions = list(campaign.get_editor_property("missions"))
        checks["campaign_mission_order"] = [
            name_text(mission.get_editor_property("mission_id"))
            for mission in campaign_missions
        ] == [spec["id"] for spec in source.MISSIONS]
        checks["campaign_governance_metadata"] = (
            unreal.EditorAssetLibrary.get_metadata_tag(
                campaign, "Skyguard.GovernedVersion"
            )
            == source.GOVERNANCE_VERSION
        )
        try:
            campaign_valid, campaign_errors = native_validation(campaign)
        except Exception as exc:
            campaign_valid, campaign_errors = False, ["exception: " + str(exc)]
        checks["campaign_native_validation"] = (
            campaign_valid and not campaign_errors
        )

    for key, passed in checks.items():
        if not passed:
            failures.append("Campaign check failed: " + key)

    report = {
        "gate": "PASS" if not failures else "FAIL",
        "governance_version": source.GOVERNANCE_VERSION,
        "content_scope": "data_definitions_only_not_completed_art_or_maps",
        "fresh_process_requirement": True,
        "spec_sha256": source.canonical_spec_hash(),
        "persisted_asset_paths": persisted_paths,
        "checks": checks,
        "campaign_native_validation_errors": campaign_errors,
        "missions": mission_reports,
        "failures": failures,
        "limitations": [
            "Mission map soft references intentionally remain unassigned until each governed map exists.",
            "This audit does not prove level geometry, art, lighting, audio, Blueprint hookups, map travel, or packaged gameplay.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("PHASE7_CAMPAIGN_AUDIT " + json.dumps(report, sort_keys=True))
    if failures:
        raise RuntimeError("Phase 7 campaign persistence audit failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
