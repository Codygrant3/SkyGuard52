from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardInputCombatPerformanceCapture.h"
CLASS_NAME = "USkyguardInputCombatPerformanceCapture"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the IsCaptureActive body in the .cpp.
# origin/main is one line
# (`static bool IsCaptureActive(const UObject* WorldContext);`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. There is no nearby
# UFUNCTION on origin/main; do not invent one. Parse the
# public class section of
# USkyguardInputCombatPerformanceCapture only. This
# observer never drives input or combat. Stay off sibling
# RecordPlayerEvent / RecordGameplayEvent (not this
# lane). Stay off leftover Initialize / Deinitialize /
# Tick / GetStatId / IsTickable overrides. Stay off
# leftover settings-apply-broadcast #1268. Stay off
# leftover Gunner, leftover apache-aircraft
# empty-fail-closed #851b, leftover apache-chin-muzzle
# #4e39, leftover apache-own-ship-systems #96c5,
# leftover apache-cpg-feel #8951. Stay off leftover
# input/combat performance capture siblings if any
# exist. Leftover briefing / debrief widget isolated
# contracts, leftover Harbor clocks, leftover
# theater-kit / flare / HUD, leftover ApacheSystem /
# weapon stations / leftover roster / loadout /
# lock-phase, leftover drafts #56–#64, leftover
# isolated-test drafts #107–#426, leftover skyline
# style HarborIndustrial (leftover enum, not a Harbor
# 40/80 retune), leftover sortie-hud-host fail-closed,
# leftover gun-fire camera shake, leftover
# DebriefWidget / BriefingWidget isolated contracts,
# leftover Pathfinder MinHeightFromOriginCm, leftover
# Apache MaxIntegrity, and leftover
# SortiePresentationWidgets stay sibling-only.
IS_CAPTURE_ACTIVE = (
    "static bool IsCaptureActive(const UObject* WorldContext);"
)
# Leftover #56–#64 production files plus
# SkyguardInputCombatPerformanceCapture.h / .cpp.
# This lane only adds an isolated Python
# IsCaptureActive declaration contract on
# USkyguardInputCombatPerformanceCapture. Stay off
# RecordPlayerEvent, RecordGameplayEvent, leftover
# Initialize / Deinitialize / Tick / GetStatId /
# IsTickable overrides, leftover apache-aircraft
# empty-fail-closed #851b, leftover apache-chin-muzzle
# #4e39, leftover apache-own-ship-systems #96c5,
# leftover apache-cpg-feel #8951, leftover
# settings-apply-broadcast #1268, leftover CPG HUD /
# sight HUD, leftover drafts #56–#64, leftover
# isolated-test drafts #107–#426, leftover
# ApacheSystem enum values, leftover roster enum
# values, leftover Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget isolated
# contracts, leftover BriefingWidget isolated
# contracts, leftover Gunner helpers, leftover
# settings contracts, leftover apache aircraft
# isolated contracts, leftover gun-fire camera shake,
# leftover sortie-hud-host fail-closed, leftover
# input/combat performance capture siblings, and dirty
# workspace paths.
LOCKED = {
    "SkyguardInputCombatPerformanceCapture.h",
    "SkyguardInputCombatPerformanceCapture.cpp",
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
# apache aircraft isolated contracts, leftover Gunner,
# leftover settings contracts, leftover
# briefing/debrief widget contracts, leftover
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover
# settings-apply-broadcast #1268, leftover
# RecordPlayerEvent / RecordGameplayEvent siblings,
# leftover Initialize / Deinitialize / Tick /
# GetStatId / IsTickable overrides, leftover
# input/combat performance capture siblings, leftover
# drafts #56–#64, leftover isolated-test drafts
# #107–#426, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover CPG HUD /
# sight HUD, leftover briefing-fail-closed, leftover
# campaign-save empty-fail-closed, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD,
# leftover ApacheSystem / weapon stations / leftover
# roster / loadout, leftover bind-hud-host, leftover
# Gunner helpers, leftover pilot drafts, leftover
# mission-weather enum, leftover skyline
# HarborIndustrial, leftover SortiePresentationWidgets,
# leftover CPG debrief, leftover apache-cpg-feel, and
# sibling capture neighbors stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_apache_aim_chin_turret_decl_contract.py",
    "Scripts/tests/test_apache_set_rotor_power_decl_contract.py",
    "Scripts/tests/test_apache_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "Scripts/tests/test_apache_set_orbit_focus_decl_contract.py",
    "Scripts/tests/test_apache_face_world_location_decl_contract.py",
    "Scripts/tests/test_apache_set_sensor_view_decl_contract.py",
    "Scripts/tests/test_apache_set_first_person_interior_decl_contract.py",
    "Scripts/tests/test_apache_set_direct_flight_input_decl_contract.py",
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_chin_turret_down_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_engine_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_pilot_command_roster_tests.py",
    "Scripts/tests/test_pilot_command_roster.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_apache_chin_muzzle.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_tests.py",
    "Scripts/tests/test_apache_own_ship_systems.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_apache_cpg_feel_tests.py",
    "Scripts/tests/test_apache_cpg_feel.py",
    "Scripts/tests/test_gunner_fill_and_finalize_contract.py",
    "Scripts/tests/test_gunner_fill_and_fail_contract.py",
    "Scripts/tests/test_gunner_fill_result_combat_stats_contract.py",
    "Scripts/tests/test_gunner_apply_hydra_for_clusters_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_set_master_volume_decl_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_debrief_widget_configure_decl_contract.py",
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
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_m01_input_combat_native_contract.py",
    "Scripts/tests/test_input_combat_runtime_bookmark_hooks.py",
    "Scripts/tests/test_input_combat_performance_contract.py",
    "Scripts/tests/test_verify_skyguard_m01_input_combat_performance_gate.py",
    "Scripts/tests/test_verify_skyguard_input_combat_performance_gate.py",
    "Scripts/tests/test_m01_input_combat_supervisor_marker_scan.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake.py",
    "Scripts/tests/test_gun_fire_camera_shake_contract.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_tests.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_contract.py",
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
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_voice_call_probe.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not
# locked here. Leftover Initialize / Deinitialize /
# Tick / GetStatId / IsTickable overrides and sibling
# RecordPlayerEvent / RecordGameplayEvent stay
# sibling-only.
UNLOCKED_NEIGHBORS = (
    "virtual void Initialize(FSubsystemCollectionBase& Collection) override;",
    "virtual void Deinitialize() override;",
    "virtual void Tick(float DeltaTime) override;",
    "virtual TStatId GetStatId() const override;",
    "virtual bool IsTickable() const override;",
    "static void RecordPlayerEvent(const UObject* WorldContext, FName EventName);",
    "static void RecordGameplayEvent(const UObject* WorldContext, FName EventName);",
)
LEFTOVER_OVERRIDES_NOT_LOCKED = (
    "virtual void Initialize(FSubsystemCollectionBase& Collection) override;",
    "virtual void Deinitialize() override;",
    "virtual void Tick(float DeltaTime) override;",
    "virtual TStatId GetStatId() const override;",
    "virtual bool IsTickable() const override;",
)
RECORD_PLAYER_EVENT_NOT_LOCKED = (
    "static void RecordPlayerEvent(const UObject* WorldContext, FName EventName);",
)
RECORD_GAMEPLAY_EVENT_NOT_LOCKED = (
    "static void RecordGameplayEvent(const UObject* WorldContext, FName EventName);",
)
# Leftover apache-aircraft empty-fail-closed #851b
# stays unlocked. Stay off those mount getters.
LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "test_apache_aircraft_empty_fail_closed.py",
    "test_apache_aircraft_empty_fail_closed_tests.py",
    "test_apache_aircraft_empty_fail_closed_contract.py",
)
# Leftover apache-chin-muzzle tests #4e39 stay unlocked.
LEFTOVER_CHIN_MUZZLE_NOT_LOCKED = (
    "test_apache_chin_muzzle_tests.py",
    "test_apache_chin_muzzle_contract.py",
    "GetChinMuzzleLocation",
)
# Leftover apache-own-ship-systems #96c5 stays unlocked.
# Do not lock ESkyguardApacheSystem enum values.
LEFTOVER_OWN_SHIP_NOT_LOCKED = (
    "test_apache_own_ship_systems_contract.py",
    "test_apache_own_ship_systems_tests.py",
    "ESkyguardApacheSystem",
)
# Leftover apache-cpg-feel #8951 stays unlocked.
LEFTOVER_CPG_FEEL_NOT_LOCKED = (
    "test_apache_cpg_feel_contract.py",
    "test_apache_cpg_feel_tests.py",
    "test_apache_cpg_feel.py",
)
# Leftover settings-apply-broadcast #1268 stays
# unlocked. Do not create or edit those files.
LEFTOVER_SETTINGS_NOT_LOCKED = (
    "test_settings_apply_broadcast_tests.py",
    "test_settings_apply_broadcast_contract.py",
    "bInvertLook",
    "ApplySettings",
)
# Leftover Gunner FillAnd* helpers stay unlocked.
LEFTOVER_GUNNER_NOT_LOCKED = (
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "ApplyHydraForClusters",
    "ASkyguardGunner",
)
# Leftover apache aircraft isolated contracts stay
# unlocked. Do not create or edit those files.
LEFTOVER_APACHE_DECL_NOT_LOCKED = (
    "test_apache_face_world_location_decl_contract.py",
    "test_apache_aim_chin_turret_decl_contract.py",
    "test_apache_set_rotor_power_decl_contract.py",
    "test_apache_get_rotor_rpm_decl_contract.py",
    "FaceWorldLocation",
    "AimChinTurret",
    "GetRotorRPM",
)
# Leftover input/combat performance capture siblings
# stay unlocked. Do not create or edit those files.
LEFTOVER_CAPTURE_SIBLINGS_NOT_LOCKED = (
    "test_m01_input_combat_native_contract.py",
    "test_input_combat_runtime_bookmark_hooks.py",
    "test_input_combat_performance_contract.py",
    "RecordPlayerEvent",
    "RecordGameplayEvent",
)
# Leftover DebriefWidget / BriefingWidget isolated
# contracts stay unlocked.
LEFTOVER_WIDGET_DECL_NOT_LOCKED = (
    "test_debrief_widget_retry_save_decl_contract.py",
    "test_debrief_widget_travel_next_decl_contract.py",
    "test_debrief_widget_handle_debrief_key_decl_contract.py",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "RetrySave",
    "TravelNext",
    "HandleDebriefKey",
)
# Leftover ApacheSystem / weapon stations / leftover
# roster type-name lock / loadout / lock-phase /
# leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
)
# Leftover skyline style HarborIndustrial is leftover
# enum, not a Harbor 40/80 clock retune.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# Pathfinder MinHeightFromOriginCm and Apache
# MaxIntegrity are the wrong headers. Do not scan
# them for Harbor clocks.
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinder",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "SkyguardApacheAircraft.h",
)
# .cpp IsCaptureActive body / invented INDEX_NONE stay
# unlocked. Do not invent INDEX_NONE or lock the
# cpp body. Do not parse leftover HUD classes.
# Private Resolve stays sibling-only.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardInputCombatPerformanceCapture::IsCaptureActive",
    "SkyguardInputCombatPerformanceCapture.cpp",
    "static USkyguardInputCombatPerformanceCapture* Resolve",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardGunner",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_harbor_clock_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
    )


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return leftover_harbor_clock_tokens() + (
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


class InputCaptureIsCaptureActiveDeclContractTests(unittest.TestCase):
    def test_input_capture_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, IS_CAPTURE_ACTIVE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedCapture "
                ": public UTickableWorldSubsystem\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherInputCapture "
            ": public UTickableWorldSubsystem\n"
            "{\n"
            "public:\n"
            f"\t{IS_CAPTURE_ACTIVE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UTickableWorldSubsystem\n"
            "{\n"
            "private:\n"
            f"\t{IS_CAPTURE_ACTIVE}\n"
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
            ": public UTickableWorldSubsystem\n"
            "{\n"
            "public:\n"
            "\tstatic void RecordPlayerEvent("
            "const UObject* WorldContext, FName EventName);\n"
            "private:\n"
            f"\t{IS_CAPTURE_ACTIVE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, IS_CAPTURE_ACTIVE)
        self.assertIn("IsCaptureActive", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, IS_CAPTURE_ACTIVE))

    def test_missing_is_capture_active_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tvirtual void Initialize("
            "FSubsystemCollectionBase& Collection) override;\n"
            "\tvirtual void Deinitialize() override;\n"
            "\tvirtual void Tick(float DeltaTime) override;\n"
            "\tvirtual TStatId GetStatId() const override;\n"
            "\tvirtual bool IsTickable() const override;\n"
            "\tstatic void RecordPlayerEvent("
            "const UObject* WorldContext, FName EventName);\n"
            "\tstatic void RecordGameplayEvent("
            "const UObject* WorldContext, FName EventName);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, IS_CAPTURE_ACTIVE)
        self.assertIn("IsCaptureActive", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tvirtual void Initialize("
            "FSubsystemCollectionBase& Collection) override;\n"
            "\tvirtual void Deinitialize() override;\n"
            "\tvirtual void Tick(float DeltaTime) override;\n"
            "\tvirtual TStatId GetStatId() const override;\n"
            "\tvirtual bool IsTickable() const override;\n"
            "\tstatic void RecordPlayerEvent("
            "const UObject* WorldContext, FName EventName);\n"
            "\tstatic void RecordGameplayEvent("
            "const UObject* WorldContext, FName EventName);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, IS_CAPTURE_ACTIVE)
        self.assertIn("IsCaptureActive", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tstatic bool IsCaptureActive;\n"
        missing_static = (
            "\tbool IsCaptureActive(const UObject* WorldContext);\n"
        )
        wrong_return_void = (
            "\tstatic void IsCaptureActive(const UObject* WorldContext);\n"
        )
        wrong_return_int = (
            "\tstatic int32 IsCaptureActive(const UObject* WorldContext);\n"
        )
        added_const = (
            "\tstatic bool IsCaptureActive("
            "const UObject* WorldContext) const;\n"
        )
        missing_const = (
            "\tstatic bool IsCaptureActive(UObject* WorldContext);\n"
        )
        wrong_type = (
            "\tstatic bool IsCaptureActive(const UWorld* WorldContext);\n"
        )
        missing_ptr = (
            "\tstatic bool IsCaptureActive(const UObject WorldContext);\n"
        )
        added_arg = (
            "\tstatic bool IsCaptureActive("
            "const UObject* WorldContext, FName Extra);\n"
        )
        no_args = "\tstatic bool IsCaptureActive();\n"
        leftover_player = (
            "\tstatic void RecordPlayerEvent("
            "const UObject* WorldContext, FName EventName);\n"
        )
        leftover_gameplay = (
            "\tstatic void RecordGameplayEvent("
            "const UObject* WorldContext, FName EventName);\n"
        )
        leftover_init = (
            "\tvirtual void Initialize("
            "FSubsystemCollectionBase& Collection) override;\n"
        )
        leftover_tick = "\tvirtual void Tick(float DeltaTime) override;\n"
        leftover_stat = "\tvirtual TStatId GetStatId() const override;\n"
        leftover_tickable = "\tvirtual bool IsTickable() const override;\n"
        leftover_deinit = "\tvirtual void Deinitialize() override;\n"
        for region in (
            missing_parens,
            missing_static,
            wrong_return_void,
            wrong_return_int,
            added_const,
            missing_const,
            wrong_type,
            missing_ptr,
            added_arg,
            no_args,
            leftover_player,
            leftover_gameplay,
            leftover_init,
            leftover_tick,
            leftover_stat,
            leftover_tickable,
            leftover_deinit,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, IS_CAPTURE_ACTIVE)
            self.assertIn("IsCaptureActive", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_is_capture_active_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )
        self.assertTrue(has_declaration(section, IS_CAPTURE_ACTIVE))
        self.assertEqual(declaration_count(section, IS_CAPTURE_ACTIVE), 1)
        self.assertTrue(
            IS_CAPTURE_ACTIVE.startswith("static bool "),
            IS_CAPTURE_ACTIVE,
        )
        self.assertTrue(IS_CAPTURE_ACTIVE.endswith(";"), IS_CAPTURE_ACTIVE)
        self.assertIn("IsCaptureActive(", IS_CAPTURE_ACTIVE)
        self.assertIn("const UObject* WorldContext", IS_CAPTURE_ACTIVE)
        self.assertNotIn("INDEX_NONE", IS_CAPTURE_ACTIVE)
        self.assertNotIn("{", IS_CAPTURE_ACTIVE)
        self.assertNotIn("}", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return ", IS_CAPTURE_ACTIVE)
        self.assertNotIn(" const;", IS_CAPTURE_ACTIVE)
        self.assertNotIn("UFUNCTION", IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordPlayerEvent", IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordGameplayEvent", IS_CAPTURE_ACTIVE)
        self.assertNotIn("Initialize", IS_CAPTURE_ACTIVE)
        self.assertNotIn("Deinitialize", IS_CAPTURE_ACTIVE)
        self.assertNotIn("GetStatId", IS_CAPTURE_ACTIVE)
        self.assertNotIn("IsTickable", IS_CAPTURE_ACTIVE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tstatic bool\n"
            "\tIsCaptureActive(const UObject* WorldContext);\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tstatic bool IsCaptureActive(\n"
            "\t\tconst UObject* WorldContext);\n"
            "private:\n"
            "};\n"
        )
        wrap_parens = (
            "public:\n"
            "\tstatic bool IsCaptureActive\n"
            "\t(const UObject* WorldContext);\n"
            "};\n"
        )
        wrap_param = (
            "public:\n"
            "\tstatic\n"
            "\tbool\n"
            "\tIsCaptureActive(\n"
            "\t\tconst UObject*\n"
            "\t\tWorldContext);\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UTickableWorldSubsystem\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UTickableWorldSubsystem\n{{\n{wrap_name}"
        )
        header_wrap_parens = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UTickableWorldSubsystem\n{{\n{wrap_parens}"
        )
        header_wrap_param = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UTickableWorldSubsystem\n{{\n{wrap_param}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_parens,
            header_wrap_param,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, IS_CAPTURE_ACTIVE),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_CAPTURE_ACTIVE),
                IS_CAPTURE_ACTIVE,
            )
            self.assertEqual(
                declaration_count(section, IS_CAPTURE_ACTIVE),
                1,
            )
        one_line = f"{{\npublic:\n\t{IS_CAPTURE_ACTIVE}\n}}\n"
        self.assertTrue(has_declaration(one_line, IS_CAPTURE_ACTIVE))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, IS_CAPTURE_ACTIVE), section)
        self.assertEqual(
            require_declaration(section, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tstatic bool IsCaptureActive(const UObject* WorldContext)\n"
            "\t{\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UTickableWorldSubsystem\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(has_declaration(section, IS_CAPTURE_ACTIVE), section)
        self.assertEqual(
            require_declaration(section, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )
        self.assertEqual(declaration_count(section, IS_CAPTURE_ACTIVE), 1)
        self.assertNotIn("{", IS_CAPTURE_ACTIVE)
        self.assertNotIn("}", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return ", IS_CAPTURE_ACTIVE)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", IS_CAPTURE_ACTIVE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_invent_ufunction(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        section = public_section(origin_main_header())
        self.assertNotIn("UFUNCTION", IS_CAPTURE_ACTIVE)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertNotIn("BlueprintCallable", IS_CAPTURE_ACTIVE)
        self.assertNotIn("BlueprintPure", IS_CAPTURE_ACTIVE)
        self.assertNotIn("UFUNCTION", section)

    def test_contract_does_not_lock_is_capture_active_cpp_body(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        self.assertNotIn("{", IS_CAPTURE_ACTIVE)
        self.assertNotIn("}", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return ", IS_CAPTURE_ACTIVE)
        self.assertNotIn(
            "USkyguardInputCombatPerformanceCapture::IsCaptureActive",
            IS_CAPTURE_ACTIVE,
        )
        self.assertNotIn(
            "SkyguardInputCombatPerformanceCapture.cpp",
            IS_CAPTURE_ACTIVE,
        )
        self.assertNotIn(
            "SkyguardInputCombatPerformanceCapture.cpp",
            locked_only,
        )
        self.assertNotIn("return false", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return true", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_overrides(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for neighbor in LEFTOVER_OVERRIDES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CAPTURE_ACTIVE)
        self.assertNotIn("Initialize", IS_CAPTURE_ACTIVE)
        self.assertNotIn("Deinitialize", IS_CAPTURE_ACTIVE)
        self.assertNotIn("GetStatId", IS_CAPTURE_ACTIVE)
        self.assertNotIn("IsTickable", IS_CAPTURE_ACTIVE)
        self.assertNotIn("DeltaTime", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_record_player_event(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for neighbor in RECORD_PLAYER_EVENT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordPlayerEvent", IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordPlayerEvent", locked_only)

    def test_contract_does_not_relock_record_gameplay_event(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for neighbor in RECORD_GAMEPLAY_EVENT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordGameplayEvent", IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordGameplayEvent", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            IS_CAPTURE_ACTIVE,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn("GetChinMuzzleLocation", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn("ESkyguardApacheSystem", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            IS_CAPTURE_ACTIVE,
        )

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn(
            "test_settings_apply_broadcast_tests.py",
            IS_CAPTURE_ACTIVE,
        )
        self.assertNotIn("ApplySettings", IS_CAPTURE_ACTIVE)
        self.assertNotIn("bInvertLook", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn("FillAndFinalize", IS_CAPTURE_ACTIVE)
        self.assertNotIn("FillAndFail", IS_CAPTURE_ACTIVE)
        self.assertNotIn("ASkyguardGunner", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn("FaceWorldLocation", IS_CAPTURE_ACTIVE)
        self.assertNotIn("AimChinTurret", IS_CAPTURE_ACTIVE)
        self.assertNotIn("GetRotorRPM", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_capture_siblings(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_CAPTURE_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn(
            "test_m01_input_combat_native_contract.py",
            IS_CAPTURE_ACTIVE,
        )
        self.assertNotIn("RecordPlayerEvent", IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordGameplayEvent", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", IS_CAPTURE_ACTIVE)
        self.assertNotIn("USkyguardBriefingWidget", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", IS_CAPTURE_ACTIVE)
        self.assertNotIn("ESkyguardMissionSkylineStyle", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        self.assertEqual(
            require_declaration(locked_only, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordPlayerEvent", locked_only)
        self.assertNotIn("RecordGameplayEvent", locked_only)
        self.assertNotIn("Initialize", locked_only)
        self.assertNotIn("Deinitialize", locked_only)
        self.assertNotIn("GetStatId", locked_only)
        self.assertNotIn("IsTickable", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("TryStartMeasurement", section)
        self.assertNotIn("CompleteMeasurement", section)
        self.assertNotIn("WriteReceipt", section)
        self.assertNotIn("HasRequiredEventCounts", section)
        self.assertNotIn("BeginTraceWindow", section)
        self.assertNotIn("EndTraceWindow", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("USkyguardDebriefWidget", body)
        self.assertNotIn("USkyguardBriefingWidget", body)
        self.assertEqual(
            require_declaration(section, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )
        self.assertEqual(declaration_count(section, IS_CAPTURE_ACTIVE), 1)
        self.assertNotIn(
            "SkyguardInputCombatPerformanceCapture.cpp",
            section,
        )
        self.assertNotIn(
            "USkyguardInputCombatPerformanceCapture::IsCaptureActive",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardInputCombatPerformanceCapture.cpp",
            section,
        )
        self.assertNotIn(
            "USkyguardInputCombatPerformanceCapture::IsCaptureActive",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", IS_CAPTURE_ACTIVE)
        self.assertNotIn("}", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return false", IS_CAPTURE_ACTIVE)
        self.assertNotIn("return true", IS_CAPTURE_ACTIVE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class public
        # section. Literal Harbor interval retune tokens fail
        # closed in this file and the locked declaration
        # only. Do not scan other headers for Harbor clocks.
        # Apache MaxIntegrity is not a Harbor clock.
        # Pathfinder MinHeightFromOriginCm is the wrong
        # header.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_clock_tokens():
            section = public_section(origin_main_header())
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "input capture IsCaptureActive contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, IS_CAPTURE_ACTIVE.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"input capture IsCaptureActive contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, IS_CAPTURE_ACTIVE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, IS_CAPTURE_ACTIVE)

    def test_contract_is_is_capture_active_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, IS_CAPTURE_ACTIVE),
            IS_CAPTURE_ACTIVE,
        )
        locked_only = f"{IS_CAPTURE_ACTIVE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CAPTURE_ACTIVE)
        self.assertNotIn("RecordPlayerEvent", locked_only)
        self.assertNotIn("RecordGameplayEvent", locked_only)
        self.assertNotIn("Initialize", locked_only)
        self.assertNotIn("Deinitialize", locked_only)
        self.assertNotIn("GetStatId", locked_only)
        self.assertNotIn("IsTickable", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("UFUNCTION", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_CAPTURE_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_CAPTURE_ACTIVE)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, IS_CAPTURE_ACTIVE.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", IS_CAPTURE_ACTIVE)
        self.assertNotIn("{", IS_CAPTURE_ACTIVE)
        self.assertTrue(IS_CAPTURE_ACTIVE.startswith("static bool "))
        self.assertTrue(IS_CAPTURE_ACTIVE.endswith(";"))

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
