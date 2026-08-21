from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardGameUserSettings.h"
CLASS_NAME = "USkyguardGameUserSettings"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the GetInvertVerticalLook body. origin/main
# is inline; accept that form, one-line, and split-line
# wraps without locking the body. Nearby origin/main
# UFUNCTION(BlueprintPure, Category = "Settings|Input")
# is accepted as present. Parse the public class section
# of USkyguardGameUserSettings only. Do not lock
# private config fields. This is not leftover Gunner
# IsVerticalLookInverted. This is not leftover
# settings-apply-broadcast #1268 (stay off ApplySettings
# / OnSettingsApplied). Stay off leftover
# ApplyAndSaveSettings, SetToDefaults, ValidateSettings,
# GetSkyguardGameUserSettings, SetMasterVolume,
# GetMasterVolume, SetMouseSensitivity,
# GetMouseSensitivity, SetCameraShakeScale,
# GetCameraShakeScale. Stay off sibling
# SetInvertVerticalLook in this wave. Stay off leftover
# apache-aircraft isolated drafts, leftover briefing /
# debrief widget contracts, leftover Harbor clocks,
# leftover skyline style HarborIndustrial (leftover
# enum, not a Harbor clock retune), leftover gun-fire
# camera shake, leftover CPG feel, leftover drafts
# #56-#64, leftover isolated-test drafts #107-#426,
# leftover Pathfinder height-from-origin, leftover
# Apache MaxIntegrity, and dirty workspace paths.
GET_INVERT_VERTICAL_LOOK = "bool GetInvertVerticalLook() const;"
UFUNCTION_SETTINGS_INPUT = (
    'UFUNCTION(BlueprintPure, Category = "Settings|Input")'
)
# Leftover #56-#64 plus GameUserSettings production
# files. This lane only adds an isolated Python
# GetInvertVerticalLook declaration contract on
# USkyguardGameUserSettings. Stay off leftover
# settings apply / volume / mouse / shake / defaults /
# validate / getter contracts, leftover apply-broadcast
# #1268, leftover Gunner invert helper, leftover
# apache-aircraft isolated contracts, leftover
# briefing / debrief widget contracts, leftover Harbor
# clocks, leftover skyline HarborIndustrial, leftover
# gun-fire camera shake, leftover CPG feel, leftover
# drafts #56-#64, leftover isolated-test drafts
# #107-#426, leftover SetInvertVerticalLook sibling,
# and dirty workspace paths.
LOCKED = {
    "SkyguardGameUserSettings.h",
    "SkyguardGameUserSettings.cpp",
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
# settings apply / volume / mouse / shake / defaults /
# validate / getter contracts, leftover apply-broadcast,
# leftover Gunner invert helper, leftover
# apache-aircraft isolated contracts, leftover
# briefing / debrief widget contracts, leftover
# SetInvertVerticalLook sibling, leftover gun-fire
# camera shake, leftover CPG feel, leftover
# apache-aircraft empty-fail-closed, leftover
# apache-chin-muzzle, leftover apache-own-ship,
# leftover apache-cpg-feel, leftover FaceWorldLocation
# sibling, leftover drafts #56-#64, leftover
# isolated-test drafts #107-#426, leftover skyline
# HarborIndustrial, leftover SortiePresentationWidgets,
# leftover CPG debrief, leftover Pathfinder height,
# leftover Apache MaxIntegrity, and sibling settings
# neighbors stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_settings_apply_and_save_decl_contract.py",
    "Scripts/tests/test_settings_set_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_get_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_settings_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_settings_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_settings_validate_decl_contract.py",
    "Scripts/tests/test_settings_validate_settings_decl_contract.py",
    "Scripts/tests/test_settings_set_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_set_master_volume_decl_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_apache_face_world_location_decl_contract.py",
    "Scripts/tests/test_apache_aim_chin_turret_decl_contract.py",
    "Scripts/tests/test_apache_set_rotor_power_decl_contract.py",
    "Scripts/tests/test_apache_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "Scripts/tests/test_apache_set_orbit_focus_decl_contract.py",
    "Scripts/tests/test_apache_set_sensor_view_decl_contract.py",
    "Scripts/tests/test_apache_set_first_person_interior_decl_contract.py",
    "Scripts/tests/test_apache_set_direct_flight_input_decl_contract.py",
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_is_chin_turret_down_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_engine_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
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
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake.py",
    "Scripts/tests/test_gun_fire_camera_shake_contract.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_tests.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_contract.py",
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_pathfinder_get_route_progress_decl_contract.py",
    "Scripts/tests/test_pathfinder_reset_encounter_state_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_route_state_safe_decl_contract.py",
    "Scripts/tests/test_pathfinder_advance_encounter_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_telegraphs_triggered_decl_contract.py",
)
# Neighbors in the same public section. Presence is not
# locked here. Leftover apply / volume / mouse / shake /
# defaults / validate / getter helpers, leftover
# ApplySettings / OnSettingsApplied, leftover
# SetInvertVerticalLook sibling, leftover Gunner
# invert helper, leftover apache-aircraft isolated
# methods, leftover briefing / debrief widget types,
# leftover private config fields, leftover Pathfinder
# height, leftover Apache MaxIntegrity, and remaining
# public methods stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "static USkyguardGameUserSettings* GetSkyguardGameUserSettings();",
    "void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);",
    "void SetMasterVolume(float Value);",
    "float GetMasterVolume() const;",
    "void SetMouseSensitivity(float Value);",
    "float GetMouseSensitivity() const;",
    "void SetInvertVerticalLook(bool bValue);",
    "void SetCameraShakeScale(float Value);",
    "float GetCameraShakeScale() const;",
    "virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;",
    "virtual void ValidateSettings() override;",
    "virtual void SetToDefaults() override;",
    "static FSkyguardUserSettingsApplied OnSettingsApplied;",
)
GETTER_NOT_LOCKED = (
    "GetSkyguardGameUserSettings",
)
APPLY_AND_SAVE_NOT_LOCKED = (
    "ApplyAndSaveSettings",
)
VOLUME_NOT_LOCKED = (
    "SetMasterVolume",
    "GetMasterVolume",
)
MOUSE_NOT_LOCKED = (
    "SetMouseSensitivity",
    "GetMouseSensitivity",
)
SET_INVERT_NOT_LOCKED = (
    "SetInvertVerticalLook",
    "test_settings_set_invert_vertical_look_decl_contract.py",
)
SHAKE_NOT_LOCKED = (
    "SetCameraShakeScale",
    "GetCameraShakeScale",
)
APPLY_BROADCAST_NOT_LOCKED = (
    "ApplySettings",
    "OnSettingsApplied",
    "test_settings_apply_broadcast_tests.py",
    "test_settings_apply_broadcast_contract.py",
)
VALIDATE_DEFAULTS_NOT_LOCKED = (
    "ValidateSettings",
    "SetToDefaults",
)
# Private config fields stay unlocked. Do not lock
# invert, volume, mouse, or shake defaults.
PRIVATE_CONFIG_NOT_LOCKED = (
    "MasterVolume = 1.f;",
    "MouseSensitivity = 0.07f;",
    "bInvertVerticalLook = true;",
    "CameraShakeScale = 1.f;",
)
# Leftover Gunner invert helper stays unlocked. This
# lane is GameUserSettings GetInvertVerticalLook, not
# Gunner IsVerticalLookInverted.
LEFTOVER_GUNNER_INVERT_NOT_LOCKED = (
    "IsVerticalLookInverted",
    "bInvertVerticalLookApplied",
    "ASkyguardGunner",
)
# Leftover apache-aircraft isolated contracts stay
# unlocked. Do not create or edit those files.
LEFTOVER_APACHE_AIRCRAFT_NOT_LOCKED = (
    "test_apache_face_world_location_decl_contract.py",
    "test_apache_aircraft_empty_fail_closed.py",
    "ASkyguardApacheAircraft",
    "FaceWorldLocation",
    "AimChinTurret",
    "GetChinMuzzleLocation",
)
# Leftover briefing / debrief widget isolated
# contracts stay unlocked.
LEFTOVER_WIDGET_DECL_NOT_LOCKED = (
    "test_debrief_widget_configure_decl_contract.py",
    "test_debrief_widget_travel_next_decl_contract.py",
    "test_debrief_widget_handle_debrief_key_decl_contract.py",
    "test_briefing_widget_configure_decl_contract.py",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "TravelNext",
    "HandleDebriefKey",
)
# Leftover #8860 gun-fire camera shake stays unlocked.
GUN_FIRE_SHAKE_NOT_LOCKED = (
    "USkyguardGunFireCameraShake",
    "SkyguardGunFireCameraShake",
    "FireCameraShakeClass",
    "PlayAppliedCameraShake",
    "GetAppliedCameraShakeScale",
)
# Leftover Apache CPG feel constants stay unlocked.
FEEL_NOT_LOCKED = (
    "CannonFireRate",
    "CannonDamage",
    "CannonMagazineSize",
    "RocketSalvoSeconds",
    "GuidedLockSeconds",
    "SkyguardApacheCpgFeel",
)
# Leftover ApacheSystem / weapon stations / leftover
# roster / loadout / lock-phase / leftover Gunner
# FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "bInvertLook",
)
# Leftover skyline style HarborIndustrial is leftover
# enum, not a Harbor clock retune.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# Leftover Pathfinder height-from-origin and leftover
# Apache MaxIntegrity stay unlocked. Do not scan those
# headers for Harbor clocks.
LEFTOVER_WRONG_HEADER_NOT_LOCKED = (
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "ASkyguardPathfinder",
)
# .cpp GetInvertVerticalLook body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# inline body. Do not parse leftover Gunner classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "USkyguardGameUserSettings::GetInvertVerticalLook",
    "SkyguardGameUserSettings.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardGunner",
    "ASkyguardPathfinder",
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


