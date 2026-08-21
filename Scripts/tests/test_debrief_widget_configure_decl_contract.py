from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardSortiePresentationWidgets.h"
CLASS_NAME = "USkyguardDebriefWidget"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the Configure body in the .cpp.
# origin/main is one line
# (`void Configure(USkyguardSortiePresentationComponent* InPresentation);`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Nearby origin/main
# UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
# is accepted as present. Parse the public class section of
# USkyguardDebriefWidget only. Do not parse
# USkyguardBriefingWidget. This is not leftover
# BriefingWidget Configure (draft #388). This is not
# leftover CPG debrief fail-closed #8ccd. This is not
# leftover mission-debrief defaults. This is not
# leftover sortie-presentation fail-closed #7600.
# This is not leftover briefing-component
# ConfigureFromMission (draft #366). Leftover
# briefing-fail-closed, leftover briefing-card
# defaults, leftover briefing-radio-row defaults,
# leftover how-to-fly-row defaults, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover briefing-component
# declaration contracts through GetRadioChatter,
# leftover CPG debrief, leftover bind-hud-host,
# leftover Gunner helpers, leftover Harbor clocks,
# leftover theater-kit / flare / HUD, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout / lock-phase, leftover drafts #56–#64,
# leftover sortie-presentation state enum, leftover
# mission-debrief-state enum, leftover skyline style
# HarborIndustrial (leftover enum, not a Harbor
# 40/80 retune), and sibling BriefingWidget
# isolated contracts stay sibling-only.
CONFIGURE = (
    "void Configure(USkyguardSortiePresentationComponent* InPresentation);"
)
UFUNCTION_DEBRIEF = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")'
)
# Leftover #56–#64 plus SortiePresentationWidgets and
# SortiePresentationComponent production files.
# This lane only adds an isolated Python Configure
# declaration contract on USkyguardDebriefWidget.
# Stay off GetPresentation, GetDebrief,
# GetDebriefNarrative, GetFinalScore,
# IsProgressSaved, GetPresentationState,
# AcknowledgeDebrief, RetrySave, TravelNext, and
# HandleDebriefKey on this class. Stay off leftover
# BriefingWidget Configure #388, leftover CPG
# debrief fail-closed #8ccd, leftover
# mission-debrief defaults, leftover
# sortie-presentation fail-closed #7600, leftover
# briefing-component ConfigureFromMission #366,
# leftover briefing-fail-closed, leftover
# briefing-card defaults, leftover
# briefing-radio-row defaults, leftover
# how-to-fly-row defaults, leftover
# mission-briefing-state enum, leftover
# radio-chatter empty-fail-closed, leftover
# briefing-component ConfigureFromMission through
# GetRadioChatter, leftover Gunner helpers,
# leftover Harbor clocks, leftover theater-kit /
# flare / HUD, leftover drafts #56–#64, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout / lock-phase, leftover settings invert-look
# / ApplySettings broadcast, leftover bind-hud-host,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover pilot line /
# confirm / warn / call-probe / duration drafts,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover mission 0N
# integration readiness, leftover
# USkyguardBriefingWidget, leftover
# sortie-presentation state enum, leftover
# mission-debrief-state enum, leftover skyline
# HarborIndustrial, and dirty workspace paths.
LOCKED = {
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardSortiePresentationWidgets.cpp",
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationComponent.cpp",
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
# BriefingWidget Configure / GetPresentation /
# GetMissionTitle / GetBriefingText /
# AcknowledgeBriefing / LaunchSortie, leftover
# CPG debrief fail-closed, leftover
# mission-debrief defaults, leftover
# sortie-presentation fail-closed, leftover
# briefing-fail-closed, leftover briefing-card
# defaults, leftover briefing-radio-row defaults,
# leftover how-to-fly-row defaults, leftover
# radio-chatter empty-fail-closed, leftover
# mission-briefing-state enum, leftover
# briefing-component declaration contracts through
# GetRadioChatter, leftover CPG debrief, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD,
# leftover ApacheSystem / weapon stations / pilot
# commands / loadout, leftover settings invert-look,
# leftover bind-hud-host, leftover Gunner helpers,
# leftover pilot drafts, leftover gun-fire camera
# shake, leftover mission-weather enum, leftover
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover mission-definition
# field / method contracts, leftover
# USkyguardBriefingWidget, leftover
# ConfigureFromMission, leftover
# sortie-presentation state enum, leftover
# mission-debrief-state enum, leftover skyline
# HarborIndustrial, and sibling DebriefWidget
# neighbors stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_debrief_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_debrief_narrative_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_final_score_decl_contract.py",
    "Scripts/tests/test_debrief_widget_is_progress_saved_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_state_decl_contract.py",
    "Scripts/tests/test_debrief_widget_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_debrief_widget_retry_save_decl_contract.py",
    "Scripts/tests/test_debrief_widget_travel_next_decl_contract.py",
    "Scripts/tests/test_debrief_widget_handle_debrief_key_decl_contract.py",
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_sortie_presentation_contract.py",
    "Scripts/tests/test_sortie_presentation_state_enum_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
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
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum.py",
    "Scripts/tests/test_mission_briefing_state_enum_tests.py",
    "Scripts/tests/test_mission_debrief_state_enum_contract.py",
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
    "Scripts/tests/test_boss_definition_defaults_contract.py",
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
    "Scripts/tests/test_cpg_debrief_fail_closed_tests.py",
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
# Neighbors in the same public section. Presence is not
# locked here. GetPresentation / GetDebrief /
# GetDebriefNarrative / GetFinalScore /
# IsProgressSaved / GetPresentationState /
# AcknowledgeDebrief / RetrySave / TravelNext /
# HandleDebriefKey stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "USkyguardSortiePresentationComponent* GetPresentation() const;",
    "FSkyguardMissionDebrief GetDebrief() const;",
    "FText GetDebriefNarrative() const;",
    "int32 GetFinalScore() const;",
    "bool IsProgressSaved() const;",
    "ESkyguardSortiePresentationState GetPresentationState() const;",
    "bool AcknowledgeDebrief();",
    "bool RetrySave();",
    "bool TravelNext();",
    "bool HandleDebriefKey(FKey Key);",
)
GET_PRESENTATION_NOT_LOCKED = (
    "USkyguardSortiePresentationComponent* GetPresentation() const;",
)
GET_DEBRIEF_NOT_LOCKED = ("FSkyguardMissionDebrief GetDebrief() const;",)
GET_DEBRIEF_NARRATIVE_NOT_LOCKED = ("FText GetDebriefNarrative() const;",)
GET_FINAL_SCORE_NOT_LOCKED = ("int32 GetFinalScore() const;",)
IS_PROGRESS_SAVED_NOT_LOCKED = ("bool IsProgressSaved() const;",)
GET_PRESENTATION_STATE_NOT_LOCKED = (
    "ESkyguardSortiePresentationState GetPresentationState() const;",
)
ACKNOWLEDGE_DEBRIEF_NOT_LOCKED = ("bool AcknowledgeDebrief();",)
RETRY_SAVE_NOT_LOCKED = ("bool RetrySave();",)
TRAVEL_NEXT_NOT_LOCKED = ("bool TravelNext();",)
HANDLE_DEBRIEF_KEY_NOT_LOCKED = ("bool HandleDebriefKey(FKey Key);",)
# Leftover BriefingWidget Configure (draft #388) and
# later BriefingWidget methods stay unlocked.
BRIEFING_WIDGET_CONFIGURE_NOT_LOCKED = (
    "test_briefing_widget_configure_decl_contract.py",
    "USkyguardBriefingWidget",
)
# Leftover briefing-component ConfigureFromMission
# (draft #366) and later briefing-component methods
# stay unlocked.
CONFIGURE_FROM_MISSION_NOT_LOCKED = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);",
)
SET_ASSETS_READY_NOT_LOCKED = ("void SetAssetsReady(bool bReady);",)
ADVANCE_BRIEFING_NOT_LOCKED = (
    "void AdvanceBriefing(float DeltaSeconds);",
)
ACKNOWLEDGE_AND_LAUNCH_NOT_LOCKED = ("bool AcknowledgeAndLaunch();",)
CAN_LAUNCH_NOT_LOCKED = ("bool CanLaunch() const;",)
GET_BRIEFING_STATE_NOT_LOCKED = (
    "ESkyguardMissionBriefingState GetBriefingState() const { return State; }",
)
GET_ELAPSED_SECONDS_NOT_LOCKED = (
    "float GetElapsedSeconds() const { return ElapsedSeconds; }",
)
GET_MINIMUM_WARMUP_NOT_LOCKED = (
    "float GetMinimumWarmupSeconds() const { return MinimumWarmupSeconds; }",
)
GET_RADIO_CHATTER_NOT_LOCKED = (
    "TArray<FText> GetRadioChatter() const { return RadioChatter; }",
)
# Leftover mission-briefing-state enum stays unlocked.
# This lane parses the public class section only.
LEFTOVER_ENUM_NOT_LOCKED = (
    "Unconfigured",
    "Warming",
    "Launched",
    "test_mission_briefing_state_enum_contract.py",
)
# Leftover briefing-fail-closed / leftover briefing-card
# defaults / leftover briefing-radio-row defaults /
# leftover how-to-fly-row defaults / leftover
# radio-chatter empty-fail-closed stay unlocked.
LEFTOVER_BRIEFING_NOT_LOCKED = (
    "test_briefing_fail_closed.py",
    "test_briefing_fail_closed_tests.py",
    "test_briefing_fail_closed_contract.py",
    "test_briefing_card_defaults_contract.py",
    "test_briefing_radio_row_defaults_contract.py",
    "test_how_to_fly_row_defaults_contract.py",
    "test_radio_chatter_empty_fail_closed.py",
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
    "FSkyguardHowToFlyRow",
)
# Leftover sortie-presentation fail-closed #7600 stays
# unlocked. Do not lock leftover presentation-state
# enum presence here.
LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED = (
    "test_sortie_presentation_fail_closed.py",
    "test_sortie_presentation_fail_closed_tests.py",
    "test_sortie_presentation_fail_closed_contract.py",
    "test_sortie_presentation_contract.py",
    "test_sortie_presentation_state_enum_contract.py",
    "SkyguardSortiePresentationFailClosed",
)
# Leftover sortie-presentation state enum values stay
# unlocked. Type name is a neighbor return type, so
# only the leftover value names / sibling file are
# listed here.
LEFTOVER_SORTIE_PRESENTATION_STATE_NOT_LOCKED = (
    "SortieActive",
    "DebriefReady",
    "SaveFailure",
    "TravelReady",
    "TravelBlocked",
    "CampaignComplete",
    "test_sortie_presentation_state_enum_contract.py",
)
# Leftover mission-debrief defaults stay unlocked.
# Do not lock leftover struct default fields when
# locking Configure. FSkyguardMissionDebrief is a
# neighbor return type, so only leftover default
# fields / sibling file are listed here.
LEFTOVER_MISSION_DEBRIEF_DEFAULTS_NOT_LOCKED = (
    "test_mission_debrief_defaults_contract.py",
    "bNewBestScore",
    "bNewBestMedal",
    "bProgressSaved",
    "bNextMissionUnlocked",
    "bCampaignComplete",
    "ESkyguardMissionDebriefState",
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
    "test_cpg_debrief_fail_closed.py",
    "test_cpg_debrief_fail_closed_contract.py",
    "test_cpg_debrief_fail_closed_tests.py",
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
# Leftover bind-hud-host / leftover theater-kit /
# leftover briefing-component ConfigureFromMission
# stay unlocked.
LEFTOVER_BIND_HUD_AND_THEATER_NOT_LOCKED = (
    "test_bind_hud_host_presentation_tests.py",
    "test_campaign_theater_kit_contract.py",
    "test_briefing_configure_from_mission_decl_contract.py",
)
# Leftover skyline style HarborIndustrial is leftover
# enum, not a Harbor 40/80 clock retune.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# .cpp Configure body / invented INDEX_NONE stay
# unlocked. Do not invent INDEX_NONE or lock the
# cpp body. Do not parse USkyguardBriefingWidget.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardDebriefWidget::Configure",
    "SkyguardSortiePresentationWidgets.cpp",
)
BRIEFING_WIDGET_NOT_LOCKED = (
    "USkyguardBriefingWidget",
    "GetMissionTitle",
    "GetBriefingText",
    "GetBriefingCards",
    "GetRadioRows",
    "GetHowToFlyRows",
    "AcknowledgeBriefing",
    "LaunchSortie",
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


class DebriefWidgetConfigureDeclContractTests(unittest.TestCase):
    def test_debrief_widget_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, CONFIGURE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedDebrief "
                ": public UUserWidget\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherDebriefWidget "
            ": public UUserWidget\n"
            "{\n"
            "public:\n"
            f"\t{CONFIGURE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_briefing_widget_does_not_satisfy_class(self) -> None:
        briefing_only = (
            "class SKYGUARD52_API USkyguardBriefingWidget "
            ": public UUserWidget\n"
            "{\n"
            "public:\n"
            f"\t{CONFIGURE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(briefing_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UUserWidget\n"
            "{\n"
            "private:\n"
            f"\t{CONFIGURE}\n"
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
            ": public UUserWidget\n"
            "{\n"
            "public:\n"
            "\tFSkyguardMissionDebrief GetDebrief() const;\n"
            "private:\n"
            f"\t{CONFIGURE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CONFIGURE)
        self.assertIn("Configure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, CONFIGURE))

    def test_missing_configure_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSkyguardSortiePresentationComponent* "
            "GetPresentation() const;\n"
            "\tFSkyguardMissionDebrief GetDebrief() const;\n"
            "\tFText GetDebriefNarrative() const;\n"
            "\tint32 GetFinalScore() const;\n"
            "\tbool IsProgressSaved() const;\n"
            "\tESkyguardSortiePresentationState "
            "GetPresentationState() const;\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tbool RetrySave();\n"
            "\tbool TravelNext();\n"
            "\tbool HandleDebriefKey(FKey Key);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, CONFIGURE)
        self.assertIn("Configure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_DEBRIEF}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, CONFIGURE)
        self.assertIn("Configure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_DEBRIEF, section)
        self.assertTrue(has_declaration(section, CONFIGURE), section)
        self.assertNotIn("BlueprintPure", CONFIGURE)
        self.assertNotIn("UFUNCTION", CONFIGURE)
        self.assertNotIn("Category", CONFIGURE)
        self.assertNotIn("BlueprintCallable", CONFIGURE)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tUSkyguardSortiePresentationComponent* "
            "GetPresentation() const;\n"
            "\tFSkyguardMissionDebrief GetDebrief() const;\n"
            "\tFText GetDebriefNarrative() const;\n"
            "\tint32 GetFinalScore() const;\n"
            "\tbool IsProgressSaved() const;\n"
            "\tESkyguardSortiePresentationState "
            "GetPresentationState() const;\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tbool RetrySave();\n"
            "\tbool TravelNext();\n"
            "\tbool HandleDebriefKey(FKey Key);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, CONFIGURE)
        self.assertIn("Configure", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = "\tvoid Configure();\n"
        wrong_return = (
            "\tbool Configure("
            "USkyguardSortiePresentationComponent* InPresentation);\n"
        )
        added_const = (
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent* InPresentation) "
            "const;\n"
        )
        const_ptr = (
            "\tvoid Configure("
            "const USkyguardSortiePresentationComponent* "
            "InPresentation);\n"
        )
        by_ref = (
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent& InPresentation);\n"
        )
        sibling_name = (
            "\tbool ConfigureFromMission("
            "USkyguardMissionDefinition* Mission);\n"
        )
        for region in (
            missing_arg,
            wrong_return,
            added_const,
            const_ptr,
            by_ref,
            sibling_name,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE)
            self.assertIn("Configure", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_configure_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CONFIGURE),
            CONFIGURE,
        )
        self.assertTrue(has_declaration(section, CONFIGURE))
        self.assertEqual(declaration_count(section, CONFIGURE), 1)
        self.assertTrue(CONFIGURE.startswith("void "), CONFIGURE)
        self.assertTrue(CONFIGURE.endswith(";"), CONFIGURE)
        self.assertIn(
            "USkyguardSortiePresentationComponent* InPresentation",
            CONFIGURE,
        )
        self.assertNotIn("INDEX_NONE", CONFIGURE)
        self.assertNotIn("{", CONFIGURE)
        self.assertNotIn("}", CONFIGURE)
        self.assertNotIn("return ", CONFIGURE)
        self.assertNotIn(" const", CONFIGURE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tConfigure("
            "USkyguardSortiePresentationComponent* InPresentation);\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tvoid Configure(\n"
            "\t\tUSkyguardSortiePresentationComponent* InPresentation);\n"
            "private:\n"
            "};\n"
        )
        wrap_ptr = (
            "public:\n"
            "\tvoid Configure(USkyguardSortiePresentationComponent*\n"
            "\t\tInPresentation);\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tvoid Configure(\n"
            "\t\tUSkyguardSortiePresentationComponent *\n"
            "\t\tInPresentation);\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_name}"
        )
        header_wrap_ptr = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_ptr}"
        )
        header_wrap_arg = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_arg}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_ptr,
            header_wrap_arg,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, CONFIGURE), section)
            self.assertEqual(
                require_declaration(section, CONFIGURE),
                CONFIGURE,
            )
            self.assertEqual(declaration_count(section, CONFIGURE), 1)
        one_line = f"{{\npublic:\n\t{CONFIGURE}\n}}\n"
        self.assertTrue(has_declaration(one_line, CONFIGURE))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CONFIGURE), section)
        self.assertEqual(
            require_declaration(section, CONFIGURE),
            CONFIGURE,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent* InPresentation)\n"
            "\t{\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(has_declaration(section, CONFIGURE), section)
        self.assertEqual(
            require_declaration(section, CONFIGURE),
            CONFIGURE,
        )
        self.assertEqual(declaration_count(section, CONFIGURE), 1)
        self.assertNotIn("{", CONFIGURE)
        self.assertNotIn("}", CONFIGURE)
        self.assertNotIn("return ", CONFIGURE)
        self.assertNotIn("return false", CONFIGURE)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", CONFIGURE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", CONFIGURE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_configure_cpp_body(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        self.assertNotIn("{", CONFIGURE)
        self.assertNotIn("}", CONFIGURE)
        self.assertNotIn("return ", CONFIGURE)
        self.assertNotIn("USkyguardDebriefWidget::Configure", CONFIGURE)
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", CONFIGURE)
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", locked_only)
        self.assertNotIn("return false", CONFIGURE)
        self.assertNotIn("return true", CONFIGURE)

    def test_contract_does_not_relock_get_presentation(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in GET_PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetPresentation", CONFIGURE)
        self.assertNotIn("GetPresentation", locked_only)

    def test_contract_does_not_relock_get_debrief(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in GET_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetDebrief", CONFIGURE)
        self.assertNotIn("GetDebrief", locked_only)

    def test_contract_does_not_relock_get_debrief_narrative(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in GET_DEBRIEF_NARRATIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetDebriefNarrative", CONFIGURE)
        self.assertNotIn("GetDebriefNarrative", locked_only)

    def test_contract_does_not_relock_get_final_score(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in GET_FINAL_SCORE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetFinalScore", CONFIGURE)
        self.assertNotIn("GetFinalScore", locked_only)

    def test_contract_does_not_relock_is_progress_saved(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in IS_PROGRESS_SAVED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("IsProgressSaved", CONFIGURE)
        self.assertNotIn("IsProgressSaved", locked_only)

    def test_contract_does_not_relock_get_presentation_state(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in GET_PRESENTATION_STATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetPresentationState", CONFIGURE)
        self.assertNotIn("GetPresentationState", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in ACKNOWLEDGE_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("AcknowledgeDebrief", CONFIGURE)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_retry_save(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in RETRY_SAVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("RetrySave", CONFIGURE)
        self.assertNotIn("RetrySave", locked_only)

    def test_contract_does_not_relock_travel_next(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in TRAVEL_NEXT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("TravelNext", CONFIGURE)
        self.assertNotIn("TravelNext", locked_only)

    def test_contract_does_not_relock_handle_debrief_key(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in HANDLE_DEBRIEF_KEY_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("HandleDebriefKey", CONFIGURE)
        self.assertNotIn("HandleDebriefKey", locked_only)

    def test_contract_does_not_relock_briefing_widget_configure(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for token in BRIEFING_WIDGET_CONFIGURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("USkyguardBriefingWidget", CONFIGURE)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn(
            "test_briefing_widget_configure_decl_contract.py",
            CONFIGURE,
        )

    def test_contract_does_not_relock_configure_from_mission(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in CONFIGURE_FROM_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("ConfigureFromMission", CONFIGURE)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("USkyguardMissionBriefingComponent", CONFIGURE)
        self.assertNotIn("USkyguardMissionBriefingComponent", locked_only)

    def test_contract_does_not_relock_briefing_component_neighbors(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in (
            *SET_ASSETS_READY_NOT_LOCKED,
            *ADVANCE_BRIEFING_NOT_LOCKED,
            *ACKNOWLEDGE_AND_LAUNCH_NOT_LOCKED,
            *CAN_LAUNCH_NOT_LOCKED,
            *GET_BRIEFING_STATE_NOT_LOCKED,
            *GET_ELAPSED_SECONDS_NOT_LOCKED,
            *GET_MINIMUM_WARMUP_NOT_LOCKED,
            *GET_RADIO_CHATTER_NOT_LOCKED,
        ):
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("SetAssetsReady", CONFIGURE)
        self.assertNotIn("AdvanceBriefing", CONFIGURE)
        self.assertNotIn("AcknowledgeAndLaunch", CONFIGURE)
        self.assertNotIn("CanLaunch", CONFIGURE)
        self.assertNotIn("GetBriefingState", CONFIGURE)
        self.assertNotIn("GetElapsedSeconds", CONFIGURE)
        self.assertNotIn("GetMinimumWarmupSeconds", CONFIGURE)
        self.assertNotIn("GetRadioChatter", CONFIGURE)
        self.assertNotIn("ESkyguardMissionBriefingState", CONFIGURE)
        self.assertNotIn("ESkyguardMissionBriefingState", locked_only)

    def test_contract_does_not_relock_leftover_briefing_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("Unconfigured", CONFIGURE)
        self.assertNotIn("Warming", CONFIGURE)
        self.assertNotIn("Launched", CONFIGURE)
        self.assertNotIn(
            "test_mission_briefing_state_enum_contract.py",
            CONFIGURE,
        )

    def test_contract_does_not_relock_leftover_briefing_siblings(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("FSkyguardBriefingCard", CONFIGURE)
        self.assertNotIn("FSkyguardBriefingRadioRow", CONFIGURE)
        self.assertNotIn("FSkyguardHowToFlyRow", CONFIGURE)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("FSkyguardHowToFlyRow", locked_only)

    def test_contract_does_not_relock_leftover_sortie_presentation(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        for token in LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("SkyguardSortiePresentationFailClosed", CONFIGURE)
        self.assertNotIn("SkyguardSortiePresentationFailClosed", locked_only)

    def test_contract_does_not_relock_leftover_sortie_presentation_state(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SORTIE_PRESENTATION_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("SortieActive", CONFIGURE)
        self.assertNotIn("DebriefReady", CONFIGURE)
        self.assertNotIn(
            "test_sortie_presentation_state_enum_contract.py",
            CONFIGURE,
        )

    def test_contract_does_not_relock_leftover_mission_debrief_defaults(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_MISSION_DEBRIEF_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("bNewBestScore", CONFIGURE)
        self.assertNotIn("bProgressSaved", CONFIGURE)
        self.assertNotIn("ESkyguardMissionDebriefState", CONFIGURE)
        self.assertNotIn(
            "test_mission_debrief_defaults_contract.py",
            CONFIGURE,
        )

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("FillResultCombatStats", CONFIGURE)
        self.assertNotIn("ASkyguardGunner", CONFIGURE)
        self.assertNotIn("FillAndFinalize", CONFIGURE)
        self.assertNotIn("FillAndFail", CONFIGURE)
        self.assertNotIn("ApplyHydraForClusters", CONFIGURE)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)
        self.assertNotIn("test_cpg_debrief_fail_closed.py", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_bind_hud_or_theater(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        for token in LEFTOVER_BIND_HUD_AND_THEATER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("test_bind_hud_host_presentation_tests.py", CONFIGURE)
        self.assertNotIn("test_campaign_theater_kit_contract.py", CONFIGURE)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", CONFIGURE)
        self.assertNotIn("ESkyguardMissionSkylineStyle", CONFIGURE)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        self.assertEqual(
            require_declaration(locked_only, CONFIGURE),
            CONFIGURE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("GetDebrief", locked_only)
        self.assertNotIn("GetDebriefNarrative", locked_only)
        self.assertNotIn("GetFinalScore", locked_only)
        self.assertNotIn("IsProgressSaved", locked_only)
        self.assertNotIn("GetPresentationState", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("RetrySave", locked_only)
        self.assertNotIn("TravelNext", locked_only)
        self.assertNotIn("HandleDebriefKey", locked_only)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_briefing_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", body)
        self.assertNotIn("GetMissionTitle", section)
        self.assertNotIn("GetBriefingText", section)
        self.assertNotIn("GetBriefingCards", section)
        self.assertNotIn("GetRadioRows", section)
        self.assertNotIn("GetHowToFlyRows", section)
        self.assertNotIn("AcknowledgeBriefing", section)
        self.assertNotIn("LaunchSortie", section)
        self.assertNotIn("NativeConstruct", section)
        self.assertNotIn("HandleContinueClicked", section)
        self.assertNotIn("RefreshRuntimeLayout", section)
        self.assertNotIn("UPROPERTY(Transient)", section)
        self.assertNotIn("RuntimeTitleText", section)
        self.assertNotIn("RuntimeContinueButton", section)
        self.assertEqual(
            require_declaration(section, CONFIGURE),
            CONFIGURE,
        )
        self.assertEqual(declaration_count(section, CONFIGURE), 1)
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", section)
        self.assertNotIn("USkyguardDebriefWidget::Configure", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", section)
        self.assertNotIn("USkyguardDebriefWidget::Configure", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", CONFIGURE)
        self.assertNotIn("}", CONFIGURE)
        self.assertNotIn("return false", CONFIGURE)
        self.assertNotIn("return true", CONFIGURE)

    def test_contract_does_not_parse_briefing_widget(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        for token in BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("GetMissionTitle", CONFIGURE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{CONFIGURE}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{CONFIGURE}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "debrief widget Configure contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, CONFIGURE.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"debrief widget Configure contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, CONFIGURE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, CONFIGURE)

    def test_contract_is_configure_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CONFIGURE),
            CONFIGURE,
        )
        locked_only = f"{CONFIGURE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("GetDebrief", locked_only)
        self.assertNotIn("GetDebriefNarrative", locked_only)
        self.assertNotIn("GetFinalScore", locked_only)
        self.assertNotIn("IsProgressSaved", locked_only)
        self.assertNotIn("GetPresentationState", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("RetrySave", locked_only)
        self.assertNotIn("TravelNext", locked_only)
        self.assertNotIn("HandleDebriefKey", locked_only)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("FSkyguardHowToFlyRow", locked_only)
        self.assertNotIn("Unconfigured", locked_only)
        self.assertNotIn("Warming", locked_only)
        self.assertNotIn("Launched", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("bNewBestScore", locked_only)
        self.assertNotIn("bProgressSaved", locked_only)
        self.assertNotIn("ESkyguardMissionDebriefState", locked_only)
        self.assertNotIn("SortieActive", locked_only)
        self.assertNotIn("DebriefReady", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_SORTIE_PRESENTATION_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_MISSION_DEBRIEF_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, CONFIGURE.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", CONFIGURE)
        self.assertNotIn("{", CONFIGURE)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(CONFIGURE.startswith("void "))
        self.assertTrue(CONFIGURE.endswith(";"))
        self.assertIn(UFUNCTION_DEBRIEF, section)

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
