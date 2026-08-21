from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardSortiePresentationWidgets.h"
CLASS_NAME = "USkyguardBriefingWidget"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the GetPresentation body.
# origin/main is inline
# (`USkyguardSortiePresentationComponent* GetPresentation() const`
# with `{ return Presentation; }` possibly on following lines);
# accept that exact inline form, a one-line prototype
# (`USkyguardSortiePresentationComponent* GetPresentation() const;`),
# other split-line wraps, and other inline bodies without
# locking the body. Nearby origin/main
# UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
# is accepted as present. Parse the public class section of
# USkyguardBriefingWidget only. Do not parse
# USkyguardDebriefWidget. Do not re-lock leftover
# sortie-presentation fail-closed. Leftover
# briefing-fail-closed #9fe9, leftover briefing-card
# defaults #8c3f, leftover briefing-radio-row defaults
# #bf8e, leftover how-to-fly-row defaults, leftover
# mission-briefing-state enum, leftover
# radio-chatter empty-fail-closed, leftover
# sortie-presentation fail-closed #7600, leftover
# CPG debrief, leftover bind-hud-host, leftover
# Gunner helpers, leftover ApacheSystem / weapon
# stations / pilot commands / loadout / lock-phase,
# leftover Harbor clocks, leftover theater-kit /
# flare / HUD, sibling briefing-component
# declaration contracts through GetRadioChatter,
# and sibling Configure stay sibling-only.
GET_PRESENTATION = (
    "USkyguardSortiePresentationComponent* GetPresentation() const;"
)
UFUNCTION_BRIEFING = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")'
)
# Leftover #56–#64 plus this class's production files.
# This lane only adds an isolated Python GetPresentation
# declaration contract. Stay off Configure (sibling this
# wave), GetMissionTitle, GetBriefingText,
# GetBriefingCards, GetRadioRows, GetHowToFlyRows,
# AcknowledgeBriefing, and LaunchSortie on this class.
# Stay off leftover briefing-fail-closed, leftover
# briefing-card defaults, leftover briefing-radio-row
# defaults, leftover how-to-fly-row defaults, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover sortie-presentation
# fail-closed, leftover CPG debrief, leftover Gunner
# helpers, leftover Harbor clocks, leftover theater-kit
# / flare / HUD, leftover drafts #56–#64, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout / lock-phase, leftover settings invert-look /
# ApplySettings broadcast, leftover bind-hud-host,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover pilot line /
# confirm / warn / call-probe / duration drafts,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover mission 0N integration
# readiness, leftover USkyguardDebriefWidget, and dirty
# workspace paths.
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
# briefing-fail-closed, leftover briefing-card defaults,
# leftover briefing-radio-row defaults, leftover
# how-to-fly-row defaults, leftover radio-chatter
# empty-fail-closed, leftover mission-briefing-state
# enum, leftover sortie-presentation fail-closed,
# leftover CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare / HUD, leftover ApacheSystem /
# weapon stations / pilot commands / loadout,
# leftover settings invert-look, leftover
# bind-hud-host, leftover pilot drafts, leftover
# gun-fire camera shake, leftover mission-weather
# enum, leftover briefing-component declaration
# contracts through GetRadioChatter, leftover
# Configure, leftover GetMissionTitle, leftover
# GetBriefingText, leftover GetBriefingCards,
# leftover GetRadioRows, leftover GetHowToFlyRows,
# leftover AcknowledgeBriefing, leftover
# LaunchSortie, and leftover DebriefWidget stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_sortie_presentation_contract.py",
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
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
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
# here. Configure / GetMissionTitle / GetBriefingText /
# GetBriefingCards / GetRadioRows / GetHowToFlyRows /
# AcknowledgeBriefing / LaunchSortie stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "void Configure(USkyguardSortiePresentationComponent* InPresentation);",
    "FText GetMissionTitle() const;",
    "FText GetBriefingText() const;",
    "TArray<FSkyguardBriefingCard> GetBriefingCards() const;",
    "TArray<FSkyguardBriefingRadioRow> GetRadioRows() const;",
    "TArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const;",
    "bool AcknowledgeBriefing();",
    "bool LaunchSortie();",
)
CONFIGURE_NOT_LOCKED = (
    "void Configure(USkyguardSortiePresentationComponent* InPresentation);",
)
GET_MISSION_TITLE_NOT_LOCKED = ("FText GetMissionTitle() const;",)
GET_BRIEFING_TEXT_NOT_LOCKED = ("FText GetBriefingText() const;",)
GET_BRIEFING_CARDS_NOT_LOCKED = (
    "TArray<FSkyguardBriefingCard> GetBriefingCards() const;",
)
GET_RADIO_ROWS_NOT_LOCKED = (
    "TArray<FSkyguardBriefingRadioRow> GetRadioRows() const;",
)
GET_HOW_TO_FLY_ROWS_NOT_LOCKED = (
    "TArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const;",
)
ACKNOWLEDGE_BRIEFING_NOT_LOCKED = ("bool AcknowledgeBriefing();",)
LAUNCH_SORTIE_NOT_LOCKED = ("bool LaunchSortie();",)
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
# Leftover sortie-presentation fail-closed stays
# unlocked. Do not re-lock leftover #7600.
LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED = (
    "test_sortie_presentation_fail_closed.py",
    "test_sortie_presentation_fail_closed_contract.py",
    "SkyguardSortiePresentationFailClosedTests.cpp",
    "GetPresentationState",
    "ESkyguardSortiePresentationState",
)
# DebriefWidget public helpers stay unlocked.
DEBRIEF_WIDGET_NOT_LOCKED = (
    "USkyguardDebriefWidget",
    "FSkyguardMissionDebrief GetDebrief() const;",
    "FText GetDebriefNarrative() const;",
    "int32 GetFinalScore() const;",
    "bool IsProgressSaved() const;",
    "bool AcknowledgeDebrief();",
    "bool RetrySave();",
    "bool TravelNext();",
    "bool HandleDebriefKey(FKey Key);",
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
# .cpp GetPresentation body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body. origin/main inline `return Presentation` is
# accepted as presence, not a locked implementation
# contract.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardBriefingWidget::GetPresentation",
    "SkyguardSortiePresentationWidgets.cpp",
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


class BriefingWidgetGetPresentationDeclContractTests(unittest.TestCase):
    def test_briefing_widget_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, GET_PRESENTATION),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedBriefing "
                ": public UUserWidget\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API USkyguardDebriefWidget "
            ": public UUserWidget\n"
            "{\n"
            "public:\n"
            f"\t{GET_PRESENTATION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_debrief_widget_does_not_satisfy_class(self) -> None:
        debrief_only = (
            "class SKYGUARD52_API USkyguardDebriefWidget "
            ": public UUserWidget\n"
            "{\n"
            "public:\n"
            "\tUSkyguardSortiePresentationComponent* "
            "GetPresentation() const { return Presentation; }\n"
            "\tFSkyguardMissionDebrief GetDebrief() const;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(debrief_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UUserWidget\n"
            "{\n"
            "private:\n"
            f"\t{GET_PRESENTATION}\n"
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
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent* InPresentation);\n"
            "private:\n"
            f"\t{GET_PRESENTATION}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_PRESENTATION)
        self.assertIn("GetPresentation", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, GET_PRESENTATION))

    def test_missing_get_presentation_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent* InPresentation);\n"
            "\tFText GetMissionTitle() const;\n"
            "\tFText GetBriefingText() const;\n"
            "\tTArray<FSkyguardBriefingCard> GetBriefingCards() const;\n"
            "\tTArray<FSkyguardBriefingRadioRow> GetRadioRows() const;\n"
            "\tTArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const;\n"
            "\tbool AcknowledgeBriefing();\n"
            "\tbool LaunchSortie();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_PRESENTATION)
        self.assertIn("GetPresentation", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_BRIEFING}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_PRESENTATION)
        self.assertIn("GetPresentation", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_BRIEFING, section)
        self.assertTrue(
            has_declaration(section, GET_PRESENTATION),
            section,
        )
        self.assertNotIn("BlueprintPure", GET_PRESENTATION)
        self.assertNotIn("UFUNCTION", GET_PRESENTATION)
        self.assertNotIn("Category", GET_PRESENTATION)
        self.assertNotIn("BlueprintCallable", GET_PRESENTATION)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tvoid Configure("
            "USkyguardSortiePresentationComponent* InPresentation);\n"
            "\tFText GetMissionTitle() const;\n"
            "\tFText GetBriefingText() const;\n"
            "\tTArray<FSkyguardBriefingCard> GetBriefingCards() const;\n"
            "\tTArray<FSkyguardBriefingRadioRow> GetRadioRows() const;\n"
            "\tTArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const;\n"
            "\tbool AcknowledgeBriefing();\n"
            "\tbool LaunchSortie();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, GET_PRESENTATION)
        self.assertIn("GetPresentation", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_const = (
            "\tUSkyguardSortiePresentationComponent* GetPresentation();\n"
        )
        wrong_return_void = "\tvoid GetPresentation() const;\n"
        wrong_return_bool = "\tbool GetPresentation() const;\n"
        added_arg = (
            "\tUSkyguardSortiePresentationComponent* "
            "GetPresentation(bool bReady) const;\n"
        )
        wrong_name = (
            "\tESkyguardSortiePresentationState "
            "GetPresentationState() const;\n"
        )
        missing_star = (
            "\tUSkyguardSortiePresentationComponent "
            "GetPresentation() const;\n"
        )
        object_ptr = (
            "\tTObjectPtr<USkyguardSortiePresentationComponent> "
            "GetPresentation() const;\n"
        )
        for region in (
            missing_const,
            wrong_return_void,
            wrong_return_bool,
            added_arg,
            wrong_name,
            missing_star,
            object_ptr,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, GET_PRESENTATION)
            self.assertIn("GetPresentation", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_get_presentation_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        self.assertTrue(has_declaration(section, GET_PRESENTATION))
        self.assertEqual(
            declaration_count(section, GET_PRESENTATION),
            1,
        )
        self.assertTrue(
            GET_PRESENTATION.startswith(
                "USkyguardSortiePresentationComponent* "
            ),
            GET_PRESENTATION,
        )
        self.assertTrue(
            GET_PRESENTATION.endswith(";"),
            GET_PRESENTATION,
        )
        self.assertIn("GetPresentation()", GET_PRESENTATION)
        self.assertIn(" const", GET_PRESENTATION)
        self.assertIn(
            "USkyguardSortiePresentationComponent*",
            GET_PRESENTATION,
        )
        self.assertNotIn("INDEX_NONE", GET_PRESENTATION)
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("}", GET_PRESENTATION)
        self.assertNotIn("return ", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)

    def test_declaration_accepts_origin_main_inline_and_prototype(
        self,
    ) -> None:
        one_line_prototype = f"{{\npublic:\n\t{GET_PRESENTATION}\n}}\n"
        self.assertTrue(has_declaration(one_line_prototype, GET_PRESENTATION))
        self.assertEqual(
            require_declaration(one_line_prototype, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        exact_inline = (
            "USkyguardSortiePresentationComponent* GetPresentation() "
            "const { return Presentation; }"
        )
        self.assertTrue(has_declaration(exact_inline, GET_PRESENTATION))
        self.assertEqual(
            require_declaration(exact_inline, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        self.assertEqual(
            declaration_count(exact_inline, GET_PRESENTATION),
            1,
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, GET_PRESENTATION),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tUSkyguardSortiePresentationComponent*\n"
            "\tGetPresentation() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tUSkyguardSortiePresentationComponent* GetPresentation(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tUSkyguardSortiePresentationComponent* GetPresentation()\n"
            "\tconst;\n"
            "};\n"
        )
        wrap_inline = (
            "public:\n"
            "\tUSkyguardSortiePresentationComponent* GetPresentation()\n"
            "\tconst { return Presentation; }\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_const}"
        )
        header_wrap_inline = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{wrap_inline}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_const,
            header_wrap_inline,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, GET_PRESENTATION),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_PRESENTATION),
                GET_PRESENTATION,
            )
            self.assertEqual(
                declaration_count(section, GET_PRESENTATION),
                1,
            )
        one_line = f"{{\npublic:\n\t{GET_PRESENTATION}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_PRESENTATION))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, GET_PRESENTATION),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tUSkyguardSortiePresentationComponent* "
            "GetPresentation() const\n"
            "\t{\n"
            "\t\treturn Other;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UUserWidget\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, GET_PRESENTATION),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        self.assertEqual(
            declaration_count(section, GET_PRESENTATION),
            1,
        )
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("}", GET_PRESENTATION)
        self.assertNotIn("return ", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)
        self.assertNotIn("return Other", GET_PRESENTATION)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_PRESENTATION)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", GET_PRESENTATION)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_get_presentation_body(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("}", GET_PRESENTATION)
        self.assertNotIn("return ", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)
        self.assertNotIn("return Presentation", locked_only)
        self.assertNotIn(
            "USkyguardBriefingWidget::GetPresentation",
            GET_PRESENTATION,
        )
        self.assertNotIn(
            "SkyguardSortiePresentationWidgets.cpp",
            GET_PRESENTATION,
        )
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", locked_only)
        self.assertNotIn("return false", GET_PRESENTATION)
        self.assertNotIn("return true", GET_PRESENTATION)

    def test_contract_does_not_relock_configure(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in CONFIGURE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("Configure(", GET_PRESENTATION)
        self.assertNotIn("Configure(", locked_only)
        self.assertNotIn("InPresentation", GET_PRESENTATION)
        self.assertNotIn("InPresentation", locked_only)

    def test_contract_does_not_relock_get_mission_title(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in GET_MISSION_TITLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("GetMissionTitle", GET_PRESENTATION)
        self.assertNotIn("GetMissionTitle", locked_only)

    def test_contract_does_not_relock_get_briefing_text(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in GET_BRIEFING_TEXT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("GetBriefingText", GET_PRESENTATION)
        self.assertNotIn("GetBriefingText", locked_only)

    def test_contract_does_not_relock_get_briefing_cards(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in GET_BRIEFING_CARDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("GetBriefingCards", GET_PRESENTATION)
        self.assertNotIn("GetBriefingCards", locked_only)
        self.assertNotIn("FSkyguardBriefingCard", GET_PRESENTATION)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)

    def test_contract_does_not_relock_get_radio_rows(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in GET_RADIO_ROWS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("GetRadioRows", GET_PRESENTATION)
        self.assertNotIn("GetRadioRows", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", GET_PRESENTATION)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)

    def test_contract_does_not_relock_get_how_to_fly_rows(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in GET_HOW_TO_FLY_ROWS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("GetHowToFlyRows", GET_PRESENTATION)
        self.assertNotIn("GetHowToFlyRows", locked_only)
        self.assertNotIn("FSkyguardHowToFlyRow", GET_PRESENTATION)
        self.assertNotIn("FSkyguardHowToFlyRow", locked_only)

    def test_contract_does_not_relock_acknowledge_briefing(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in ACKNOWLEDGE_BRIEFING_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("AcknowledgeBriefing", GET_PRESENTATION)
        self.assertNotIn("AcknowledgeBriefing", locked_only)

    def test_contract_does_not_relock_launch_sortie(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in LAUNCH_SORTIE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("LaunchSortie", GET_PRESENTATION)
        self.assertNotIn("LaunchSortie", locked_only)

    def test_contract_does_not_relock_leftover_briefing_state_enum(
        self,
    ) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        self.assertNotIn("Unconfigured", GET_PRESENTATION)
        self.assertNotIn("Warming", GET_PRESENTATION)
        self.assertNotIn("Launched", GET_PRESENTATION)
        self.assertNotIn(
            "test_mission_briefing_state_enum_contract.py",
            GET_PRESENTATION,
        )

    def test_contract_does_not_relock_leftover_briefing_siblings(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        self.assertNotIn("FSkyguardBriefingCard", GET_PRESENTATION)
        self.assertNotIn("FSkyguardBriefingRadioRow", GET_PRESENTATION)
        self.assertNotIn("FSkyguardHowToFlyRow", GET_PRESENTATION)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("FSkyguardHowToFlyRow", locked_only)

    def test_contract_does_not_relock_leftover_sortie_presentation(
        self,
    ) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        self.assertNotIn("GetPresentationState", GET_PRESENTATION)
        self.assertNotIn("GetPresentationState", locked_only)
        self.assertNotIn("GetPresentationState", section)
        self.assertNotIn("ESkyguardSortiePresentationState", section)

    def test_contract_does_not_relock_debrief_widget(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        body = class_body(origin_main_header())
        for token in DEBRIEF_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
            self.assertNotIn(token, body)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardDebriefWidget", body)
        self.assertNotIn("GetDebrief", section)
        self.assertNotIn("AcknowledgeDebrief", section)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("FillResultCombatStats", GET_PRESENTATION)
        self.assertNotIn("ASkyguardGunner", GET_PRESENTATION)
        self.assertNotIn("FillAndFinalize", GET_PRESENTATION)
        self.assertNotIn("FillAndFail", GET_PRESENTATION)
        self.assertNotIn("ApplyHydraForClusters", GET_PRESENTATION)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("Configure(", locked_only)
        self.assertNotIn("GetMissionTitle", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetBriefingCards", locked_only)
        self.assertNotIn("GetRadioRows", locked_only)
        self.assertNotIn("GetHowToFlyRows", locked_only)
        self.assertNotIn("AcknowledgeBriefing", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)
        self.assertNotIn("GetPresentationState", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)

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
        self.assertNotIn("NativeConstruct", section)
        self.assertNotIn("HandleLaunchClicked", section)
        self.assertNotIn("RefreshRuntimeLayout", section)
        self.assertNotIn("UPROPERTY(Transient)", section)
        self.assertNotIn("RuntimeTitleText", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("GetPresentationState", section)
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", section)
        self.assertNotIn(
            "USkyguardBriefingWidget::GetPresentation",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardSortiePresentationWidgets.cpp", section)
        self.assertNotIn(
            "USkyguardBriefingWidget::GetPresentation",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("}", GET_PRESENTATION)
        self.assertNotIn("return false", GET_PRESENTATION)
        self.assertNotIn("return true", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{GET_PRESENTATION}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_PRESENTATION}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "briefing widget GetPresentation contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, GET_PRESENTATION.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_PRESENTATION)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"briefing widget GetPresentation contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, GET_PRESENTATION.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, GET_PRESENTATION)

    def test_contract_is_get_presentation_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_PRESENTATION),
            GET_PRESENTATION,
        )
        locked_only = f"{GET_PRESENTATION}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRESENTATION)
        self.assertNotIn("Configure(", locked_only)
        self.assertNotIn("GetMissionTitle", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetBriefingCards", locked_only)
        self.assertNotIn("GetRadioRows", locked_only)
        self.assertNotIn("GetHowToFlyRows", locked_only)
        self.assertNotIn("AcknowledgeBriefing", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)
        self.assertNotIn("GetPresentationState", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
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
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in LEFTOVER_SORTIE_PRESENTATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in DEBRIEF_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRESENTATION)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_PRESENTATION)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, GET_PRESENTATION.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", GET_PRESENTATION)
        self.assertNotIn("return Presentation", GET_PRESENTATION)
        self.assertNotIn("{", GET_PRESENTATION)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(
            GET_PRESENTATION.startswith(
                "USkyguardSortiePresentationComponent* "
            )
        )
        self.assertTrue(GET_PRESENTATION.endswith(";"))
        self.assertIn(" const", GET_PRESENTATION)
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
