from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionMapAssemblyDirector.h"
CLASS_NAME = "ASkyguardMissionMapAssemblyDirector"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the RebuildRouteSpline body in the .cpp.
# origin/main is one line
# (`void RebuildRouteSpline();`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Nearby origin/main
# UFUNCTION(BlueprintCallable, Category = "Skyguard|MissionMap")
# is accepted as present. Parse the public class section of
# ASkyguardMissionMapAssemblyDirector only. Do not parse
# leftover skyline-style enum #e017
# ESkyguardMissionSkylineStyle, leftover
# objective-anchor defaults #692c
# FSkyguardMissionObjectiveAnchor, leftover
# landmark-anchor defaults #4230
# FSkyguardMissionLandmarkAnchor, or leftover
# map-readiness defaults #3a2a
# FSkyguardMissionMapReadiness. Leftover
# skyline-style enum value HarborIndustrial is leftover
# skyline-style enum, not a leftover Harbor clock token.
# Leftover briefing-fail-closed #9fe9, leftover briefing
# declaration contracts through GetRadioChatter,
# leftover pathfinder AdvanceEncounter through
# GetTelegraphsTriggered, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover campaign-roster #111,
# leftover campaign-save empty-fail-closed, leftover
# Gunner helpers, leftover ApacheSystem / weapon
# stations / pilot commands / loadout / lock-phase,
# leftover Harbor clocks, leftover theater-kit /
# flare / HUD, leftover settings invert-look /
# ApplySettings, leftover bind-hud-host, leftover
# objective-runtime / route-runtime fail-closed,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover ValidateAssembly
# (sibling this wave), leftover
# IsPointInsideFlightClearance, leftover GetReadiness,
# leftover UPROPERTY fields, leftover skyline-style
# enum, leftover objective-anchor defaults, leftover
# landmark-anchor defaults, and leftover
# map-readiness defaults stay sibling-only.
REBUILD_ROUTE_SPLINE = "void RebuildRouteSpline();"
UFUNCTION_MISSION_MAP = (
    'UFUNCTION(BlueprintCallable, Category = "Skyguard|MissionMap")'
)
# Leftover #56–#64 plus MissionMapAssemblyDirector
# production files. This lane only adds an isolated
# Python RebuildRouteSpline declaration contract. Stay
# off ValidateAssembly (sibling this wave),
# IsPointInsideFlightClearance, GetReadiness,
# UPROPERTY fields, leftover skyline-style enum
# #e017, leftover objective-anchor defaults #692c,
# leftover landmark-anchor defaults #4230, leftover
# map-readiness defaults #3a2a, leftover
# briefing-fail-closed, leftover briefing
# declaration contracts, leftover pathfinder
# AdvanceEncounter through GetTelegraphsTriggered,
# leftover mission-briefing-state enum, leftover
# radio-chatter empty-fail-closed, leftover
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover Gunner helpers,
# leftover Harbor clocks, leftover theater-kit /
# flare / HUD, leftover drafts #56–#64, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout / lock-phase, leftover settings invert-look
# / ApplySettings broadcast, leftover bind-hud-host,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover gun-fire
# camera shake, leftover mission-weather enum,
# leftover mission 0N integration readiness, and
# dirty workspace paths.
LOCKED = {
    "SkyguardMissionMapAssemblyDirector.h",
    "SkyguardMissionMapAssemblyDirector.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
}
# Isolated-test drafts stay off this lane. Leftover
# skyline-style enum #e017, leftover
# mission-objective-anchor defaults #692c, leftover
# mission-landmark-anchor defaults #4230, leftover
# mission-map-readiness defaults #3a2a, leftover
# briefing-fail-closed #9fe9, leftover briefing
# declaration contracts through GetRadioChatter,
# leftover pathfinder AdvanceEncounter through
# GetTelegraphsTriggered, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover campaign-roster #111,
# leftover campaign-save empty-fail-closed, leftover
# CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare / HUD, leftover ApacheSystem /
# weapon stations / pilot commands / loadout,
# leftover settings invert-look, leftover
# bind-hud-host, leftover gun-fire camera shake,
# leftover mission-weather enum, leftover
# ValidateAssembly, leftover
# IsPointInsideFlightClearance, leftover
# GetReadiness, leftover UPROPERTY fields, leftover
# skyline-style enum, leftover objective-anchor
# defaults, leftover landmark-anchor defaults, and
# leftover map-readiness defaults stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_mission_objective_anchor_defaults_contract.py",
    "Scripts/tests/test_mission_landmark_anchor_defaults_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_briefing_advance_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_acknowledge_and_launch_decl_contract.py",
    "Scripts/tests/test_briefing_can_launch_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_state_decl_contract.py",
    "Scripts/tests/test_briefing_get_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_get_radio_chatter_decl_contract.py",
    "Scripts/tests/test_pathfinder_advance_encounter_decl_contract.py",
    "Scripts/tests/test_pathfinder_reset_encounter_state_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_route_state_safe_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_route_progress_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_telegraphs_triggered_decl_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum.py",
    "Scripts/tests/test_mission_briefing_state_enum_tests.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_mission_definition_waves_decl_contract.py",
    "Scripts/tests/test_mission_definition_weather_decl_contract.py",
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_mission_definition_presentation_decl_contract.py",
    "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
    "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
    "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
    "Scripts/tests/test_mission_definition_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_find_objective_decl_contract.py",
    "Scripts/tests/test_mission_definition_validate_definition_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_empty_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_confirm_command_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_line_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_text_decl_contract.py",
    "Scripts/tests/test_pilot_make_radio_line_decl_contract.py",
    "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
    "Scripts/tests/test_pilot_voice_call_probe.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. ValidateAssembly (sibling this wave) /