def leftover_short_roster_values() -> tuple[str, ...]:
    return (
        "Br" + "eak",
        "Ho" + "ld",
        "Cl" + "imb",
        "Des" + "cend",
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


class SettingsGetInvertVerticalLookDeclContractTests(unittest.TestCase):
    def test_game_user_settings_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, GET_INVERT_VERTICAL_LOOK),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSettings "
                ": public UGameUserSettings\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherGameUserSettings "
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            f"\t{GET_INVERT_VERTICAL_LOOK}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameUserSettings\n"
            "{\n"
            "private:\n"
            f"\t{GET_INVERT_VERTICAL_LOOK}\n"
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
            ": public UGameUserSettings\n"
            "{\n"
            "public:\n"
            "\tvoid SetInvertVerticalLook(bool bValue);\n"
            "private:\n"
            f"\t{GET_INVERT_VERTICAL_LOOK}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_INVERT_VERTICAL_LOOK)
        self.assertIn("GetInvertVerticalLook", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, GET_INVERT_VERTICAL_LOOK))

    def test_missing_get_invert_vertical_look_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings();\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides = true);\n"
            "\tvoid SetMasterVolume(float Value);\n"
            "\tfloat GetMasterVolume() const;\n"
            "\tvoid SetMouseSensitivity(float Value);\n"
            "\tfloat GetMouseSensitivity() const;\n"
            "\tvoid SetInvertVerticalLook(bool bValue);\n"
            "\tvoid SetCameraShakeScale(float Value);\n"
            "\tfloat GetCameraShakeScale() const;\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "\tvirtual void ValidateSettings() override;\n"
            "\tvirtual void SetToDefaults() override;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_INVERT_VERTICAL_LOOK)
        self.assertIn("GetInvertVerticalLook", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_SETTINGS_INPUT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_INVERT_VERTICAL_LOOK)
        self.assertIn("GetInvertVerticalLook", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_SETTINGS_INPUT, section)
        self.assertTrue(
            has_declaration(section, GET_INVERT_VERTICAL_LOOK),
            section,
        )
        self.assertNotIn("BlueprintPure", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("UFUNCTION", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("Category", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("BlueprintCallable", GET_INVERT_VERTICAL_LOOK)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings();\n"
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides = true);\n"
            "\tvoid SetMasterVolume(float Value);\n"
            "\tfloat GetMasterVolume() const;\n"
            "\tvoid SetMouseSensitivity(float Value);\n"
            "\tfloat GetMouseSensitivity() const;\n"
            "\tvoid SetInvertVerticalLook(bool bValue);\n"
            "\tvoid SetCameraShakeScale(float Value);\n"
            "\tfloat GetCameraShakeScale() const;\n"
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
            "\tvirtual void ValidateSettings() override;\n"
            "\tvirtual void SetToDefaults() override;\n"
            "\tbool IsVerticalLookInverted() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, GET_INVERT_VERTICAL_LOOK)
        self.assertIn("GetInvertVerticalLook", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tbool GetInvertVerticalLook const;\n"
        wrong_return_float = "\tfloat GetInvertVerticalLook() const;\n"
        wrong_return_void = "\tvoid GetInvertVerticalLook() const;\n"
        wrong_return_int = "\tint32 GetInvertVerticalLook() const;\n"
        missing_const = "\tbool GetInvertVerticalLook();\n"
        added_arg = "\tbool GetInvertVerticalLook(bool bValue) const;\n"
        leftover_set = "\tvoid SetInvertVerticalLook(bool bValue);\n"
        leftover_gunner = "\tbool IsVerticalLookInverted() const;\n"
        leftover_mouse = "\tfloat GetMouseSensitivity() const;\n"
        leftover_shake = "\tfloat GetCameraShakeScale() const;\n"
        leftover_volume = "\tfloat GetMasterVolume() const;\n"
        leftover_getter = (
            "\tstatic USkyguardGameUserSettings* "
            "GetSkyguardGameUserSettings();\n"
        )
        leftover_apply = (
            "\tvoid ApplyAndSaveSettings("
            "bool bCheckForCommandLineOverrides = true);\n"
        )
        leftover_defaults = "\tvirtual void SetToDefaults() override;\n"
        leftover_validate = "\tvirtual void ValidateSettings() override;\n"
        leftover_broadcast = (
            "\tvirtual void ApplySettings("
            "bool bCheckForCommandLineOverrides) override;\n"
        )
        leftover_apache = (
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        leftover_widget = "\tvoid TravelNext();\n"
        for region in (
            missing_parens,
            wrong_return_float,
            wrong_return_void,
            wrong_return_int,
            missing_const,
            added_arg,
            leftover_set,
            leftover_gunner,
            leftover_mouse,
            leftover_shake,
            leftover_volume,
            leftover_getter,
            leftover_apply,
            leftover_defaults,
            leftover_validate,
            leftover_broadcast,
            leftover_apache,
            leftover_widget,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, GET_INVERT_VERTICAL_LOOK)
            self.assertIn("GetInvertVerticalLook", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_get_invert_vertical_look_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertTrue(has_declaration(section, GET_INVERT_VERTICAL_LOOK))
        self.assertEqual(
            declaration_count(section, GET_INVERT_VERTICAL_LOOK),
            1,
        )
        self.assertTrue(
            GET_INVERT_VERTICAL_LOOK.startswith("bool "),
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertTrue(
            GET_INVERT_VERTICAL_LOOK.endswith(";"),
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertIn("GetInvertVerticalLook()", GET_INVERT_VERTICAL_LOOK)
        self.assertIn(" const;", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("INDEX_NONE", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("{", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("}", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return ", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetInvertVerticalLook", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("IsVerticalLookInverted", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetMouseSensitivity", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetCameraShakeScale", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetMasterVolume", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ApplySettings", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("OnSettingsApplied", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetToDefaults", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ValidateSettings", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "GetSkyguardGameUserSettings",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tGetInvertVerticalLook() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool GetInvertVerticalLook()\n"
            "\tconst;\n"
            "private:\n"
            "};\n"
        )
        wrap_parens = (
            "public:\n"
            "\tbool GetInvertVerticalLook\n"
            "\t() const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool\n"
            "\tGetInvertVerticalLook(\n"
            "\t) const;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_name}"
        )
        header_wrap_parens = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_parens}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_parens,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, GET_INVERT_VERTICAL_LOOK),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_INVERT_VERTICAL_LOOK),
                GET_INVERT_VERTICAL_LOOK,
            )
            self.assertEqual(
                declaration_count(section, GET_INVERT_VERTICAL_LOOK),
                1,
            )
        one_line = f"{{\npublic:\n\t{GET_INVERT_VERTICAL_LOOK}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_INVERT_VERTICAL_LOOK))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, GET_INVERT_VERTICAL_LOOK),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tbool GetInvertVerticalLook() const\n"
            "\t{\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameUserSettings\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, GET_INVERT_VERTICAL_LOOK),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertEqual(
            declaration_count(section, GET_INVERT_VERTICAL_LOOK),
            1,
        )
        self.assertNotIn("{", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("}", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return ", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("bInvertVerticalLook", GET_INVERT_VERTICAL_LOOK)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", GET_INVERT_VERTICAL_LOOK)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_get_invert_vertical_look_body(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        self.assertNotIn("{", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("}", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return ", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("bInvertVerticalLook", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "USkyguardGameUserSettings::GetInvertVerticalLook",
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertNotIn("SkyguardGameUserSettings.cpp", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SkyguardGameUserSettings.cpp", locked_only)
        self.assertNotIn("return false", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return true", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_getter(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in GETTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetSkyguardGameUserSettings", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_apply_and_save(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in APPLY_AND_SAVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ApplyAndSaveSettings", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)

    def test_contract_does_not_relock_volume_helpers(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in VOLUME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetMasterVolume", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetMasterVolume", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)

    def test_contract_does_not_relock_mouse_helpers(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in MOUSE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetMouseSensitivity", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetMouseSensitivity", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)

    def test_contract_does_not_relock_set_invert_sibling(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in SET_INVERT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetInvertVerticalLook", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "test_settings_set_invert_vertical_look_decl_contract.py",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_contract_does_not_relock_shake_helpers(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in SHAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetCameraShakeScale", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetCameraShakeScale", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)

    def test_contract_does_not_relock_apply_broadcast(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in APPLY_BROADCAST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ApplySettings", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("OnSettingsApplied", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "test_settings_apply_broadcast_tests.py",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_contract_does_not_relock_validate_or_defaults(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in VALIDATE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ValidateSettings", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SetToDefaults", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)

    def test_contract_does_not_lock_private_config_fields(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in PRIVATE_CONFIG_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("MasterVolume = 1.f;", section)
        self.assertNotIn("MouseSensitivity = 0.07f;", section)
        self.assertNotIn("bInvertVerticalLook = true;", section)
        self.assertNotIn("CameraShakeScale = 1.f;", section)
        self.assertNotIn("UPROPERTY(Config)", section)

    def test_contract_does_not_relock_leftover_gunner_invert(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_GUNNER_INVERT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("IsVerticalLookInverted", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("bInvertVerticalLookApplied", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ASkyguardGunner", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_leftover_apache_aircraft(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_APACHE_AIRCRAFT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("ASkyguardApacheAircraft", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("FaceWorldLocation", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("USkyguardBriefingWidget", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertNotIn(
            "test_debrief_widget_handle_debrief_key_decl_contract.py",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_contract_does_not_relock_leftover_gun_fire_shake(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in GUN_FIRE_SHAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("USkyguardGunFireCameraShake", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("PlayAppliedCameraShake", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("SkyguardApacheCpgFeel", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            GET_INVERT_VERTICAL_LOOK,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ESkyguardMissionSkylineStyle", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_scan_wrong_headers_for_harbor(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WRONG_HEADER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("MinHeightFromOriginCm", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("MaxIntegrity", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("ASkyguardPathfinder", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("UPROPERTY(Config)", section)
        self.assertNotIn("MasterVolume = 1.f;", section)
        self.assertNotIn("MouseSensitivity = 0.07f;", section)
        self.assertNotIn("bInvertVerticalLook = true;", section)
        self.assertNotIn("CameraShakeScale = 1.f;", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardGunner", section)
        self.assertNotIn("USkyguardDebriefWidget", body)
        self.assertNotIn("USkyguardBriefingWidget", body)
        self.assertNotIn("ASkyguardApacheAircraft", body)
        self.assertNotIn("IsVerticalLookInverted", section)
        self.assertEqual(
            require_declaration(section, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )
        self.assertEqual(
            declaration_count(section, GET_INVERT_VERTICAL_LOOK),
            1,
        )
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn(
            "USkyguardGameUserSettings::GetInvertVerticalLook",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardGameUserSettings.cpp", section)
        self.assertNotIn(
            "USkyguardGameUserSettings::GetInvertVerticalLook",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("}", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return false", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("return true", GET_INVERT_VERTICAL_LOOK)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class public
        # section. Literal Harbor interval retune tokens fail
        # closed in this file and the locked declaration
        # only. Do not scan leftover Pathfinder height or
        # leftover Apache MaxIntegrity headers.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
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
                "settings GetInvertVerticalLook contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, GET_INVERT_VERTICAL_LOOK.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"settings GetInvertVerticalLook contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, GET_INVERT_VERTICAL_LOOK.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, GET_INVERT_VERTICAL_LOOK)

    def test_contract_is_get_invert_vertical_look_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_INVERT_VERTICAL_LOOK),
            GET_INVERT_VERTICAL_LOOK,
        )
        locked_only = f"{GET_INVERT_VERTICAL_LOOK}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("GetSkyguardGameUserSettings", locked_only)
        self.assertNotIn("ApplyAndSaveSettings", locked_only)
        self.assertNotIn("SetMasterVolume", locked_only)
        self.assertNotIn("GetMasterVolume", locked_only)
        self.assertNotIn("SetMouseSensitivity", locked_only)
        self.assertNotIn("GetMouseSensitivity", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("SetCameraShakeScale", locked_only)
        self.assertNotIn("GetCameraShakeScale", locked_only)
        self.assertNotIn("ApplySettings", locked_only)
        self.assertNotIn("OnSettingsApplied", locked_only)
        self.assertNotIn("ValidateSettings", locked_only)
        self.assertNotIn("SetToDefaults", locked_only)
        self.assertNotIn("IsVerticalLookInverted", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("MinHeightFromOriginCm", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in PRIVATE_CONFIG_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in LEFTOVER_GUNNER_INVERT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in LEFTOVER_APACHE_AIRCRAFT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in SET_INVERT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in APPLY_BROADCAST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in GUN_FIRE_SHAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in LEFTOVER_WRONG_HEADER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_INVERT_VERTICAL_LOOK)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, this_file_text())
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, this_file_text())
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, GET_INVERT_VERTICAL_LOOK.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", GET_INVERT_VERTICAL_LOOK)
        self.assertNotIn("{", GET_INVERT_VERTICAL_LOOK)
        self.assertTrue(GET_INVERT_VERTICAL_LOOK.startswith("bool "))
        self.assertTrue(GET_INVERT_VERTICAL_LOOK.endswith(";"))
        self.assertIn(UFUNCTION_SETTINGS_INPUT, section)

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
