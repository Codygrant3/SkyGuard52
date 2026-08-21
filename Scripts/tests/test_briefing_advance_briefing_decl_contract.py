from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionBriefingComponent.h"
CLASS_NAME = "USkyguardMissionBriefingComponent"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the AdvanceBriefing body in the .cpp.
# origin/main is one line
# (`void AdvanceBriefing(float DeltaSeconds);`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Nearby origin/main
# UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")
# is accepted as present. Parse the public class section of
# USkyguardMissionBriefingComponent only. Do not parse
# ESkyguardMissionBriefingState. Leftover briefing-fail-closed
# #9fe9, leftover briefing-card defaults #8c3f, leftover
# briefing-radio-row defaults #bf8e, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover campaign-roster #111, leftover
# campaign-save empty-fail-closed, and mission-definition
# field / method contracts stay sibling-only.
ADVANCE_BRIEFING = "void AdvanceBriefing(float DeltaSeconds);"
UFUNCTION_BRIEFING = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")'
)
# Leftover #56–#64 plus BriefingComponent production files.
# This lane only adds an isolated Python AdvanceBriefing
# declaration contract. Stay off ConfigureFromMission
# (in-flight sibling), SetAssetsReady (sibling this wave),
# AcknowledgeAndLaunch, CanLaunch, GetBriefingState,
# GetElapsedSeconds, GetMinimumWarmupSeconds,
# GetBriefingText, and GetRadioChatter on this class.
# Stay off leftover briefing-fail-closed, leftover
# briefing-card defaults, leftover briefing-radio-row
# defaults, leftover mission-briefing-state enum, leftover
# radio-chatter empty-fail-closed, leftover campaign-roster
# lookup, leftover campaign-save empty-fail-closed, leftover
# mission-definition field / method contracts, leftover
# CPG debrief, leftover Gunner helpers, leftover Harbor
# clocks, leftover theater-kit / flare / HUD, leftover
# drafts #56–#64, leftover ApacheSystem / weapon stations
# / pilot commands / loadout / lock-phase, leftover
# settings invert-look / ApplySettings broadcast, leftover
# bind-hud-host, leftover objective-runtime fail-closed,
# leftover route-runtime fail-closed, leftover pilot line
# / confirm / warn / call-probe / duration drafts,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover mission 0N integration
# readiness, and dirty workspace paths.
LOCKED = {
    "SkyguardMissionBriefingComponent.h",
    "SkyguardMissionBriefingComponent.cpp",
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
# briefing-fail-closed, leftover briefing-card defaults,
# leftover briefing-radio-row defaults, leftover
# radio-chatter empty-fail-closed, leftover
# mission-briefing-state enum, leftover campaign-roster
# lookup, leftover campaign-save empty-fail-closed,
# leftover mission-definition field / method contracts,
# leftover CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit / Harbor
# / flare / HUD, leftover ApacheSystem / weapon stations /
# pilot commands / loadout, leftover settings invert-look,
# leftover bind-hud-host, leftover pilot drafts, leftover
# gun-fire camera shake, leftover mission-weather enum,
# in-flight ConfigureFromMission, and SetAssetsReady
# (sibling this wave) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
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
# here. ConfigureFromMission / SetAssetsReady /
# AcknowledgeAndLaunch / CanLaunch / GetBriefingState /
# GetElapsedSeconds / GetMinimumWarmupSeconds /
# GetBriefingText / GetRadioChatter stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "USkyguardMissionBriefingComponent();",
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);",
    "void SetAssetsReady(bool bReady);",
    "bool AcknowledgeAndLaunch();",
    "bool CanLaunch() const;",
    "ESkyguardMissionBriefingState GetBriefingState() const { return State; }",
    "float GetElapsedSeconds() const { return ElapsedSeconds; }",
    "float GetMinimumWarmupSeconds() const { return MinimumWarmupSeconds; }",
    "FText GetBriefingText() const { return BriefingText; }",
    "TArray<FText> GetRadioChatter() const { return RadioChatter; }",
)
CONFIGURE_FROM_MISSION_NOT_LOCKED = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);",
)
SET_ASSETS_READY_NOT_LOCKED = ("void SetAssetsReady(bool bReady);",)
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
GET_BRIEFING_TEXT_NOT_LOCKED = (
    "FText GetBriefingText() const { return BriefingText; }",
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
# .cpp AdvanceBriefing body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionBriefingComponent::AdvanceBriefing",
    "SkyguardMissionBriefingComponent.cpp",
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


class BriefingAdvanceBriefingDeclContractTests(unittest.TestCase):
    def test_briefing_component_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, ADVANCE_BRIEFING),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedBriefing "
                ": public UActorComponent\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherMissionBriefingComponent "
            ": public UActorComponent\n"
            "{\n"
            "public:\n"
            f"\t{ADVANCE_BRIEFING}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_briefing_state_enum_does_not_satisfy_class(self) -> None:
        enum_only = (
            "UENUM(BlueprintType)\n"
            "enum class ESkyguardMissionBriefingState : uint8\n"
            "{\n"
            "\tUnconfigured,\n"
            "\tWarming,\n"
            "\tReady,\n"
            "\tLaunched\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(enum_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UActorComponent\n"
            "{\n"
            "private:\n"
            f"\t{ADVANCE_BRIEFING}\n"
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
            ": public UActorComponent\n"
            "{\n"
            "public:\n"
            "\tvoid SetAssetsReady(bool bReady);\n"
            "private:\n"
            f"\t{ADVANCE_BRIEFING}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, ADVANCE_BRIEFING)
        self.assertIn("AdvanceBriefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, ADVANCE_BRIEFING))

    def test_missing_advance_briefing_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSkyguardMissionBriefingComponent();\n"
            "\tbool ConfigureFromMission("
            "USkyguardMissionDefinition* Mission);\n"
            "\tvoid SetAssetsReady(bool bReady);\n"
            "\tbool AcknowledgeAndLaunch();\n"
            "\tbool CanLaunch() const;\n"
            "\tESkyguardMissionBriefingState GetBriefingState() "
            "const { return State; }\n"
            "\tfloat GetElapsedSeconds() const { return ElapsedSeconds; }\n"
            "\tfloat GetMinimumWarmupSeconds() const { "
            "return MinimumWarmupSeconds; }\n"
            "\tFText GetBriefingText() const { return BriefingText; }\n"
            "\tTArray<FText> GetRadioChatter() const { "
            "return RadioChatter; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, ADVANCE_BRIEFING)
        self.assertIn("AdvanceBriefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_BRIEFING}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, ADVANCE_BRIEFING)
        self.assertIn("AdvanceBriefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_BRIEFING, section)
        self.assertTrue(
            has_declaration(section, ADVANCE_BRIEFING),
            section,
        )
        self.assertNotIn("BlueprintPure", ADVANCE_BRIEFING)
        self.assertNotIn("UFUNCTION", ADVANCE_BRIEFING)
        self.assertNotIn("Category", ADVANCE_BRIEFING)
        self.assertNotIn("BlueprintCallable", ADVANCE_BRIEFING)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tbool ConfigureFromMission("
            "USkyguardMissionDefinition* Mission);\n"
            "\tvoid SetAssetsReady(bool bReady);\n"
            "\tbool AcknowledgeAndLaunch();\n"
            "\tbool CanLaunch() const;\n"
            "\tESkyguardMissionBriefingState GetBriefingState() "
            "const { return State; }\n"
            "\tfloat GetElapsedSeconds() const { return ElapsedSeconds; }\n"
            "\tfloat GetMinimumWarmupSeconds() const { "
            "return MinimumWarmupSeconds; }\n"
            "\tFText GetBriefingText() const { return BriefingText; }\n"
            "\tTArray<FText> GetRadioChatter() const { "
            "return RadioChatter; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, ADVANCE_BRIEFING)
        self.assertIn("AdvanceBriefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = "\tvoid AdvanceBriefing();\n"
        wrong_return = "\tbool AdvanceBriefing(float DeltaSeconds);\n"
        added_const = "\tvoid AdvanceBriefing(float DeltaSeconds) const;\n"
        wrong_type = "\tvoid AdvanceBriefing(double DeltaSeconds);\n"
        int_type = "\tvoid AdvanceBriefing(int32 DeltaSeconds);\n"
        for region in (
            missing_arg,
            wrong_return,
            added_const,
            wrong_type,
            int_type,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, ADVANCE_BRIEFING)
            self.assertIn("AdvanceBriefing", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_advance_briefing_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )
        self.assertTrue(has_declaration(section, ADVANCE_BRIEFING))
        self.assertEqual(declaration_count(section, ADVANCE_BRIEFING), 1)
        self.assertTrue(
            ADVANCE_BRIEFING.startswith("void "),
            ADVANCE_BRIEFING,
        )
        self.assertTrue(ADVANCE_BRIEFING.endswith(";"), ADVANCE_BRIEFING)
        self.assertIn("float DeltaSeconds", ADVANCE_BRIEFING)
        self.assertNotIn("INDEX_NONE", ADVANCE_BRIEFING)
        self.assertNotIn("{", ADVANCE_BRIEFING)
        self.assertNotIn("}", ADVANCE_BRIEFING)
        self.assertNotIn("return ", ADVANCE_BRIEFING)
        self.assertNotIn(" const", ADVANCE_BRIEFING)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tAdvanceBriefing(float DeltaSeconds);\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tvoid AdvanceBriefing(\n"
            "\t\tfloat DeltaSeconds);\n"
            "private:\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tvoid AdvanceBriefing(float\n"
            "\t\tDeltaSeconds);\n"
            "};\n"
        )
        wrap_space = (
            "public:\n"
            "\tvoid AdvanceBriefing(\n"
            "\t\tfloat  DeltaSeconds);\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_name}"
        )
        header_wrap_arg = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_arg}"
        )
        header_wrap_space = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_space}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_arg,
            header_wrap_space,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, ADVANCE_BRIEFING),
                section,
            )
            self.assertEqual(
                require_declaration(section, ADVANCE_BRIEFING),
                ADVANCE_BRIEFING,
            )
            self.assertEqual(declaration_count(section, ADVANCE_BRIEFING), 1)
        one_line = f"{{\npublic:\n\t{ADVANCE_BRIEFING}\n}}\n"
        self.assertTrue(has_declaration(one_line, ADVANCE_BRIEFING))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, ADVANCE_BRIEFING),
            section,
        )
        self.assertEqual(
            require_declaration(section, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvoid AdvanceBriefing(float DeltaSeconds)\n"
            "\t{\n"
            "\t\tElapsedSeconds += DeltaSeconds;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, ADVANCE_BRIEFING),
            section,
        )
        self.assertEqual(
            require_declaration(section, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )
        self.assertEqual(declaration_count(section, ADVANCE_BRIEFING), 1)
        self.assertNotIn("{", ADVANCE_BRIEFING)
        self.assertNotIn("}", ADVANCE_BRIEFING)
        self.assertNotIn("return ", ADVANCE_BRIEFING)
        self.assertNotIn("ElapsedSeconds +=", ADVANCE_BRIEFING)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", ADVANCE_BRIEFING)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", ADVANCE_BRIEFING)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_advance_briefing_cpp_body(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        self.assertNotIn("{", ADVANCE_BRIEFING)
        self.assertNotIn("}", ADVANCE_BRIEFING)
        self.assertNotIn("return ", ADVANCE_BRIEFING)
        self.assertNotIn(
            "USkyguardMissionBriefingComponent::AdvanceBriefing",
            ADVANCE_BRIEFING,
        )
        self.assertNotIn(
            "SkyguardMissionBriefingComponent.cpp",
            ADVANCE_BRIEFING,
        )
        self.assertNotIn("SkyguardMissionBriefingComponent.cpp", locked_only)
        self.assertNotIn("return false", ADVANCE_BRIEFING)
        self.assertNotIn("return true", ADVANCE_BRIEFING)

    def test_contract_does_not_relock_configure_from_mission(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in CONFIGURE_FROM_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("ConfigureFromMission", ADVANCE_BRIEFING)
        self.assertNotIn("ConfigureFromMission", locked_only)

    def test_contract_does_not_relock_set_assets_ready(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in SET_ASSETS_READY_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("SetAssetsReady", ADVANCE_BRIEFING)
        self.assertNotIn("SetAssetsReady", locked_only)

    def test_contract_does_not_relock_acknowledge_and_launch(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in ACKNOWLEDGE_AND_LAUNCH_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("AcknowledgeAndLaunch", ADVANCE_BRIEFING)
        self.assertNotIn("AcknowledgeAndLaunch", locked_only)

    def test_contract_does_not_relock_can_launch(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in CAN_LAUNCH_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("CanLaunch", ADVANCE_BRIEFING)
        self.assertNotIn("CanLaunch", locked_only)

    def test_contract_does_not_relock_get_briefing_state(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in GET_BRIEFING_STATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("GetBriefingState", ADVANCE_BRIEFING)
        self.assertNotIn("GetBriefingState", locked_only)
        self.assertNotIn(
            "ESkyguardMissionBriefingState",
            ADVANCE_BRIEFING,
        )
        self.assertNotIn("ESkyguardMissionBriefingState", locked_only)

    def test_contract_does_not_relock_get_elapsed_seconds(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in GET_ELAPSED_SECONDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("GetElapsedSeconds", ADVANCE_BRIEFING)
        self.assertNotIn("GetElapsedSeconds", locked_only)

    def test_contract_does_not_relock_get_minimum_warmup_seconds(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in GET_MINIMUM_WARMUP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("GetMinimumWarmupSeconds", ADVANCE_BRIEFING)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)

    def test_contract_does_not_relock_get_briefing_text(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in GET_BRIEFING_TEXT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("GetBriefingText", ADVANCE_BRIEFING)
        self.assertNotIn("GetBriefingText", locked_only)

    def test_contract_does_not_relock_get_radio_chatter(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in GET_RADIO_CHATTER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("GetRadioChatter", ADVANCE_BRIEFING)
        self.assertNotIn("GetRadioChatter", locked_only)

    def test_contract_does_not_relock_leftover_briefing_state_enum(
        self,
    ) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        self.assertNotIn("Unconfigured", ADVANCE_BRIEFING)
        self.assertNotIn("Warming", ADVANCE_BRIEFING)
        self.assertNotIn("Launched", ADVANCE_BRIEFING)
        self.assertNotIn(
            "test_mission_briefing_state_enum_contract.py",
            ADVANCE_BRIEFING,
        )

    def test_contract_does_not_relock_leftover_briefing_siblings(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        self.assertNotIn("FSkyguardBriefingCard", ADVANCE_BRIEFING)
        self.assertNotIn("FSkyguardBriefingRadioRow", ADVANCE_BRIEFING)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("FillResultCombatStats", ADVANCE_BRIEFING)
        self.assertNotIn("ASkyguardGunner", ADVANCE_BRIEFING)
        self.assertNotIn("FillAndFinalize", ADVANCE_BRIEFING)
        self.assertNotIn("FillAndFail", ADVANCE_BRIEFING)
        self.assertNotIn("ApplyHydraForClusters", ADVANCE_BRIEFING)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        self.assertEqual(
            require_declaration(locked_only, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("SetAssetsReady", locked_only)
        self.assertNotIn("AcknowledgeAndLaunch", locked_only)
        self.assertNotIn("CanLaunch", locked_only)
        self.assertNotIn("GetBriefingState", locked_only)
        self.assertNotIn("GetElapsedSeconds", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetRadioChatter", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("Unconfigured", section)
        self.assertNotIn("Warming", section)
        self.assertNotIn("Launched", section)
        self.assertNotIn("RefreshState", section)
        self.assertNotIn("bAssetsReady", section)
        self.assertNotIn("UPROPERTY(Transient)", section)
        self.assertEqual(
            require_declaration(section, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )
        self.assertNotIn("SkyguardMissionBriefingComponent.cpp", section)
        self.assertNotIn(
            "USkyguardMissionBriefingComponent::AdvanceBriefing",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionBriefingComponent.cpp", section)
        self.assertNotIn(
            "USkyguardMissionBriefingComponent::AdvanceBriefing",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", ADVANCE_BRIEFING)
        self.assertNotIn("}", ADVANCE_BRIEFING)
        self.assertNotIn("return false", ADVANCE_BRIEFING)
        self.assertNotIn("return true", ADVANCE_BRIEFING)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{ADVANCE_BRIEFING}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "briefing AdvanceBriefing contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, ADVANCE_BRIEFING.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"briefing AdvanceBriefing contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, ADVANCE_BRIEFING.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, ADVANCE_BRIEFING)

    def test_contract_is_advance_briefing_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, ADVANCE_BRIEFING),
            ADVANCE_BRIEFING,
        )
        locked_only = f"{ADVANCE_BRIEFING}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ADVANCE_BRIEFING)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("SetAssetsReady", locked_only)
        self.assertNotIn("AcknowledgeAndLaunch", locked_only)
        self.assertNotIn("CanLaunch", locked_only)
        self.assertNotIn("GetBriefingState", locked_only)
        self.assertNotIn("GetElapsedSeconds", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetRadioChatter", locked_only)
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
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ADVANCE_BRIEFING)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, ADVANCE_BRIEFING)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, ADVANCE_BRIEFING.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", ADVANCE_BRIEFING)
        self.assertNotIn("{", ADVANCE_BRIEFING)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(ADVANCE_BRIEFING.startswith("void "))
        self.assertTrue(ADVANCE_BRIEFING.endswith(";"))
        self.assertIn(UFUNCTION_BRIEFING, section)

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