# IsPointInsideFlightClearance / GetReadiness /
# leftover UPROPERTY fields stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "ASkyguardMissionMapAssemblyDirector();",
    "virtual void OnConstruction(const FTransform& Transform) override;",
    "bool ValidateAssembly(TArray<FText>& OutErrors);",
    "bool IsPointInsideFlightClearance(const FVector& WorldPoint) const;",
    "const FSkyguardMissionMapReadiness& GetReadiness() const;",
)
VALIDATE_ASSEMBLY_NOT_LOCKED = (
    "bool ValidateAssembly(TArray<FText>& OutErrors);",
)
IS_POINT_INSIDE_NOT_LOCKED = (
    "bool IsPointInsideFlightClearance(const FVector& WorldPoint) const;",
)
GET_READINESS_NOT_LOCKED = (
    "const FSkyguardMissionMapReadiness& GetReadiness() const;",
)
# Leftover UPROPERTY fields stay unlocked.
UPROP_FIELDS_NOT_LOCKED = (
    "TObjectPtr<USceneComponent> Root;",
    "TObjectPtr<USplineComponent> FlightRouteSpline;",
    "TObjectPtr<USkyguardMissionDefinition> MissionDefinition;",
    "FName MissionId;",
    "FName AssemblyRevision = TEXT(\"CampaignMapAssembly_v1\");",
    "ESkyguardMissionSkylineStyle SkylineStyle =",
    "FName WeatherProfileId;",
    "TArray<FVector> RoutePoints;",
    "TArray<FSkyguardMissionObjectiveAnchor> ObjectiveAnchors;",
    "TArray<FSkyguardMissionLandmarkAnchor> LandmarkAnchors;",
    "float FlightClearanceRadiusCentimeters = 3000.f;",
    "float FlightClearanceVerticalCentimeters = 2500.f;",
    "FSkyguardMissionMapReadiness Readiness;",
)
# Leftover skyline-style enum #e017 stays unlocked.
# Leftover enum value HarborIndustrial is leftover
# skyline-style enum, not a leftover Harbor clock.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "test_mission_skyline_style_enum_contract.py",
    "enum class ESkyguardMissionSkylineStyle",
    "HarborIndustrial",
    "CoastalHighway",
    "BlackoutUrban",
    "OffshoreStorm",
    "AirfieldMilitary",
    "IslandSearch",
)
# Leftover objective-anchor defaults #692c stay unlocked.
LEFTOVER_OBJECTIVE_ANCHOR_NOT_LOCKED = (
    "test_mission_objective_anchor_defaults_contract.py",
    "struct FSkyguardMissionObjectiveAnchor",
    "FName ObjectiveId;",
)
# Leftover landmark-anchor defaults #4230 stay unlocked.
LEFTOVER_LANDMARK_ANCHOR_NOT_LOCKED = (
    "test_mission_landmark_anchor_defaults_contract.py",
    "struct FSkyguardMissionLandmarkAnchor",
    "FName LandmarkId;",
    "bool bMissionExclusive = false;",
)
# Leftover map-readiness defaults #3a2a stay unlocked.
LEFTOVER_MAP_READINESS_NOT_LOCKED = (
    "test_mission_map_readiness_defaults_contract.py",
    "struct FSkyguardMissionMapReadiness",
    "bool bDefinitionValid = false;",
    "bool bRouteMatchesDefinition = false;",
    "float RouteLengthCentimeters = 0.f;",
)
# Leftover pathfinder AdvanceEncounter through
# GetTelegraphsTriggered stay unlocked.
LEFTOVER_PATHFINDER_NOT_LOCKED = (
    "test_pathfinder_advance_encounter_decl_contract.py",
    "test_pathfinder_reset_encounter_state_decl_contract.py",
    "test_pathfinder_is_route_state_safe_decl_contract.py",
    "test_pathfinder_get_route_progress_decl_contract.py",
    "test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "test_pathfinder_get_telegraphs_triggered_decl_contract.py",
    "void AdvanceEncounter(float DeltaSeconds);",
    "void ResetEncounterState(const FTransform& NewRouteOrigin);",
    "bool IsRouteStateSafe() const;",
    "float GetRouteProgress() const;",
    "float GetEffectiveSpeedMultiplier() const;",
    "bool IsAttackTelegraphActive() const;",
    "int32 GetTelegraphsTriggered() const;",
)
# Leftover mission-briefing-state enum stays unlocked.
LEFTOVER_ENUM_NOT_LOCKED = (
    "Unconfigured",
    "Warming",
    "Launched",
    "test_mission_briefing_state_enum_contract.py",
)
# Leftover briefing-fail-closed / leftover briefing-card
# defaults / leftover briefing-radio-row defaults /
# leftover radio-chatter empty-fail-closed stay unlocked.
LEFTOVER_BRIEFING_NOT_LOCKED = (
    "test_briefing_fail_closed.py",
    "test_briefing_fail_closed_tests.py",
    "test_briefing_fail_closed_contract.py",
    "test_briefing_card_defaults_contract.py",
    "test_briefing_radio_row_defaults_contract.py",
    "test_radio_chatter_empty_fail_closed.py",
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
)
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)
# Leftover CPG debrief copy / snapshot defaults /
# fail-closed / empty-capture stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover objective-runtime fail-closed / leftover
# route-runtime fail-closed stay unlocked.
LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED = (
    "SkyguardObjectiveRuntimeFailClosed",
    "SkyguardRouteRuntimeFailClosed",
    "ObjectiveRuntimeFailClosed",
    "RouteRuntimeFailClosed",
)
# Leftover ApacheSystem / weapon stations / pilot
# commands / loadout / lock-phase / invert-look /
# ApplySettings / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
)
# .cpp RebuildRouteSpline body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardMissionMapAssemblyDirector::RebuildRouteSpline",
    "SkyguardMissionMapAssemblyDirector.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_harbor_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        forty,
        eighty,
        forty + ", " + eighty,
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    return compact


def declaration_stem(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
    return compact


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    # Accept `;` or an inline `{` body after the signature
    # without locking that body.
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return pattern.search(compact_region) is not None


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return len(pattern.findall(compact_region))


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{HEADER_PATH} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def class_body(header: str) -> str:
    match = CLASS_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{CLASS_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index("{", match.start())
    depth = 0
    for index, char in enumerate(header[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[start : index + 1]
    raise AssertionError(
        f"{CLASS_NAME} class body is missing from origin/main:{HEADER_PATH}"
    )


def public_section(header: str) -> str:
    body = class_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        return rest[: next_access.start()]
    close = rest.rfind("}")
    if close == -1:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    return rest[:close]


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class MissionMapRebuildRouteSplineDeclContractTests(unittest.TestCase):
    def test_mission_map_director_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, REBUILD_ROUTE_SPLINE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API ASkyguardUnrelatedMissionMap "
                ": public AActor\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API AOtherMissionMapAssemblyDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{REBUILD_ROUTE_SPLINE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_skyline_style_enum_does_not_satisfy_class(self) -> None:
        enum_only = (
            "UENUM(BlueprintType)\n"
            "enum class ESkyguardMissionSkylineStyle : uint8\n"
            "{\n"
            "\tHarborIndustrial,\n"
            "\tCoastalHighway,\n"
            "\tBlackoutUrban,\n"
            "\tOffshoreStorm,\n"
            "\tAirfieldMilitary,\n"
            "\tIslandSearch\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(enum_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_objective_anchor_struct_does_not_satisfy_class(
        self,
    ) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionObjectiveAnchor\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tFName ObjectiveId;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_landmark_anchor_struct_does_not_satisfy_class(
        self,
    ) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionLandmarkAnchor\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tFName LandmarkId;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_map_readiness_struct_does_not_satisfy_class(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionMapReadiness\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tbool bDefinitionValid = false;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public AActor\n"
            "{\n"
            "private:\n"
            f"\t{REBUILD_ROUTE_SPLINE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_private_declaration_does_not_satisfy_public_lock(self) -> None:
        mixed = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tbool ValidateAssembly(TArray<FText>& OutErrors);\n"
            "private:\n"
            f"\t{REBUILD_ROUTE_SPLINE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, REBUILD_ROUTE_SPLINE)
        self.assertIn("RebuildRouteSpline", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, REBUILD_ROUTE_SPLINE))

    def test_missing_rebuild_route_spline_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tASkyguardMissionMapAssemblyDirector();\n"
            "\tvirtual void OnConstruction("
            "const FTransform& Transform) override;\n"
            "\tbool ValidateAssembly(TArray<FText>& OutErrors);\n"
            "\tbool IsPointInsideFlightClearance("
            "const FVector& WorldPoint) const;\n"
            "\tconst FSkyguardMissionMapReadiness& GetReadiness() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, REBUILD_ROUTE_SPLINE)
        self.assertIn("RebuildRouteSpline", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_MISSION_MAP}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, REBUILD_ROUTE_SPLINE)
        self.assertIn("RebuildRouteSpline", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_MISSION_MAP, section)
        self.assertTrue(
            has_declaration(section, REBUILD_ROUTE_SPLINE),
            section,
        )
        self.assertNotIn("BlueprintPure", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("UFUNCTION", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("Category", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("BlueprintCallable", REBUILD_ROUTE_SPLINE)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tbool ValidateAssembly(TArray<FText>& OutErrors);\n"
            "\tbool IsPointInsideFlightClearance("
            "const FVector& WorldPoint) const;\n"
            "\tconst FSkyguardMissionMapReadiness& GetReadiness() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, REBUILD_ROUTE_SPLINE)
        self.assertIn("RebuildRouteSpline", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        added_arg = "\tvoid RebuildRouteSpline(float DeltaSeconds);\n"
        wrong_return = "\tbool RebuildRouteSpline();\n"
        added_const = "\tvoid RebuildRouteSpline() const;\n"
        int_type = "\tint32 RebuildRouteSpline();\n"
        for region in (added_arg, wrong_return, added_const, int_type):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REBUILD_ROUTE_SPLINE)
            self.assertIn("RebuildRouteSpline", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_rebuild_route_spline_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )
        self.assertTrue(has_declaration(section, REBUILD_ROUTE_SPLINE))
        self.assertEqual(declaration_count(section, REBUILD_ROUTE_SPLINE), 1)
        self.assertTrue(
            REBUILD_ROUTE_SPLINE.startswith("void "),
            REBUILD_ROUTE_SPLINE,
        )
        self.assertTrue(REBUILD_ROUTE_SPLINE.endswith(";"), REBUILD_ROUTE_SPLINE)
        self.assertNotIn("INDEX_NONE", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("{", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("}", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return ", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(" const", REBUILD_ROUTE_SPLINE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tRebuildRouteSpline();\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tvoid RebuildRouteSpline(\n"
            "\t\t);\n"
            "private:\n"
            "};\n"
        )
        wrap_space = (
            "public:\n"
            "\tvoid  RebuildRouteSpline();\n"
            "};\n"
        )
        wrap_close = (
            "public:\n"
            "\tvoid RebuildRouteSpline(\n"
            ");\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_name}"
        )
        header_wrap_space = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_space}"
        )
        header_wrap_close = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_close}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_space,
            header_wrap_close,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, REBUILD_ROUTE_SPLINE),
                section,
            )
            self.assertEqual(
                require_declaration(section, REBUILD_ROUTE_SPLINE),
                REBUILD_ROUTE_SPLINE,
            )
            self.assertEqual(
                declaration_count(section, REBUILD_ROUTE_SPLINE),
                1,
            )
        one_line = f"{{\npublic:\n\t{REBUILD_ROUTE_SPLINE}\n}}\n"
        self.assertTrue(has_declaration(one_line, REBUILD_ROUTE_SPLINE))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, REBUILD_ROUTE_SPLINE),
            section,
        )
        self.assertEqual(
            require_declaration(section, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvoid RebuildRouteSpline()\n"
            "\t{\n"
            "\t\tFlightRouteSpline = nullptr;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, REBUILD_ROUTE_SPLINE),
            section,
        )
        self.assertEqual(
            require_declaration(section, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )
        self.assertEqual(declaration_count(section, REBUILD_ROUTE_SPLINE), 1)
        self.assertNotIn("{", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("}", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return ", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FlightRouteSpline = nullptr", REBUILD_ROUTE_SPLINE)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", REBUILD_ROUTE_SPLINE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_rebuild_route_spline_cpp_body(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        self.assertNotIn("{", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("}", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return ", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "ASkyguardMissionMapAssemblyDirector::RebuildRouteSpline",
            REBUILD_ROUTE_SPLINE,
        )
        self.assertNotIn(
            "SkyguardMissionMapAssemblyDirector.cpp",
            REBUILD_ROUTE_SPLINE,
        )
        self.assertNotIn(
            "SkyguardMissionMapAssemblyDirector.cpp",
            locked_only,
        )
        self.assertNotIn("return false", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return true", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_relock_validate_assembly(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for neighbor in VALIDATE_ASSEMBLY_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ValidateAssembly", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ValidateAssembly", locked_only)

    def test_contract_does_not_relock_is_point_inside_flight_clearance(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for neighbor in IS_POINT_INSIDE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("IsPointInsideFlightClearance", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("IsPointInsideFlightClearance", locked_only)

    def test_contract_does_not_relock_get_readiness(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for neighbor in GET_READINESS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("GetReadiness", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("GetReadiness", locked_only)

    def test_contract_does_not_relock_uprop_fields(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        self.assertNotIn("UPROPERTY", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("UPROPERTY", locked_only)
        for neighbor in UPROP_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FlightRouteSpline", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("MissionDefinition", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ObjectiveAnchors", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("LandmarkAnchors", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FlightClearanceRadiusCentimeters", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("Readiness", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_relock_leftover_skyline_style_enum(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ESkyguardMissionSkylineStyle", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ESkyguardMissionSkylineStyle", locked_only)
        self.assertNotIn("HarborIndustrial", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "test_mission_skyline_style_enum_contract.py",
            REBUILD_ROUTE_SPLINE,
        )

    def test_contract_does_not_relock_leftover_objective_anchor_defaults(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_OBJECTIVE_ANCHOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardMissionObjectiveAnchor", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "test_mission_objective_anchor_defaults_contract.py",
            REBUILD_ROUTE_SPLINE,
        )

    def test_contract_does_not_relock_leftover_landmark_anchor_defaults(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_LANDMARK_ANCHOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardMissionLandmarkAnchor", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "test_mission_landmark_anchor_defaults_contract.py",
            REBUILD_ROUTE_SPLINE,
        )

    def test_contract_does_not_relock_leftover_map_readiness_defaults(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_MAP_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardMissionMapReadiness", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "test_mission_map_readiness_defaults_contract.py",
            REBUILD_ROUTE_SPLINE,
        )

    def test_contract_does_not_relock_leftover_pathfinder_decls(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_PATHFINDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("AdvanceEncounter", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("GetTelegraphsTriggered", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_relock_leftover_briefing_state_enum(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("Unconfigured", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("Warming", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("Launched", REBUILD_ROUTE_SPLINE)
        self.assertNotIn(
            "test_mission_briefing_state_enum_contract.py",
            REBUILD_ROUTE_SPLINE,
        )

    def test_contract_does_not_relock_leftover_briefing_siblings(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardBriefingCard", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardBriefingRadioRow", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("GetBriefingText", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("GetRadioChatter", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FillResultCombatStats", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ASkyguardGunner", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FillAndFinalize", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FillAndFail", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ApplyHydraForClusters", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        self.assertEqual(
            require_declaration(locked_only, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ValidateAssembly", locked_only)
        self.assertNotIn("IsPointInsideFlightClearance", locked_only)
        self.assertNotIn("GetReadiness", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_leftover_types_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("USTRUCT", section)
        self.assertNotIn("Unconfigured", section)
        self.assertNotIn("Warming", section)
        self.assertNotIn("Launched", section)
        self.assertNotIn("CalculateRouteLength", section)
        self.assertEqual(
            require_declaration(section, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )
        self.assertNotIn("SkyguardMissionMapAssemblyDirector.cpp", section)
        self.assertNotIn(
            "ASkyguardMissionMapAssemblyDirector::RebuildRouteSpline",
            section,
        )
        self.assertNotEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardBossTypes.h",
        )
        self.assertNotIn("SkyguardBossTypes.h", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionMapAssemblyDirector.cpp", section)
        self.assertNotIn(
            "ASkyguardMissionMapAssemblyDirector::RebuildRouteSpline",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("}", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return false", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("return true", REBUILD_ROUTE_SPLINE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        file_text = this_file_text()
        incoming = leftover_harbor_tokens()[:3]
        clocks = leftover_harbor_tokens()[3:]
        for token in incoming:
            self.assertNotIn(token, section)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in clocks:
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens()[3:]:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, file_text)

    def test_leftover_skyline_harbor_industrial_is_not_harbor_clock(
        self,
    ) -> None:
        leftover_style = "HarborIndustrial"
        self.assertNotIn(leftover_style, leftover_harbor_tokens())
        self.assertNotIn(leftover_style, REBUILD_ROUTE_SPLINE)
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        self.assertNotIn(leftover_style, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, leftover_style)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission-map RebuildRouteSpline contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, REBUILD_ROUTE_SPLINE.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission-map RebuildRouteSpline contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, REBUILD_ROUTE_SPLINE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, REBUILD_ROUTE_SPLINE)

    def test_contract_is_rebuild_route_spline_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, REBUILD_ROUTE_SPLINE),
            REBUILD_ROUTE_SPLINE,
        )
        locked_only = f"{REBUILD_ROUTE_SPLINE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ValidateAssembly", locked_only)
        self.assertNotIn("IsPointInsideFlightClearance", locked_only)
        self.assertNotIn("GetReadiness", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("Unconfigured", locked_only)
        self.assertNotIn("Warming", locked_only)
        self.assertNotIn("Launched", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetRadioChatter", locked_only)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_OBJECTIVE_ANCHOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_LANDMARK_ANCHOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_MAP_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in LEFTOVER_PATHFINDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens()[:3]:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens()[3:]:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REBUILD_ROUTE_SPLINE)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, REBUILD_ROUTE_SPLINE.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("{", REBUILD_ROUTE_SPLINE)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(REBUILD_ROUTE_SPLINE.startswith("void "))
        self.assertTrue(REBUILD_ROUTE_SPLINE.endswith(";"))
        self.assertIn(UFUNCTION_MISSION_MAP, section)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
            if (ROOT / sibling).exists():
                existing.append(sibling)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", *existing],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
